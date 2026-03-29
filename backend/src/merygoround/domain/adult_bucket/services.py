"""Domain services for the Adult Bucket bounded context."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone

from merygoround.domain.adult_bucket.entities import BucketDraw, BucketItem, DrawStatus
from merygoround.domain.adult_bucket.exceptions import (
    ActiveDrawExistsError,
    DrawNotActiveError,
    JustificationTooShortError,
    NoBucketItemsError,
)


class BucketDrawService:
    """Pure domain service that manages bucket draw operations.

    Enforces the invariant that at most one ACTIVE draw may exist per user.
    """

    def draw(
        self,
        user_id: uuid.UUID,
        active_draw: BucketDraw | None,
        available_items: list[BucketItem],
    ) -> BucketDraw:
        """Draw a random item from the bucket.

        Args:
            user_id: The user performing the draw.
            active_draw: The user's current active draw, or None.
            available_items: Items eligible for drawing.

        Returns:
            A new BucketDraw with ACTIVE status.

        Raises:
            ActiveDrawExistsError: If the user already has an active draw.
            NoBucketItemsError: If no items are available for drawing.
        """
        if active_draw is not None:
            raise ActiveDrawExistsError()

        if not available_items:
            raise NoBucketItemsError()

        selected_item = random.choice(available_items)

        return BucketDraw(
            id=uuid.uuid4(),
            bucket_item_id=selected_item.id,
            user_id=user_id,
            drawn_at=datetime.now(timezone.utc),
            status=DrawStatus.ACTIVE,
        )

    def resolve(self, draw: BucketDraw) -> BucketDraw:
        """Mark a draw as resolved (task completed).

        Args:
            draw: The draw to resolve.

        Returns:
            The updated BucketDraw with RESOLVED status.

        Raises:
            DrawNotActiveError: If the draw is not in ACTIVE status.
        """
        if draw.status != DrawStatus.ACTIVE:
            raise DrawNotActiveError()

        draw.status = DrawStatus.RESOLVED
        draw.resolved_at = datetime.now(timezone.utc)
        return draw

    def return_draw(self, draw: BucketDraw, justification: str) -> BucketDraw:
        """Return a draw to the bucket with a justification.

        Args:
            draw: The draw to return.
            justification: Reason for returning (minimum 10 characters).

        Returns:
            The updated BucketDraw with RETURNED status.

        Raises:
            DrawNotActiveError: If the draw is not in ACTIVE status.
            JustificationTooShortError: If justification is shorter than 10 characters.
        """
        if draw.status != DrawStatus.ACTIVE:
            raise DrawNotActiveError()

        if len(justification.strip()) < 10:
            raise JustificationTooShortError()

        draw.status = DrawStatus.RETURNED
        draw.resolved_at = datetime.now(timezone.utc)
        draw.return_justification = justification.strip()
        return draw
