"""HER AI — RAG (Retrieval-Augmented Generation) Service

Orchestrates the full pipeline:
  User Message → Memory Retrieval → Emotional Analysis →
  Personality Context → LLM Generation → Response
"""

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.personality import build_system_prompt
from app.services.llm_service import llm_service
from app.services.memory_retrieval_service import memory_retrieval_service
from app.services.emotional_intelligence_service import (
    emotional_intelligence_service,
    EmotionalContext,
    Emotion,
)

logger = logging.getLogger(__name__)


class RAGService:

    # ==========================================
    # RAG CONFIGURATION
    # ==========================================

    # Minimum cosine similarity for a memory to be included in context.
    # Verified against real retrieval data: 0.20 successfully retrieves
    # the "career_goal" memory at similarity 0.23–0.27.
    MIN_MEMORY_SIMILARITY = 0.20

    # Maximum number of conversation history messages to include.
    MAX_HISTORY_MESSAGES = 15

    # Include recent conversation history in LLM context.
    ENABLE_HISTORY = True

    # ==========================================
    # GENERATE RESPONSE
    # ==========================================

    async def generate_response(
        self,
        db: Session,
        user_id: UUID,
        user_message: str,
        conversation_history: list[dict] | None = None,
        user_name: str | None = None,
    ) -> dict:
        """
        Full RAG pipeline: retrieve memories, analyze emotion,
        build personalized context, generate response.

        Returns dict with:
          - response: str
          - retrieved_memories: list[dict]
          - memory_count: int
          - model: str
          - emotional_context: dict
        """

        if not user_message or not user_message.strip():
            raise ValueError("User message cannot be empty.")

        user_message = user_message.strip()

        # ======================================
        # 1. RETRIEVE RELEVANT MEMORIES
        # ======================================

        try:
            raw_memories = memory_retrieval_service.search_similar_memories(
                db=db,
                user_id=user_id,
                query=user_message,
                limit=settings.RAG_TOP_K,
            )
        except Exception as exc:
            logger.warning("Memory retrieval skipped due to exception: %s", exc)
            raw_memories = []

        logger.debug(
            "Memory retrieval: user=%s query=%r raw=%d",
            user_id,
            user_message[:60],
            len(raw_memories),
        )

        # ======================================
        # 2. FILTER MEMORIES BY SIMILARITY
        # ======================================

        memories = [
            m for m in raw_memories
            if m.get("similarity", 0) >= self.MIN_MEMORY_SIMILARITY
        ]

        logger.debug(
            "Memory filter: threshold=%.2f relevant=%d",
            self.MIN_MEMORY_SIMILARITY,
            len(memories),
        )

        # ======================================
        # 3. ANALYZE EMOTIONAL CONTEXT
        # ======================================

        emotional_ctx: EmotionalContext = (
            emotional_intelligence_service.analyze_message(
                message=user_message,
                conversation_history=conversation_history,
            )
        )

        emotional_guidance = emotional_intelligence_service.format_for_prompt(
            emotional_ctx
        )

        logger.debug(
            "Emotion: %s / %s / confidence=%.2f",
            emotional_ctx.primary_emotion,
            emotional_ctx.intensity,
            emotional_ctx.confidence,
        )

        # ======================================
        # 4. BUILD PERSONALIZED SYSTEM PROMPT
        # ======================================

        system_message = build_system_prompt(
            memories=memories,
            emotional_context=emotional_guidance if emotional_guidance else None,
            user_name=user_name,
        )

        # ======================================
        # 5. ASSEMBLE LLM MESSAGE LIST
        # ======================================

        messages: list[dict] = [
            {"role": "system", "content": system_message}
        ]

        # ======================================
        # 6. INJECT CONVERSATION HISTORY
        # ======================================

        if self.ENABLE_HISTORY and conversation_history:
            valid_history = [
                msg
                for msg in conversation_history
                if msg.get("role") in ("user", "assistant")
                and isinstance(msg.get("content"), str)
                and msg["content"].strip()
                # Exclude the current message if it was already appended
                and msg["content"].strip() != user_message
            ]
            messages.extend(valid_history[-self.MAX_HISTORY_MESSAGES :])

        # ======================================
        # 7. APPEND CURRENT USER MESSAGE
        # ======================================

        messages.append({"role": "user", "content": user_message})

        # ======================================
        # 8. GENERATE RESPONSE VIA LLM
        # ======================================

        response = await llm_service.generate_response(messages)

        logger.debug("LLM response length: %d chars", len(response))

        # ======================================
        # 9. RETURN STRUCTURED RESULT
        # ======================================

        return {
            "response": response,
            "retrieved_memories": memories,
            "memory_count": len(memories),
            "model": llm_service.model,
            "emotional_context": {
                "emotion": emotional_ctx.primary_emotion.value,
                "intensity": emotional_ctx.intensity.value,
                "confidence": emotional_ctx.confidence,
                "should_acknowledge": emotional_ctx.should_acknowledge,
            },
        }


# ==========================================
# SERVICE INSTANCE
# ==========================================

rag_service = RAGService()
