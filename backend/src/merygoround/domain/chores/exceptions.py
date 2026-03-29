"""Domain exceptions for the Chores bounded context."""

from __future__ import annotations

from merygoround.domain.shared.exceptions import DomainException


class ChoreNotFoundError(DomainException):
    """Raised when a chore cannot be found.

    Args:
        chore_id: The identifier used in the lookup.
    """

    def __init__(self, chore_id: str = "") -> None:
        msg = f"Chore not found: '{chore_id}'" if chore_id else "Chore not found"
        super().__init__(msg)


class InvalidDurationError(DomainException):
    """Raised when a chore duration is outside the 1-10 minute range.

    Args:
        duration: The invalid duration value.
    """

    def __init__(self, duration: int) -> None:
        super().__init__(f"Invalid chore duration: {duration}. Must be between 1 and 10 minutes.")


class InvalidMultiplicityError(DomainException):
    """Raised when a wheel multiplicity value is less than 1.

    Args:
        multiplicity: The invalid multiplicity value.
    """

    def __init__(self, multiplicity: int) -> None:
        super().__init__(f"Invalid multiplicity: {multiplicity}. Must be >= 1.")
