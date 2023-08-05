"""Surfaces for simulation."""

from dataclasses import dataclass, field
from typing import List

import numpy as np

from deltaq.base import BaseElement
from deltaq.material import Material
from deltaq.boundary import Boundary


def _calculate_frequencies():
    """Calculate the frequencies for the FDR method."""
    # frequency parameters
    lower_limit_power = 9  # n1
    upper_limit_power = 3  # n2
    num_freqs = 9 * (lower_limit_power - upper_limit_power) + 1

    return np.logspace(-lower_limit_power, -upper_limit_power, num=num_freqs)


def _calculate_response_functions(response_matrix):
    """Calculate the response functions for FDR method."""
    response_functions = 1.0 / response_matrix[:, 0, 1]
    response_functions = np.tile(response_functions, (3, 1))
    response_functions[0] *= response_matrix[:, 0, 0]
    response_functions[2] *= response_matrix[:, 1, 1]

    return response_functions


def _resistance_only_matrix(resistance):
    matrix = np.identity(2)
    matrix[0, 1] = resistance
    return matrix


def _create_gamma_matrix_theta_vector(poly_order_r, poly_order_m, d_w, g_vec):
    # V submatrix
    v_submatrix = np.zeros((poly_order_r + 1, poly_order_r + 1))
    for i in range(poly_order_r + 1):
        for j in range(i, poly_order_r + 1):
            v_submatrix[i, j] = np.sum(
                np.sin(i * d_w) * np.sin(j * d_w) + np.cos(i * d_w) * np.cos(j * d_w)
            )

    # U submatrix
    u_submatrix = np.zeros((poly_order_m + 1, poly_order_m + 1))
    for i in range(poly_order_m + 1):
        for j in range(i, poly_order_m + 1):
            u_submatrix[i, j] = np.sum(
                (np.sin(i * d_w) * np.sin(j * d_w) + np.cos(i * d_w) * np.cos(j * d_w))
                * (g_vec.real ** 2 + g_vec.imag ** 2)
            )

    # S submatrices
    s_submatrix = np.zeros((poly_order_r + 1, poly_order_m + 1))
    for i in range(poly_order_r + 1):
        for j in range(poly_order_m + 1):
            s_submatrix[i, j] = np.sum(
                -(np.sin(i * d_w) * np.sin(j * d_w) + np.cos(i * d_w) * np.cos(j * d_w))
                * g_vec.real
                + (
                    np.sin(i * d_w) * np.cos(j * d_w)
                    - np.cos(i * d_w) * np.sin(j * d_w)
                )
                * g_vec.imag
            )

    gamma = np.block(
        [
            [v_submatrix, s_submatrix[:, 1:]],
            [np.zeros_like(s_submatrix[:, 1:].T), u_submatrix[1:, 1:]],
        ]
    )
    diag = np.diag(np.diag(gamma))
    gamma += gamma.T
    gamma -= diag

    # calculate the theta vector
    theta = np.zeros(poly_order_r + poly_order_m + 1)
    theta[: poly_order_r + 1] = -s_submatrix[:, 0]
    theta[poly_order_r + 1 :] = -u_submatrix[1:, 0]

    return gamma, theta


@dataclass
class Surface(BaseElement):
    """Class for surfaces."""

    materials: List[Material] = field(default_factory=list)  # outside to inside
    thicknesses: List[float] = field(default_factory=list)
    boundaries: List[Boundary] = field(default_factory=list)
    vertices: np.array = field(default_factory=list)
    normal: np.array = field(default_factory=list)

    def __post_init__(self):
        """Do post-init checks."""
        assert len(self.materials) == len(self.thicknesses)
        assert len(self.vertices) == 3
        self.normal = np.cross(
            self.vertices[1] - self.vertices[0], self.vertices[2] - self.vertices[0]
        )

    def resolve_references(self, references):
        """Resolve material guids."""
        self.materials = [self._resolve_element(m, references) for m in self.materials]

    def get_dependencies(self):
        """Return the guids of element dependencies."""
        return {m.guid for m in self.materials}

    @property
    def layer_count(self):
        """Return the number of layers in the surface."""
        return len(self.thicknesses)

    @property
    def conductivity(self):
        """Layer conductivity."""
        return np.fromiter((m.conductivity for m in self.materials), np.float)

    @property
    def density(self):
        """Layer density."""
        return np.fromiter((m.density for m in self.materials), np.float)

    @property
    def specific_heat(self):
        """Layer specific heat."""
        return np.fromiter((m.specific_heat for m in self.materials), np.float)

    @property
    def sunlit_fraction(self):
        """Surface sunlit fraction."""
        return self._sunlit_fraction[self.time.timestep]

    @sunlit_fraction.setter
    def sunlit_fraction(self, value):
        """Set the sunlit fraction."""
        self._sunlit_fraction[self.time.timestep] = value

    def _calculate_response_matrix(self, frequencies):
        # use 1/sqrt(diffusivity) since that's what we use later
        layer_diffusivity = self.density * self.specific_heat / self.conductivity
        np.sqrt(layer_diffusivity, out=layer_diffusivity)

        layer_resistance = self.thicknesses / self.conductivity

        # common args for sinh/cosh
        value_grid = np.outer(
            self.thicknesses * layer_diffusivity, np.sqrt(frequencies * 1.0j)
        )

        # precompute sinh value
        sinh = np.sinh(value_grid)

        # matrix components
        a_component = d_component = np.cosh(value_grid)
        b_component = layer_resistance[:, np.newaxis] * sinh / value_grid
        c_component = value_grid * sinh / layer_resistance[:, np.newaxis]

        layer_matrices = np.dstack((a_component, b_component, c_component, d_component))
        layer_matrices = layer_matrices.reshape(layer_matrices.shape[:-1] + (2, 2))

        # calculate the product over all layers
        # XXX: can this be vectorised?
        ms_matrix = layer_matrices[0]
        for i in range(1, self.layer_count):
            ms_matrix = layer_matrices[i] @ ms_matrix

        # XXX: needs to adapt to actual boundary conditions class
        mout_matrix = _resistance_only_matrix(self.boundaries[0])
        min_matrix = _resistance_only_matrix(self.boundaries[1])

        ms_matrix = min_matrix @ ms_matrix @ mout_matrix

        return ms_matrix

    def calculate_ctfs(self, timestep=3600):
        """Calculate the CTFs for the surface."""
        frequencies = _calculate_frequencies()
        response_matrix = self._calculate_response_matrix(frequencies)
        response_functions = _calculate_response_functions(response_matrix)

        poly_order_r = 4  # b
        poly_order_m = 4  # d

        # calculate two parts of matrix from eq. 21
        # b_comp = np.exp(
        #     np.outer(-1.0j * timestep * frequencies, np.arange(poly_order_r + 1))
        # )
        # d_comp = np.exp(
        #     np.outer(-1.0j * timestep * frequencies, np.arange(1, poly_order_m + 1))
        # )

        # identity_matrix = np.identity(len(frequencies))

        ctf = np.ndarray((3, poly_order_r + poly_order_m + 1))

        # now calculate for each g matrix
        for idx, g_vec in enumerate(response_functions):
            d_w = timestep * frequencies

            gamma, theta = _create_gamma_matrix_theta_vector(
                poly_order_r, poly_order_m, d_w, g_vec
            )

            # calculate the ctf
            # g_tile = np.tile(g_vec, (poly_order_m, 1)).T
            # h_matrix = np.concatenate((b_comp, d_comp * g_tile), axis=1)
            # gamma = np.real(h_matrix.T @ identity_matrix @ h_matrix)
            # theta = np.real(h_matrix.T @ identity_matrix @ g_vec)

            ctf[idx, :] = np.linalg.solve(gamma, theta)

        ctf = np.insert(ctf, poly_order_r + 1, 1, axis=1)

        return ctf
