"""Base interface for all LLM providers."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderHealth:
    is_healthy: bool
    provider_name: str
    model: str
    error: str | None = None


class BaseLLMProvider(ABC):
    provider_name: str = "base"

    @abstractmethod
    async def generate_response(self, messages: list[dict]) -> str:
        """Generate a response. messages is list of {role: str, content: str}."""

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Check if provider is reachable."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return current model identifier."""
