
import httpx

from app.core.config import settings


class LLMService:

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL

    async def generate_response(
        self,
        messages: list[dict],
    ) -> str:

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }

        async with httpx.AsyncClient(
            timeout=settings.OLLAMA_TIMEOUT_SECONDS
        ) as client:

            response = await client.post(
                url,
                json=payload
            )

            response.raise_for_status()

            result = response.json()

            content = result.get("message", {}).get("content")

            if not content:
                raise RuntimeError(
                    "Ollama returned an empty response."
                )

            return content.strip()


llm_service = LLMService()
