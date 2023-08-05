"""Material classes and helpers."""

from dataclasses import dataclass
from typing import Union

from deltaq.base import BaseElement


@dataclass
class Material(BaseElement):
    """Class for representing material properties."""

    name: str = ""
    density: float = None
    specific_heat: float = None
    conductivity: float = None
    resistance: float = None
    valid_thickness: Union[float, tuple, None] = None

    def __post_init__(self):
        """Do some post-init checks."""
        if self.resistance is not None:
            assert self.conductivity is None

    def is_valid_thickness(self, thickness: float) -> bool:
        """Determine if a given thickness is valid.

        Args:
            thickness (float): Thickness to check validity of.

        Returns:
            bool: True if thickness lies in valid range.
        """
        if self.valid_thickness is None:
            return True

        if isinstance(self.valid_thickness, float):
            return self.valid_thickness == thickness

        if isinstance(self.valid_thickness, (list, tuple)):
            return self.valid_thickness[0] <= thickness <= self.valid_thickness[1]

        raise ValueError(
            f"thickness: {thickness} not in valid range: {self.valid_thickness}"
        )

    def calculate_resistance(self, thickness: float) -> float:
        """Calculate the resistance for a given thickness.

        Args:
            thickness (float): Thickness to use for calculation.

        Returns:
            float: The resistance of the given material thickness.
        """
        return self.resistance or thickness / self.conductivity


class MaterialLayer:
    """Class to represent a material layer."""

    def __init__(self, material: Material, thickness: float) -> None:
        """Create a material layer.

        Args:
            material (Material): Material used in the layer.
            thickness (float): Thickness of the material layer.
        """
        self.material = material
        self.thickness = thickness
        self._validate()

    def _validate(self) -> bool:
        return self.material.is_valid_thickness(self.thickness)

    @property
    def resistance(self) -> float:
        """Calculate the resistance of the layer."""
        return self.material.calculate_resistance(self.thickness)
