"""Base domain exceptions used across all bounded contexts."""

from __future__ import annotations


class DomainException(Exception):
    """Base exception for all domain-level errors.

    Args:
        message: Human-readable error description.
    """

    def __init__(self, message: str = "A domain error occurred") -> None:
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(DomainException):
    """Raised when a requested entity does not exist.

    Args:
        entity_type: Name of the entity type.
        entity_id: Identifier of the missing entity.
    """

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(f"{entity_type} with id '{entity_id}' not found")


class ValidationError(DomainException):
    """Raised when a domain invariant or value object constraint is violated.

    Args:
        message: Description of the validation failure.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class AuthorizationError(DomainException):
    """Raised when an operation is not permitted for the current user.

    Args:
        message: Description of the authorization failure.
    """

    def __init__(self, message: str = "Not authorized") -> None:
        super().__init__(message)
