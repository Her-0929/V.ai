"""Unified LLM Service wrapper delegating to llm_provider_service."""
from app.services.llm_provider_service import llm_provider_service


class LLMService:
    @property
    def model(self) -> str:
        return getattr(llm_provider_service.active_provider, "model", "default")

    async def generate_response(self, messages: list[dict]) -> str:
        return await llm_provider_service.generate_response(messages)


llm_service = LLMService()
