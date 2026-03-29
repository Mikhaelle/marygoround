"""Query use cases for the Notification bounded context."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from merygoround.application.notification.dtos import NotificationPreferenceResponse
from merygoround.application.shared.use_case import BaseQuery

if TYPE_CHECKING:
    from merygoround.domain.notification.repository import NotificationPreferenceRepository


class GetNotificationPreferencesQuery(
    BaseQuery[uuid.UUID, NotificationPreferenceResponse]
):
    """Retrieves notification preferences for the authenticated user.

    Args:
        pref_repo: Notification preference repository for lookup.
    """

    def __init__(self, pref_repo: NotificationPreferenceRepository) -> None:
        self._pref_repo = pref_repo

    async def execute(self, input_data: uuid.UUID) -> NotificationPreferenceResponse:
        """Get notification preferences for the user.

        If no preferences exist, returns defaults.

        Args:
            input_data: The UUID of the authenticated user.

        Returns:
            NotificationPreferenceResponse with the user's preferences.
        """
        pref = await self._pref_repo.get_by_user_id(input_data)

        if pref is None:
            return NotificationPreferenceResponse(
                interval_minutes=60,
                enabled=False,
                quiet_hours_start=None,
                quiet_hours_end=None,
                last_notified_at=None,
            )

        return NotificationPreferenceResponse(
            interval_minutes=pref.interval_minutes,
            enabled=pref.enabled,
            quiet_hours_start=pref.quiet_hours_start,
            quiet_hours_end=pref.quiet_hours_end,
            last_notified_at=pref.last_notified_at,
        )
