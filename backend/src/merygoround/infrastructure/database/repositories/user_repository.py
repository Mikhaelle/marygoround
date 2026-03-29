"""SQLAlchemy implementation of the UserRepository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from merygoround.domain.identity.entities import User
from merygoround.domain.identity.repository import UserRepository
from merygoround.domain.identity.value_objects import Email
from merygoround.infrastructure.database.models.user import UserModel


class SqlAlchemyUserRepository(UserRepository):
    """Concrete UserRepository backed by SQLAlchemy and PostgreSQL.

    Args:
        session: The async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Retrieve a user by their unique identifier.

        Args:
            user_id: The UUID of the user.

        Returns:
            The User domain entity if found, otherwise None.
        """
        result = await self._session.get(UserModel, user_id)
        if result is None:
            return None
        return self._to_domain(result)

    async def get_by_email(self, email: Email) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email: The Email value object to search for.

        Returns:
            The User domain entity if found, otherwise None.
        """
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def add(self, user: User) -> User:
        """Persist a new user.

        Args:
            user: The User domain entity to persist.

        Returns:
            The persisted User domain entity.
        """
        model = UserModel(
            id=user.id,
            email=user.email.value,
            hashed_password=user.hashed_password,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, user: User) -> User:
        """Update an existing user.

        Args:
            user: The User domain entity with updated state.

        Returns:
            The updated User domain entity.
        """
        model = await self._session.get(UserModel, user.id)
        if model is not None:
            model.email = user.email.value
            model.hashed_password = user.hashed_password
            model.name = user.name
            model.updated_at = user.updated_at
            await self._session.flush()
        return user

    def _to_domain(self, model: UserModel) -> User:
        """Map a UserModel ORM instance to a User domain entity."""
        return User(
            id=model.id,
            email=Email(model.email),
            hashed_password=model.hashed_password,
            name=model.name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
