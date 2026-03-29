"""Repository interface for the Wheel bounded context."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import date

from merygoround.domain.wheel.entities import SpinSession


class SpinSessionRepository(ABC):
    """Abstract repository for SpinSession persistence."""

    @abstractmethod
    async def get_by_id(self, session_id: uuid.UUID) -> SpinSession | None:
        """Retrieve a spin session by its unique identifier.

        Args:
            session_id: The UUID of the spin session.

        Returns:
            The SpinSession if found, otherwise None.
        """

    @abstractmethod
    async def get_by_user_id(
        self, user_id: uuid.UUID, page: int = 1, per_page: int = 20
    ) -> tuple[list[SpinSession], int]:
        """Retrieve paginated spin sessions for a user.

        Args:
            user_id: The UUID of the user.
            page: Page number (1-indexed).
            per_page: Number of items per page.

        Returns:
            Tuple of (list of SpinSession entities, total count).
        """

    @abstractmethod
    async def get_completed_counts_for_date(
        self, user_id: uuid.UUID, target_date: date
    ) -> dict[uuid.UUID, int]:
        """Return completion counts per chore for the given date.

        Args:
            user_id: The UUID of the user.
            target_date: The date to check.

        Returns:
            Dict mapping chore UUID to number of completions on that date.
        """

    @abstractmethod
    async def add(self, session: SpinSession) -> SpinSession:
        """Persist a new spin session.

        Args:
            session: The SpinSession entity to persist.

        Returns:
            The persisted SpinSession.
        """

    @abstractmethod
    async def update(self, session: SpinSession) -> SpinSession:
        """Update an existing spin session.

        Args:
            session: The SpinSession entity with updated state.

        Returns:
            The updated SpinSession.
        """
