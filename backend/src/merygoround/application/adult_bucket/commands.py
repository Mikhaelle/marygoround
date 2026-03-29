"""Command use cases for the Adult Bucket bounded context."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from merygoround.application.adult_bucket.dtos import (
    BucketDrawResponse,
    BucketItemResponse,
    ReturnDrawRequest,
)
from merygoround.application.shared.use_case import BaseCommand
from merygoround.domain.adult_bucket.entities import BucketItem
from merygoround.domain.adult_bucket.exceptions import BucketItemNotFoundError
from merygoround.domain.shared.exceptions import AuthorizationError, EntityNotFoundError

if TYPE_CHECKING:
    from merygoround.application.adult_bucket.dtos import (
        CreateBucketItemRequest,
        UpdateBucketItemRequest,
    )
    from merygoround.domain.adult_bucket.repository import (
        BucketDrawRepository,
        BucketItemRepository,
    )
    from merygoround.domain.adult_bucket.services import BucketDrawService


def _item_to_response(item: BucketItem) -> BucketItemResponse:
    """Convert a BucketItem domain entity to a BucketItemResponse DTO."""
    return BucketItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        category=item.category,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@dataclass
class CreateBucketItemInput:
    """Input for CreateBucketItemCommand.

    Attributes:
        user_id: Owner of the new bucket item.
        request: Item creation data.
    """

    user_id: uuid.UUID
    request: CreateBucketItemRequest


@dataclass
class UpdateBucketItemInput:
    """Input for UpdateBucketItemCommand.

    Attributes:
        user_id: Requesting user.
        item_id: ID of the item to update.
        request: Item update data.
    """

    user_id: uuid.UUID
    item_id: uuid.UUID
    request: UpdateBucketItemRequest


@dataclass
class DeleteBucketItemInput:
    """Input for DeleteBucketItemCommand.

    Attributes:
        user_id: Requesting user.
        item_id: ID of the item to delete.
    """

    user_id: uuid.UUID
    item_id: uuid.UUID


@dataclass
class DrawFromBucketInput:
    """Input for DrawFromBucketCommand.

    Attributes:
        user_id: The user performing the draw.
    """

    user_id: uuid.UUID


@dataclass
class ResolveDrawInput:
    """Input for ResolveDrawCommand.

    Attributes:
        user_id: The requesting user.
        draw_id: ID of the draw to resolve.
    """

    user_id: uuid.UUID
    draw_id: uuid.UUID


@dataclass
class ReturnDrawInput:
    """Input for ReturnDrawCommand.

    Attributes:
        user_id: The requesting user.
        draw_id: ID of the draw to return.
        request: Return justification data.
    """

    user_id: uuid.UUID
    draw_id: uuid.UUID
    request: ReturnDrawRequest


class CreateBucketItemCommand(BaseCommand[CreateBucketItemInput, BucketItemResponse]):
    """Creates a new bucket item for the authenticated user.

    Args:
        item_repo: Bucket item repository for persistence.
    """

    def __init__(self, item_repo: BucketItemRepository) -> None:
        self._item_repo = item_repo

    async def execute(self, input_data: CreateBucketItemInput) -> BucketItemResponse:
        """Create and persist a new bucket item.

        Args:
            input_data: Contains the user ID and creation request.

        Returns:
            BucketItemResponse representing the created item.
        """
        req = input_data.request
        item = BucketItem(
            user_id=input_data.user_id,
            name=req.name,
            description=req.description,
            category=req.category,
        )
        item = await self._item_repo.add(item)
        return _item_to_response(item)


class UpdateBucketItemCommand(BaseCommand[UpdateBucketItemInput, BucketItemResponse]):
    """Updates an existing bucket item.

    Args:
        item_repo: Bucket item repository for persistence.
    """

    def __init__(self, item_repo: BucketItemRepository) -> None:
        self._item_repo = item_repo

    async def execute(self, input_data: UpdateBucketItemInput) -> BucketItemResponse:
        """Update an existing bucket item with the provided fields.

        Args:
            input_data: Contains the user ID, item ID, and update request.

        Returns:
            BucketItemResponse representing the updated item.

        Raises:
            BucketItemNotFoundError: If the item does not exist.
            AuthorizationError: If the user does not own the item.
        """
        item = await self._item_repo.get_by_id(input_data.item_id)
        if item is None:
            raise BucketItemNotFoundError(str(input_data.item_id))

        if item.user_id != input_data.user_id:
            raise AuthorizationError("You do not own this bucket item")

        req = input_data.request
        if req.name is not None:
            item.name = req.name
        if req.description is not None:
            item.description = req.description
        if req.category is not None:
            item.category = req.category

        item.updated_at = datetime.now(timezone.utc)
        item = await self._item_repo.update(item)
        return _item_to_response(item)


class DeleteBucketItemCommand(BaseCommand[DeleteBucketItemInput, None]):
    """Deletes an existing bucket item.

    Args:
        item_repo: Bucket item repository for persistence.
    """

    def __init__(self, item_repo: BucketItemRepository) -> None:
        self._item_repo = item_repo

    async def execute(self, input_data: DeleteBucketItemInput) -> None:
        """Delete a bucket item by its ID.

        Args:
            input_data: Contains the user ID and item ID.

        Raises:
            BucketItemNotFoundError: If the item does not exist.
            AuthorizationError: If the user does not own the item.
        """
        item = await self._item_repo.get_by_id(input_data.item_id)
        if item is None:
            raise BucketItemNotFoundError(str(input_data.item_id))

        if item.user_id != input_data.user_id:
            raise AuthorizationError("You do not own this bucket item")

        await self._item_repo.delete(input_data.item_id)


class DrawFromBucketCommand(BaseCommand[DrawFromBucketInput, BucketDrawResponse]):
    """Draws a random item from the bucket.

    Args:
        item_repo: Bucket item repository for loading items.
        draw_repo: Bucket draw repository for persistence.
        draw_service: Domain service for draw logic.
    """

    def __init__(
        self,
        item_repo: BucketItemRepository,
        draw_repo: BucketDrawRepository,
        draw_service: BucketDrawService,
    ) -> None:
        self._item_repo = item_repo
        self._draw_repo = draw_repo
        self._draw_service = draw_service

    async def execute(self, input_data: DrawFromBucketInput) -> BucketDrawResponse:
        """Draw a random item and persist the draw.

        Args:
            input_data: Contains the user ID.

        Returns:
            BucketDrawResponse with the drawn item.

        Raises:
            ActiveDrawExistsError: If the user already has an active draw.
            NoBucketItemsError: If no items are available.
        """
        active_draw = await self._draw_repo.get_active_by_user_id(input_data.user_id)
        available_items = await self._item_repo.get_available_for_draw(input_data.user_id)

        draw = self._draw_service.draw(input_data.user_id, active_draw, available_items)
        draw = await self._draw_repo.add(draw)

        item = await self._item_repo.get_by_id(draw.bucket_item_id)
        if item is None:
            raise BucketItemNotFoundError(str(draw.bucket_item_id))

        return BucketDrawResponse(
            id=draw.id,
            item=_item_to_response(item),
            drawn_at=draw.drawn_at,
            status=draw.status.value,
            resolved_at=draw.resolved_at,
            return_justification=draw.return_justification,
        )


class ResolveDrawCommand(BaseCommand[ResolveDrawInput, BucketDrawResponse]):
    """Marks a bucket draw as resolved.

    Args:
        item_repo: Bucket item repository for item lookup.
        draw_repo: Bucket draw repository for persistence.
        draw_service: Domain service for resolve logic.
    """

    def __init__(
        self,
        item_repo: BucketItemRepository,
        draw_repo: BucketDrawRepository,
        draw_service: BucketDrawService,
    ) -> None:
        self._item_repo = item_repo
        self._draw_repo = draw_repo
        self._draw_service = draw_service

    async def execute(self, input_data: ResolveDrawInput) -> BucketDrawResponse:
        """Resolve a bucket draw.

        Args:
            input_data: Contains the user ID and draw ID.

        Returns:
            BucketDrawResponse with the resolved draw.

        Raises:
            EntityNotFoundError: If the draw does not exist.
            DrawNotActiveError: If the draw is not in ACTIVE status.
        """
        draw = await self._draw_repo.get_by_id(input_data.draw_id)
        if draw is None:
            raise EntityNotFoundError("BucketDraw", str(input_data.draw_id))

        draw = self._draw_service.resolve(draw)
        draw = await self._draw_repo.update(draw)

        item = await self._item_repo.get_by_id(draw.bucket_item_id)
        if item is None:
            raise BucketItemNotFoundError(str(draw.bucket_item_id))

        return BucketDrawResponse(
            id=draw.id,
            item=_item_to_response(item),
            drawn_at=draw.drawn_at,
            status=draw.status.value,
            resolved_at=draw.resolved_at,
            return_justification=draw.return_justification,
        )


class ReturnDrawCommand(BaseCommand[ReturnDrawInput, BucketDrawResponse]):
    """Returns a bucket draw to the bucket with a justification.

    Args:
        item_repo: Bucket item repository for item lookup.
        draw_repo: Bucket draw repository for persistence.
        draw_service: Domain service for return logic.
    """

    def __init__(
        self,
        item_repo: BucketItemRepository,
        draw_repo: BucketDrawRepository,
        draw_service: BucketDrawService,
    ) -> None:
        self._item_repo = item_repo
        self._draw_repo = draw_repo
        self._draw_service = draw_service

    async def execute(self, input_data: ReturnDrawInput) -> BucketDrawResponse:
        """Return a bucket draw with justification.

        Args:
            input_data: Contains the user ID, draw ID, and justification.

        Returns:
            BucketDrawResponse with the returned draw.

        Raises:
            EntityNotFoundError: If the draw does not exist.
            DrawNotActiveError: If the draw is not in ACTIVE status.
            JustificationTooShortError: If justification is too short.
        """
        draw = await self._draw_repo.get_by_id(input_data.draw_id)
        if draw is None:
            raise EntityNotFoundError("BucketDraw", str(input_data.draw_id))

        draw = self._draw_service.return_draw(draw, input_data.request.justification)
        draw = await self._draw_repo.update(draw)

        item = await self._item_repo.get_by_id(draw.bucket_item_id)
        if item is None:
            raise BucketItemNotFoundError(str(draw.bucket_item_id))

        return BucketDrawResponse(
            id=draw.id,
            item=_item_to_response(item),
            drawn_at=draw.drawn_at,
            status=draw.status.value,
            resolved_at=draw.resolved_at,
            return_justification=draw.return_justification,
        )
