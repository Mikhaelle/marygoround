"""Data transfer objects for the Identity application layer."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class RegisterUserRequest(BaseModel):
    """Request DTO for user registration.

    Attributes:
        email: Valid email address string (validated by domain layer).
        password: User password (minimum 8 characters).
        name: Display name.
    """

    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)


class LoginUserRequest(BaseModel):
    """Request DTO for user login.

    Attributes:
        email: User email address string (validated by domain layer).
        password: User password.
    """

    email: str = Field(min_length=1, max_length=255)
    password: str


class UserResponse(BaseModel):
    """Response DTO representing a user.

    Attributes:
        id: User unique identifier.
        email: User email address.
        name: User display name.
    """

    id: uuid.UUID
    email: str
    name: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Response DTO for authentication tokens.

    Attributes:
        access_token: JWT access token.
        refresh_token: JWT refresh token.
        token_type: Token type (always "bearer").
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Combined response for authentication operations.

    Attributes:
        user: User details.
        tokens: Authentication tokens.
    """

    user: UserResponse
    tokens: TokenResponse
