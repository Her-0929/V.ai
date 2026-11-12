
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.memory import Memory
from app.services.memory_retrieval_service import (
    memory_retrieval_service
)


def test_memory_retrieval():

    db = SessionLocal()

    try:
        # Get an existing user who has embedded memories
        memory = db.execute(
            select(Memory)
            .where(
                Memory.embedding.is_not(None),
                Memory.is_active.is_(True)
            )
            .limit(1)
        ).scalar_one_or_none()

        if memory is None:
            raise RuntimeError("No embedded memories found.")

        user_id = memory.user_id

        # Search using different wording
        query = "What career does the user want to pursue?"

        results = (
            memory_retrieval_service.search_similar_memories(
                db=db,
                user_id=user_id,
                query=query,
                limit=5
            )
        )

        print("\n========== HER SEMANTIC SEARCH TEST ==========")
        print("Query:", query)

        for index, result in enumerate(results, start=1):
            print(f"\nResult {index}")
            print("Memory:", result["content"])
            print("Type:", result["memory_type"])
            print("Similarity:", result["similarity"])

        assert results, "No relevant memories retrieved."

        print("\nHER SEMANTIC RETRIEVAL SUCCESSFUL!")

    finally:
        db.close()


if __name__ == "__main__":
    test_memory_retrieval()
