"""Domain service interfaces for the Notification bounded context."""

from __future__ import annotations

from abc import ABC, abstractmethod

from merygoround.domain.notification.entities import PushSubscription


class PushNotificationService(ABC):
    """Abstract service for sending Web Push notifications."""

    @abstractmethod
    async def send(self, subscription: PushSubscription, payload: dict) -> bool:
        """Send a push notification to a subscription.

        Args:
            subscription: The target PushSubscription.
            payload: Notification data payload (title, body, etc.).

        Returns:
            True if the notification was sent successfully, False otherwise.
        """
