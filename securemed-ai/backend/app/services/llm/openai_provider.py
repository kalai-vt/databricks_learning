"""OpenAI implementation of LLMProvider, using GPT-4o-mini by default.

The model name is never hard-coded here - it is read from configuration
(OPENAI_MODEL) so the model can be changed without touching this file.

If no API key is configured, or MOCK_LLM=true, this provider runs in
deterministic Mock/Demo mode: it never calls the network and always
returns a stable, presentation-safe answer built from the tenant-scoped
context the governance layer already assembled. This guarantees a live
demo works even with no internet access, no API key, or a quota outage.
"""
import logging

from app.config import settings
from app.services.llm.base import LLMProvider

logger = logging.getLogger("securemed.llm")

SYSTEM_PROMPT = (
    "You are the SecureMed AI Healthcare Assistant, a demonstration assistant for a "
    "multi-tenant hospital SaaS platform. You ONLY answer using the synthetic, tenant-scoped "
    "data context provided to you. You must never invent patient data, never discuss data from "
    "any hospital other than the one in the provided context, and never provide real medical "
    "diagnosis or treatment advice. This is a synthetic data demo environment, not a medical "
    "device."
)


class OpenAIProvider(LLMProvider):
    def __init__(self):
        self._model = settings.openai_model
        self._mock = settings.effective_mock_mode
        self._client = None
        if not self._mock:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=settings.openai_api_key)
            except Exception as exc:  # pragma: no cover - defensive, never leaks details to user
                logger.warning("Falling back to mock mode: could not initialize OpenAI client (%s)", type(exc).__name__)
                self._mock = True

    def get_model_name(self) -> str:
        return self._model

    def get_provider_name(self) -> str:
        return "OpenAI"

    def is_mock(self) -> bool:
        return self._mock

    def generate_response(self, prompt: str) -> str:
        return self.generate_with_context(prompt, context={})

    def generate_with_context(self, prompt: str, context: dict) -> str:
        if self._mock:
            return self._mock_response(prompt, context)

        try:
            context_text = self._format_context(context)
            completion = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "system", "content": f"Authorized tenant-scoped data context:\n{context_text}"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=400,
                temperature=0.3,
                timeout=20,
            )
            return completion.choices[0].message.content or ""
        except Exception:
            # Never leak provider errors, stack traces, or key details to the user.
            logger.exception("LLM call failed")
            return (
                "The AI service is temporarily unavailable. Your request has been logged. "
                "Please try again shortly."
            )

    @staticmethod
    def _format_context(context: dict) -> str:
        if not context:
            return "(no additional data context)"
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _mock_response(self, prompt: str, context: dict) -> str:
        tenant_name = context.get("tenant_name", "your hospital")
        if "admission" in prompt.lower() or "admitted" in prompt.lower():
            count = context.get("admissions_this_month", "several")
            return (
                f"[DEMO / MOCK MODE] Based on {tenant_name}'s synthetic records, "
                f"{count} patient(s) were admitted this month. This response was generated "
                f"from tenant-scoped demo data only."
            )
        if "statistic" in prompt.lower() or "how many patients" in prompt.lower():
            total = context.get("total_patients", "an authorized set of")
            return (
                f"[DEMO / MOCK MODE] {tenant_name} currently has {total} synthetic patient "
                f"record(s) on file, scoped strictly to this hospital's tenant."
            )
        return (
            f"[DEMO / MOCK MODE] This is a simulated GPT-4o-mini response for {tenant_name}. "
            f"In a live deployment with an OpenAI API key configured, this would be answered "
            f"by the configured LLM using only the authorized, tenant-scoped data context "
            f"shown in the security trace."
        )
