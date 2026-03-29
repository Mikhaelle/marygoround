"""Domain exceptions for the Identity bounded context."""

from __future__ import annotations

from merygoround.domain.shared.exceptions import DomainException


class UserNotFoundError(DomainException):
    """Raised when a user cannot be found.

    Args:
        identifier: The email or id used in the lookup.
    """

    def __init__(self, identifier: str = "") -> None:
        msg = f"User not found: '{identifier}'" if identifier else "User not found"
        super().__init__(msg)


class DuplicateEmailError(DomainException):
    """Raised when attempting to register with an already-used email.

    Args:
        email: The duplicate email address.
    """

    def __init__(self, email: str) -> None:
        super().__init__(f"Email already registered: '{email}'")


class InvalidCredentialsError(DomainException):
    """Raised when login credentials are incorrect."""

    def __init__(self) -> None:
        super().__init__("Invalid email or password")
