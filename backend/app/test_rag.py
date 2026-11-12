
import asyncio
from uuid import UUID

from app.core.database import SessionLocal
from app.services.rag_service import rag_service


async def test_rag():

    user_id = UUID(
        "35d636d9-fa44-4e92-9ecd-2e39a9194559"
    )

    db = SessionLocal()

    try:
        result = await rag_service.generate_response(
            db=db,
            user_id=user_id,
            user_message="What career do I want to pursue?"
        )

        print("\n========== HER RAG TEST ==========")

        print("\nUser question:")
        print("What career do I want to pursue?")

        print("\nRetrieved memories:")
        for memory in result["retrieved_memories"]:
            print("-", memory["content"])
            print("  Similarity:", memory["similarity"])

        print("\nHER response:")
        print(result["response"])

        print("\nMemory count:", result["memory_count"])
        print("Model:", result["model"])

        print("\nHER RAG PIPELINE SUCCESSFUL!")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_rag())
