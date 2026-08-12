from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class TraceStep(BaseModel):
    step: int
    label: str
    status: str  # PASS | FAIL | SKIPPED | BLOCKED | N/A
    detail: str


class RetrievedDocument(BaseModel):
    title: str
    score: float


class ChatResponse(BaseModel):
    action: str  # ALLOW | BLOCK
    risk_level: str  # LOW | CRITICAL
    policy_code: str
    policies_triggered: list[str] = []
    message: str
    llm_invoked: bool
    model: str
    provider: str
    mock_mode: bool
    tool_used: str | None = None  # "SQL" | "RAG" | None
    retrieved_documents: list[RetrievedDocument] = []
    trace: list[TraceStep]
    cross_tenant: dict | None = None
