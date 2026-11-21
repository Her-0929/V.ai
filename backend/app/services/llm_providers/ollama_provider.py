"""Ollama LLM provider implementation."""
from __future__ import annotations

import asyncio
import httpx

from app.core.config import settings
from app.services.llm_providers.base import BaseLLMProvider, ProviderHealth


class OllamaProvider(BaseLLMProvider):
    provider_name: str = "ollama"

    def __init__(self) -> None:
        self._base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self._model = settings.OLLAMA_MODEL
        self._timeout = settings.OLLAMA_TIMEOUT_SECONDS

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_response(self, messages: list[dict]) -> str:
        url = f"{self._base_url}/api/chat"
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
            },
        }

        retries = 2
        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    result = response.json()
                    content = result.get("message", {}).get("content")
                    if not content:
                        raise RuntimeError("Ollama returned an empty response.")
                    return content.strip()
            except httpx.TimeoutException as exc:
                if attempt < retries:
                    await asyncio.sleep(0.5)
                    continue
                raise exc

    async def health_check(self) -> ProviderHealth:
        url = f"{self._base_url}/api/tags"
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


ollama_provider = OllamaProvider()
