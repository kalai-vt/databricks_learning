from typing import Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class TraceStep(BaseModel):
    step: int
    label: str
    status: str  # PASS | FAIL | SKIPPED
    detail: str


class ChatResponse(BaseModel):
    action: str  # ALLOW | BLOCK | MASK | HUMAN_REVIEW
    risk_level: str  # LOW | MEDIUM | HIGH | CRITICAL
    policy_code: str
    policies_triggered: list[str] = []
    message: str
    llm_invoked: bool
    model: str
    provider: str
    mock_mode: bool
    trace: list[TraceStep]
    pii_detected: list[dict[str, Any]] = []
    cross_tenant: dict[str, Any] | None = None
