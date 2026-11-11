
import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "key",
            name="uq_user_preference_key"
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

    key: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    value: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
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

    user = relationship(
        "User",
        back_populates="preferences"
    )
