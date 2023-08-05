"""Time related classes."""

from dataclasses import dataclass, field

from deltaq.base import BaseElement


@dataclass
class Time(BaseElement):
    """Time object."""

    timestep: int = 1
    start_time: int = 0
    current_time: int = field(default=0, init=False)

    def __post_init__(self):
        """Set the current time from start time."""
        self.current_time = self.start_time

    def update(self):
        """Update the time."""
        self.current_time += self.timestep

    @property
    def day(self):
        """Return day component of current time."""
        return self.current_time // 24 + 1

    @property
    def hour(self):
        """Return hour component of current time."""
        _, hour = divmod(self.current_time, 24)
        return hour
