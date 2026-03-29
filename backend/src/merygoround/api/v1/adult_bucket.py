"""Adult Bucket API routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from merygoround.api.dependencies import get_current_user, get_session
from merygoround.application.adult_bucket.commands import (
    CreateBucketItemCommand,
    CreateBucketItemInput,
    DeleteBucketItemCommand,
    DeleteBucketItemInput,
    DrawFromBucketCommand,
    DrawFromBucketInput,
    ResolveDrawCommand,
    ResolveDrawInput,
    ReturnDrawCommand,
    ReturnDrawInput,
    UpdateBucketItemCommand,
    UpdateBucketItemInput,
)
from merygoround.application.adult_bucket.dtos import (
    BucketDrawResponse,
    BucketItemResponse,
    CreateBucketItemRequest,
    ReturnDrawRequest,
    UpdateBucketItemRequest,
)
from merygoround.application.adult_bucket.queries import GetActiveDrawQuery, ListBucketItemsQuery
from merygoround.domain.adult_bucket.services import BucketDrawService
from merygoround.infrastructure.database.repositories.bucket_repository import (
    SqlAlchemyBucketDrawRepository,
    SqlAlchemyBucketItemRepository,
)

router = APIRouter(prefix="/bucket", tags=["adult-bucket"])


@router.get("/items", response_model=list[BucketItemResponse])
async def list_items(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[BucketItemResponse]:
    """List all bucket items for the authenticated user.

    Args:
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        List of BucketItemResponse DTOs.
    """
    repo = SqlAlchemyBucketItemRepository(session)
    query = ListBucketItemsQuery(repo)
    return await query.execute(user_id)


@router.post("/items", response_model=BucketItemResponse, status_code=201)
async def create_item(
    body: CreateBucketItemRequest,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BucketItemResponse:
    """Create a new bucket item.

    Args:
        body: Item creation request.
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        BucketItemResponse representing the created item.
    """
    repo = SqlAlchemyBucketItemRepository(session)
    command = CreateBucketItemCommand(repo)
    return await command.execute(CreateBucketItemInput(user_id=user_id, request=body))


@router.put("/items/{item_id}", response_model=BucketItemResponse)
async def update_item(
    item_id: uuid.UUID,
    body: UpdateBucketItemRequest,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BucketItemResponse:
    """Update an existing bucket item.

    Args:
        item_id: The UUID of the item to update.
        body: Item update request.
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        BucketItemResponse representing the updated item.
    """
    repo = SqlAlchemyBucketItemRepository(session)
    command = UpdateBucketItemCommand(repo)
    return await command.execute(
        UpdateBucketItemInput(user_id=user_id, item_id=item_id, request=body)
    )


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    item_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete a bucket item.

    Args:
        item_id: The UUID of the item to delete.
        user_id: The authenticated user's UUID.
        session: Database session.
    """
    repo = SqlAlchemyBucketItemRepository(session)
    command = DeleteBucketItemCommand(repo)
    await command.execute(DeleteBucketItemInput(user_id=user_id, item_id=item_id))


@router.post("/draw", response_model=BucketDrawResponse, status_code=201)
async def draw_from_bucket(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BucketDrawResponse:
    """Draw a random item from the bucket.

    Args:
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        BucketDrawResponse with the drawn item.
    """
    item_repo = SqlAlchemyBucketItemRepository(session)
    draw_repo = SqlAlchemyBucketDrawRepository(session)
    draw_service = BucketDrawService()
    command = DrawFromBucketCommand(item_repo, draw_repo, draw_service)
    return await command.execute(DrawFromBucketInput(user_id=user_id))


@router.get("/draws/active", response_model=BucketDrawResponse | None)
async def get_active_draw(
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BucketDrawResponse | None:
    """Get the current active draw for the user.

    Args:
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        BucketDrawResponse if an active draw exists, otherwise None.
    """
    item_repo = SqlAlchemyBucketItemRepository(session)
    draw_repo = SqlAlchemyBucketDrawRepository(session)
    query = GetActiveDrawQuery(draw_repo, item_repo)
    return await query.execute(user_id)


@router.put("/draws/{draw_id}/resolve", response_model=BucketDrawResponse)
async def resolve_draw(
    draw_id: uuid.UUID,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BucketDrawResponse:
    """Resolve (complete) a bucket draw.

    Args:
        draw_id: The UUID of the draw to resolve.
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        BucketDrawResponse with the resolved draw.
    """
    item_repo = SqlAlchemyBucketItemRepository(session)
    draw_repo = SqlAlchemyBucketDrawRepository(session)
    draw_service = BucketDrawService()
    command = ResolveDrawCommand(item_repo, draw_repo, draw_service)
    return await command.execute(ResolveDrawInput(user_id=user_id, draw_id=draw_id))


@router.put("/draws/{draw_id}/return", response_model=BucketDrawResponse)
async def return_draw(
    draw_id: uuid.UUID,
    body: ReturnDrawRequest,
    user_id: Annotated[uuid.UUID, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BucketDrawResponse:
    """Return a bucket draw with a justification.

    Args:
        draw_id: The UUID of the draw to return.
        body: Return request with justification.
        user_id: The authenticated user's UUID.
        session: Database session.

    Returns:
        BucketDrawResponse with the returned draw.
    """
    item_repo = SqlAlchemyBucketItemRepository(session)
    draw_repo = SqlAlchemyBucketDrawRepository(session)
    draw_service = BucketDrawService()
    command = ReturnDrawCommand(item_repo, draw_repo, draw_service)
    return await command.execute(
        ReturnDrawInput(user_id=user_id, draw_id=draw_id, request=body)
    )
