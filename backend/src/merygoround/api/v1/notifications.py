"""Notification API routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from merygoround.api.dependencies import get_current_user, get_session
from merygoround.application.notification.commands import (
    SubscribePushCommand,
    SubscribePushInput,
    UnsubscribePushCommand,
    UnsubscribePushInput,
    UpdateNotificationPreferencesCommand,
    UpdatePreferencesInput,
)
from merygoround.application.notification.dtos import (
    NotificationPreferenceResponse,
    SubscribePushRequest,
    UnsubscribePushRequest,
    UpdateNotificationPreferenceRequest,
)
from merygoround.application.notification.queries import GetNotificationPreferencesQuery
from merygoround.infrastructure.database.repositories.push_subscription_repository import (
    SqlAlchemyNotificationPreferenceRepository,
    SqlAlchemyPushSubscriptionRepository,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/subscribe", status_code=204)
async def subscribe(
    body: SubscribePushRequest,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Register a push notification subscription.

    Args:
        body: Subscription request with endpoint and keys.
        user_id: The authenticated user's UUID.
        session: Database session.
    """
    repo = SqlAlchemyPushSubscriptionRepository(session)
    command = SubscribePushCommand(repo)
    await command.execute(SubscribePushInput(user_id=user_id, request=body))


@router.delete("/unsubscribe", status_code=204)
async def unsubscribe(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Remove all push notification subscriptions for the user.

    Args:
        user_id: The authenticated user's UUID.
        session: Database session.
    """
    repo = SqlAlchemyPushSubscriptionRepository(session)
    await repo.delete_all_by_user_id(user_id)


@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_preferences(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NotificationPreferenceResponse:
    """Get notification preferences for the authenticated user.

    Args:
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        NotificationPreferenceResponse with the user's preferences.
    """
    repo = SqlAlchemyNotificationPreferenceRepository(session)
    query = GetNotificationPreferencesQuery(repo)
    return await query.execute(user_id)


@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_preferences(
    body: UpdateNotificationPreferenceRequest,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NotificationPreferenceResponse:
    """Update notification preferences.

    Args:
        body: Preference update request.
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        NotificationPreferenceResponse with the updated preferences.
    """
    repo = SqlAlchemyNotificationPreferenceRepository(session)
    command = UpdateNotificationPreferencesCommand(repo)
    return await command.execute(UpdatePreferencesInput(user_id=user_id, request=body))
