
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.memory import Memory
from app.services.embedding_service import embedding_service


class MemoryEmbeddingService:

    @staticmethod
    def generate_and_store(
        db: Session,
        memory: Memory
    ) -> Memory:

        if not memory.content or not memory.content.strip():
            raise ValueError("Memory content cannot be empty.")

        embedding = embedding_service.generate_embedding(
            memory.content
        )

        memory.embedding = embedding

        try:
            db.commit()
            db.refresh(memory)
        except Exception:
            db.rollback()
            raise

        return memory

    @staticmethod
    def generate_missing_embeddings(
        db: Session,
        batch_size: int = 16
    ) -> int:

        if batch_size < 1:
            raise ValueError("Batch size must be positive.")

        memories = db.execute(
            select(Memory)
            .where(Memory.embedding.is_(None))
            .order_by(Memory.created_at)
            .limit(batch_size)
        ).scalars().all()

        if not memories:
            return 0

        try:
            for memory in memories:
                memory.embedding = (
                    embedding_service.generate_embedding(
                        memory.content
                    )
                )

            db.commit()

        except Exception:
            db.rollback()
            raise

        return len(memories)
