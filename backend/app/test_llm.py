
import asyncio

from app.services.llm_service import llm_service


async def test_llm():

    messages = [
        {
            "role": "system",
            "content": (
                "You are HER, a helpful personal AI companion. "
                "Respond naturally and clearly."
            )
        },
        {
            "role": "user",
            "content": "Hello HER! Introduce yourself."
        }
    ]

    print("\n========== HER LLM TEST ==========")

    response = await llm_service.generate_response(
        messages
    )

    print("Model:", llm_service.model)
    print("\nHER:", response)

    print("\nHER LOCAL LLM CONNECTION SUCCESSFUL!")


if __name__ == "__main__":
    asyncio.run(test_llm())
