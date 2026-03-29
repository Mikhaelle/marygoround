"""Query use cases for the Wheel bounded context."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from merygoround.application.shared.use_case import BaseQuery
from merygoround.application.wheel.dtos import (
    SpinHistoryItem,
    SpinHistoryResponse,
    WheelSegmentResponse,
)

if TYPE_CHECKING:
    from merygoround.domain.chores.repository import ChoreRepository
    from merygoround.domain.wheel.repository import SpinSessionRepository
    from merygoround.domain.wheel.services import WheelSpinService


def _generate_color(name: str) -> str:
    """Generate a deterministic hex color from a string."""
    digest = hashlib.md5(name.encode()).hexdigest()  # noqa: S324
    return f"#{digest[:6]}"


class GetWheelSegmentsQuery(BaseQuery[uuid.UUID, list[WheelSegmentResponse]]):
    """Returns wheel segments with effective weights for the current hour.

    Excludes chores that were already completed today.

    Args:
        chore_repo: Chore repository for loading user chores.
        spin_repo: Spin session repository for checking today's completions.
        spin_service: Domain service for weight calculation.
    """

    def __init__(
        self,
        chore_repo: ChoreRepository,
        spin_repo: SpinSessionRepository,
        spin_service: WheelSpinService,
    ) -> None:
        self._chore_repo = chore_repo
        self._spin_repo = spin_repo
        self._spin_service = spin_service

    async def execute(self, input_data: uuid.UUID) -> list[WheelSegmentResponse]:
        """Build wheel segments for the user's chores.

        Args:
            input_data: The UUID of the authenticated user.

        Returns:
            List of WheelSegmentResponse DTOs excluding today's completed chores.
        """
        from merygoround.domain.chores.entities import Chore, WheelConfiguration
        from merygoround.domain.chores.value_objects import Multiplicity

        chores = await self._chore_repo.get_by_user_id(input_data)
        now = datetime.now(timezone.utc)

        completed_counts = await self._spin_repo.get_completed_counts_for_date(
            input_data, now.date()
        )

        segments: list[WheelSegmentResponse] = []
        for chore in chores:
            done = completed_counts.get(chore.id, 0)
            remaining = chore.wheel_config.multiplicity.value - done
            if remaining <= 0:
                continue

            adjusted = Chore(
                id=chore.id,
                user_id=chore.user_id,
                name=chore.name,
                estimated_duration=chore.estimated_duration,
                category=chore.category,
                wheel_config=WheelConfiguration(
                    multiplicity=Multiplicity(remaining),
                    time_weight_rules=chore.wheel_config.time_weight_rules,
                ),
                created_at=chore.created_at,
                updated_at=chore.updated_at,
            )
            segments.append(
                WheelSegmentResponse(
                    chore_id=adjusted.id,
                    name=adjusted.name,
                    color=_generate_color(adjusted.name),
                    effective_weight=self._spin_service.get_effective_weight(adjusted, now.hour),
                )
            )

        return segments


@dataclass
class GetSpinHistoryInput:
    """Input for GetSpinHistoryQuery.

    Attributes:
        user_id: The authenticated user.
        page: Page number.
        per_page: Items per page.
    """

    user_id: uuid.UUID
    page: int = 1
    per_page: int = 20


class GetSpinHistoryQuery(BaseQuery[GetSpinHistoryInput, SpinHistoryResponse]):
    """Retrieves paginated spin history for the authenticated user.

    Args:
        spin_repo: Spin session repository for lookup.
    """

    def __init__(self, spin_repo: SpinSessionRepository) -> None:
        self._spin_repo = spin_repo

    async def execute(self, input_data: GetSpinHistoryInput) -> SpinHistoryResponse:
        """Fetch paginated spin history.

        Args:
            input_data: Contains user ID and pagination parameters.

        Returns:
            SpinHistoryResponse with paginated spin sessions.
        """
        sessions, total = await self._spin_repo.get_by_user_id(
            input_data.user_id,
            page=input_data.page,
            per_page=input_data.per_page,
        )

        items = [
            SpinHistoryItem(
                id=s.id,
                chore_name=s.chore_name,
                spun_at=s.spun_at,
                completed_at=s.completed_at,
                status=s.status.value,
            )
            for s in sessions
        ]

        return SpinHistoryResponse(
            items=items,
            total=total,
            page=input_data.page,
            per_page=input_data.per_page,
        )
