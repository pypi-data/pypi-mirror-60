"""Surfaces for simulation."""


class Boundary:
    """Class for surface boundary definitions."""

    def __init__(self, temperature):
        """Create a boundary definition."""
        self._temperature = temperature

    @property
    def temperature(self):
        """Temperature of surface boundary."""
        return self._temperature
