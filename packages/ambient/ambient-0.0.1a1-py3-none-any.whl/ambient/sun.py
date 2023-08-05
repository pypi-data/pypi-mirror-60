"""Calculate sunlit fraction for surfaces."""

from dataclasses import dataclass, field
from typing import Sequence, Union

import numpy as np

from deltaq.base import BaseElement
from deltaq.surface import Surface
from deltaq.location import Location
from deltaq.time import Time

PIXEL_SIZE = 0.001


def _calculate_equation_of_time(day: int):
    """Calculate the declination angle."""
    gamma = 2 * np.pi * (day - 1) / 365
    equation_of_time = 2.2918 * (
        0.0075
        + 0.1868 * np.cos(gamma)
        - 3.2077 * np.sin(gamma)
        - 1.4615 * np.cos(2 * gamma)
        - 4.089 * np.sin(2 * gamma)
    )

    declination = (
        0.3963723
        - 22.9132745 * np.cos(gamma)
        + 4.0254304 * np.sin(gamma)
        - 0.387205 * np.cos(2 * gamma)
        + 0.05196728 * np.sin(2 * gamma)
        - 0.1545267 * np.cos(3 * gamma)
        + 0.08479777 * np.sin(3 * gamma)
    )

    return equation_of_time, declination


@dataclass
class Sun(BaseElement):
    """Sun related calculations."""

    surfaces: Union[Sequence[Surface], None] = None
    sun_direction: np.array = None
    time: Union[Time, None] = None
    location: Union[Location, None] = None
    _vertices: np.array = field(default=None, init=False)
    _normals: np.array = field(default=None, init=False)
    _projection_matrix: np.array = field(default=None, init=False)

    def __post_init__(self):
        """Set normals and vertices."""
        self.create_projection_matrix()
        self._vertices = np.array(
            [v for s in self.surfaces for v in s.vertices], dtype=np.float64
        )
        self._normals = np.array([s.normal for s in self.surfaces], dtype=np.float64)

    def resolve_references(self, references):
        """Resolve time and location guids."""
        self.time = self._resolve_element(self.time, references)
        self.location = self._resolve_element(self.location, references)

    def calculate_sunlit_fractions(self):
        """Calculate the sunlit fraction of surfaces."""
        self.create_projection_matrix()

        projected_vertices = self._vertices @ self._projection_matrix

        num_surfaces = len(self.surfaces)

        # shift minimum point to the origin
        projected_vertices -= np.amin(projected_vertices, axis=0)

        # determine the limits so we can create the "pixel" layout
        bounds = np.amax(projected_vertices, axis=0)[:2]

        # num_points = (np.around(bounds / PIXEL_SIZE) + (1, 1)).astype(np.int64)
        num_points = np.around(bounds / PIXEL_SIZE).astype(np.int64)
        pixels = np.full((num_points[1], num_points[0]), -1, dtype=np.int64)
        depths = np.full((num_points[1], num_points[0]), np.inf, dtype=np.float64)
        pixel_count = np.zeros(len(self.surfaces), dtype=np.int64)

        # calculate all matrices
        matrices = projected_vertices.reshape(-1, 3, 3)
        z_comps = np.copy(matrices[:, :, 2])

        # calculate bounds
        lower_bounds = np.around(np.amin(matrices, axis=1)[:, :2] / PIXEL_SIZE).astype(
            np.int64
        )
        upper_bounds = np.around(np.amax(matrices, axis=1)[:, :2] / PIXEL_SIZE).astype(
            np.int64
        )

        # bounds slices
        bounds = [
            (slice(lb[1], ub[1]), slice(lb[0], ub[0]))
            for lb, ub in zip(lower_bounds, upper_bounds)
        ]

        matrices[:, :, 2] = 1.0
        inv_matrices = np.linalg.inv(matrices)

        # create the grid of pixels for the triangle bounds
        x_coord = np.arange(0, num_points[0], dtype=np.float64) * PIXEL_SIZE
        y_coord = np.arange(0, num_points[1], dtype=np.float64) * PIXEL_SIZE
        x_grid, y_grid = np.meshgrid(x_coord, y_coord)
        z_grid = np.ones_like(x_grid)
        grids = np.dstack((x_grid, y_grid, z_grid))

        for idx, (bound, inv_matrix) in enumerate(zip(bounds, inv_matrices)):
            lambdas = grids[bound] @ inv_matrix
            in_tri_mask = np.logical_and(
                np.all(lambdas >= 0.0, axis=-1), np.all(lambdas <= 1.0, axis=-1)
            )

            # count pixels for each surface before depth testing
            pixel_count[idx] = np.count_nonzero(in_tri_mask)

            # calculate depths
            depth_bounds = lambdas @ z_comps[idx]
            depth_mask = np.logical_and(in_tri_mask, depth_bounds < depths[bound])
            depths[bound][depth_mask] = depth_bounds[depth_mask]

            pixels[bound][depth_mask] = idx

        return pixels

    def create_projection_matrix(self):
        """Create a projection matrix based on sun direction."""
        basis = np.ndarray((3, 3))

        basis[0] = self.sun_direction
        basis[0] /= np.linalg.norm(basis[0])
        basis[1] = (0, 0, 1)
        basis[2] = (1, 0, 0)

        if abs(np.dot(basis[0], basis[1])) >= 0.99:
            basis[1] = (0, 1, 0)

        # make the projection matrix orthonormal using Gram-Schmidt
        for i in range(3):
            basis[i] /= np.linalg.norm(basis[i])
            for j in range(i + 1, 3):
                basis[j] -= np.dot(basis[i], basis[j]) * basis[i]

        self._projection_matrix = np.fliplr(basis.T)
