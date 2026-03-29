"""Value objects for the Identity bounded context."""

from __future__ import annotations

import re
from dataclasses import dataclass

from merygoround.domain.shared.exceptions import ValidationError

_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email:
    """Represents a validated and normalized email address.

    The email is lowercased upon construction. Construction raises
    ValidationError if the format is invalid.

    Args:
        value: The raw email string.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        object.__setattr__(self, "value", normalized)
        if not _EMAIL_REGEX.match(normalized):
            raise ValidationError(f"Invalid email format: '{self.value}'")

    def __str__(self) -> str:
        return self.value
