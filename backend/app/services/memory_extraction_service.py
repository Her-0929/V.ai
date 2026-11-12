
import json
import logging

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.memory import Memory
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service

logger = logging.getLogger(__name__)

VALID_MEMORY_TYPES = {
    "personal_info", "personality_trait", "communication_preference",
    "like", "dislike", "hobby", "interest", "career_goal", "dream",
    "ambition", "life_event", "relationship", "emotional_experience",
    "important_conversation", "daily_experience", "future_plan",
    "learning_progress", "milestone", "general"
}


class MemoryExtractionService:

    EXTRACTION_PROMPT = """You are analyzing a conversation to extract long-term personal facts about the user.

Extract ONLY clear, meaningful, long-term personal information. Do NOT extract:
- Temporary states or passing comments
- Generic observations
- Information that is already obvious from context
- Anything uncertain or ambiguous

For each fact, output a JSON object on its own line with these fields:
- content: the fact, written as a clear statement about the user (e.g. "User wants to become an AI engineer")
- memory_type: one of [personal_info, personality_trait, communication_preference, like, dislike, hobby, interest, career_goal, dream, ambition, life_event, relationship, emotional_experience, important_conversation, daily_experience, future_plan, learning_progress, milestone, general]
- importance: integer 1-5 (5=life-changing, 4=very significant, 3=moderately significant, 2=minor, 1=trivial)
- confidence: float 0.0-1.0 (how certain you are this is accurate)
- excerpt: the specific text from the conversation that supports this fact

If there are no long-term facts worth storing, output exactly: NO_MEMORIES

Analyze the user messages only. The assistant messages provide context but are not facts about the user.

CONVERSATION:
{conversation}

Output only valid JSON objects (one per line) or NO_MEMORIES:"""

    # ------------------------------------------------------------------ #
    #  Public interface                                                    #
    # ------------------------------------------------------------------ #

    async def extract_memories_from_conversation(
        self,
        db: Session,
        user_id: UUID,
        conversation: list[dict],   # list of {role, content}
        conversation_id: UUID | None = None,
    ) -> list[Memory]:
        """
        Send a conversation to the LLM and persist extracted memories.

        For each extracted fact:
          1. Check for semantic duplicates (threshold 0.90).
          2. If duplicate found: update existing memory's importance/confidence.
          3. Otherwise: create a new memory with embedding.

        Returns list of created/updated Memory objects.
        """
        if not conversation:
            return []

        # Build the conversation text for the prompt
        conversation_text = self._format_conversation(conversation)
        prompt = self.EXTRACTION_PROMPT.format(conversation=conversation_text)

        try:
            response = await llm_service.generate_response(
                messages=[{"role": "user", "content": prompt}]
            )
        except Exception:
            logger.exception(
                "LLM call failed during memory extraction for user %s", user_id
            )
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
                # --- Duplicate check ---
                duplicate = memory_service.find_duplicate(
                    db=db,
                    user_id=user_id,
                    content=content,
                    memory_type=memory_type,
                    similarity_threshold=0.90,
                )

                if duplicate is not None:
                    # Update existing memory instead of creating a new one
                    updated = memory_service.update_memory(
                        db=db,
                        user_id=user_id,
                        memory_id=duplicate.id,
                        # Raise importance/confidence if the new extraction is stronger
                        importance=max(duplicate.importance, importance),
                        confidence=max(duplicate.confidence, confidence),
                    )
                    if updated is not None:
                        results.append(updated)
                else:
                    # Create brand-new memory
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
                # Continue with remaining extractions rather than aborting all

        return results

    async def extract_from_message_pair(
        self,
        db: Session,
        user_id: UUID,
        user_message: str,
        assistant_response: str,
        conversation_id: UUID | None = None,
    ) -> list[Memory]:
        """Extract memories from a single user + assistant message exchange."""
        conversation = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_response},
        ]
        return await self.extract_memories_from_conversation(
            db=db,
            user_id=user_id,
            conversation=conversation,
            conversation_id=conversation_id,
        )

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _parse_extraction_response(self, response: str) -> list[dict]:
        """
        Parse LLM extraction output.

        Handles:
          - Valid JSON objects (one per line)
          - NO_MEMORIES sentinel
          - Malformed / partial JSON (skipped gracefully)
          - Field validation (memory_type, importance range, confidence range)

        Returns a list of validated extraction dicts.
        """
        response = response.strip()

        if not response or response.upper() == "NO_MEMORIES":
            return []

        results: list[dict] = []

        for line in response.splitlines():
            line = line.strip()
            if not line:
                continue

            # Skip lines that are plainly not JSON objects
            if not line.startswith("{"):
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                logger.debug("Skipping malformed JSON line: %s", line[:120])
                continue

            # --- Validate required fields ---
            content = obj.get("content", "").strip()
            if not content:
                continue

            memory_type = obj.get("memory_type", "general")
            if memory_type not in VALID_MEMORY_TYPES:
                logger.debug(
                    "Unknown memory_type %r — defaulting to 'general'", memory_type
                )
                memory_type = "general"

            # Clamp importance to [1, 5]
            try:
                importance = int(obj.get("importance", 3))
            except (TypeError, ValueError):
                importance = 3
            importance = max(1, min(5, importance))

            # Clamp confidence to [0.0, 1.0]
            try:
                confidence = float(obj.get("confidence", 1.0))
            except (TypeError, ValueError):
                confidence = 1.0
            confidence = max(0.0, min(1.0, confidence))

            excerpt: str | None = obj.get("excerpt") or None

            results.append({
                "content": content,
                "memory_type": memory_type,
                "importance": importance,
                "confidence": confidence,
                "excerpt": excerpt,
            })

        return results

    @staticmethod
    def _format_conversation(conversation: list[dict]) -> str:
        """Format conversation list into a readable string for the LLM prompt."""
        lines: list[str] = []
        for turn in conversation:
            role = turn.get("role", "unknown").upper()
            content = turn.get("content", "").strip()
            if content:
                lines.append(f"{role}: {content}")
        return "\n".join(lines)


memory_extraction_service = MemoryExtractionService()
