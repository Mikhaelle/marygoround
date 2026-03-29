"""SQLAlchemy ORM models for the Adult Bucket bounded context."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from merygoround.infrastructure.database.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class BucketItemModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """ORM model mapping to the 'bucket_items' table.

    Attributes:
        id: UUID primary key.
        user_id: Foreign key to the owning user.
        name: Display name.
        description: Detailed description.
        category: Optional category label.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "bucket_items"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)


class BucketDrawModel(UUIDPrimaryKeyMixin, Base):
    """ORM model mapping to the 'bucket_draws' table.

    Includes a partial unique index ensuring at most one ACTIVE draw per user.

    Attributes:
        id: UUID primary key.
        bucket_item_id: Foreign key to the drawn item.
        user_id: Foreign key to the drawing user.
        drawn_at: Timestamp of the draw.
        status: Status string (active, resolved, returned).
        resolved_at: Timestamp of resolution.
        return_justification: Reason for returning.
    """

    __tablename__ = "bucket_draws"
    __table_args__ = (
        Index(
            "ix_bucket_draws_active_user",
            "user_id",
            unique=True,
            postgresql_where="status = 'active'",
        ),
    )

    bucket_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bucket_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    drawn_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    return_justification: Mapped[str | None] = mapped_column(Text, nullable=True)
