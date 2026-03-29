"""pywebpush implementation of the PushNotificationService."""

from __future__ import annotations

import json
import logging

from pywebpush import WebPushException, webpush

from merygoround.domain.notification.entities import PushSubscription
from merygoround.domain.notification.services import PushNotificationService

logger = logging.getLogger(__name__)


class PyWebPushNotificationService(PushNotificationService):
    """Push notification service using the pywebpush library.

    Args:
        vapid_private_key: The VAPID private key for signing push messages.
        vapid_claims: VAPID claims dict (must include 'sub' with mailto: URL).
    """

    def __init__(self, vapid_private_key: str, vapid_claims: dict) -> None:
        self._vapid_private_key = vapid_private_key
        self._vapid_claims = vapid_claims

    async def send(self, subscription: PushSubscription, payload: dict) -> bool:
        """Send a push notification to a subscription.

        Args:
            subscription: The target PushSubscription with endpoint and keys.
            payload: Notification data payload (title, body, etc.).

        Returns:
            True if the notification was sent successfully, False otherwise.
        """
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh_key,
                "auth": subscription.auth_key,
            },
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self._vapid_private_key,
                vapid_claims=self._vapid_claims,
            )
            return True
        except WebPushException:
            logger.exception("Failed to send push notification to %s", subscription.endpoint)
            return False
