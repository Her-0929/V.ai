"""HER AI — Chat API Endpoint

Handles the full chat turn:
  1. Validate user and conversation
  2. Retrieve conversation history
  3. Generate RAG response (memories + emotion + personality)
  4. Persist messages
  5. Extract memories in background (async, non-blocking)
"""

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.rate_limit import limiter
from app.core.config import settings
from app.models import User, Conversation, Message
from app.schemas.chat import ChatRequest, ChatResponse, EmotionalContextResponse
from app.services.rag_service import rag_service


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


async def _extract_memories_background(
    user_id: UUID,
    user_message: str,
    assistant_response: str,
    conversation_id: UUID,
) -> None:
    """
    Background task: extract long-term memories from the completed exchange.
    Runs after the HTTP response has been sent — does not block the user.
    Failures are logged but do not affect the conversation.
    """
    try:
        # Import here to avoid circular dependency and to keep startup fast
        from app.services.memory_extraction_service import memory_extraction_service
        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            extracted = await memory_extraction_service.extract_from_message_pair(
                db=db,
                user_id=user_id,
                user_message=user_message,
                assistant_response=assistant_response,
                conversation_id=conversation_id,
            )
            if extracted:
                logger.info(
                    "Memory extraction: %d memories stored for user=%s",
                    len(extracted),
                    user_id,
                )
        finally:
            db.close()
    except Exception as exc:
        logger.warning("Memory extraction failed (non-fatal): %s", exc)


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def chat(
    request: Request,
    payload: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Send a message to HER and receive a personalized, memory-aware response.

    - Authenticated via JWT Bearer token (enforces current_user).
    - Creates a new conversation if conversation_id is not provided.
    - Retrieves relevant long-term memories via semantic search scoped to current_user.
    - Analyzes emotional context of the message.
    - Builds a personalized system prompt using the personality engine.
    - Saves both user message and HER response to the conversation.
    - Triggers background memory extraction from the exchange.
    """
    try:
        user_id = current_user.id
        user = current_user

        # --------------------------------------------------
        # 1. Retrieve or create conversation (Strict User Isolation)
        # --------------------------------------------------
        if payload.conversation_id:
            conversation = db.execute(
                select(Conversation).where(
                    Conversation.id == payload.conversation_id,
                    Conversation.user_id == user_id,
                )
            ).scalar_one_or_none()

            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found.",
                )
        else:
            conversation = Conversation(
                user_id=user_id,
                title=payload.message.strip()[:200],
            )
            db.add(conversation)
            db.flush()

        # --------------------------------------------------
        # 2. Retrieve recent conversation history
        # --------------------------------------------------
        history_rows = (
            db.execute(
                select(Message)
                .where(Message.conversation_id == conversation.id)
                .order_by(desc(Message.created_at), desc(Message.id))
                .limit(15)
            )
            .scalars()
            .all()
        )
        history_rows.reverse()  # chronological order for LLM

        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in history_rows
            if msg.role in ("user", "assistant")
        ]

        # --------------------------------------------------
        # 3. Generate HER response via RAG pipeline
        # --------------------------------------------------
        rag_result = await rag_service.generate_response(
            db=db,
            user_id=user_id,
            user_message=payload.message.strip(),
            conversation_history=conversation_history,
            user_name=user.username,
        )

        # --------------------------------------------------
        # 4. Persist user message
        # --------------------------------------------------
        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=payload.message.strip(),
        )
        db.add(user_msg)

        # --------------------------------------------------
        # 5. Persist HER response
        # --------------------------------------------------
        her_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=rag_result["response"],
            message_metadata={
                "emotional_context": rag_result.get("emotional_context"),
                "memory_count": rag_result["memory_count"],
                "model": rag_result["model"],
            },
        )
        db.add(her_msg)

        # --------------------------------------------------
        # 6. Update conversation timestamp
        # --------------------------------------------------
        conversation.updated_at = datetime.now(timezone.utc)

        db.commit()

        # --------------------------------------------------
        # 7. Schedule background memory extraction
        # --------------------------------------------------
        background_tasks.add_task(
            _extract_memories_background,
            user_id=user_id,
            user_message=payload.message.strip(),
            assistant_response=rag_result["response"],
            conversation_id=conversation.id,
        )


        # --------------------------------------------------
        # 9. Return response
        # --------------------------------------------------
        raw_ec = rag_result.get("emotional_context")
        emotional_context_out = (
            EmotionalContextResponse(**raw_ec) if raw_ec else None
        )

        return ChatResponse(
            conversation_id=conversation.id,
            response=rag_result["response"],
            retrieved_memories=rag_result["retrieved_memories"],
            memory_count=rag_result["memory_count"],
            model=rag_result["model"],
            emotional_context=emotional_context_out,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as error:
        db.rollback()
        logger.error("Chat endpoint error: %s", error, exc_info=True)
        raise HTTPException(
            status_code=502,
            detail=f"HER failed to generate a response: {str(error)}",
        )
