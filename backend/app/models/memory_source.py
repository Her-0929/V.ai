
import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MemorySource(Base):
    __tablename__ = "memory_sources"

    __table_args__ = (
        CheckConstraint(
            "source_type IN ('message', 'manual', 'imported', 'system')",
            name="ck_memory_source_type"
        ),
        # CheckConstraint(
        #     "source_type != 'message' OR message_id IS NOT NULL",
        #     name="ck_memory_source_message"
        # ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    memory_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    message_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    source_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    source_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    excerpt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    memory = relationship(
        "Memory",
        back_populates="sources"
    )

    message = relationship("Message")
