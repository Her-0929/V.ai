"""OpenRouter LLM provider implementation."""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.services.llm_providers.base import BaseLLMProvider, ProviderHealth


class OpenRouterProvider(BaseLLMProvider):
    provider_name: str = "openrouter"

    def __init__(self) -> None:
        self._api_key = settings.OPENROUTER_API_KEY
        self._model = settings.OPENROUTER_MODEL
        self._base_url = "https://openrouter.ai/api/v1/chat/completions"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_response(self, messages: list[dict]) -> str:
        if not self._api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": "https://her.ai",
            "X-Title": "HER AI",
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
                raise RuntimeError("OpenRouter returned an empty response.")
            return content.strip()

    async def health_check(self) -> ProviderHealth:
        if not self._api_key:
            return ProviderHealth(
                is_healthy=False,
                provider_name=self.provider_name,
                model=self.model_name,
                error="OPENROUTER_API_KEY not configured",
            )

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": "https://her.ai",
            "X-Title": "HER AI",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://openrouter.ai/api/v1/auth/key", headers=headers)
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


openrouter_provider = OpenRouterProvider()
