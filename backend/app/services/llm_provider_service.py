"""Unified LLM provider service. Use this instead of llm_service.py for new code."""
from __future__ import annotations

import asyncio

from app.core.config import settings
from app.services.llm_providers.base import BaseLLMProvider, ProviderHealth
from app.services.llm_providers.ollama_provider import OllamaProvider
from app.services.llm_providers.groq_provider import GroqProvider
from app.services.llm_providers.gemini_provider import GeminiProvider
from app.services.llm_providers.openrouter_provider import OpenRouterProvider


class LLMProviderService:
    def __init__(self) -> None:
        self._providers: dict[str, BaseLLMProvider] = {}
        self._active_provider_name: str = settings.LLM_PROVIDER
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        # Always register Ollama
        self._providers["ollama"] = OllamaProvider()
        # Register cloud providers only if keys are configured
        if settings.GROQ_API_KEY:
            self._providers["groq"] = GroqProvider()
        if settings.GEMINI_API_KEY:
            self._providers["gemini"] = GeminiProvider()
        if settings.OPENROUTER_API_KEY:
            self._providers["openrouter"] = OpenRouterProvider()
        # Fallback to ollama if requested provider not registered
        if self._active_provider_name not in self._providers:
            self._active_provider_name = "ollama"

    @property
    def active_provider(self) -> BaseLLMProvider:
        return self._providers[self._active_provider_name]

    @property
    def active_provider_name(self) -> str:
        return self._active_provider_name

    def set_provider(self, provider_name: str) -> None:
        if provider_name not in self._providers:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {list(self._providers.keys())}")
        self._active_provider_name = provider_name

    def available_providers(self) -> list[str]:
        return list(self._providers.keys())

    async def generate_response(self, messages: list[dict]) -> str:
        try:
            return await self.active_provider.generate_response(messages)
        except Exception as primary_error:
            # Fallback to Ollama if enabled and not already using it
            if settings.LLM_ENABLE_FALLBACK and self._active_provider_name != "ollama":
                try:
                    return await self._providers["ollama"].generate_response(messages)
                except Exception:
                    pass
            raise primary_error

    async def health_check_all(self) -> dict[str, ProviderHealth]:
        tasks = {name: provider.health_check() for name, provider in self._providers.items()}
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        return {
            name: (result if isinstance(result, ProviderHealth) else ProviderHealth(is_healthy=False, provider_name=name, model="unknown", error=str(result)))
            for name, result in zip(tasks.keys(), results)
        }


llm_provider_service = LLMProviderService()
