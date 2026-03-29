"""Chores API routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from merygoround.api.dependencies import get_current_user, get_session
from merygoround.application.chores.commands import (
    CreateChoreCommand,
    CreateChoreInput,
    DeleteChoreCommand,
    DeleteChoreInput,
    UpdateChoreCommand,
    UpdateChoreInput,
)
from merygoround.application.chores.dtos import (
    ChoreResponse,
    CreateChoreRequest,
    UpdateChoreRequest,
)
from merygoround.application.chores.queries import GetChoreInput, GetChoreQuery, ListChoresQuery
from merygoround.infrastructure.database.repositories.chore_repository import (
    SqlAlchemyChoreRepository,
)

router = APIRouter(prefix="/chores", tags=["chores"])


@router.get("", response_model=list[ChoreResponse])
async def list_chores(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[ChoreResponse]:
    """List all chores for the authenticated user.

    Args:
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        List of ChoreResponse DTOs.
    """
    repo = SqlAlchemyChoreRepository(session)
    query = ListChoresQuery(repo)
    return await query.execute(user_id)


@router.post("", response_model=ChoreResponse, status_code=201)
async def create_chore(
    body: CreateChoreRequest,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ChoreResponse:
    """Create a new chore.

    Args:
        body: Chore creation request.
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        ChoreResponse representing the created chore.
    """
    repo = SqlAlchemyChoreRepository(session)
    command = CreateChoreCommand(repo)
    return await command.execute(CreateChoreInput(user_id=user_id, request=body))


@router.get("/{chore_id}", response_model=ChoreResponse)
async def get_chore(
    chore_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ChoreResponse:
    """Get a single chore by ID.

    Args:
        chore_id: The UUID of the chore.
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        ChoreResponse for the requested chore.
    """
    repo = SqlAlchemyChoreRepository(session)
    query = GetChoreQuery(repo)
    return await query.execute(GetChoreInput(user_id=user_id, chore_id=chore_id))


@router.put("/{chore_id}", response_model=ChoreResponse)
async def update_chore(
    chore_id: uuid.UUID,
    body: UpdateChoreRequest,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ChoreResponse:
    """Update an existing chore.

    Args:
        chore_id: The UUID of the chore to update.
        body: Chore update request.
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        ChoreResponse representing the updated chore.
    """
    repo = SqlAlchemyChoreRepository(session)
    command = UpdateChoreCommand(repo)
    return await command.execute(
        UpdateChoreInput(user_id=user_id, chore_id=chore_id, request=body)
    )


@router.delete("/{chore_id}", status_code=204)
async def delete_chore(
    chore_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete a chore.

    Args:
        chore_id: The UUID of the chore to delete.
        user_id: The authenticated user's UUID.
        session: Database session.
    """
    repo = SqlAlchemyChoreRepository(session)
    command = DeleteChoreCommand(repo)
    await command.execute(DeleteChoreInput(user_id=user_id, chore_id=chore_id))
