import asyncio
import json
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.memory import Memory
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service, VALID_MEMORY_TYPES

logger = logging.getLogger(__name__)

VALID_MEMORY_TYPES_SET = set(VALID_MEMORY_TYPES)

EXTRACTION_SYSTEM_PROMPT = """You are analyzing a conversation to extract long-term personal facts about the user.

Extract ONLY clear, meaningful, long-term personal information. Do NOT extract:
- Temporary states ("I'm tired today")
- Generic observations
- Anything ambiguous or uncertain
- Information that is obvious from context

For each meaningful fact, output a JSON object on its own line with EXACTLY these fields:
{
  "content": "User wants to become an AI engineer",
  "memory_type": "career_goal",
  "importance": 5,
  "confidence": 0.95,
  "excerpt": "the exact text from the conversation that supports this"
}

memory_type must be one of: personal_info, personality_trait, communication_preference, like, dislike, hobby, interest, career_goal, dream, ambition, life_event, relationship, emotional_experience, important_conversation, daily_experience, future_plan, learning_progress, milestone, general

importance: 1-5 integer (5=life-changing, 4=very significant, 3=moderately significant, 2=minor, 1=trivial)
confidence: 0.0-1.0 float

If there are NO long-term facts worth storing, output exactly: NO_MEMORIES

Analyze only the USER messages. Assistant messages provide context only."""


class MemoryExtractionService:

    async def extract_from_conversation(
        self,
        db: Session,
        user_id: UUID,
        conversation: list[dict],
        conversation_id: UUID | None = None,
    ) -> list[Memory]:
        """Extract memories from a full conversation."""
        if not conversation:
            return []

        conversation_text = self._format_conversation(conversation)
        prompt = (
            f"{EXTRACTION_SYSTEM_PROMPT}\n\n"
            f"CONVERSATION:\n{conversation_text}\n\n"
            f"Output only valid JSON objects (one per line) or NO_MEMORIES:"
        )

        try:
            response = await llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}]
            )
        except Exception:
            logger.exception("LLM call failed during memory extraction for user %s", user_id)
            return []

        extractions = self._parse_extraction_response(response)
        if not extractions:
            return []

        results: list[Memory] = []
        for item in extractions:
            content: str = item["content"]
            memory_type: str = item["memory_type"]
            importance: int = item["importance"]
            confidence: float = item["confidence"]
            excerpt: str | None = item.get("excerpt")

            try:
                # 1. Check for duplicate using memory_service.find_duplicate()
                duplicate = memory_service.find_duplicate(
                    db=db,
                    user_id=user_id,
                    content=content,
                    memory_type=memory_type,
                    similarity_threshold=0.90,
                )

                if duplicate is not None:
                    # 2. If duplicate found: update existing memory's confidence/importance if higher
                    updated = memory_service.update_memory(
                        db=db,
                        user_id=user_id,
                        memory_id=duplicate.id,
                        importance=max(duplicate.importance, importance),
                        confidence=max(duplicate.confidence, confidence),
                    )
                    if updated is not None:
                        results.append(updated)
                else:
                    # 3. If new: create memory using memory_service.create_memory()
                    new_memory = memory_service.create_memory(
                        db=db,
                        user_id=user_id,
                        memory_type=memory_type,
                        content=content,
                        importance=importance,
                        confidence=confidence,
                        source_message_id=None,
                        source_excerpt=excerpt,
                    )
                    results.append(new_memory)

            except Exception:
                logger.exception(
                    "Failed to persist extracted memory for user %s: %s",
                    user_id,
                    content[:80],
                )

        return results

    # Alias for compatibility
    extract_memories_from_conversation = extract_from_conversation

    async def extract_from_message_pair(
        self,
        db: Session,
        user_id: UUID,
        user_message: str,
        assistant_response: str,
        conversation_id: UUID | None = None,
    ) -> list[Memory]:
        """Extract memories from a single exchange."""
        conversation = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_response},
        ]
        return await self.extract_from_conversation(db, user_id, conversation, conversation_id)

    def _format_conversation(self, conversation: list[dict]) -> str:
        """Format conversation as text for LLM analysis."""
        lines = []
        for msg in conversation:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def _parse_extraction_response(self, response: str) -> list[dict]:
        """Parse LLM response. Handle NO_MEMORIES, malformed JSON gracefully."""
        response = response.strip()
        if response == "NO_MEMORIES" or not response:
            return []

        results = []
        for line in response.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("```"):
                continue
            try:
                data = json.loads(line)
                if not isinstance(data, dict):
                    continue
                # Validate required fields and ranges
                if not isinstance(data.get("content"), str) or not data["content"].strip():
                    continue
                if data.get("memory_type") not in VALID_MEMORY_TYPES_SET:
                    data["memory_type"] = "general"
                importance = int(data.get("importance", 3))
                data["importance"] = max(1, min(5, importance))
                confidence = float(data.get("confidence", 1.0))
                data["confidence"] = max(0.0, min(1.0, confidence))
                results.append(data)
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
        return results


memory_extraction_service = MemoryExtractionService()
