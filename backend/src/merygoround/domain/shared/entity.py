"""Base entity and aggregate root classes for the domain layer."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Entity:
    """Base class for all domain entities.

    Provides a UUID-based identity.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class AggregateRoot(Entity):
    """Base class for aggregate roots.

    Extends Entity with creation and modification timestamps.
    """

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
