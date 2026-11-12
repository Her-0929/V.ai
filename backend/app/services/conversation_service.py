
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message


class ConversationService:

    @staticmethod
    def create_conversation(
        db: Session,
        user_id: UUID,
        title: str | None = None
    ) -> Conversation:

        conversation = Conversation(
            user_id=user_id,
            title=title
        )

        try:
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_conversation(
        db: Session,
        user_id: UUID,
        conversation_id: UUID
    ) -> Conversation | None:

        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def save_message(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
        role: str,
        content: str,
        metadata: dict | None = None
    ) -> Message:

        if role not in ("user", "assistant"):
            raise ValueError("Invalid message role.")

        if not content or not content.strip():
            raise ValueError("Message content cannot be empty.")

        conversation = ConversationService.get_conversation(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id
        )

        if conversation is None:
            raise ValueError("Conversation not found.")

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content.strip(),
            message_metadata=metadata
        )

        try:
            db.add(message)

            conversation.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(message)

            return message

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_conversation_history(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 20
    ) -> list[dict]:

        if limit < 1:
            raise ValueError("Limit must be positive.")

        conversation = ConversationService.get_conversation(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id
        )

        if conversation is None:
            raise ValueError("Conversation not found.")

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at), desc(Message.id))
            .limit(limit)
        )

        messages = db.execute(statement).scalars().all()

        # Reverse so the LLM receives chronological history.
        messages.reverse()

        return [
            {
                "role": message.role,
                "content": message.content
            }
            for message in messages
        ]

    @staticmethod
    def get_user_conversations(
        db: Session,
        user_id: UUID,
        limit: int = 50
    ) -> list[Conversation]:

        if limit < 1:
            raise ValueError("Limit must be positive.")

        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(
                desc(Conversation.updated_at),
                desc(Conversation.id)
            )
            .limit(limit)
        )

        return db.execute(statement).scalars().all()

    @staticmethod
    def delete_conversation(
        db: Session,
        user_id: UUID,
        conversation_id: UUID
    ) -> bool:

        conversation = ConversationService.get_conversation(
            db=db,
            user_id=user_id,
            conversation_id=conversation_id
        )

        if conversation is None:
            return False

        try:
            db.delete(conversation)
            db.commit()
            return True

        except Exception:
            db.rollback()
            raise


conversation_service = ConversationService()
