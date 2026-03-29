"""SQLAlchemy ORM model for the Wheel bounded context."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from merygoround.infrastructure.database.models.base import Base, UUIDPrimaryKeyMixin


class SpinSessionModel(UUIDPrimaryKeyMixin, Base):
    """ORM model mapping to the 'spin_sessions' table.

    Attributes:
        id: UUID primary key.
        user_id: Foreign key to the spinning user.
        selected_chore_id: Foreign key to the selected chore.
        chore_name: Snapshot of the chore name at spin time.
        spun_at: Timestamp of the spin.
        completed_at: Timestamp of completion.
        status: Status string (pending, completed, skipped).
    """

    __tablename__ = "spin_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    selected_chore_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chores.id", ondelete="SET NULL"), nullable=True
    )
    chore_name: Mapped[str] = mapped_column(String(200), nullable=False)
    spun_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
