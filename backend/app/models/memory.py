import uuid
from datetime import date, datetime, timezone
from pgvector.sqlalchemy import Vector

from sqlalchemy import (
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    Boolean,
    JSON,
    CheckConstraint
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Memory(Base):
    __tablename__ = "memories"

    __table_args__ = (
        CheckConstraint(
            "importance >= 1 AND importance <= 5",
            name="ck_memory_importance"
        ),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_memory_confidence"
        ),
        CheckConstraint(
            "event_date_precision IN ('day', 'month', 'year', 'decade', 'unknown')",
            name="ck_memory_event_date_precision"
        ),
        CheckConstraint(
            "status IN ('active', 'superseded', 'disputed')",
            name="ck_memory_status"
        ),
        CheckConstraint(
            "access_scope IN ('default', 'private', 'archival')",
            name="ck_memory_access_scope"
        ),
        CheckConstraint(
            "superseded_by_id IS NULL OR superseded_by_id != id",
            name="ck_memory_no_self_supersede"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    memory_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    importance: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False
    )

    event_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True
    )

    event_date_precision: Mapped[str] = mapped_column(
        String(20),
        default="unknown",
        nullable=False
    )

    source_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
        index=True
    )

    superseded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("memories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    access_scope: Mapped[str] = mapped_column(
        String(30),
        default="default",
        nullable=False
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    memory_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="memories"
    )

    sources = relationship(
        "MemorySource",
        back_populates="memory",
        cascade="all, delete-orphan"
    )

    superseded_by = relationship(
        "Memory",
        remote_side="[Memory.id]",
        foreign_keys="[Memory.superseded_by_id]",
        backref="superseded_memories",
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(384),
        nullable=True
    )
