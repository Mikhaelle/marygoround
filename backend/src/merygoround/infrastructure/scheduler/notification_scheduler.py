"""APScheduler-based notification scheduler."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

    from merygoround.domain.notification.services import PushNotificationService

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Scheduler that periodically checks and sends push notifications.

    Runs a job every minute to evaluate each user's notification preferences
    and send push notifications when due.

    Args:
        session_factory: Factory for creating async database sessions.
        push_service: Service for sending push notifications.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        push_service: PushNotificationService,
    ) -> None:
        self._session_factory = session_factory
        self._push_service = push_service
        self._scheduler = AsyncIOScheduler()

    def start(self) -> None:
        """Start the notification scheduler.

        Adds a job that runs every 60 seconds to check and send notifications.
        """
        self._scheduler.add_job(
            self._check_and_send_notifications,
            "interval",
            seconds=60,
            id="notification_check",
            replace_existing=True,
        )
        self._scheduler.start()
        logger.info("Notification scheduler started")

    def shutdown(self) -> None:
        """Shut down the notification scheduler gracefully."""
        self._scheduler.shutdown(wait=False)
        logger.info("Notification scheduler shut down")

    async def _check_and_send_notifications(self) -> None:
        """Check all users' notification preferences and send when due."""
        from sqlalchemy import select

        from merygoround.infrastructure.database.models.notification import (
            NotificationPreferenceModel,
            PushSubscriptionModel,
        )

        async with self._session_factory() as session:
            stmt = select(NotificationPreferenceModel).where(
                NotificationPreferenceModel.enabled.is_(True)
            )
            result = await session.execute(stmt)
            preferences = result.scalars().all()

            now = datetime.now(timezone.utc)

            for pref in preferences:
                if not self._should_notify(pref, now):
                    continue

                sub_stmt = select(PushSubscriptionModel).where(
                    PushSubscriptionModel.user_id == pref.user_id
                )
                sub_result = await session.execute(sub_stmt)
                subscriptions = sub_result.scalars().all()

                for sub in subscriptions:
                    from merygoround.domain.notification.entities import PushSubscription

                    domain_sub = PushSubscription(
                        id=sub.id,
                        user_id=sub.user_id,
                        endpoint=sub.endpoint,
                        p256dh_key=sub.p256dh_key,
                        auth_key=sub.auth_key,
                        created_at=sub.created_at,
                    )

                    payload = {
                        "title": "MeryGoRound",
                        "body": "Time to spin the wheel and get a chore done!",
                    }

                    await self._push_service.send(domain_sub, payload)

                pref.last_notified_at = now
                await session.commit()

    def _should_notify(self, pref: object, now: datetime) -> bool:
        """Determine whether a notification should be sent based on preferences.

        Args:
            pref: The notification preference ORM model.
            now: The current UTC datetime.

        Returns:
            True if a notification should be sent, False otherwise.
        """
        if pref.quiet_hours_start is not None and pref.quiet_hours_end is not None:
            current_hour = now.hour
            start = pref.quiet_hours_start
            end = pref.quiet_hours_end

            if start <= end:
                if start <= current_hour < end:
                    return False
            elif current_hour >= start or current_hour < end:
                return False

        if pref.last_notified_at is None:
            return True

        elapsed = (now - pref.last_notified_at).total_seconds() / 60
        return elapsed >= pref.interval_minutes
