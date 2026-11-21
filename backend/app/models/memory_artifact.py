import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    BigInteger,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MemoryArtifact(Base):
    __tablename__ = "memory_artifacts"

    __table_args__ = (
        CheckConstraint(
            "artifact_type IN ('note', 'letter', 'document', 'photo', 'audio_transcript')",
            name="ck_artifact_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_artifact_status"
        ),
        Index("ix_memory_artifacts_user_id_status", "user_id", "status"),
        Index("ix_memory_artifacts_user_checksum", "user_id", "checksum_sha256"),
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

    artifact_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    checksum_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
        index=True
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    context_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    retry_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False
    )

    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    user = relationship("User", back_populates="artifacts")
    sources = relationship(
        "MemorySource",
        back_populates="artifact",
        cascade="all, delete-orphan"
    )

