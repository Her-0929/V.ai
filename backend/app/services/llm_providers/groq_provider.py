"""Groq LLM provider implementation."""
from __future__ import annotations

import httpx

import logging
import httpx

from app.core.config import settings
from app.services.llm_providers.base import BaseLLMProvider, ProviderHealth

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    provider_name: str = "groq"

    def __init__(self) -> None:
        self._api_key = (settings.GROQ_API_KEY or "").strip().strip("'\"")
        self._model = (settings.GROQ_MODEL or "llama-3.1-8b-instant").strip().strip("'\"")
        self._base_url = "https://api.groq.com/openai/v1/chat/completions"
        self._models_url = "https://api.groq.com/openai/v1/models"

    @property
    def model_name(self) -> str:
        return self._model

    async def _discover_available_models(self, client: httpx.AsyncClient) -> list[str]:
        """Fetch the live list of models currently supported by Groq for this API key."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }
        try:
            resp = await client.get(self._models_url, headers=headers)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                model_ids = [
                    m.get("id") for m in data
                    if m.get("id") and not m.get("id", "").startswith("whisper")
                ]
                logger.info("Discovered live Groq models: %s", model_ids)
                return model_ids
            else:
                logger.warning("Groq /models returned %d: %s", resp.status_code, resp.text)
        except Exception as exc:
            logger.warning("Failed to query Groq /models: %s", exc)
        return []

    async def generate_response(self, messages: list[dict]) -> str:
        if not self._api_key:
            raise RuntimeError("GROQ_API_KEY is not configured in environment.")

        clean_key = self._api_key.strip().strip("'\"")
        headers = {
            "Authorization": f"Bearer {clean_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Dynamically query available models from Groq
            live_models = await self._discover_available_models(client)

            # Build candidate list: user model first if valid, then live models, then fallbacks
            candidate_models = []
            if self._model and (not live_models or self._model in live_models):
                candidate_models.append(self._model)
            for m in live_models:
                if m not in candidate_models:
                    candidate_models.append(m)
            for fallback in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "gemma2-9b-it"]:
                if fallback not in candidate_models:
                    candidate_models.append(fallback)

            last_error = None
            for model in candidate_models:
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                }

                response = await client.post(self._base_url, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content")
                    if content:
                        self._model = model  # remember working model
                        return content.strip()

                error_body = response.text
                last_error = f"Groq error ({response.status_code}) on model '{model}': {error_body}"
                logger.warning(last_error)

                # If non-model error (e.g. invalid API key 401), stop immediately
                if response.status_code in (401, 403):
                    raise RuntimeError(f"Groq Authentication Error ({response.status_code}): Invalid GROQ_API_KEY. Please verify your key on console.groq.com.")

            raise RuntimeError(last_error or "Groq failed to generate a response.")

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
