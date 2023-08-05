"""Location related objects."""

from dataclasses import dataclass

from deltaq.base import BaseElement


@dataclass
class Location(BaseElement):
    """Location class."""

    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0
