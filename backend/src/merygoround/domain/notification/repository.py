"""Repository interfaces for the Notification bounded context."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from merygoround.domain.notification.entities import NotificationPreference, PushSubscription


class PushSubscriptionRepository(ABC):
    """Abstract repository for PushSubscription persistence."""

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[PushSubscription]:
        """Retrieve all push subscriptions for a user.

        Args:
            user_id: The UUID of the user.

        Returns:
            List of PushSubscription entities.
        """

    @abstractmethod
    async def get_by_endpoint(self, endpoint: str) -> PushSubscription | None:
        """Retrieve a push subscription by its endpoint URL.

        Args:
            endpoint: The push service endpoint URL.

        Returns:
            The PushSubscription if found, otherwise None.
        """

    @abstractmethod
    async def add(self, subscription: PushSubscription) -> PushSubscription:
        """Persist a new push subscription.

        Args:
            subscription: The PushSubscription entity to persist.

        Returns:
            The persisted PushSubscription.
        """

    @abstractmethod
    async def delete_by_endpoint(self, endpoint: str) -> None:
        """Remove a push subscription by its endpoint URL.

        Args:
            endpoint: The push service endpoint URL.
        """


class NotificationPreferenceRepository(ABC):
    """Abstract repository for NotificationPreference persistence."""

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> NotificationPreference | None:
        """Retrieve notification preferences for a user.

        Args:
            user_id: The UUID of the user.

        Returns:
            The NotificationPreference if found, otherwise None.
        """

    @abstractmethod
    async def upsert(self, preference: NotificationPreference) -> NotificationPreference:
        """Create or update notification preferences for a user.

        Args:
            preference: The NotificationPreference entity to upsert.

        Returns:
            The persisted NotificationPreference.
        """
