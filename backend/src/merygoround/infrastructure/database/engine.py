"""SQLAlchemy async engine and session factory configuration."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine as sa_create_async_engine,
)


def create_async_engine(database_url: str) -> sa_create_async_engine:
    """Create an async SQLAlchemy engine from the given database URL.

    Args:
        database_url: The database connection string (asyncpg-compatible).

    Returns:
        An AsyncEngine instance.
    """
    return sa_create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


def create_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the given engine.

    Args:
        engine: The AsyncEngine to bind sessions to.

    Returns:
        An async_sessionmaker configured for the engine.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_async_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for dependency injection.

    Args:
        session_factory: The session factory to create sessions from.

    Yields:
        An AsyncSession instance that is closed after use.
    """
    async with session_factory() as session:
        yield session
