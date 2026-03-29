"""Domain exceptions for the Adult Bucket bounded context."""

from __future__ import annotations

from merygoround.domain.shared.exceptions import DomainException


class ActiveDrawExistsError(DomainException):
    """Raised when a user attempts to draw while already having an active draw."""

    def __init__(self) -> None:
        super().__init__("An active draw already exists. Resolve or return it first.")


class NoBucketItemsError(DomainException):
    """Raised when no bucket items are available for drawing."""

    def __init__(self) -> None:
        super().__init__("No bucket items available for drawing.")


class DrawNotActiveError(DomainException):
    """Raised when attempting to resolve or return a draw that is not active."""

    def __init__(self) -> None:
        super().__init__("Draw is not in ACTIVE status.")


class JustificationTooShortError(DomainException):
    """Raised when a return justification is shorter than the minimum length."""

    def __init__(self) -> None:
        super().__init__("Justification must be at least 10 characters long.")


class BucketItemNotFoundError(DomainException):
    """Raised when a bucket item cannot be found.

    Args:
        item_id: The identifier used in the lookup.
    """

    def __init__(self, item_id: str = "") -> None:
        msg = f"Bucket item not found: '{item_id}'" if item_id else "Bucket item not found"
        super().__init__(msg)
