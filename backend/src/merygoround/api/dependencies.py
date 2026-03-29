"""FastAPI dependency injection configuration."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from merygoround.api.config import Settings
from merygoround.infrastructure.auth.jwt_service import JWTService
from merygoround.infrastructure.auth.password_service import BcryptPasswordHashingService
from merygoround.infrastructure.database.engine import create_async_engine, create_session_factory

_security = HTTPBearer()
_engine = None
_session_factory = None


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    Returns:
        The Settings instance.
    """
    return Settings()


def _get_engine(settings: Annotated[Settings, Depends(get_settings)]):
    """Return the SQLAlchemy async engine, creating it if needed."""
    global _engine  # noqa: PLW0603
    if _engine is None:
        _engine = create_async_engine(settings.DATABASE_URL)
    return _engine


def _get_session_factory(engine=Depends(_get_engine)):
    """Return the session factory, creating it if needed."""
    global _session_factory  # noqa: PLW0603
    if _session_factory is None:
        _session_factory = create_session_factory(engine)
    return _session_factory


async def get_session(
    factory=Depends(_get_session_factory),
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for a single request.

    Args:
        factory: The async session factory.

    Yields:
        An AsyncSession instance that is committed on success and closed after use.
    """
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_jwt_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> JWTService:
    """Create a JWTService from application settings.

    Args:
        settings: The application settings.

    Returns:
        A configured JWTService instance.
    """
    return JWTService(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_token_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    )


def get_password_service() -> BcryptPasswordHashingService:
    """Create a BcryptPasswordHashingService instance.

    Returns:
        A BcryptPasswordHashingService instance.
    """
    return BcryptPasswordHashingService()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_security)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> uuid.UUID:
    """Extract and validate the current user from the JWT bearer token.

    Args:
        credentials: The HTTP bearer credentials.
        jwt_service: The JWT service for token verification.

    Returns:
        The authenticated user's UUID.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    subject = jwt_service.verify_token(credentials.credentials, token_type="access")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return uuid.UUID(subject)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
