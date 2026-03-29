"""Command use cases for the Identity bounded context."""

from __future__ import annotations

from typing import TYPE_CHECKING

from merygoround.application.identity.dtos import (
    AuthResponse,
    LoginUserRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from merygoround.application.shared.use_case import BaseCommand
from merygoround.domain.identity.entities import User
from merygoround.domain.identity.exceptions import DuplicateEmailError, InvalidCredentialsError
from merygoround.domain.identity.value_objects import Email

if TYPE_CHECKING:
    from merygoround.domain.identity.repository import UserRepository
    from merygoround.domain.identity.services import PasswordHashingService
    from merygoround.infrastructure.auth.jwt_service import JWTService


class RegisterUserCommand(BaseCommand[RegisterUserRequest, AuthResponse]):
    """Registers a new user account and returns authentication tokens.

    Args:
        user_repo: User repository for persistence.
        password_service: Service for hashing passwords.
        jwt_service: Service for generating JWT tokens.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordHashingService,
        jwt_service: JWTService,
    ) -> None:
        self._user_repo = user_repo
        self._password_service = password_service
        self._jwt_service = jwt_service

    async def execute(self, input_data: RegisterUserRequest) -> AuthResponse:
        """Register the user and generate auth tokens.

        Args:
            input_data: Registration request with email, password, and name.

        Returns:
            AuthResponse containing the user and tokens.

        Raises:
            DuplicateEmailError: If the email is already registered.
        """
        email = Email(input_data.email)

        existing = await self._user_repo.get_by_email(email)
        if existing is not None:
            raise DuplicateEmailError(email.value)

        hashed = self._password_service.hash_password(input_data.password)

        user = User(
            email=email,
            hashed_password=hashed,
            name=input_data.name,
        )

        user = await self._user_repo.add(user)

        tokens = TokenResponse(
            access_token=self._jwt_service.create_access_token(str(user.id)),
            refresh_token=self._jwt_service.create_refresh_token(str(user.id)),
        )

        return AuthResponse(
            user=UserResponse(id=user.id, email=user.email.value, name=user.name),
            tokens=tokens,
        )


class LoginUserCommand(BaseCommand[LoginUserRequest, AuthResponse]):
    """Authenticates a user and returns tokens.

    Args:
        user_repo: User repository for lookup.
        password_service: Service for verifying passwords.
        jwt_service: Service for generating JWT tokens.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordHashingService,
        jwt_service: JWTService,
    ) -> None:
        self._user_repo = user_repo
        self._password_service = password_service
        self._jwt_service = jwt_service

    async def execute(self, input_data: LoginUserRequest) -> AuthResponse:
        """Verify credentials and generate auth tokens.

        Args:
            input_data: Login request with email and password.

        Returns:
            AuthResponse containing the user and tokens.

        Raises:
            InvalidCredentialsError: If the email or password is incorrect.
        """
        email = Email(input_data.email)

        user = await self._user_repo.get_by_email(email)
        if user is None:
            raise InvalidCredentialsError()

        if not self._password_service.verify_password(
            input_data.password, user.hashed_password
        ):
            raise InvalidCredentialsError()

        tokens = TokenResponse(
            access_token=self._jwt_service.create_access_token(str(user.id)),
            refresh_token=self._jwt_service.create_refresh_token(str(user.id)),
        )

        return AuthResponse(
            user=UserResponse(id=user.id, email=user.email.value, name=user.name),
            tokens=tokens,
        )
