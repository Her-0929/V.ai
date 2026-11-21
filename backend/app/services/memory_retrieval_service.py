
import re
from datetime import date
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.memory import Memory
from app.services.embedding_service import embedding_service

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_RE_DMY = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})\b", re.IGNORECASE)
_RE_MDY = re.compile(r"\b([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b", re.IGNORECASE)
_RE_ISO = re.compile(r"\b(\d{4})[-/](0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])\b")


def extract_date_from_query(query: str) -> date | None:
    """Extract an explicit date from a search query if present."""
    m = _RE_DMY.search(query)
    if m:
        day, month_name, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        if month_name in _MONTHS:
            try:
                return date(year, _MONTHS[month_name], day)
            except ValueError:
                pass

    m = _RE_MDY.search(query)
    if m:
        month_name, day, year = m.group(1).lower(), int(m.group(2)), int(m.group(3))
        if month_name in _MONTHS:
            try:
                return date(year, _MONTHS[month_name], day)
            except ValueError:
                pass

    m = _RE_ISO.search(query)
    if m:
        year, month, day = map(int, m.groups())
        try:
            return date(year, month, day)
        except ValueError:
            pass

    return None


class MemoryRetrievalService:

    @staticmethod
    def search_similar_memories(
        db: Session,
        user_id: UUID,
        query: str,
        limit: int = 5
    ) -> list[dict]:

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if limit < 1:
            raise ValueError("Limit must be positive.")

        # Generate query embedding on NVIDIA GPU
        query_embedding = embedding_service.generate_embedding(
            query
        )

        # Calculate cosine distance using pgvector
        distance = Memory.embedding.cosine_distance(
            query_embedding
        ).label("distance")

        # Hybrid temporal filtering: check if query specifies an explicit date
        explicit_date = extract_date_from_query(query)
        results = []
        seen_ids = set()

        if explicit_date:
            date_statement = (
                select(Memory, distance)
                .where(
                    Memory.user_id == user_id,
                    Memory.is_active.is_(True),
                    Memory.status == "active",
                    Memory.event_date == explicit_date,
                    Memory.embedding.is_not(None)
                )
                .order_by(distance)
                .limit(limit)
            )
            date_results = db.execute(date_statement).all()
            for mem, dist in date_results:
                results.append((mem, dist))
                seen_ids.add(mem.id)

        # Vector similarity search for remaining slots
        remaining = limit - len(results)
        if remaining > 0:
            conds = [
                Memory.user_id == user_id,
                Memory.is_active.is_(True),
                Memory.status == "active",
                Memory.embedding.is_not(None)
            ]
            if seen_ids:
                conds.append(Memory.id.not_in(seen_ids))

            statement = (
                select(Memory, distance)
                .where(*conds)
                .order_by(distance)
                .limit(remaining)
            )
            results.extend(db.execute(statement).all())

        memories = []

        for memory, cosine_distance in results:

            similarity = 1.0 - float(cosine_distance)

            primary_src_type = "general"
            primary_src_loc = None
            primary_src_filename = None

            if memory.sources:
                first_src = memory.sources[0]
                primary_src_type = first_src.source_type
                primary_src_loc = first_src.source_location
                if first_src.artifact:
                    primary_src_filename = first_src.artifact.filename

            memories.append({
                "id": str(memory.id),
                "content": memory.content,
                "memory_type": memory.memory_type,
                "importance": memory.importance,
                "confidence": memory.confidence,
                "similarity": round(similarity, 4),
                "event_date": memory.event_date.isoformat() if memory.event_date else None,
                "event_date_precision": memory.event_date_precision,
                "status": memory.status,
                "version": memory.version,
                "source_type": primary_src_type,
                "source_location": primary_src_loc,
                "source_filename": primary_src_filename,
            })

        return memories


memory_retrieval_service = MemoryRetrievalService()
