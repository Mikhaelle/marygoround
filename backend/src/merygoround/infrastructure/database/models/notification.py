"""SQLAlchemy ORM models for the Notification bounded context."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from merygoround.infrastructure.database.models.base import Base, UUIDPrimaryKeyMixin


class PushSubscriptionModel(UUIDPrimaryKeyMixin, Base):
    """ORM model mapping to the 'push_subscriptions' table.

    Attributes:
        id: UUID primary key.
        user_id: Foreign key to the subscribing user.
        endpoint: Push service endpoint URL.
        p256dh_key: Client public key for encryption.
        auth_key: Authentication secret.
        created_at: Subscription creation timestamp.
    """

    __tablename__ = "push_subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    endpoint: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    p256dh_key: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_key: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class NotificationPreferenceModel(UUIDPrimaryKeyMixin, Base):
    """ORM model mapping to the 'notification_preferences' table.

    Attributes:
        id: UUID primary key.
        user_id: Foreign key to the owning user (unique).
        interval_minutes: Minutes between notifications.
        enabled: Whether notifications are enabled.
        quiet_hours_start: Start hour of quiet period.
        quiet_hours_end: End hour of quiet period.
        last_notified_at: Timestamp of last notification sent.
    """

    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    quiet_hours_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quiet_hours_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
