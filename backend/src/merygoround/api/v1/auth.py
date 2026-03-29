"""Authentication API routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from merygoround.api.dependencies import (
    get_current_user,
    get_jwt_service,
    get_password_service,
    get_session,
)
from merygoround.application.identity.commands import LoginUserCommand, RegisterUserCommand
from merygoround.application.identity.dtos import (
    AuthResponse,
    LoginUserRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from merygoround.application.identity.queries import GetCurrentUserQuery
from merygoround.infrastructure.auth.jwt_service import JWTService
from merygoround.infrastructure.auth.password_service import BcryptPasswordHashingService
from merygoround.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterUserRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
    password_service: Annotated[BcryptPasswordHashingService, Depends(get_password_service)],
) -> AuthResponse:
    """Register a new user account.

    Args:
        body: Registration request with email, password, and name.
        session: Database session.
        jwt_service: JWT token service.
        password_service: Password hashing service.

    Returns:
        AuthResponse with the created user and authentication tokens.
    """
    repo = SqlAlchemyUserRepository(session)
    command = RegisterUserCommand(repo, password_service, jwt_service)
    return await command.execute(body)


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginUserRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
    password_service: Annotated[BcryptPasswordHashingService, Depends(get_password_service)],
) -> AuthResponse:
    """Authenticate a user and return tokens.

    Args:
        body: Login request with email and password.
        session: Database session.
        jwt_service: JWT token service.
        password_service: Password hashing service.

    Returns:
        AuthResponse with the user and authentication tokens.
    """
    repo = SqlAlchemyUserRepository(session)
    command = LoginUserCommand(repo, password_service, jwt_service)
    return await command.execute(body)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token_str: str,
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> TokenResponse:
    """Refresh an access token using a valid refresh token.

    Args:
        refresh_token_str: The refresh token string.
        jwt_service: JWT token service.

    Returns:
        TokenResponse with new access and refresh tokens.

    Raises:
        HTTPException: If the refresh token is invalid.
    """
    from fastapi import HTTPException, status

    subject = jwt_service.verify_token(refresh_token_str, token_type="refresh")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    return TokenResponse(
        access_token=jwt_service.create_access_token(subject),
        refresh_token=jwt_service.create_refresh_token(subject),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    """Get the authenticated user's profile.

    Args:
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        UserResponse with the user's profile data.
    """
    repo = SqlAlchemyUserRepository(session)
    query = GetCurrentUserQuery(repo)
    return await query.execute(user_id)
