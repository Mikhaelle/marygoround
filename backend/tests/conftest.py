"""Shared test fixtures for the MeryGoRound test suite."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from merygoround.api.config import Settings
from merygoround.api.dependencies import get_session, get_settings
from merygoround.api.main import create_app
from merygoround.infrastructure.database.models.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def settings() -> Settings:
    """Provide test settings with in-memory SQLite database."""
    return Settings(
        DATABASE_URL=TEST_DATABASE_URL,
        JWT_SECRET_KEY="test-secret-key-for-testing-only",
        JWT_ALGORITHM="HS256",
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30,
        JWT_REFRESH_TOKEN_EXPIRE_DAYS=7,
        VAPID_PRIVATE_KEY="",
        VAPID_PUBLIC_KEY="",
        CORS_ORIGINS="http://localhost:3000",
        ENVIRONMENT="test",
    )


@pytest.fixture
async def engine():
    """Create an async SQLite engine for testing."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the test engine."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
async def session(session_factory) -> AsyncSession:
    """Yield a database session for a single test."""
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(settings, engine) -> AsyncClient:
    """Create an async test client with dependency overrides."""
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    app = create_app()

    app.dependency_overrides[get_settings] = lambda: settings

    async def override_session():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def test_user_id() -> uuid.UUID:
    """Provide a fixed test user UUID."""
    return uuid.UUID("12345678-1234-1234-1234-123456789abc")


@pytest.fixture
def test_user_data() -> dict:
    """Provide test user registration data."""
    return {
        "email": "test@example.com",
        "password": "securepassword123",
        "name": "Test User",
    }
