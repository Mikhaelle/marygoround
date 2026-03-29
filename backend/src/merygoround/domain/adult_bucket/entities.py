"""Entities for the Adult Bucket bounded context."""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from merygoround.domain.shared.entity import AggregateRoot, Entity


class DrawStatus(enum.Enum):
    """Status of a bucket draw."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    RETURNED = "returned"


@dataclass
class BucketItem(AggregateRoot):
    """Represents an adult life task in the bucket.

    Args:
        id: Unique identifier.
        user_id: Owner of the bucket item.
        name: Display name of the task.
        description: Detailed description of the task.
        category: Optional categorization label.
        created_at: Timestamp of creation.
        updated_at: Timestamp of last modification.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    description: str = ""
    category: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BucketDraw(Entity):
    """Records a single draw from the bucket.

    Args:
        id: Unique identifier.
        bucket_item_id: The drawn bucket item.
        user_id: The user who performed the draw.
        drawn_at: Timestamp of the draw.
        status: Current status of the draw.
        resolved_at: Timestamp when the draw was resolved.
        return_justification: Reason for returning the draw.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    bucket_item_id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    drawn_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: DrawStatus = DrawStatus.ACTIVE
    resolved_at: datetime | None = None
    return_justification: str | None = None
