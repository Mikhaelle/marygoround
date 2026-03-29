"""Abstract Unit of Work pattern for transactional consistency."""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType


class UnitOfWork(ABC):
    """Abstract unit of work providing transactional boundaries.

    Used as an async context manager to group repository operations
    into a single atomic transaction.
    """

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""

    @abstractmethod
    async def rollback(self) -> None:
        """Roll back the current transaction."""

    @abstractmethod
    async def __aenter__(self) -> UnitOfWork:
        """Enter the transactional context."""

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the transactional context, rolling back on exception."""
