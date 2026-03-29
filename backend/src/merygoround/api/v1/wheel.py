"""Wheel API routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from merygoround.api.dependencies import get_current_user, get_session
from merygoround.application.wheel.commands import (
    CompleteSpinInput,
    CompleteSpinSessionCommand,
    SkipSpinInput,
    SkipSpinSessionCommand,
    SpinWheelCommand,
    SpinWheelInput,
)
from merygoround.application.wheel.dtos import (
    SpinHistoryResponse,
    SpinResultResponse,
    WheelSegmentResponse,
)
from merygoround.application.wheel.queries import (
    GetSpinHistoryInput,
    GetSpinHistoryQuery,
    GetWheelSegmentsQuery,
)
from merygoround.domain.wheel.services import WheelSpinService
from merygoround.infrastructure.database.repositories.chore_repository import (
    SqlAlchemyChoreRepository,
)
from merygoround.infrastructure.database.repositories.spin_session_repository import (
    SqlAlchemySpinSessionRepository,
)

router = APIRouter(prefix="/wheel", tags=["wheel"])


@router.post("/spin", response_model=SpinResultResponse, status_code=201)
async def spin_wheel(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SpinResultResponse:
    """Spin the wheel and get a random chore.

    Args:
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        SpinResultResponse with the selected chore.
    """
    chore_repo = SqlAlchemyChoreRepository(session)
    spin_repo = SqlAlchemySpinSessionRepository(session)
    spin_service = WheelSpinService()
    command = SpinWheelCommand(chore_repo, spin_repo, spin_service)
    return await command.execute(SpinWheelInput(user_id=user_id))


@router.put("/sessions/{session_id}/complete", status_code=204)
async def complete_session(
    session_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Mark a spin session as completed.

    Args:
        session_id: The UUID of the spin session.
        user_id: The authenticated user's UUID.
        session: Database session.
    """
    spin_repo = SqlAlchemySpinSessionRepository(session)
    command = CompleteSpinSessionCommand(spin_repo)
    await command.execute(CompleteSpinInput(user_id=user_id, session_id=session_id))


@router.put("/sessions/{session_id}/skip", status_code=204)
async def skip_session(
    session_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Mark a spin session as skipped.

    Args:
        session_id: The UUID of the spin session.
        user_id: The authenticated user's UUID.
        session: Database session.
    """
    spin_repo = SqlAlchemySpinSessionRepository(session)
    command = SkipSpinSessionCommand(spin_repo)
    await command.execute(SkipSpinInput(user_id=user_id, session_id=session_id))


@router.get("/history", response_model=SpinHistoryResponse)
async def get_history(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> SpinHistoryResponse:
    """Get paginated spin history.

    Args:
        user_id: The authenticated user's UUID.
        session: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.

    Returns:
        SpinHistoryResponse with paginated spin sessions.
    """
    spin_repo = SqlAlchemySpinSessionRepository(session)
    query = GetSpinHistoryQuery(spin_repo)
    return await query.execute(
        GetSpinHistoryInput(user_id=user_id, page=page, per_page=per_page)
    )


@router.get("/segments", response_model=list[WheelSegmentResponse])
async def get_segments(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[WheelSegmentResponse]:
    """Get wheel segments with effective weights for the current hour.

    Args:
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        List of WheelSegmentResponse DTOs.
    """
    chore_repo = SqlAlchemyChoreRepository(session)
    spin_repo = SqlAlchemySpinSessionRepository(session)
    spin_service = WheelSpinService()
    query = GetWheelSegmentsQuery(chore_repo, spin_repo, spin_service)
    return await query.execute(user_id)
