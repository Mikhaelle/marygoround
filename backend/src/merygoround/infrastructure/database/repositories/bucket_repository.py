"""SQLAlchemy implementations of the Adult Bucket repositories."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from merygoround.domain.adult_bucket.entities import BucketDraw, BucketItem, DrawStatus
from merygoround.domain.adult_bucket.repository import BucketDrawRepository, BucketItemRepository
from merygoround.infrastructure.database.models.bucket import BucketDrawModel, BucketItemModel


class SqlAlchemyBucketItemRepository(BucketItemRepository):
    """Concrete BucketItemRepository backed by SQLAlchemy and PostgreSQL.

    Args:
        session: The async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, item_id: uuid.UUID) -> BucketItem | None:
        """Retrieve a bucket item by its unique identifier.

        Args:
            item_id: The UUID of the bucket item.

        Returns:
            The BucketItem domain entity if found, otherwise None.
        """
        model = await self._session.get(BucketItemModel, item_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[BucketItem]:
        """Retrieve all bucket items belonging to a user.

        Args:
            user_id: The UUID of the owning user.

        Returns:
            List of BucketItem domain entities.
        """
        stmt = select(BucketItemModel).where(BucketItemModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_available_for_draw(self, user_id: uuid.UUID) -> list[BucketItem]:
        """Retrieve bucket items eligible for drawing.

        Excludes items that have been resolved in a previous draw.

        Args:
            user_id: The UUID of the owning user.

        Returns:
            List of BucketItem domain entities available for drawing.
        """
        resolved_item_ids = (
            select(BucketDrawModel.bucket_item_id)
            .where(
                BucketDrawModel.user_id == user_id,
                BucketDrawModel.status == DrawStatus.RESOLVED.value,
            )
            .scalar_subquery()
        )

        stmt = select(BucketItemModel).where(
            BucketItemModel.user_id == user_id,
            BucketItemModel.id.notin_(resolved_item_ids),
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def add(self, item: BucketItem) -> BucketItem:
        """Persist a new bucket item.

        Args:
            item: The BucketItem domain entity to persist.

        Returns:
            The persisted BucketItem domain entity.
        """
        model = BucketItemModel(
            id=item.id,
            user_id=item.user_id,
            name=item.name,
            description=item.description,
            category=item.category,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, item: BucketItem) -> BucketItem:
        """Update an existing bucket item.

        Args:
            item: The BucketItem domain entity with updated state.

        Returns:
            The updated BucketItem domain entity.
        """
        model = await self._session.get(BucketItemModel, item.id)
        if model is not None:
            model.name = item.name
            model.description = item.description
            model.category = item.category
            model.updated_at = item.updated_at
            await self._session.flush()
        return item

    async def delete(self, item_id: uuid.UUID) -> None:
        """Remove a bucket item by its unique identifier.

        Args:
            item_id: The UUID of the bucket item to remove.
        """
        stmt = delete(BucketItemModel).where(BucketItemModel.id == item_id)
        await self._session.execute(stmt)
        await self._session.flush()

    def _to_domain(self, model: BucketItemModel) -> BucketItem:
        """Map a BucketItemModel ORM instance to a BucketItem domain entity."""
        return BucketItem(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            description=model.description,
            category=model.category,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SqlAlchemyBucketDrawRepository(BucketDrawRepository):
    """Concrete BucketDrawRepository backed by SQLAlchemy and PostgreSQL.

    Args:
        session: The async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, draw_id: uuid.UUID) -> BucketDraw | None:
        """Retrieve a bucket draw by its unique identifier.

        Args:
            draw_id: The UUID of the bucket draw.

        Returns:
            The BucketDraw domain entity if found, otherwise None.
        """
        model = await self._session.get(BucketDrawModel, draw_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def get_active_by_user_id(self, user_id: uuid.UUID) -> BucketDraw | None:
        """Retrieve the current active draw for a user.

        Args:
            user_id: The UUID of the user.

        Returns:
            The active BucketDraw if one exists, otherwise None.
        """
        stmt = select(BucketDrawModel).where(
            BucketDrawModel.user_id == user_id,
            BucketDrawModel.status == DrawStatus.ACTIVE.value,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def get_by_user_id(
        self, user_id: uuid.UUID, page: int = 1, per_page: int = 20
    ) -> tuple[list[BucketDraw], int]:
        """Retrieve paginated bucket draws for a user.

        Args:
            user_id: The UUID of the user.
            page: Page number (1-indexed).
            per_page: Number of items per page.

        Returns:
            Tuple of (list of BucketDraw entities, total count).
        """
        count_stmt = (
            select(func.count())
            .select_from(BucketDrawModel)
            .where(BucketDrawModel.user_id == user_id)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        offset = (page - 1) * per_page
        stmt = (
            select(BucketDrawModel)
            .where(BucketDrawModel.user_id == user_id)
            .order_by(BucketDrawModel.drawn_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        draws = [self._to_domain(m) for m in result.scalars().all()]

        return draws, total

    async def add(self, draw: BucketDraw) -> BucketDraw:
        """Persist a new bucket draw.

        Args:
            draw: The BucketDraw domain entity to persist.

        Returns:
            The persisted BucketDraw domain entity.
        """
        model = BucketDrawModel(
            id=draw.id,
            bucket_item_id=draw.bucket_item_id,
            user_id=draw.user_id,
            drawn_at=draw.drawn_at,
            status=draw.status.value,
            resolved_at=draw.resolved_at,
            return_justification=draw.return_justification,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def update(self, draw: BucketDraw) -> BucketDraw:
        """Update an existing bucket draw.

        Args:
            draw: The BucketDraw domain entity with updated state.

        Returns:
            The updated BucketDraw domain entity.
        """
        model = await self._session.get(BucketDrawModel, draw.id)
        if model is not None:
            model.status = draw.status.value
            model.resolved_at = draw.resolved_at
            model.return_justification = draw.return_justification
            await self._session.flush()
        return draw

    def _to_domain(self, model: BucketDrawModel) -> BucketDraw:
        """Map a BucketDrawModel ORM instance to a BucketDraw domain entity."""
        return BucketDraw(
            id=model.id,
            bucket_item_id=model.bucket_item_id,
            user_id=model.user_id,
            drawn_at=model.drawn_at,
            status=DrawStatus(model.status),
            resolved_at=model.resolved_at,
            return_justification=model.return_justification,
        )
