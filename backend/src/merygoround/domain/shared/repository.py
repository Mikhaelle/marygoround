"""Generic abstract repository interface for domain entities."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from merygoround.domain.shared.entity import Entity

T = TypeVar("T", bound=Entity)


class Repository(ABC, Generic[T]):
    """Abstract base repository providing standard CRUD operations.

    Type parameter T must be a subclass of Entity.
    """

    @abstractmethod
    async def get_by_id(self, entity_id: uuid.UUID) -> T | None:
        """Retrieve an entity by its unique identifier.

        Args:
            entity_id: The UUID of the entity to retrieve.

        Returns:
            The entity if found, otherwise None.
        """

    @abstractmethod
    async def add(self, entity: T) -> T:
        """Persist a new entity.

        Args:
            entity: The entity to persist.

        Returns:
            The persisted entity.
        """

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity.

        Args:
            entity: The entity with updated state.

        Returns:
            The updated entity.
        """

    @abstractmethod
    async def delete(self, entity_id: uuid.UUID) -> None:
        """Remove an entity by its unique identifier.

        Args:
            entity_id: The UUID of the entity to remove.
        """
