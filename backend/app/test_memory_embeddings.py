
from app.core.database import SessionLocal
from app.models.memory import Memory
from app.services.memory_embedding_service import (
    MemoryEmbeddingService
)

from sqlalchemy import select, func


def test_memory_embeddings():

    db = SessionLocal()

    try:
        # Generate embeddings for existing memories
        processed = (
            MemoryEmbeddingService.generate_missing_embeddings(
                db,
                batch_size=16
            )
        )

        print("\n========== HER MEMORY EMBEDDING TEST ==========")

        print("New embeddings generated:", processed)

        # Count memories with embeddings
        embedded_count = db.scalar(
            select(func.count())
            .select_from(Memory)
            .where(Memory.embedding.is_not(None))
        )

        total_count = db.scalar(
            select(func.count()).select_from(Memory)
        )

        print("Total memories:", total_count)
        print("Memories with embeddings:", embedded_count)

        # Inspect one embedded memory
        memory = db.execute(
            select(Memory)
            .where(Memory.embedding.is_not(None))
            .limit(1)
        ).scalar_one_or_none()

        if memory:
            print("Memory content:", memory.content)
            print("Embedding dimensions:", len(memory.embedding))

            assert len(memory.embedding) == 384

        print("\nHER POSTGRESQL MEMORY EMBEDDINGS SUCCESSFUL!")

    finally:
        db.close()


if __name__ == "__main__":
    test_memory_embeddings()
