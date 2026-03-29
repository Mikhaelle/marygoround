"""Data transfer objects for the Notification application layer."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SubscribePushRequest(BaseModel):
    """Request DTO for creating a push subscription.

    Attributes:
        endpoint: The push service endpoint URL.
        p256dh_key: The client public key for encryption.
        auth_key: The authentication secret.
    """

    endpoint: str = Field(min_length=1)
    p256dh_key: str = Field(min_length=1)
    auth_key: str = Field(min_length=1)


class UnsubscribePushRequest(BaseModel):
    """Request DTO for removing a push subscription.

    Attributes:
        endpoint: The push service endpoint URL to remove.
    """

    endpoint: str = Field(min_length=1)


class NotificationPreferenceResponse(BaseModel):
    """Response DTO representing notification preferences.

    Attributes:
        interval_minutes: Minutes between notifications.
        enabled: Whether notifications are enabled.
        quiet_hours_start: Start hour of quiet period (if set).
        quiet_hours_end: End hour of quiet period (if set).
        last_notified_at: Timestamp of last notification sent.
    """

    interval_minutes: int
    enabled: bool
    quiet_hours_start: int | None
    quiet_hours_end: int | None
    last_notified_at: datetime | None

    model_config = {"from_attributes": True}


class UpdateNotificationPreferenceRequest(BaseModel):
    """Request DTO for updating notification preferences.

    Attributes:
        interval_minutes: Minutes between notifications (1-1440).
        enabled: Whether notifications are enabled.
        quiet_hours_start: Start hour of quiet period (0-23).
        quiet_hours_end: End hour of quiet period (0-23).
    """

    interval_minutes: int | None = Field(default=None, ge=1, le=1440)
    enabled: bool | None = None
    quiet_hours_start: int | None = Field(default=None, ge=0, le=23)
    quiet_hours_end: int | None = Field(default=None, ge=0, le=23)
