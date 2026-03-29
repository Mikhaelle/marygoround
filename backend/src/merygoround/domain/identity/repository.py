"""Repository interface for the Identity bounded context."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from merygoround.domain.identity.entities import User
from merygoround.domain.identity.value_objects import Email


class UserRepository(ABC):
    """Abstract repository for User aggregate persistence."""

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Retrieve a user by their unique identifier.

        Args:
            user_id: The UUID of the user.

        Returns:
            The User if found, otherwise None.
        """

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email: The Email value object to search for.

        Returns:
            The User if found, otherwise None.
        """

    @abstractmethod
    async def add(self, user: User) -> User:
        """Persist a new user.

        Args:
            user: The User entity to persist.

        Returns:
            The persisted User.
        """

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user.

        Args:
            user: The User entity with updated state.

        Returns:
            The updated User.
        """
