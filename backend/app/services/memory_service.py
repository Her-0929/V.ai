
import logging

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models.memory import Memory
from app.models.memory_source import MemorySource
from app.services.embedding_service import embedding_service
from app.services.memory_embedding_service import memory_embedding_service
from app.services.memory_retrieval_service import memory_retrieval_service

logger = logging.getLogger(__name__)

VALID_MEMORY_TYPES = {
    "personal_info", "personality_trait", "communication_preference",
    "like", "dislike", "hobby", "interest", "career_goal", "dream",
    "ambition", "life_event", "relationship", "emotional_experience",
    "important_conversation", "daily_experience", "future_plan",
    "learning_progress", "milestone", "general"
}


class MemoryService:

    def create_memory(
        self,
        db: Session,
        user_id: UUID,
        memory_type: str,
        content: str,
        importance: int = 3,
        confidence: float = 1.0,
        metadata: dict | None = None,
        source_message_id: UUID | None = None,
        source_excerpt: str | None = None,
    ) -> Memory:
        """Create a memory with embedding and optional MemorySource in one transaction."""
        try:
            # Generate embedding before persisting
            embedding = embedding_service.generate_embedding(content)

            memory = Memory(
                user_id=user_id,
                memory_type=memory_type,
                content=content,
                importance=importance,
                confidence=confidence,
                is_active=True,
                memory_metadata=metadata,
                embedding=embedding,
            )
            db.add(memory)
            db.flush()  # get memory.id without committing yet

            # Attach source record if relevant info provided
            if source_message_id is not None or source_excerpt is not None:
                source = MemorySource(
                    memory_id=memory.id,
                    message_id=source_message_id,
                    source_type="message" if source_message_id else "manual",
                    excerpt=source_excerpt,
                )
                db.add(source)

            db.commit()
            db.refresh(memory)
            return memory

        except Exception:
            db.rollback()
            logger.exception("Failed to create memory for user %s", user_id)
            raise

    def get_memory(
        self,
        db: Session,
        user_id: UUID,
        memory_id: UUID,
    ) -> Memory | None:
        """Retrieve a single memory scoped to the given user."""
        return db.execute(
            select(Memory).where(
                Memory.id == memory_id,
                Memory.user_id == user_id,
            )
        ).scalar_one_or_none()

    def update_memory(
        self,
        db: Session,
        user_id: UUID,
        memory_id: UUID,
        content: str | None = None,
        importance: int | None = None,
        confidence: float | None = None,
        is_active: bool | None = None,
        metadata: dict | None = None,
    ) -> Memory | None:
        """Update a memory. Regenerates embedding if content changes."""
        memory = self.get_memory(db, user_id, memory_id)
        if memory is None:
            return None

        try:
            if content is not None and content != memory.content:
                memory.content = content
                memory.embedding = embedding_service.generate_embedding(content)

            if importance is not None:
                memory.importance = importance

            if confidence is not None:
                memory.confidence = confidence

            if is_active is not None:
                memory.is_active = is_active

            if metadata is not None:
                memory.memory_metadata = metadata

            memory.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(memory)
            return memory

        except Exception:
            db.rollback()
            logger.exception("Failed to update memory %s", memory_id)
            raise

    def deactivate_memory(
        self,
        db: Session,
        user_id: UUID,
        memory_id: UUID,
    ) -> bool:
        """Soft-delete: set is_active=False. Returns True if found and deactivated."""
        memory = self.get_memory(db, user_id, memory_id)
        if memory is None:
            return False

        try:
            memory.is_active = False
            memory.updated_at = datetime.now(timezone.utc)
            db.commit()
            return True

        except Exception:
            db.rollback()
            logger.exception("Failed to deactivate memory %s", memory_id)
            raise

    def delete_memory(
        self,
        db: Session,
        user_id: UUID,
        memory_id: UUID,
    ) -> bool:
        """Hard-delete a memory. Returns True if deleted, False if not found."""
        memory = self.get_memory(db, user_id, memory_id)
        if memory is None:
            return False

        try:
            db.delete(memory)
            db.commit()
            return True

        except Exception:
            db.rollback()
            logger.exception("Failed to delete memory %s", memory_id)
            raise

    def list_memories(
        self,
        db: Session,
        user_id: UUID,
        memory_type: str | None = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Memory]:
        """List memories for a user with optional type filter and pagination."""
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.is_active == is_active,
        )

        if memory_type is not None:
            stmt = stmt.where(Memory.memory_type == memory_type)

        stmt = (
            stmt
            .order_by(Memory.importance.desc(), Memory.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(db.execute(stmt).scalars().all())

    def find_duplicate(
        self,
        db: Session,
        user_id: UUID,
        content: str,
        memory_type: str,
        similarity_threshold: float = 0.90,
    ) -> Memory | None:
        """
        Use vector similarity to find a semantically duplicate memory.
        Returns the closest match above the threshold, or None.
        """
        try:
            query_embedding = embedding_service.generate_embedding(content)
            distance = Memory.embedding.cosine_distance(query_embedding).label("distance")

            stmt = (
                select(Memory, distance)
                .where(
                    Memory.user_id == user_id,
                    Memory.memory_type == memory_type,
                    Memory.is_active.is_(True),
                    Memory.embedding.is_not(None),
                )
                .order_by(distance)
                .limit(1)
            )

            result = db.execute(stmt).first()
            if result is None:
                return None

            memory, cosine_distance = result
            similarity = 1.0 - float(cosine_distance)

            if similarity >= similarity_threshold:
                return memory

            return None

        except Exception:
            logger.exception("find_duplicate failed for user %s", user_id)
            return None

    def merge_memories(
        self,
        db: Session,
        user_id: UUID,
        primary_id: UUID,
        duplicate_id: UUID,
    ) -> Memory:
        """
        Merge duplicate into primary:
        - Deactivates the duplicate
        - Annotates primary's metadata with merge provenance
        """
        primary = self.get_memory(db, user_id, primary_id)
        duplicate = self.get_memory(db, user_id, duplicate_id)

        if primary is None:
            raise ValueError(f"Primary memory {primary_id} not found for user {user_id}")
        if duplicate is None:
            raise ValueError(f"Duplicate memory {duplicate_id} not found for user {user_id}")

        try:
            # Build merged metadata
            existing_meta: dict = primary.memory_metadata or {}
            merged_from: list = existing_meta.get("merged_from", [])
            merged_from.append({
                "memory_id": str(duplicate.id),
                "content": duplicate.content,
                "merged_at": datetime.now(timezone.utc).isoformat(),
            })
            existing_meta["merged_from"] = merged_from
            primary.memory_metadata = existing_meta

            # Keep the higher importance / confidence values
            primary.importance = max(primary.importance, duplicate.importance)
            primary.confidence = max(primary.confidence, duplicate.confidence)
            primary.updated_at = datetime.now(timezone.utc)

            # Soft-delete duplicate
            duplicate.is_active = False
            duplicate.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(primary)
            return primary

        except Exception:
            db.rollback()
            logger.exception("Failed to merge memories %s <- %s", primary_id, duplicate_id)
            raise

    def search_memories(
        self,
        db: Session,
        user_id: UUID,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.20,
    ) -> list[dict]:
        """
        Vector search via memory_retrieval_service with importance-weighted ranking.
        Returns list of dicts sorted by combined score (similarity * importance).
        """
        raw_results = memory_retrieval_service.search_similar_memories(
            db=db,
            user_id=user_id,
            query=query,
            limit=limit * 2,  # over-fetch to allow re-ranking
        )

        # Filter by minimum similarity and apply importance weight
        scored: list[dict] = []
        for item in raw_results:
            similarity = item.get("similarity", 0.0)
            if similarity < min_similarity:
                continue
            importance = item.get("importance", 3)
            # Weighted score: similarity is primary, importance (1-5 -> 0.2-1.0) is secondary
            item["score"] = round(similarity * (0.8 + 0.2 * (importance / 5.0)), 4)
            scored.append(item)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    def update_last_accessed(
        self,
        db: Session,
        memory_id: UUID,
    ) -> None:
        """Stamp last_accessed_at on a memory (best-effort, no user scope needed)."""
        try:
            memory = db.get(Memory, memory_id)
            if memory is not None:
                memory.last_accessed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            db.rollback()
            logger.warning("Could not update last_accessed for memory %s", memory_id)

    def export_memories(
        self,
        db: Session,
        user_id: UUID,
    ) -> list[dict]:
        """Return all active memories for a user as serialisable dicts."""
        memories = self.list_memories(db, user_id, is_active=True, limit=10_000)
        return [
            {
                "id": str(m.id),
                "memory_type": m.memory_type,
                "content": m.content,
                "importance": m.importance,
                "confidence": m.confidence,
                "memory_metadata": m.memory_metadata,
                "created_at": m.created_at.isoformat(),
                "updated_at": m.updated_at.isoformat(),
                "last_accessed_at": (
                    m.last_accessed_at.isoformat() if m.last_accessed_at else None
                ),
            }
            for m in memories
        ]

    def delete_all_user_memories(
        self,
        db: Session,
        user_id: UUID,
    ) -> int:
        """Hard-delete every memory for a user (privacy / account deletion). Returns count."""
        try:
            result = db.execute(
                delete(Memory).where(Memory.user_id == user_id)
            )
            db.commit()
            return result.rowcount

        except Exception:
            db.rollback()
            logger.exception("Failed to delete all memories for user %s", user_id)
            raise


memory_service = MemoryService()
