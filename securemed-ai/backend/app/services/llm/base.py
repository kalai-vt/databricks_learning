"""Model-agnostic LLM provider interface.

Nothing outside this package should ever import an OpenAI/Anthropic/Gemini
SDK directly. governance_service.py (and everything upstream of it - RBAC,
tenant isolation, PII protection, audit logging) talks only to this
interface, so swapping GPT-4o-mini for Claude, Gemini, or a local model in
the future never touches security or governance code.
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a response for a plain prompt (no extra data context)."""
        raise NotImplementedError

    @abstractmethod
    def generate_with_context(self, prompt: str, context: dict) -> str:
        """Generate a response for a prompt plus a minimized, tenant-scoped
        data context assembled by the governance layer."""
        raise NotImplementedError

    @abstractmethod
    def get_model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_provider_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def is_mock(self) -> bool:
        raise NotImplementedError
