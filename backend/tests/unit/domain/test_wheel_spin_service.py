"""Tests for the WheelSpinService domain service."""

from __future__ import annotations

import uuid
from unittest.mock import patch

import pytest

from merygoround.domain.chores.entities import Chore, WheelConfiguration
from merygoround.domain.chores.value_objects import Duration, Multiplicity, TimeWeightRule
from merygoround.domain.wheel.exceptions import NoChoresAvailableError
from merygoround.domain.wheel.services import WheelSpinService


@pytest.fixture
def spin_service() -> WheelSpinService:
    """Provide a WheelSpinService instance."""
    return WheelSpinService()


def _make_chore(
    name: str = "Test Chore",
    multiplicity: int = 1,
    time_weight_rules: list[TimeWeightRule] | None = None,
) -> Chore:
    """Create a Chore for testing."""
    return Chore(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        name=name,
        estimated_duration=Duration(5),
        wheel_config=WheelConfiguration(
            multiplicity=Multiplicity(multiplicity),
            time_weight_rules=time_weight_rules or [],
        ),
    )


class TestWheelSpinService:
    """Test suite for WheelSpinService."""

    def test_spin_raises_when_no_chores(self, spin_service: WheelSpinService) -> None:
        """Spinning with an empty chore list raises NoChoresAvailableError."""
        with pytest.raises(NoChoresAvailableError):
            spin_service.spin([], current_hour=12)

    def test_spin_returns_single_chore(self, spin_service: WheelSpinService) -> None:
        """Spinning with a single chore always returns that chore."""
        chore = _make_chore(name="Only Chore")
        result = spin_service.spin([chore], current_hour=12)
        assert result.id == chore.id
        assert result.name == "Only Chore"

    def test_spin_uses_weighted_selection(self, spin_service: WheelSpinService) -> None:
        """Spinning uses random.choices with calculated weights."""
        chore_a = _make_chore(name="A", multiplicity=1)
        chore_b = _make_chore(name="B", multiplicity=5)

        with patch("merygoround.domain.wheel.services.random.choices") as mock_choices:
            mock_choices.return_value = [chore_b]
            result = spin_service.spin([chore_a, chore_b], current_hour=12)

            mock_choices.assert_called_once()
            call_args = mock_choices.call_args
            weights = call_args.kwargs["weights"]
            assert weights == [1.0, 5.0]
            assert result.name == "B"

    def test_time_weight_applied(self, spin_service: WheelSpinService) -> None:
        """Time weight rule is applied when hour matches."""
        chore = _make_chore(
            name="Timed",
            multiplicity=2,
            time_weight_rules=[TimeWeightRule(hour=10, weight=3.0)],
        )

        weight = spin_service.get_effective_weight(chore, current_hour=10)
        assert weight == 6.0

    def test_default_time_weight_when_no_match(
        self, spin_service: WheelSpinService
    ) -> None:
        """Default weight of 1.0 is used when no time rule matches the hour."""
        chore = _make_chore(
            name="No Match",
            multiplicity=3,
            time_weight_rules=[TimeWeightRule(hour=8, weight=2.0)],
        )

        weight = spin_service.get_effective_weight(chore, current_hour=15)
        assert weight == 3.0

    def test_spin_with_multiple_chores_returns_valid_chore(
        self, spin_service: WheelSpinService
    ) -> None:
        """Spinning with multiple chores returns one of the input chores."""
        chores = [_make_chore(name=f"Chore {i}") for i in range(5)]
        result = spin_service.spin(chores, current_hour=12)
        assert result in chores

    def test_effective_weight_multiplicity_times_time_weight(
        self, spin_service: WheelSpinService
    ) -> None:
        """Effective weight equals multiplicity times the matching time weight."""
        chore = _make_chore(
            name="Weighted",
            multiplicity=4,
            time_weight_rules=[
                TimeWeightRule(hour=0, weight=0.5),
                TimeWeightRule(hour=12, weight=2.0),
            ],
        )

        assert spin_service.get_effective_weight(chore, current_hour=0) == 2.0
        assert spin_service.get_effective_weight(chore, current_hour=12) == 8.0
        assert spin_service.get_effective_weight(chore, current_hour=6) == 4.0
