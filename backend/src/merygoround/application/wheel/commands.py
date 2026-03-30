"""Command use cases for the Wheel bounded context."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from merygoround.application.chores.dtos import (
    ChoreResponse,
    TimeWeightRuleDTO,
    WheelConfigDTO,
)
from merygoround.application.shared.use_case import BaseCommand
from merygoround.application.wheel.dtos import SpinResultResponse
from merygoround.domain.shared.exceptions import EntityNotFoundError
from merygoround.domain.wheel.entities import SpinSession, SpinStatus

if TYPE_CHECKING:
    from merygoround.domain.chores.repository import ChoreRepository
    from merygoround.domain.wheel.repository import SpinSessionRepository
    from merygoround.domain.wheel.services import WheelSpinService


@dataclass
class SpinWheelInput:
    """Input for SpinWheelCommand.

    Attributes:
        user_id: The user performing the spin.
    """

    user_id: uuid.UUID


@dataclass
class CompleteSpinInput:
    """Input for CompleteSpinSessionCommand.

    Attributes:
        user_id: The requesting user.
        session_id: The spin session to complete.
    """

    user_id: uuid.UUID
    session_id: uuid.UUID


class SpinWheelCommand(BaseCommand[SpinWheelInput, SpinResultResponse]):
    """Spins the wheel and selects a random chore for the user.

    Args:
        chore_repo: Chore repository for loading user chores.
        spin_repo: Spin session repository for persistence.
        spin_service: Domain service for weighted random selection.
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

    async def execute(self, input_data: SpinWheelInput) -> SpinResultResponse:
        """Load user chores, spin the wheel, and persist the result.

        Args:
            input_data: Contains the user ID.

        Returns:
            SpinResultResponse with the selected chore.

        Raises:
            NoChoresAvailableError: If the user has no chores.
        """
        from merygoround.domain.chores.entities import Chore, WheelConfiguration
        from merygoround.domain.chores.value_objects import Multiplicity

        chores = await self._chore_repo.get_by_user_id(input_data.user_id)
        now = datetime.now(timezone.utc)

        completed_counts = await self._spin_repo.get_completed_counts_for_date(
            input_data.user_id, now.date()
        )

        available_chores: list[Chore] = []
        for chore in chores:
            done = completed_counts.get(chore.id, 0)
            remaining = chore.wheel_config.multiplicity.value - done
            if remaining > 0:
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
                available_chores.append(adjusted)

        selected = self._spin_service.spin(available_chores, now.hour)

        session = SpinSession(
            user_id=input_data.user_id,
            selected_chore_id=selected.id,
            chore_name=selected.name,
            spun_at=datetime.now(timezone.utc),
            status=SpinStatus.PENDING,
        )

        session = await self._spin_repo.add(session)

        chore_response = ChoreResponse(
            id=selected.id,
            name=selected.name,
            estimated_duration_minutes=selected.estimated_duration.value,
            category=selected.category,
            wheel_config=WheelConfigDTO(
                multiplicity=selected.wheel_config.multiplicity.value,
                time_weight_rules=[
                    TimeWeightRuleDTO(hour=r.hour, weight=r.weight)
                    for r in selected.wheel_config.time_weight_rules
                ],
            ),
            created_at=selected.created_at,
            updated_at=selected.updated_at,
        )

        return SpinResultResponse(
            id=session.id,
            chore=chore_response,
            spun_at=session.spun_at,
            status=session.status.value,
        )


@dataclass
class ResetDailyWheelInput:
    """Input for ResetDailyWheelCommand.

    Attributes:
        user_id: The user requesting the reset.
    """

    user_id: uuid.UUID


@dataclass
class ResetChoreInput:
    """Input for ResetChoreCommand.

    Attributes:
        user_id: The requesting user.
        chore_id: The chore to reset.
    """

    user_id: uuid.UUID
    chore_id: uuid.UUID


class ResetChoreCommand(BaseCommand[ResetChoreInput, int]):
    """Resets a specific chore for today by deleting its spin sessions.

    Args:
        spin_repo: Spin session repository for persistence.
    """

    def __init__(self, spin_repo: SpinSessionRepository) -> None:
        self._spin_repo = spin_repo

    async def execute(self, input_data: ResetChoreInput) -> int:
        """Delete all spin sessions for a chore today.

        Args:
            input_data: Contains the user ID and chore ID.

        Returns:
            The number of deleted sessions.
        """
        today = datetime.now(timezone.utc).date()
        return await self._spin_repo.delete_for_chore_on_date(
            input_data.user_id, input_data.chore_id, today
        )


class ResetDailyWheelCommand(BaseCommand[ResetDailyWheelInput, int]):
    """Resets the daily wheel by deleting all of today's spin sessions.

    Args:
        spin_repo: Spin session repository for persistence.
    """

    def __init__(self, spin_repo: SpinSessionRepository) -> None:
        self._spin_repo = spin_repo

    async def execute(self, input_data: ResetDailyWheelInput) -> int:
        """Delete all spin sessions for today.

        Args:
            input_data: Contains the user ID.

        Returns:
            The number of deleted sessions.
        """
        today = datetime.now(timezone.utc).date()
        return await self._spin_repo.delete_for_date(input_data.user_id, today)


@dataclass
class QuickCompleteChoreInput:
    """Input for QuickCompleteChoreCommand.

    Attributes:
        user_id: The requesting user.
        chore_id: The chore to mark as completed.
    """

    user_id: uuid.UUID
    chore_id: uuid.UUID


class QuickCompleteChoreCommand(BaseCommand[QuickCompleteChoreInput, None]):
    """Creates a completed spin session for a chore directly (without spinning).

    Args:
        chore_repo: Chore repository for validation.
        spin_repo: Spin session repository for persistence.
    """

    def __init__(
        self, chore_repo: ChoreRepository, spin_repo: SpinSessionRepository
    ) -> None:
        self._chore_repo = chore_repo
        self._spin_repo = spin_repo

    async def execute(self, input_data: QuickCompleteChoreInput) -> None:
        """Create a completed spin session for the given chore.

        Args:
            input_data: Contains the user ID and chore ID.

        Raises:
            EntityNotFoundError: If the chore does not exist.
        """
        chore = await self._chore_repo.get_by_id(input_data.chore_id)
        if chore is None:
            raise EntityNotFoundError("Chore", str(input_data.chore_id))

        now = datetime.now(timezone.utc)
        session = SpinSession(
            user_id=input_data.user_id,
            selected_chore_id=chore.id,
            chore_name=chore.name,
            spun_at=now,
            completed_at=now,
            status=SpinStatus.COMPLETED,
        )
        await self._spin_repo.add(session)


@dataclass
class QuickSkipChoreInput:
    """Input for QuickSkipChoreCommand.

    Attributes:
        user_id: The requesting user.
        chore_id: The chore to mark as skipped.
    """

    user_id: uuid.UUID
    chore_id: uuid.UUID


class QuickSkipChoreCommand(BaseCommand[QuickSkipChoreInput, None]):
    """Creates a skipped spin session for a chore directly (without spinning).

    Args:
        chore_repo: Chore repository for validation.
        spin_repo: Spin session repository for persistence.
    """

    def __init__(
        self, chore_repo: ChoreRepository, spin_repo: SpinSessionRepository
    ) -> None:
        self._chore_repo = chore_repo
        self._spin_repo = spin_repo

    async def execute(self, input_data: QuickSkipChoreInput) -> None:
        """Create a skipped spin session for the given chore.

        Args:
            input_data: Contains the user ID and chore ID.

        Raises:
            EntityNotFoundError: If the chore does not exist.
        """
        chore = await self._chore_repo.get_by_id(input_data.chore_id)
        if chore is None:
            raise EntityNotFoundError("Chore", str(input_data.chore_id))

        now = datetime.now(timezone.utc)
        session = SpinSession(
            user_id=input_data.user_id,
            selected_chore_id=chore.id,
            chore_name=chore.name,
            spun_at=now,
            completed_at=now,
            status=SpinStatus.SKIPPED,
        )
        await self._spin_repo.add(session)


class CompleteSpinSessionCommand(BaseCommand[CompleteSpinInput, None]):
    """Marks a spin session as completed.

    Args:
        spin_repo: Spin session repository for persistence.
    """

    def __init__(self, spin_repo: SpinSessionRepository) -> None:
        self._spin_repo = spin_repo

    async def execute(self, input_data: CompleteSpinInput) -> None:
        """Complete a spin session.

        Args:
            input_data: Contains the user ID and session ID.

        Raises:
            EntityNotFoundError: If the session does not exist.
        """
        session = await self._spin_repo.get_by_id(input_data.session_id)
        if session is None:
            raise EntityNotFoundError("SpinSession", str(input_data.session_id))

        session.status = SpinStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
        await self._spin_repo.update(session)


@dataclass
class SkipSpinInput:
    """Input for SkipSpinSessionCommand.

    Attributes:
        user_id: The requesting user.
        session_id: The spin session to skip.
    """

    user_id: uuid.UUID
    session_id: uuid.UUID


class SkipSpinSessionCommand(BaseCommand[SkipSpinInput, None]):
    """Marks a spin session as skipped.

    Args:
        spin_repo: Spin session repository for persistence.
    """

    def __init__(self, spin_repo: SpinSessionRepository) -> None:
        self._spin_repo = spin_repo

    async def execute(self, input_data: SkipSpinInput) -> None:
        """Skip a spin session.

        Args:
            input_data: Contains the user ID and session ID.

        Raises:
            EntityNotFoundError: If the session does not exist.
        """
        session = await self._spin_repo.get_by_id(input_data.session_id)
        if session is None:
            raise EntityNotFoundError("SpinSession", str(input_data.session_id))

        session.status = SpinStatus.SKIPPED
        session.completed_at = datetime.now(timezone.utc)
        await self._spin_repo.update(session)
