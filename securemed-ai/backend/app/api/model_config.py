from fastapi import APIRouter, Depends

from app.security.rbac import require_any_authenticated
from app.security.tenant_context import TenantContext
from app.services.llm.factory import get_llm_provider

router = APIRouter(prefix="/api/model", tags=["model"])

WHY_GPT4O_MINI = [
    "Cost-effective for repeated live demonstrations",
    "Fast response time, suited for conversational UI",
    "Sufficient capability for structured application workflows",
    "Good fit for a local proof-of-concept",
    "Keeps API cost low during repeated demos",
    "Easily replaced through the provider abstraction",
]

FUTURE_MODELS = ["GPT models", "Claude", "Gemini", "Llama", "Other enterprise/open-source models"]
EVALUATION_CRITERIA = [
    "Response Quality", "Reasoning", "Security Behavior", "Latency",
    "Cost", "Privacy Controls", "Tool Calling", "Deployment Options",
]


@router.get("/config")
def model_config(ctx: TenantContext = Depends(require_any_authenticated)):
    provider = get_llm_provider()
    return {
        "provider": provider.get_provider_name(),
        "model": provider.get_model_name(),
        "status": "ACTIVE",
        "mock_mode": provider.is_mock(),
        "architecture": "Model-Agnostic Governance Layer",
        "why_this_model": WHY_GPT4O_MINI,
        "positioning_statement": (
            "GPT-4o-mini is selected for this prototype based on cost, speed, availability and "
            "sufficient capability for the demonstration workload. The application architecture "
            "is model-agnostic."
        ),
        "future_models": FUTURE_MODELS,
        "evaluation_criteria": EVALUATION_CRITERIA,
        "note": "The model can be replaced without changing the governance layer.",
    }
