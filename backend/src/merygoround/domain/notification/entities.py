"""Entities for the Notification bounded context."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from merygoround.domain.shared.entity import Entity


@dataclass
class PushSubscription(Entity):
    """Represents a Web Push subscription for a user's browser.

    Args:
        id: Unique identifier.
        user_id: The subscribing user.
        endpoint: The push service endpoint URL.
        p256dh_key: The client public key for encryption.
        auth_key: The authentication secret.
        created_at: Timestamp of subscription creation.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    endpoint: str = ""
    p256dh_key: str = ""
    auth_key: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class NotificationPreference(Entity):
    """User preferences for push notification scheduling.

    Args:
        id: Unique identifier.
        user_id: The owning user.
        interval_minutes: Minimum minutes between notifications.
        enabled: Whether notifications are enabled.
        quiet_hours_start: Start hour of quiet period (0-23), or None.
        quiet_hours_end: End hour of quiet period (0-23), or None.
        last_notified_at: Timestamp of the last notification sent.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    interval_minutes: int = 60
    enabled: bool = True
    quiet_hours_start: int | None = None
    quiet_hours_end: int | None = None
    last_notified_at: datetime | None = None
