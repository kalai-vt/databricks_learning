"""Provider factory - the single place LLM_PROVIDER is interpreted.

Only 'openai' is implemented today. Adding 'anthropic' / 'gemini' / 'local'
later means adding a new module + one branch here; nothing in governance,
RBAC, tenant isolation, PII protection, or audit logging changes.
"""
from app.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.openai_provider import OpenAIProvider

_provider_instance: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    provider_name = settings.llm_provider.lower()
    if provider_name == "openai":
        _provider_instance = OpenAIProvider()
    else:
        # Future providers (anthropic, gemini, local) plug in here.
        raise ValueError(f"Unsupported LLM_PROVIDER '{provider_name}'. Only 'openai' is implemented.")

    return _provider_instance
