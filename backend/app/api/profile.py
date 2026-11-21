"""HER AI — User Profile & Preferences REST API Endpoints (Milestone 11 Hardened)

Provides endpoints to view profile stats, manage preferences (upsert/delete),
perform GDPR privacy exports, and update or delete accounts.
All endpoints strictly enforce authenticated user identity.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.conversation import Conversation
from app.models.memory import Memory
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.profile import (
    AccountDeleteResponse,
    PreferenceResponse,
    PreferenceUpdate,
    PrivacyExportResponse,
    ProfileResponse,
    UserResponse,
    UserUpdate,
)
from app.services.memory_service import memory_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"],
)


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    """Retrieve user profile, preferences, and aggregate counts for authenticated user."""
    user_id = current_user.id

    memory_count = db.scalar(
        select(func.count()).select_from(Memory).where(Memory.user_id == user_id)
    ) or 0

    conversation_count = db.scalar(
        select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
    ) or 0

    preferences = list(
        db.execute(
            select(UserPreference)
            .where(UserPreference.user_id == user_id)
            .order_by(UserPreference.key)
        ).scalars().all()
    )

    return ProfileResponse(
        user=current_user,
        preferences=preferences,
        memory_count=memory_count,
        conversation_count=conversation_count,
    )


@router.patch("", response_model=UserResponse)
def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Update profile details such as username for authenticated user."""
    if payload.username is not None:
        # Check if new username is already taken by another user
        existing = db.execute(
            select(User).where(
                User.username == payload.username,
                User.id != current_user.id,
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already in use.",
            )

        current_user.username = payload.username
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(current_user)

    return current_user


@router.delete("", response_model=AccountDeleteResponse)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountDeleteResponse:
    """Permanently delete authenticated user account and all associated data."""
    user_id = current_user.id

    try:
        memories_deleted = memory_service.delete_all_user_memories(db=db, user_id=user_id)
        db.delete(current_user)
        db.commit()
        return AccountDeleteResponse(
            deleted=True,
            memories_deleted=memories_deleted,
            message="User account and associated data successfully deleted.",
        )
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to delete account for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account.",
        )


@router.get("/export", response_model=PrivacyExportResponse)
def export_profile_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PrivacyExportResponse:
    """Export complete user data including preferences and memories (GDPR privacy export)."""
    user_id = current_user.id

    preferences = list(
        db.execute(
            select(UserPreference)
            .where(UserPreference.user_id == user_id)
            .order_by(UserPreference.key)
        ).scalars().all()
    )

    memories_data = memory_service.export_memories(db=db, user_id=user_id)

    return PrivacyExportResponse(
        user=current_user,
        preferences=preferences,
        memories=memories_data,
        total_memories=len(memories_data),
        exported_at=datetime.now(timezone.utc),
    )


@router.get("/preferences", response_model=list[PreferenceResponse])
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PreferenceResponse]:
    """List all preferences for the authenticated user."""
    preferences = list(
        db.execute(
            select(UserPreference)
            .where(UserPreference.user_id == current_user.id)
            .order_by(UserPreference.key)
        ).scalars().all()
    )
    return preferences


@router.put("/preferences", response_model=PreferenceResponse)
def upsert_preference(
    payload: PreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PreferenceResponse:
    """Create or update a user preference (upsert) for the authenticated user."""
    user_id = current_user.id

    try:
        pref = db.execute(
            select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.key == payload.key,
            )
        ).scalar_one_or_none()

        if pref:
            pref.value = payload.value
            pref.updated_at = datetime.now(timezone.utc)
        else:
            pref = UserPreference(
                user_id=user_id,
                key=payload.key,
                value=payload.value,
            )
            db.add(pref)

        db.commit()
        db.refresh(pref)
        return pref
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to upsert preference for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preference.",
        )


@router.delete("/preferences/{key}")
def delete_preference(
    key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Delete a user preference by key for the authenticated user."""
    user_id = current_user.id

    try:
        pref = db.execute(
            select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.key == key,
            )
        ).scalar_one_or_none()

        if not pref:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Preference '{key}' not found.",
            )

        db.delete(pref)
        db.commit()
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to delete preference '%s' for user %s: %s", key, user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete preference.",
        )
