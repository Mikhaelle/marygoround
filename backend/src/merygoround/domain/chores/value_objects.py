"""Value objects for the Chores bounded context."""

from __future__ import annotations

from dataclasses import dataclass

from merygoround.domain.shared.exceptions import ValidationError

ALLOWED_DURATIONS = (5, 10)
MAX_TIME_WEIGHT = 3.0


@dataclass(frozen=True)
class Duration:
    """Represents chore estimated duration in minutes.

    Must be either 5 or 10 minutes.

    Args:
        value: Duration in minutes.
    """

    value: int

    def __post_init__(self) -> None:
        if self.value not in ALLOWED_DURATIONS:
            raise ValidationError(
                f"Duration must be one of {ALLOWED_DURATIONS}, got {self.value}"
            )


@dataclass(frozen=True)
class Multiplicity:
    """Represents how many slots a chore occupies on the wheel.

    Must be an integer greater than or equal to 1.

    Args:
        value: Number of wheel slots.
    """

    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value < 1:
            raise ValidationError(f"Multiplicity must be >= 1, got {self.value}")


@dataclass(frozen=True)
class TimeWeightRule:
    """Maps an hour of the day to a probability weight for wheel spinning.

    Args:
        hour: Hour of the day (0-23).
        weight: Positive float weight up to 3.0.
    """

    hour: int
    weight: float

    def __post_init__(self) -> None:
        if not isinstance(self.hour, int) or self.hour < 0 or self.hour > 23:
            raise ValidationError(f"Hour must be an integer between 0 and 23, got {self.hour}")
        if not isinstance(self.weight, (int, float)) or self.weight <= 0:
            raise ValidationError(f"Weight must be a positive number, got {self.weight}")
        if self.weight > MAX_TIME_WEIGHT:
            raise ValidationError(
                f"Weight must be at most {MAX_TIME_WEIGHT}, got {self.weight}"
            )
