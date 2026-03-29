"""Command use cases for the Notification bounded context."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from merygoround.application.notification.dtos import (
    NotificationPreferenceResponse,
    SubscribePushRequest,
    UnsubscribePushRequest,
    UpdateNotificationPreferenceRequest,
)
from merygoround.application.shared.use_case import BaseCommand
from merygoround.domain.notification.entities import NotificationPreference, PushSubscription

if TYPE_CHECKING:
    from merygoround.domain.notification.repository import (
        NotificationPreferenceRepository,
        PushSubscriptionRepository,
    )


@dataclass
class SubscribePushInput:
    """Input for SubscribePushCommand.

    Attributes:
        user_id: The subscribing user.
        request: Subscription data.
    """

    user_id: uuid.UUID
    request: SubscribePushRequest


@dataclass
class UnsubscribePushInput:
    """Input for UnsubscribePushCommand.

    Attributes:
        user_id: The user unsubscribing.
        request: Unsubscription data.
    """

    user_id: uuid.UUID
    request: UnsubscribePushRequest


@dataclass
class UpdatePreferencesInput:
    """Input for UpdateNotificationPreferencesCommand.

    Attributes:
        user_id: The user updating preferences.
        request: Preference update data.
    """

    user_id: uuid.UUID
    request: UpdateNotificationPreferenceRequest


class SubscribePushCommand(BaseCommand[SubscribePushInput, None]):
    """Registers a new push subscription for the user.

    Args:
        push_repo: Push subscription repository for persistence.
    """

    def __init__(self, push_repo: PushSubscriptionRepository) -> None:
        self._push_repo = push_repo

    async def execute(self, input_data: SubscribePushInput) -> None:
        """Create a new push subscription.

        If a subscription for the same endpoint already exists, it is replaced.

        Args:
            input_data: Contains the user ID and subscription data.
        """
        existing = await self._push_repo.get_by_endpoint(input_data.request.endpoint)
        if existing is not None:
            await self._push_repo.delete_by_endpoint(input_data.request.endpoint)

        subscription = PushSubscription(
            user_id=input_data.user_id,
            endpoint=input_data.request.endpoint,
            p256dh_key=input_data.request.p256dh_key,
            auth_key=input_data.request.auth_key,
        )
        await self._push_repo.add(subscription)


class UnsubscribePushCommand(BaseCommand[UnsubscribePushInput, None]):
    """Removes a push subscription by endpoint.

    Args:
        push_repo: Push subscription repository for persistence.
    """

    def __init__(self, push_repo: PushSubscriptionRepository) -> None:
        self._push_repo = push_repo

    async def execute(self, input_data: UnsubscribePushInput) -> None:
        """Delete the push subscription for the given endpoint.

        Args:
            input_data: Contains the user ID and endpoint to remove.
        """
        await self._push_repo.delete_by_endpoint(input_data.request.endpoint)


class UpdateNotificationPreferencesCommand(
    BaseCommand[UpdatePreferencesInput, NotificationPreferenceResponse]
):
    """Updates notification preferences for the user.

    Args:
        pref_repo: Notification preference repository for persistence.
    """

    def __init__(self, pref_repo: NotificationPreferenceRepository) -> None:
        self._pref_repo = pref_repo

    async def execute(
        self, input_data: UpdatePreferencesInput
    ) -> NotificationPreferenceResponse:
        """Update or create notification preferences.

        Args:
            input_data: Contains the user ID and preference updates.

        Returns:
            NotificationPreferenceResponse with the updated preferences.
        """
        existing = await self._pref_repo.get_by_user_id(input_data.user_id)

        if existing is None:
            existing = NotificationPreference(user_id=input_data.user_id)

        req = input_data.request
        if req.interval_minutes is not None:
            existing.interval_minutes = req.interval_minutes
        if req.enabled is not None:
            existing.enabled = req.enabled
        if req.quiet_hours_start is not None:
            existing.quiet_hours_start = req.quiet_hours_start
        if req.quiet_hours_end is not None:
            existing.quiet_hours_end = req.quiet_hours_end

        existing = await self._pref_repo.upsert(existing)

        return NotificationPreferenceResponse(
            interval_minutes=existing.interval_minutes,
            enabled=existing.enabled,
            quiet_hours_start=existing.quiet_hours_start,
            quiet_hours_end=existing.quiet_hours_end,
            last_notified_at=existing.last_notified_at,
        )
