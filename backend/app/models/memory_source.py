import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MemorySource(Base):
    __tablename__ = "memory_sources"

    __table_args__ = (
        CheckConstraint(
            "source_type IN ('message', 'letter', 'note', 'document', 'photo', 'audio', 'manual', 'imported', 'system')",
            name="ck_memory_source_type"
        ),
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

    artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("memory_artifacts.id", ondelete="CASCADE"),
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

    source_location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    excerpt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    source_metadata: Mapped[dict | None] = mapped_column(
        JSON,
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

    artifact = relationship(
        "MemoryArtifact",
        back_populates="sources"
    )
