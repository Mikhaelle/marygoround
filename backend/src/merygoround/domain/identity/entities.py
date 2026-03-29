"""Entities for the Identity bounded context."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from merygoround.domain.identity.value_objects import Email
from merygoround.domain.shared.entity import AggregateRoot


@dataclass
class User(AggregateRoot):
    """Represents an authenticated user of the system.

    Args:
        id: Unique identifier.
        email: Validated email address value object.
        hashed_password: Bcrypt-hashed password string.
        name: Display name of the user.
        created_at: Timestamp of account creation.
        updated_at: Timestamp of last account update.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: Email = field(default_factory=lambda: Email("placeholder@example.com"))
    hashed_password: str = ""
    name: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
