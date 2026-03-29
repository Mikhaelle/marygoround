"""Query use cases for the Adult Bucket bounded context."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from merygoround.application.adult_bucket.dtos import (
    BucketDrawResponse,
    BucketItemResponse,
)
from merygoround.application.shared.use_case import BaseQuery
from merygoround.domain.adult_bucket.exceptions import BucketItemNotFoundError

if TYPE_CHECKING:
    from merygoround.domain.adult_bucket.repository import (
        BucketDrawRepository,
        BucketItemRepository,
    )


class ListBucketItemsQuery(BaseQuery[uuid.UUID, list[BucketItemResponse]]):
    """Retrieves all bucket items for the authenticated user.

    Args:
        item_repo: Bucket item repository for lookup.
    """

    def __init__(self, item_repo: BucketItemRepository) -> None:
        self._item_repo = item_repo

    async def execute(self, input_data: uuid.UUID) -> list[BucketItemResponse]:
        """List all bucket items belonging to the user.

        Args:
            input_data: The UUID of the authenticated user.

        Returns:
            List of BucketItemResponse DTOs.
        """
        items = await self._item_repo.get_by_user_id(input_data)
        return [
            BucketItemResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                category=item.category,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]


class GetActiveDrawQuery(BaseQuery[uuid.UUID, BucketDrawResponse | None]):
    """Retrieves the active bucket draw for the authenticated user.

    Args:
        draw_repo: Bucket draw repository for lookup.
        item_repo: Bucket item repository for item details.
    """

    def __init__(
        self,
        draw_repo: BucketDrawRepository,
        item_repo: BucketItemRepository,
    ) -> None:
        self._draw_repo = draw_repo
        self._item_repo = item_repo

    async def execute(self, input_data: uuid.UUID) -> BucketDrawResponse | None:
        """Get the active draw for the user, if one exists.

        Args:
            input_data: The UUID of the authenticated user.

        Returns:
            BucketDrawResponse if an active draw exists, otherwise None.

        Raises:
            BucketItemNotFoundError: If the drawn item cannot be found.
        """
        draw = await self._draw_repo.get_active_by_user_id(input_data)
        if draw is None:
            return None

        item = await self._item_repo.get_by_id(draw.bucket_item_id)
        if item is None:
            raise BucketItemNotFoundError(str(draw.bucket_item_id))

        return BucketDrawResponse(
            id=draw.id,
            item=BucketItemResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                category=item.category,
                created_at=item.created_at,
                updated_at=item.updated_at,
            ),
            drawn_at=draw.drawn_at,
            status=draw.status.value,
            resolved_at=draw.resolved_at,
            return_justification=draw.return_justification,
        )
