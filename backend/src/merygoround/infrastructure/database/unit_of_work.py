"""SQLAlchemy implementation of the Unit of Work pattern."""

from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from merygoround.application.shared.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Concrete UnitOfWork backed by a SQLAlchemy async session.

    Manages transactional boundaries for database operations.

    Args:
        session_factory: Factory for creating async database sessions.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        """Return the current session.

        Returns:
            The active AsyncSession.

        Raises:
            RuntimeError: If the unit of work context has not been entered.
        """
        if self._session is None:
            raise RuntimeError("UnitOfWork context has not been entered")
        return self._session

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction."""
        await self.session.rollback()

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        """Enter the transactional context and create a new session."""
        self._session = self._session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the transactional context, rolling back on exception."""
        if exc_type is not None:
            await self.rollback()
        await self.session.close()
        self._session = None
