"""Groq LLM provider implementation."""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.services.llm_providers.base import BaseLLMProvider, ProviderHealth


class GroqProvider(BaseLLMProvider):
    provider_name: str = "groq"

    def __init__(self) -> None:
        self._api_key = (settings.GROQ_API_KEY or "").strip()
        self._model = (settings.GROQ_MODEL or "llama-3.1-8b-instant").strip()
        self._base_url = "https://api.groq.com/openai/v1/chat/completions"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_response(self, messages: list[dict]) -> str:
        if not self._api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        # Active, verified models on Groq in priority order (llama3-8b-8192 is decommissioned)
        verified_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        candidate_models = []
        if self._model and self._model not in ["llama3-8b-8192", "llama3-70b-8192"]:
            candidate_models.append(self._model)
        for m in verified_models:
            if m not in candidate_models:
                candidate_models.append(m)

        last_error = None
        for model in candidate_models:
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self._base_url, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content")
                    if content:
                        self._model = model  # cache working model
                        return content.strip()
                
                # If error, record and try next model if decommissioned or not found
                error_body = response.text
                last_error = f"Groq error ({response.status_code}): {error_body}"
                is_model_issue = (
                    response.status_code in (400, 404)
                    or "decommissioned" in error_body
                    or "model_not_found" in error_body
                )
                if not is_model_issue:
                    # Non-model error (e.g. 401 invalid API key) — don't retry other models
                    raise RuntimeError(last_error)

        raise RuntimeError(last_error or "Groq failed to generate response with candidate models.")

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
