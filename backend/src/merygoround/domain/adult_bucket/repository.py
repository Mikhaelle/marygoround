"""Repository interfaces for the Adult Bucket bounded context."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from merygoround.domain.adult_bucket.entities import BucketDraw, BucketItem


class BucketItemRepository(ABC):
    """Abstract repository for BucketItem aggregate persistence."""

    @abstractmethod
    async def get_by_id(self, item_id: uuid.UUID) -> BucketItem | None:
        """Retrieve a bucket item by its unique identifier.

        Args:
            item_id: The UUID of the bucket item.

        Returns:
            The BucketItem if found, otherwise None.
        """

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[BucketItem]:
        """Retrieve all bucket items belonging to a user.

        Args:
            user_id: The UUID of the owning user.

        Returns:
            List of BucketItem entities.
        """

    @abstractmethod
    async def get_available_for_draw(self, user_id: uuid.UUID) -> list[BucketItem]:
        """Retrieve bucket items eligible for drawing.

        Excludes items that have been resolved in a previous draw.

        Args:
            user_id: The UUID of the owning user.

        Returns:
            List of BucketItem entities available for drawing.
        """

    @abstractmethod
    async def add(self, item: BucketItem) -> BucketItem:
        """Persist a new bucket item.

        Args:
            item: The BucketItem entity to persist.

        Returns:
            The persisted BucketItem.
        """

    @abstractmethod
    async def update(self, item: BucketItem) -> BucketItem:
        """Update an existing bucket item.

        Args:
            item: The BucketItem entity with updated state.

        Returns:
            The updated BucketItem.
        """

    @abstractmethod
    async def delete(self, item_id: uuid.UUID) -> None:
        """Remove a bucket item by its unique identifier.

        Args:
            item_id: The UUID of the bucket item to remove.
        """


class BucketDrawRepository(ABC):
    """Abstract repository for BucketDraw persistence."""

    @abstractmethod
    async def get_by_id(self, draw_id: uuid.UUID) -> BucketDraw | None:
        """Retrieve a bucket draw by its unique identifier.

        Args:
            draw_id: The UUID of the bucket draw.

        Returns:
            The BucketDraw if found, otherwise None.
        """

    @abstractmethod
    async def get_active_by_user_id(self, user_id: uuid.UUID) -> BucketDraw | None:
        """Retrieve the current active draw for a user.

        Args:
            user_id: The UUID of the user.

        Returns:
            The active BucketDraw if one exists, otherwise None.
        """

    @abstractmethod
    async def get_by_user_id(
        self, user_id: uuid.UUID, page: int = 1, per_page: int = 20
    ) -> tuple[list[BucketDraw], int]:
        """Retrieve paginated bucket draws for a user.

        Args:
            user_id: The UUID of the user.
            page: Page number (1-indexed).
            per_page: Number of items per page.

        Returns:
            Tuple of (list of BucketDraw entities, total count).
        """

    @abstractmethod
    async def add(self, draw: BucketDraw) -> BucketDraw:
        """Persist a new bucket draw.

        Args:
            draw: The BucketDraw entity to persist.

        Returns:
            The persisted BucketDraw.
        """

    @abstractmethod
    async def update(self, draw: BucketDraw) -> BucketDraw:
        """Update an existing bucket draw.

        Args:
            draw: The BucketDraw entity with updated state.

        Returns:
            The updated BucketDraw.
        """
