"""Repository interface for the Chores bounded context."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from merygoround.domain.chores.entities import Chore


class ChoreRepository(ABC):
    """Abstract repository for Chore aggregate persistence."""

    @abstractmethod
    async def get_by_id(self, chore_id: uuid.UUID) -> Chore | None:
        """Retrieve a chore by its unique identifier.

        Args:
            chore_id: The UUID of the chore.

        Returns:
            The Chore if found, otherwise None.
        """

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Chore]:
        """Retrieve all chores belonging to a user.

        Args:
            user_id: The UUID of the owning user.

        Returns:
            List of Chore entities.
        """

    @abstractmethod
    async def add(self, chore: Chore) -> Chore:
        """Persist a new chore.

        Args:
            chore: The Chore entity to persist.

        Returns:
            The persisted Chore.
        """

    @abstractmethod
    async def update(self, chore: Chore) -> Chore:
        """Update an existing chore.

        Args:
            chore: The Chore entity with updated state.

        Returns:
            The updated Chore.
        """

    @abstractmethod
    async def delete(self, chore_id: uuid.UUID) -> None:
        """Remove a chore by its unique identifier.

        Args:
            chore_id: The UUID of the chore to remove.
        """
