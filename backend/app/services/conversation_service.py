
import logging
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, desc, or_, func
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message

logger = logging.getLogger(__name__)


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

    @staticmethod
    async def generate_title(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
    ) -> str | None:
        """Generate a short title for a conversation using the LLM."""
        from app.services.llm_service import llm_service

        conversation = ConversationService.get_conversation(db, user_id, conversation_id)
        if not conversation:
            return None

        # Fetch first few messages for context
        messages = db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(6)
        ).scalars().all()

        if not messages:
            return None

        convo_text = "\n".join(
            f"{m.role.upper()}: {m.content[:300]}" for m in messages
        )

        prompt = (
            "Generate a short title (maximum 8 words) for this conversation. "
            "Reply with ONLY the title — no quotes, no punctuation at the end:\n\n"
            + convo_text
        )

        try:
            raw = await llm_service.generate_response([
                {"role": "user", "content": prompt}
            ])
            title = raw.strip().strip('"\'').strip()[:200]

            if title:
                conversation.title = title
                conversation.updated_at = datetime.now(timezone.utc)
                db.commit()

            return title or None

        except Exception as exc:
            logger.warning("Title generation LLM call failed: %s", exc)
            return None

    @staticmethod
    async def summarize_conversation(
        db: Session,
        user_id: UUID,
        conversation_id: UUID,
        max_messages: int = 50,
    ) -> str:
        """Generate a concise summary of a conversation."""
        from app.services.llm_service import llm_service

        conversation = ConversationService.get_conversation(db, user_id, conversation_id)
        if not conversation:
            raise ValueError("Conversation not found.")

        messages = db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(max_messages)
        ).scalars().all()

        if not messages:
            return "This conversation has no messages yet."

        convo_text = "\n".join(
            f"{m.role.upper()}: {m.content[:500]}" for m in messages
        )

        prompt = (
            "Summarize this conversation in 3–5 sentences. "
            "Focus on the most important facts, decisions, and context shared. "
            "Be concise and factual:\n\n" + convo_text
        )

        summary = await llm_service.generate_response([
            {"role": "user", "content": prompt}
        ])
        return summary.strip()

    @staticmethod
    def search_conversations(
        db: Session,
        user_id: UUID,
        query: str,
        limit: int = 20,
    ) -> list[Conversation]:
        """Search conversations by title or message content (ILIKE)."""
        # Title match
        title_ids = db.execute(
            select(Conversation.id).where(
                Conversation.user_id == user_id,
                Conversation.title.ilike(f"%{query}%"),
            )
        ).scalars().all()

        # Message content match
        msg_ids = db.execute(
            select(Conversation.id)
            .join(Message, Message.conversation_id == Conversation.id)
            .where(
                Conversation.user_id == user_id,
                Message.content.ilike(f"%{query}%"),
            )
            .distinct()
        ).scalars().all()

        all_ids = list(set(list(title_ids) + list(msg_ids)))
        if not all_ids:
            return []

        return db.execute(
            select(Conversation)
            .where(Conversation.id.in_(all_ids))
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
        ).scalars().all()


conversation_service = ConversationService()

