
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.memory import Memory
from app.services.embedding_service import embedding_service


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

        statement = (
            select(Memory, distance)
            .where(
                Memory.user_id == user_id,
                Memory.is_active.is_(True),
                Memory.embedding.is_not(None)
            )
            .order_by(distance)
            .limit(limit)
        )

        results = db.execute(statement).all()

        memories = []

        for memory, cosine_distance in results:

            similarity = 1.0 - float(cosine_distance)

            memories.append({
                "id": str(memory.id),
                "content": memory.content,
                "memory_type": memory.memory_type,
                "importance": memory.importance,
                "confidence": memory.confidence,
                "similarity": round(similarity, 4)
            })

        return memories


memory_retrieval_service = MemoryRetrievalService()
