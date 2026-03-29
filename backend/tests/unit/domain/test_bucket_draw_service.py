"""Tests for the BucketDrawService domain service."""

from __future__ import annotations

import uuid

import pytest

from merygoround.domain.adult_bucket.entities import BucketDraw, BucketItem, DrawStatus
from merygoround.domain.adult_bucket.exceptions import (
    ActiveDrawExistsError,
    DrawNotActiveError,
    JustificationTooShortError,
    NoBucketItemsError,
)
from merygoround.domain.adult_bucket.services import BucketDrawService


@pytest.fixture
def draw_service() -> BucketDrawService:
    """Provide a BucketDrawService instance."""
    return BucketDrawService()


@pytest.fixture
def user_id() -> uuid.UUID:
    """Provide a fixed test user UUID."""
    return uuid.uuid4()


def _make_item(user_id: uuid.UUID, name: str = "Test Item") -> BucketItem:
    """Create a BucketItem for testing."""
    return BucketItem(
        id=uuid.uuid4(),
        user_id=user_id,
        name=name,
        description="A test bucket item",
    )


def _make_active_draw(user_id: uuid.UUID) -> BucketDraw:
    """Create an active BucketDraw for testing."""
    return BucketDraw(
        id=uuid.uuid4(),
        bucket_item_id=uuid.uuid4(),
        user_id=user_id,
        status=DrawStatus.ACTIVE,
    )


class TestBucketDrawService:
    """Test suite for BucketDrawService."""

    def test_draw_when_no_active_draw(
        self, draw_service: BucketDrawService, user_id: uuid.UUID
    ) -> None:
        """Drawing without an active draw succeeds and returns an ACTIVE draw."""
        items = [_make_item(user_id, f"Item {i}") for i in range(3)]
        result = draw_service.draw(user_id, active_draw=None, available_items=items)

        assert result.status == DrawStatus.ACTIVE
        assert result.user_id == user_id
        assert result.bucket_item_id in {item.id for item in items}

    def test_draw_raises_when_active_draw_exists(
        self, draw_service: BucketDrawService, user_id: uuid.UUID
    ) -> None:
        """Drawing with an existing active draw raises ActiveDrawExistsError."""
        active = _make_active_draw(user_id)
        items = [_make_item(user_id)]

        with pytest.raises(ActiveDrawExistsError):
            draw_service.draw(user_id, active_draw=active, available_items=items)

    def test_draw_raises_when_no_items(
        self, draw_service: BucketDrawService, user_id: uuid.UUID
    ) -> None:
        """Drawing with no available items raises NoBucketItemsError."""
        with pytest.raises(NoBucketItemsError):
            draw_service.draw(user_id, active_draw=None, available_items=[])

    def test_resolve_sets_status_to_resolved(
        self, draw_service: BucketDrawService, user_id: uuid.UUID
    ) -> None:
        """Resolving an active draw sets status to RESOLVED with a timestamp."""
        draw = _make_active_draw(user_id)
        result = draw_service.resolve(draw)

        assert result.status == DrawStatus.RESOLVED
        assert result.resolved_at is not None

    def test_resolve_raises_when_not_active(
        self, draw_service: BucketDrawService, user_id: uuid.UUID
    ) -> None:
        """Resolving a non-active draw raises DrawNotActiveError."""
        draw = _make_active_draw(user_id)
        draw.status = DrawStatus.RESOLVED

        with pytest.raises(DrawNotActiveError):
            draw_service.resolve(draw)

    def test_return_with_valid_justification(
        self, draw_service: BucketDrawService, user_id: uuid.UUID
    ) -> None:
        """Returning a draw with a valid justification sets status to RETURNED."""
        draw = _make_active_draw(user_id)
        justification = "I need more time to prepare for this task"
        result = draw_service.return_draw(draw, justification)

        assert result.status == DrawStatus.RETURNED
        assert result.return_justification == justification
        assert result.resolved_at is not None

    def test_return_with_short_justification_raises(
        self, draw_service: BucketDrawService, user_id: uuid.UUID
    ) -> None:
        """Returning a draw with a justification shorter than 10 chars raises error."""
        draw = _make_active_draw(user_id)

        with pytest.raises(JustificationTooShortError):
            draw_service.return_draw(draw, "too short")

    def test_return_raises_when_not_active(
        self, draw_service: BucketDrawService, user_id: uuid.UUID
    ) -> None:
        """Returning a non-active draw raises DrawNotActiveError."""
        draw = _make_active_draw(user_id)
        draw.status = DrawStatus.RETURNED

        with pytest.raises(DrawNotActiveError):
            draw_service.return_draw(draw, "This is a valid justification text")

    def test_return_strips_justification_whitespace(
        self, draw_service: BucketDrawService, user_id: uuid.UUID
    ) -> None:
        """Justification whitespace is stripped before length validation."""
        draw = _make_active_draw(user_id)

        with pytest.raises(JustificationTooShortError):
            draw_service.return_draw(draw, "   short   ")
