"""Groq LLM provider implementation."""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.services.llm_providers.base import BaseLLMProvider, ProviderHealth


class GroqProvider(BaseLLMProvider):
    provider_name: str = "groq"

    def __init__(self) -> None:
        self._api_key = settings.GROQ_API_KEY
        self._model = settings.GROQ_MODEL
        self._base_url = "https://api.groq.com/openai/v1/chat/completions"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_response(self, messages: list[dict]) -> str:
        if not self._api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.7,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self._base_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content")
            if not content:
                raise RuntimeError("Groq returned an empty response.")
            return content.strip()

    async def health_check(self) -> ProviderHealth:
        if not self._api_key:
            return ProviderHealth(
                is_healthy=False,
                provider_name=self.provider_name,
                model=self.model_name,
                error="GROQ_API_KEY not configured",
            )

        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.groq.com/openai/v1/models", headers=headers)
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


groq_provider = GroqProvider()
