
import uuid

from datetime import datetime, timezone
from pgvector.sqlalchemy import Vector

from sqlalchemy import (
    String,
    Text,
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

    embedding: Mapped[list[float] | None] = mapped_column(
         Vector(384),
        nullable=True
    )