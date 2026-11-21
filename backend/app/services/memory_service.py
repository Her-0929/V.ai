import logging
from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select, delete, desc, asc, nullslast, and_, or_, func
from sqlalchemy.orm import Session

from app.core.temporal import normalize_event_date, TemporalPrecision
from app.models.memory import Memory
from app.models.memory_source import MemorySource
from app.models.memory_artifact import MemoryArtifact
from app.services.embedding_service import embedding_service
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
        event_date: date | None = None,
        event_date_precision: str = "unknown",
        source_created_at: datetime | None = None,
        access_scope: str = "default",
        artifact_id: UUID | None = None,
        source_type: str | None = None,
        source_location: str | None = None,
        source_metadata: dict | None = None,
    ) -> Memory:
        """Create a memory with embedding and optional source tracking."""
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Memory content cannot be empty.")

        if memory_type not in VALID_MEMORY_TYPES:
            raise ValueError(f"Invalid memory_type '{memory_type}'. Must be one of {VALID_MEMORY_TYPES}")

        if not (1 <= importance <= 5):
            raise ValueError("Importance must be between 1 and 5.")

        if not (0.0 <= confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0.")

        try:
            embedding = embedding_service.generate_embedding(content.strip())

            memory = Memory(
                user_id=user_id,
                memory_type=memory_type,
                content=content.strip(),
                importance=importance,
                confidence=confidence,
                event_date=event_date,
                event_date_precision=event_date_precision,
                source_created_at=source_created_at,
                status="active",
                access_scope=access_scope,
                version=1,
                is_active=True,
                memory_metadata=metadata,
                embedding=embedding,
            )
            db.add(memory)
            db.flush()

            has_source = (
                source_message_id is not None
                or source_excerpt is not None
                or artifact_id is not None
                or source_type is not None
            )

            if has_source:
                resolved_source_type = source_type or (
                    "message" if source_message_id is not None else "manual"
                )
                source = MemorySource(
                    memory_id=memory.id,
                    message_id=source_message_id,
                    artifact_id=artifact_id,
                    source_type=resolved_source_type,
                    source_location=source_location,
                    excerpt=source_excerpt,
                    source_metadata=source_metadata,
                )
                db.add(source)

            db.commit()
            db.refresh(memory)
            return memory

        except Exception:
            db.rollback()
            logger.exception("Failed to create memory for user %s", user_id)
            raise

    def get_memory(self, db: Session, user_id: UUID, memory_id: UUID) -> Memory | None:
        """Get a specific memory, scoped to user."""
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
        """Update memory fields. Regenerate embedding if content changes."""
        memory = self.get_memory(db, user_id, memory_id)
        if memory is None:
            return None

        if importance is not None and not (1 <= importance <= 5):
            raise ValueError("Importance must be between 1 and 5.")

        if confidence is not None and not (0.0 <= confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0.")

        try:
            if content is not None:
                cleaned_content = content.strip()
                if not cleaned_content:
                    raise ValueError("Memory content cannot be empty.")
                if cleaned_content != memory.content:
                    memory.content = cleaned_content
                    memory.embedding = embedding_service.generate_embedding(cleaned_content)

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

    def deactivate_memory(self, db: Session, user_id: UUID, memory_id: UUID) -> bool:
        """Soft-delete: set is_active=False."""
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

    def delete_memory(self, db: Session, user_id: UUID, memory_id: UUID) -> bool:
        """Hard delete, user-scoped."""
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
        """List user memories with optional type filter."""
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
        """Find semantically duplicate memory using vector search."""
        try:
            candidates = memory_retrieval_service.search_similar_memories(
                db=db,
                user_id=user_id,
                query=content,
                limit=3,
            )
            for candidate in candidates:
                if (
                    candidate.get("memory_type") == memory_type
                    and candidate.get("similarity", 0.0) >= similarity_threshold
                ):
                    candidate_id = candidate.get("id")
                    if candidate_id:
                        memory_obj = self.get_memory(db, user_id, UUID(candidate_id))
                        if memory_obj is not None:
                            return memory_obj
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
        """Deactivate duplicate, keep primary. Update primary metadata with merge info."""
        primary = self.get_memory(db, user_id, primary_id)
        duplicate = self.get_memory(db, user_id, duplicate_id)

        if primary is None:
            raise ValueError(f"Primary memory {primary_id} not found for user {user_id}")
        if duplicate is None:
            raise ValueError(f"Duplicate memory {duplicate_id} not found for user {user_id}")

        try:
            existing_meta: dict = primary.memory_metadata or {}
            merged_from: list = existing_meta.get("merged_from", [])
            merged_from.append({
                "memory_id": str(duplicate.id),
                "content": duplicate.content,
                "merged_at": datetime.now(timezone.utc).isoformat(),
            })
            existing_meta["merged_from"] = merged_from
            primary.memory_metadata = existing_meta

            primary.importance = max(primary.importance, duplicate.importance)
            primary.confidence = max(primary.confidence, duplicate.confidence)
            primary.updated_at = datetime.now(timezone.utc)

            duplicate.is_active = False
            duplicate.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(primary)
            return primary

        except Exception:
            db.rollback()
            logger.exception("Failed to merge memories %s <- %s", primary_id, duplicate_id)
            raise

    def supersede_memory(
        self,
        db: Session,
        user_id: UUID,
        old_memory_id: UUID,
        new_memory_id: UUID,
        reason: str | None = None,
    ) -> Memory:
        """
        Supersede an existing memory with a new/corrected memory.
        Enforces:
          - Both memories must exist and belong to user_id.
          - Cannot supersede self (old_memory_id != new_memory_id).
          - Supersession relationship cannot form cycles.
          - Old memory is marked status='superseded' and is_active=False.
          - New memory version is incremented.
        """
        if old_memory_id == new_memory_id:
            raise ValueError("A memory cannot supersede itself.")

        old_memory = self.get_memory(db, user_id, old_memory_id)
        if old_memory is None:
            raise ValueError(f"Old memory {old_memory_id} not found for user.")

        new_memory = self.get_memory(db, user_id, new_memory_id)
        if new_memory is None:
            raise ValueError(f"New memory {new_memory_id} not found for user.")

        # Cycle check: traverse supersession chain starting from new_memory
        curr = new_memory
        visited = {old_memory.id, new_memory.id}
        while curr.superseded_by_id is not None:
            if curr.superseded_by_id == old_memory.id:
                raise ValueError("Supersession cycle detected: cannot form circular supersession chain.")
            if curr.superseded_by_id in visited:
                break
            visited.add(curr.superseded_by_id)
            curr = self.get_memory(db, user_id, curr.superseded_by_id)
            if curr is None:
                break

        try:
            old_memory.status = "superseded"
            old_memory.superseded_by_id = new_memory.id
            old_memory.is_active = False
            old_memory.updated_at = datetime.now(timezone.utc)

            # Store correction metadata in old and new memories
            old_meta = dict(old_memory.memory_metadata or {})
            old_meta["superseded_at"] = datetime.now(timezone.utc).isoformat()
            if reason:
                old_meta["superseded_reason"] = reason
            old_memory.memory_metadata = old_meta

            new_meta = dict(new_memory.memory_metadata or {})
            new_meta["supersedes_memory_id"] = str(old_memory.id)
            if reason:
                new_meta["correction_reason"] = reason
            new_memory.memory_metadata = new_meta

            new_memory.version = max(new_memory.version, old_memory.version + 1)
            new_memory.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(old_memory)
            db.refresh(new_memory)
            return old_memory
        except Exception:
            db.rollback()
            logger.exception("Failed to supersede memory %s with %s", old_memory_id, new_memory_id)
            raise

    def search_memories(
        self,
        db: Session,
        user_id: UUID,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.20,
    ) -> list[dict]:
        """Search memories using semantic similarity."""
        raw_results = memory_retrieval_service.search_similar_memories(
            db=db,
            user_id=user_id,
            query=query,
            limit=limit * 2,
        )

        scored: list[dict] = []
        for item in raw_results:
            similarity = item.get("similarity", 0.0)
            if similarity < min_similarity:
                continue
            importance = item.get("importance", 3)
            item["score"] = round(similarity * (0.8 + 0.2 * (importance / 5.0)), 4)
            scored.append(item)

        scored.sort(key=lambda x: x.get("score", x.get("similarity", 0.0)), reverse=True)
        return scored[:limit]

    def update_last_accessed(self, db: Session, memory_id: UUID) -> None:
        """Update last_accessed_at timestamp."""
        try:
            memory = db.get(Memory, memory_id)
            if memory is not None:
                memory.last_accessed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            db.rollback()
            logger.warning("Could not update last_accessed for memory %s", memory_id)

    def export_memories(self, db: Session, user_id: UUID) -> list[dict]:
        """Export all active memories as dicts for data export/privacy."""
        memories = self.list_memories(db, user_id, is_active=True, limit=10_000)
        return [
            {
                "id": str(m.id),
                "memory_type": m.memory_type,
                "content": m.content,
                "importance": m.importance,
                "confidence": m.confidence,
                "memory_metadata": m.memory_metadata,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "updated_at": m.updated_at.isoformat() if m.updated_at else None,
                "last_accessed_at": (
                    m.last_accessed_at.isoformat() if m.last_accessed_at else None
                ),
            }
            for m in memories
        ]

    def delete_all_user_memories(self, db: Session, user_id: UUID) -> int:
        """Delete ALL memories for a user. Returns count. For account deletion."""
        try:
            result = db.execute(
                delete(Memory).where(Memory.user_id == user_id)
            )
            db.commit()
            return result.rowcount or 0

        except Exception:
            db.rollback()
            logger.exception("Failed to delete all memories for user %s", user_id)
            raise


    def correct_memory(
        self,
        db: Session,
        user_id: UUID,
        memory_id: UUID,
        content: str,
        reason: str,
        memory_type: str | None = None,
        importance: int | None = None,
        confidence: float | None = None,
        event_date: str | None = None,
        event_date_precision: str | None = None,
    ) -> tuple[Memory, Memory]:
        """
        Concurrency-safe, transaction-atomic user memory correction.
        1. Precomputes embedding outside row lock.
        2. Acquires row lock via with_for_update() on target memory.
        3. Creates new Memory (version = old.version + 1, status='active', is_active=True).
        4. Copies prior artifact sources and attaches manual correction source.
        5. Marks old memory status='superseded', is_active=False, superseded_by_id=new.id.
        6. Preserves separate audit metadata.
        Returns: (old_memory, new_memory)
        """
        if not content or not content.strip():
            raise ValueError("Corrected memory content cannot be empty.")
        if not reason or not reason.strip():
            raise ValueError("Correction reason must be provided.")

        cleaned_content = content.strip()

        # Generate embedding safely prior to acquiring DB lock
        new_embedding = embedding_service.generate_embedding(cleaned_content)

        try:
            # 1. Acquire row lock on target memory
            stmt = (
                select(Memory)
                .where(Memory.id == memory_id, Memory.user_id == user_id)
                .with_for_update()
            )
            old_memory = db.execute(stmt).scalar_one_or_none()

            if old_memory is None:
                raise ValueError(f"Memory {memory_id} not found for authenticated user.")

            if not old_memory.is_active or old_memory.status == "superseded":
                raise ValueError(f"Cannot correct memory {memory_id}: it has already been superseded or deactivated.")

            resolved_memory_type = memory_type or old_memory.memory_type
            if resolved_memory_type not in VALID_MEMORY_TYPES:
                raise ValueError(f"Invalid memory_type '{resolved_memory_type}'.")

            resolved_importance = importance if importance is not None else old_memory.importance
            if not (1 <= resolved_importance <= 5):
                raise ValueError("Importance must be between 1 and 5.")

            resolved_confidence = confidence if confidence is not None else 1.0
            if not (0.0 <= resolved_confidence <= 1.0):
                raise ValueError("Confidence must be between 0.0 and 1.0.")

            # Date normalization
            if event_date is not None:
                resolved_date, resolved_prec = normalize_event_date(
                    event_date,
                    explicit_precision=event_date_precision,
                )
            else:
                resolved_date = old_memory.event_date
                resolved_prec = old_memory.event_date_precision

            # 2. Instantiate new memory
            new_memory = Memory(
                user_id=user_id,
                memory_type=resolved_memory_type,
                content=cleaned_content,
                importance=resolved_importance,
                confidence=resolved_confidence,
                event_date=resolved_date,
                event_date_precision=resolved_prec,
                source_created_at=old_memory.source_created_at,
                status="active",
                access_scope=old_memory.access_scope,
                version=old_memory.version + 1,
                is_active=True,
                memory_metadata={
                    "correction_reason": reason.strip(),
                    "supersedes_memory_id": str(old_memory.id),
                    "corrected_at": datetime.now(timezone.utc).isoformat(),
                },
                embedding=new_embedding,
            )
            db.add(new_memory)
            db.flush()

            # 3. Attach correction provenance & copy over artifact associations
            correction_source = MemorySource(
                memory_id=new_memory.id,
                source_type="manual",
                source_location="User Correction",
                excerpt=f"User correction: {reason.strip()}",
                source_metadata={"correction_reason": reason.strip(), "prior_memory_id": str(old_memory.id)},
            )
            db.add(correction_source)

            # Copy prior artifact sources to maintain provenance chain
            for src in old_memory.sources:
                if src.artifact_id is not None:
                    linked_source = MemorySource(
                        memory_id=new_memory.id,
                        artifact_id=src.artifact_id,
                        source_type=src.source_type,
                        source_location=src.source_location,
                        excerpt=src.excerpt,
                        source_metadata=src.source_metadata,
                    )
                    db.add(linked_source)

            # 4. Mark old memory as superseded
            old_memory.status = "superseded"
            old_memory.is_active = False
            old_memory.superseded_by_id = new_memory.id
            old_meta = dict(old_memory.memory_metadata or {})
            old_meta["superseded_at"] = datetime.now(timezone.utc).isoformat()
            old_meta["superseded_reason"] = reason.strip()
            old_meta["superseded_by_memory_id"] = str(new_memory.id)
            old_memory.memory_metadata = old_meta
            old_memory.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(old_memory)
            db.refresh(new_memory)
            return old_memory, new_memory

        except Exception:
            db.rollback()
            logger.exception("Failed to execute atomic correction on memory %s", memory_id)
            raise

    def get_memory_provenance(self, db: Session, user_id: UUID, memory_id: UUID) -> dict | None:
        """Retrieve complete provenance audit trail for a memory."""
        memory = self.get_memory(db, user_id, memory_id)
        if not memory:
            return None

        # Resolve sources with artifact details
        sources_data = []
        for src in memory.sources:
            art_info = None
            if src.artifact and src.artifact.user_id == user_id:
                art_info = {
                    "artifact_id": src.artifact.id,
                    "filename": src.artifact.filename,
                    "artifact_type": src.artifact.artifact_type,
                    "checksum_sha256": src.artifact.checksum_sha256,
                }
            sources_data.append({
                "source_id": src.id,
                "source_type": src.source_type,
                "source_location": src.source_location,
                "excerpt": src.excerpt,
                "created_at": src.created_at,
                "artifact": art_info,
            })

        # Resolve history chain
        history_entries = []
        # Find all memories in this lineage (ancestors and successors)
        curr_id = memory.id
        visited = set()
        
        # Traverse downwards if superseded
        target = memory
        while target and target.id not in visited:
            visited.add(target.id)
            meta = target.memory_metadata or {}
            history_entries.append({
                "memory_id": target.id,
                "version": target.version,
                "status": target.status,
                "is_active": target.is_active,
                "created_at": target.created_at,
                "superseded_at": meta.get("superseded_at"),
                "superseded_reason": meta.get("superseded_reason"),
            })
            if target.superseded_by_id:
                target = self.get_memory(db, user_id, target.superseded_by_id)
            else:
                break

        # Also find any earlier versions that were superseded by this memory
        earlier_stmt = (
            select(Memory)
            .where(Memory.superseded_by_id == memory.id, Memory.user_id == user_id)
        )
        earlier_memories = db.scalars(earlier_stmt).all()
        for e in earlier_memories:
            if e.id not in visited:
                visited.add(e.id)
                meta = e.memory_metadata or {}
                history_entries.insert(0, {
                    "memory_id": e.id,
                    "version": e.version,
                    "status": e.status,
                    "is_active": e.is_active,
                    "created_at": e.created_at,
                    "superseded_at": meta.get("superseded_at"),
                    "superseded_reason": meta.get("superseded_reason"),
                })

        history_entries.sort(key=lambda h: h["version"])

        return {
            "memory_id": memory.id,
            "content": memory.content,
            "memory_type": memory.memory_type,
            "importance": memory.importance,
            "confidence": memory.confidence,
            "event_date": memory.event_date,
            "event_date_precision": memory.event_date_precision,
            "version": memory.version,
            "status": memory.status,
            "superseded_by_id": memory.superseded_by_id,
            "sources": sources_data,
            "history": history_entries,
        }

    @staticmethod
    def format_precision_date(event_date: date | None, precision: str) -> str:
        """Format date accurately according to precision without fabricating detail."""
        if not event_date:
            return "Date unknown"
        p = (precision or "unknown").lower()
        if p == "day":
            return f"{event_date.strftime('%B %d, %Y')} (exact day)"
        if p == "month":
            return f"{event_date.strftime('%B %Y')} (month)"
        if p == "year":
            return f"{event_date.year} (year)"
        if p == "decade":
            return f"{event_date.year}s (decade)"
        return f"{event_date.isoformat()} (unknown precision)"

    def get_memory_timeline(
        self,
        db: Session,
        user_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        precision: str | None = None,
        include_unknown_dates: bool = True,
        include_superseded: bool = False,
        order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """Query user memories chronologically with precision handling."""
        conditions = [Memory.user_id == user_id]

        if not include_superseded:
            conditions.append(and_(Memory.status == "active", Memory.is_active.is_(True)))

        if start_date is not None:
            conditions.append(Memory.event_date >= start_date)

        if end_date is not None:
            conditions.append(Memory.event_date <= end_date)

        if precision is not None:
            conditions.append(Memory.event_date_precision == precision.lower())

        if not include_unknown_dates:
            conditions.append(Memory.event_date.is_not(None))

        # Count total
        count_stmt = select(func.count()).select_from(Memory).where(*conditions)
        total = db.scalar(count_stmt) or 0

        # Query items
        stmt = select(Memory).where(*conditions)
        if order.lower() == "asc":
            stmt = stmt.order_by(nullslast(asc(Memory.event_date)), asc(Memory.created_at))
        else:
            stmt = stmt.order_by(nullslast(desc(Memory.event_date)), desc(Memory.created_at))

        stmt = stmt.limit(limit).offset(offset)
        memories = db.scalars(stmt).all()

        items = []
        for m in memories:
            primary_src_type = "general"
            primary_src_loc = None
            if m.sources:
                first_src = m.sources[0]
                primary_src_type = first_src.source_type
                primary_src_loc = first_src.source_location

            formatted_date_str = self.format_precision_date(m.event_date, m.event_date_precision)

            items.append({
                "id": m.id,
                "content": m.content,
                "memory_type": m.memory_type,
                "importance": m.importance,
                "confidence": m.confidence,
                "event_date": m.event_date,
                "event_date_precision": m.event_date_precision,
                "formatted_date": formatted_date_str,
                "source_created_at": m.source_created_at,
                "status": m.status,
                "version": m.version,
                "primary_source_type": primary_src_type,
                "primary_source_location": primary_src_loc,
            })

        return items, total


memory_service = MemoryService()
