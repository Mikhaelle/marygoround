"""SQLAlchemy implementations of the Notification repositories."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from merygoround.domain.notification.entities import NotificationPreference, PushSubscription
from merygoround.domain.notification.repository import (
    NotificationPreferenceRepository,
    PushSubscriptionRepository,
)
from merygoround.infrastructure.database.models.notification import (
    NotificationPreferenceModel,
    PushSubscriptionModel,
)


class SqlAlchemyPushSubscriptionRepository(PushSubscriptionRepository):
    """Concrete PushSubscriptionRepository backed by SQLAlchemy and PostgreSQL.

    Args:
        session: The async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[PushSubscription]:
        """Retrieve all push subscriptions for a user.

        Args:
            user_id: The UUID of the user.

        Returns:
            List of PushSubscription domain entities.
        """
        stmt = select(PushSubscriptionModel).where(
            PushSubscriptionModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_endpoint(self, endpoint: str) -> PushSubscription | None:
        """Retrieve a push subscription by its endpoint URL.

        Args:
            endpoint: The push service endpoint URL.

        Returns:
            The PushSubscription if found, otherwise None.
        """
        stmt = select(PushSubscriptionModel).where(
            PushSubscriptionModel.endpoint == endpoint
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def add(self, subscription: PushSubscription) -> PushSubscription:
        """Persist a new push subscription.

        Args:
            subscription: The PushSubscription domain entity to persist.

        Returns:
            The persisted PushSubscription domain entity.
        """
        model = PushSubscriptionModel(
            id=subscription.id,
            user_id=subscription.user_id,
            endpoint=subscription.endpoint,
            p256dh_key=subscription.p256dh_key,
            auth_key=subscription.auth_key,
            created_at=subscription.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def delete_all_by_user_id(self, user_id: uuid.UUID) -> None:
        """Remove all push subscriptions for a user.

        Args:
            user_id: The UUID of the user.
        """
        stmt = delete(PushSubscriptionModel).where(
            PushSubscriptionModel.user_id == user_id
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete_by_endpoint(self, endpoint: str) -> None:
        """Remove a push subscription by its endpoint URL.

        Args:
            endpoint: The push service endpoint URL.
        """
        stmt = delete(PushSubscriptionModel).where(
            PushSubscriptionModel.endpoint == endpoint
        )
        await self._session.execute(stmt)
        await self._session.flush()

    def _to_domain(self, model: PushSubscriptionModel) -> PushSubscription:
        """Map a PushSubscriptionModel ORM instance to a PushSubscription domain entity."""
        return PushSubscription(
            id=model.id,
            user_id=model.user_id,
            endpoint=model.endpoint,
            p256dh_key=model.p256dh_key,
            auth_key=model.auth_key,
            created_at=model.created_at,
        )


class SqlAlchemyNotificationPreferenceRepository(NotificationPreferenceRepository):
    """Concrete NotificationPreferenceRepository backed by SQLAlchemy and PostgreSQL.

    Args:
        session: The async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: uuid.UUID) -> NotificationPreference | None:
        """Retrieve notification preferences for a user.

        Args:
            user_id: The UUID of the user.

        Returns:
            The NotificationPreference if found, otherwise None.
        """
        stmt = select(NotificationPreferenceModel).where(
            NotificationPreferenceModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def upsert(self, preference: NotificationPreference) -> NotificationPreference:
        """Create or update notification preferences for a user.

        Args:
            preference: The NotificationPreference domain entity to upsert.

        Returns:
            The persisted NotificationPreference domain entity.
        """
        stmt = select(NotificationPreferenceModel).where(
            NotificationPreferenceModel.user_id == preference.user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            model = NotificationPreferenceModel(
                id=preference.id,
                user_id=preference.user_id,
                interval_minutes=preference.interval_minutes,
                enabled=preference.enabled,
                quiet_hours_start=preference.quiet_hours_start,
                quiet_hours_end=preference.quiet_hours_end,
                last_notified_at=preference.last_notified_at,
            )
            self._session.add(model)
        else:
            model.interval_minutes = preference.interval_minutes
            model.enabled = preference.enabled
            model.quiet_hours_start = preference.quiet_hours_start
            model.quiet_hours_end = preference.quiet_hours_end
            model.last_notified_at = preference.last_notified_at

        await self._session.flush()
        return self._to_domain(model)

    def _to_domain(self, model: NotificationPreferenceModel) -> NotificationPreference:
        """Map a NotificationPreferenceModel to a NotificationPreference domain entity."""
        return NotificationPreference(
            id=model.id,
            user_id=model.user_id,
            interval_minutes=model.interval_minutes,
            enabled=model.enabled,
            quiet_hours_start=model.quiet_hours_start,
            quiet_hours_end=model.quiet_hours_end,
            last_notified_at=model.last_notified_at,
        )
