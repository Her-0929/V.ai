"""Google Gemini LLM provider implementation."""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.services.llm_providers.base import BaseLLMProvider, ProviderHealth


class GeminiProvider(BaseLLMProvider):
    provider_name: str = "gemini"

    def __init__(self) -> None:
        self._api_key = settings.GEMINI_API_KEY
        self._model = settings.GEMINI_MODEL

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_response(self, messages: list[dict]) -> str:
        if not self._api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._api_key}"
        )

        system_parts = []
        contents = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_parts.append(content)
            else:
                gemini_role = "model" if role == "assistant" else "user"
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": content}],
                })

        payload: dict = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
            },
        }

        if system_parts:
            payload["systemInstruction"] = {
                "parts": [{"text": "\n\n".join(system_parts)}],
            }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            candidates = result.get("candidates", [])
            if not candidates:
                raise RuntimeError("Gemini returned no candidates.")

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise RuntimeError("Gemini returned empty parts.")

            text = parts[0].get("text", "")
            if not text:
                raise RuntimeError("Gemini returned an empty response.")

            return text.strip()

    async def health_check(self) -> ProviderHealth:
        if not self._api_key:
            return ProviderHealth(
                is_healthy=False,
                provider_name=self.provider_name,
                model=self.model_name,
                error="GEMINI_API_KEY not configured",
            )

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}?key={self._api_key}"
        )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return ProviderHealth(
                    is_healthy=True,
                    provider_name=self.provider_name,
                    model=self.model_name,
                )
        except Exception as exc:
            return ProviderHealth(
                is_healthy=False,
                provider_name=self.provider_name,
                model=self.model_name,
                error=str(exc),
            )


gemini_provider = GeminiProvider()
