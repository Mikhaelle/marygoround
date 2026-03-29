"""Data transfer objects for the Adult Bucket application layer."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CreateBucketItemRequest(BaseModel):
    """Request DTO for creating a new bucket item.

    Attributes:
        name: Display name of the bucket item.
        description: Detailed description.
        category: Optional category label.
    """

    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    category: str | None = None


class UpdateBucketItemRequest(BaseModel):
    """Request DTO for updating an existing bucket item.

    All fields are optional; only provided fields are updated.

    Attributes:
        name: Display name.
        description: Detailed description.
        category: Category label.
    """

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = None


class BucketItemResponse(BaseModel):
    """Response DTO representing a bucket item.

    Attributes:
        id: Bucket item unique identifier.
        name: Display name.
        description: Detailed description.
        category: Category label (if any).
        created_at: Creation timestamp.
        updated_at: Last modification timestamp.
    """

    id: uuid.UUID
    name: str
    description: str
    category: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BucketDrawResponse(BaseModel):
    """Response DTO representing a bucket draw.

    Attributes:
        id: Draw unique identifier.
        item: The drawn bucket item.
        drawn_at: Timestamp of the draw.
        status: Current status of the draw.
        resolved_at: Timestamp of resolution (if applicable).
        return_justification: Return reason (if applicable).
    """

    id: uuid.UUID
    item: BucketItemResponse
    drawn_at: datetime
    status: str
    resolved_at: datetime | None
    return_justification: str | None


class ReturnDrawRequest(BaseModel):
    """Request DTO for returning a bucket draw.

    Attributes:
        justification: Reason for returning (minimum 10 characters).
    """

    justification: str = Field(min_length=10, max_length=2000)
