"""SQLAlchemy ORM model for the User entity."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from merygoround.infrastructure.database.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class UserModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model mapping to the 'users' table.

    Attributes:
        id: UUID primary key.
        email: Unique email address.
        hashed_password: Bcrypt password hash.
        name: Display name.
        created_at: Account creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
