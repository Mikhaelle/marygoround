"""Domain exceptions for the Wheel bounded context."""

from __future__ import annotations

from merygoround.domain.shared.exceptions import DomainException


class NoChoresAvailableError(DomainException):
    """Raised when attempting to spin the wheel with no available chores."""

    def __init__(self) -> None:
        super().__init__("No chores available for spinning. Add at least one chore first.")
