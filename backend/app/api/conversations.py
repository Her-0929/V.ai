"""HER AI — Conversation Management API (Milestone 6 & Milestone 11 Hardening)"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_, desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import User, Conversation, Message
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    ConversationStatsResponse,
    ConversationHistoryResponse,
    MessageResponse,
    TitleGenerateResponse,
    SummaryResponse,
)
from app.services.conversation_service import conversation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


def _require_conversation(conversation_id: UUID, user_id: UUID, db: Session) -> Conversation:
    """Enforce strict user-level data isolation: conversations are only accessible by owner."""
    conv = db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    ).scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conv


@router.get("", response_model=ConversationListResponse)
def list_conversations(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationListResponse:
    """List all conversations for the authenticated user, most recent first."""
    conversations = conversation_service.get_user_conversations(db, current_user.id, limit=limit)
    return ConversationListResponse(
        conversations=[ConversationResponse.model_validate(c) for c in conversations],
        total=len(conversations),
    )


@router.post("", response_model=ConversationResponse, status_code=201)
def create_conversation(
    body: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Create a new conversation for the authenticated user."""
    conv = conversation_service.create_conversation(db, current_user.id, title=body.title)
    return ConversationResponse.model_validate(conv)


@router.get("/search", response_model=ConversationListResponse)
def search_conversations(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationListResponse:
    """Search conversations by title or message content for the authenticated user."""
    user_id = current_user.id

    # Match on title
    title_match = select(Conversation.id).where(
        Conversation.user_id == user_id,
        Conversation.title.ilike(f"%{q}%"),
    )

    # Match on message content via subquery
    msg_match = select(Conversation.id).join(
        Message, Message.conversation_id == Conversation.id
    ).where(
        Conversation.user_id == user_id,
        Message.content.ilike(f"%{q}%"),
    )

    combined = title_match.union(msg_match).subquery()

    conversations = db.execute(
        select(Conversation)
        .where(Conversation.id.in_(select(combined)))
        .order_by(desc(Conversation.updated_at))
        .limit(limit)
    ).scalars().all()

    return ConversationListResponse(
        conversations=[ConversationResponse.model_validate(c) for c in conversations],
        total=len(conversations),
    )


@router.get("/{conversation_id}", response_model=ConversationHistoryResponse)
def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationHistoryResponse:
    """Get a conversation with its full message history. Enforces ownership."""
    conv = _require_conversation(conversation_id, current_user.id, db)

    messages = db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    ).scalars().all()

    return ConversationHistoryResponse(
        conversation=ConversationResponse.model_validate(conv),
        messages=[MessageResponse.model_validate(m) for m in messages],
        total_messages=len(messages),
    )


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Delete a conversation and all its messages. Enforces ownership."""
    _require_conversation(conversation_id, current_user.id, db)
    deleted = conversation_service.delete_conversation(db, current_user.id, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"deleted": True, "conversation_id": str(conversation_id)}


@router.get("/{conversation_id}/stats", response_model=ConversationStatsResponse)
def get_conversation_stats(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationStatsResponse:
    """Get stats for a conversation. Enforces ownership."""
    conv = _require_conversation(conversation_id, current_user.id, db)

    message_count = db.execute(
        select(func.count()).where(Message.conversation_id == conversation_id)
    ).scalar_one()

    return ConversationStatsResponse(
        id=conv.id,
        title=conv.title,
        message_count=message_count,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.post("/{conversation_id}/generate-title", response_model=TitleGenerateResponse)
async def generate_title(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TitleGenerateResponse:
    """Generate a title for a conversation using the LLM. Enforces ownership."""
    _require_conversation(conversation_id, current_user.id, db)

    try:
        title = await conversation_service.generate_title(db, current_user.id, conversation_id)
        if not title:
            raise HTTPException(status_code=422, detail="Not enough messages to generate a title.")
        return TitleGenerateResponse(conversation_id=conversation_id, title=title)
    except Exception as exc:
        logger.error("Title generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Title generation failed: {exc}")


@router.post("/{conversation_id}/summarize", response_model=SummaryResponse)
async def summarize_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    """Generate a summary of a conversation for context compression. Enforces ownership."""
    _require_conversation(conversation_id, current_user.id, db)

    try:
        summary = await conversation_service.summarize_conversation(db, current_user.id, conversation_id)
        return SummaryResponse(conversation_id=conversation_id, summary=summary)
    except Exception as exc:
        logger.error("Summarization failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Summarization failed: {exc}")
