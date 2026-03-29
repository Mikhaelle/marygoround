"""Tests for domain value objects."""

from __future__ import annotations

import pytest

from merygoround.domain.chores.value_objects import Duration, Multiplicity, TimeWeightRule
from merygoround.domain.identity.value_objects import Email
from merygoround.domain.shared.exceptions import ValidationError


class TestDuration:
    """Test suite for the Duration value object."""

    def test_valid_five_minutes(self) -> None:
        """Duration of 5 is valid."""
        d = Duration(5)
        assert d.value == 5

    def test_valid_ten_minutes(self) -> None:
        """Duration of 10 is valid."""
        d = Duration(10)
        assert d.value == 10

    def test_invalid_one(self) -> None:
        """Duration of 1 raises ValidationError."""
        with pytest.raises(ValidationError):
            Duration(1)

    def test_invalid_zero(self) -> None:
        """Duration of 0 raises ValidationError."""
        with pytest.raises(ValidationError):
            Duration(0)

    def test_invalid_negative(self) -> None:
        """Duration of -1 raises ValidationError."""
        with pytest.raises(ValidationError):
            Duration(-1)

    def test_invalid_seven(self) -> None:
        """Duration of 7 raises ValidationError (only 5 or 10 allowed)."""
        with pytest.raises(ValidationError):
            Duration(7)

    def test_invalid_fifteen(self) -> None:
        """Duration of 15 raises ValidationError."""
        with pytest.raises(ValidationError):
            Duration(15)


class TestMultiplicity:
    """Test suite for the Multiplicity value object."""

    def test_valid_one(self) -> None:
        """Multiplicity of 1 is valid."""
        m = Multiplicity(1)
        assert m.value == 1

    def test_valid_large(self) -> None:
        """Multiplicity of 10 is valid."""
        m = Multiplicity(10)
        assert m.value == 10

    def test_valid_two(self) -> None:
        """Multiplicity of 2 is valid."""
        m = Multiplicity(2)
        assert m.value == 2

    def test_invalid_zero(self) -> None:
        """Multiplicity of 0 raises ValidationError."""
        with pytest.raises(ValidationError):
            Multiplicity(0)

    def test_invalid_negative(self) -> None:
        """Multiplicity of -1 raises ValidationError."""
        with pytest.raises(ValidationError):
            Multiplicity(-1)


class TestTimeWeightRule:
    """Test suite for the TimeWeightRule value object."""

    def test_valid_midnight(self) -> None:
        """Hour 0 with positive weight is valid."""
        r = TimeWeightRule(hour=0, weight=1.0)
        assert r.hour == 0
        assert r.weight == 1.0

    def test_valid_last_hour(self) -> None:
        """Hour 23 with positive weight is valid."""
        r = TimeWeightRule(hour=23, weight=0.5)
        assert r.hour == 23

    def test_valid_max_weight(self) -> None:
        """Weight of 3.0 is valid (maximum)."""
        r = TimeWeightRule(hour=12, weight=3.0)
        assert r.weight == 3.0

    def test_invalid_hour_negative(self) -> None:
        """Negative hour raises ValidationError."""
        with pytest.raises(ValidationError):
            TimeWeightRule(hour=-1, weight=1.0)

    def test_invalid_hour_above_23(self) -> None:
        """Hour 24 raises ValidationError."""
        with pytest.raises(ValidationError):
            TimeWeightRule(hour=24, weight=1.0)

    def test_invalid_weight_zero(self) -> None:
        """Weight of 0 raises ValidationError."""
        with pytest.raises(ValidationError):
            TimeWeightRule(hour=12, weight=0)

    def test_invalid_weight_negative(self) -> None:
        """Negative weight raises ValidationError."""
        with pytest.raises(ValidationError):
            TimeWeightRule(hour=12, weight=-1.0)

    def test_invalid_weight_above_max(self) -> None:
        """Weight above 3.0 raises ValidationError."""
        with pytest.raises(ValidationError):
            TimeWeightRule(hour=12, weight=3.1)

    def test_invalid_weight_large(self) -> None:
        """Weight of 5.0 raises ValidationError."""
        with pytest.raises(ValidationError):
            TimeWeightRule(hour=12, weight=5.0)


class TestEmail:
    """Test suite for the Email value object."""

    def test_valid_email(self) -> None:
        """Standard email format is accepted."""
        e = Email("user@example.com")
        assert e.value == "user@example.com"

    def test_normalization_lowercase(self) -> None:
        """Email is normalized to lowercase."""
        e = Email("User@Example.COM")
        assert e.value == "user@example.com"

    def test_normalization_whitespace(self) -> None:
        """Leading and trailing whitespace is stripped."""
        e = Email("  user@example.com  ")
        assert e.value == "user@example.com"

    def test_valid_with_plus(self) -> None:
        """Email with plus addressing is accepted."""
        e = Email("user+tag@example.com")
        assert e.value == "user+tag@example.com"

    def test_valid_with_dots(self) -> None:
        """Email with dots in local part is accepted."""
        e = Email("first.last@example.com")
        assert e.value == "first.last@example.com"

    def test_invalid_no_at_sign(self) -> None:
        """Email without @ raises ValidationError."""
        with pytest.raises(ValidationError):
            Email("notanemail")

    def test_invalid_no_domain(self) -> None:
        """Email without domain raises ValidationError."""
        with pytest.raises(ValidationError):
            Email("user@")

    def test_invalid_no_local_part(self) -> None:
        """Email without local part raises ValidationError."""
        with pytest.raises(ValidationError):
            Email("@example.com")

    def test_invalid_empty(self) -> None:
        """Empty string raises ValidationError."""
        with pytest.raises(ValidationError):
            Email("")

    def test_invalid_spaces_in_middle(self) -> None:
        """Email with spaces in middle raises ValidationError."""
        with pytest.raises(ValidationError):
            Email("user @example.com")
