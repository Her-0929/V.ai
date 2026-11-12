
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, Conversation, Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import rag_service


router = APIRouter(
    prefix="/api",
    tags=["Chat"]
)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        # 1. Validate user
        user = db.get(User, request.user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        # 2. Retrieve or create conversation
        if request.conversation_id:

            conversation = db.execute(
                select(Conversation).where(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == request.user_id
                )
            ).scalar_one_or_none()

            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found."
                )

        else:
            conversation = Conversation(
                user_id=request.user_id,
                title=request.message.strip()[:200]
            )

            db.add(conversation)
            db.flush()

        # 3. Retrieve recent conversation history
        history_statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation.id
            )
            .order_by(desc(Message.created_at), desc(Message.id))
            .limit(15)
        )

        history_messages = (
            db.execute(history_statement)
            .scalars()
            .all()
        )

        # Restore chronological order
        history_messages.reverse()

        conversation_history = [
            {
                "role": message.role,
                "content": message.content
            }
            for message in history_messages
            if message.role in ("user", "assistant")
        ]

        # 4. Generate HER response using RAG
        rag_result = await rag_service.generate_response(
            db=db,
            user_id=request.user_id,
            user_message=request.message.strip(),
            conversation_history=conversation_history
        )

        # 5. Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message.strip()
        )

        db.add(user_message)

        # 6. Save HER response
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=rag_result["response"]
        )

        db.add(assistant_message)

        # 7. Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)

        # 8. Commit transaction
        db.commit()

        return ChatResponse(
            conversation_id=conversation.id,
            response=rag_result["response"],
            retrieved_memories=rag_result["retrieved_memories"],
            memory_count=rag_result["memory_count"],
            model=rag_result["model"]
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=f"HER failed to generate a response: {str(error)}"
        )
