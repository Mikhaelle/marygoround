"""Domain exceptions for the Notification bounded context."""

from __future__ import annotations

from merygoround.domain.shared.exceptions import DomainException


class SubscriptionNotFoundError(DomainException):
    """Raised when a push subscription cannot be found.

    Args:
        endpoint: The endpoint used in the lookup.
    """

    def __init__(self, endpoint: str = "") -> None:
        msg = (
            f"Push subscription not found for endpoint: '{endpoint}'"
            if endpoint
            else "Push subscription not found"
        )
        super().__init__(msg)
