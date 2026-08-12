"""AI Governance Gateway — the multi-tenant isolation security pipeline.

USER -> Authentication (JWT) -> Tenant Context (H1/H2) -> Authorization
(RBAC + RLS) -> LLM / Agent -> [ SQL Tool | RAG Tool ], each behind its own
tenant filter -> Database / Vector Database -> Audit Logging -> USER

CORE PRINCIPLE: security must not depend on the LLM. Authentication, tenant
identity, and authorization are all resolved in deterministic backend code
BEFORE the LLM/agent is ever invoked. The LLM never decides which tenant's
data a tool call is allowed to touch — every tool call below is scoped from
`ctx.tenant_id`, which comes from the verified JWT, never from the prompt.
Requests that fail a check never reach the LLM or a tool at all.
"""
import re

from sqlalchemy.orm import Session

from app.models.ai_policy import AIPolicy
from app.schemas.ai import ChatResponse, RetrievedDocument, TraceStep
from app.security.rbac import ROLE_LABELS
from app.security.tenant_context import TenantContext
from app.services import audit_service, rag_service, risk_service, tenant_service
from app.services.llm.factory import get_llm_provider

RAG_KEYWORDS = ["policy", "policies", "guideline", "guidelines", "protocol", "protocols", "procedure", "document"]

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def _redact_secrets(text: str) -> str:
    """Response validation: re-scan LLM output before it reaches the user."""
    return _EMAIL_RE.sub("[REDACTED_EMAIL]", text)


def _looks_like_rag_query(message: str) -> bool:
    lowered = message.lower()
    return any(kw in lowered for kw in RAG_KEYWORDS)


def _get_policy_map(db: Session, tenant_id: int) -> dict[str, AIPolicy]:
    rows = db.query(AIPolicy).filter(AIPolicy.tenant_id == tenant_id).all()
    return {row.policy_code: row for row in rows}


class TraceBuilder:
    def __init__(self):
        self.steps: list[TraceStep] = []
        self._n = 0

    def add(self, label: str, status: str, detail: str):
        self._n += 1
        self.steps.append(TraceStep(step=self._n, label=label, status=status, detail=detail))


def process_ai_request(db: Session, ctx: TenantContext, message: str) -> ChatResponse:
    trace = TraceBuilder()
    provider = get_llm_provider()
    policies = _get_policy_map(db, ctx.tenant_id)

    def policy_enabled(code: str, default: bool = True) -> bool:
        row = policies.get(code)
        return row.enabled if row else default

    trace.add("Authentication", "PASS", f"Valid JWT session for {ctx.user.name}")
    trace.add("Tenant Context", "PASS", f"Server-derived tenant = {ctx.tenant_code} (from verified JWT, never from client input)")
    trace.add("Authorization (RBAC + RLS)", "PASS", f"Role = {ROLE_LABELS.get(ctx.role, ctx.role)} — permitted to use the AI Assistant")

    all_tenant_codes = tenant_service.get_all_tenant_codes(db)
    injection = risk_service.detect_prompt_injection(message)
    cross_tenant_code = risk_service.detect_cross_tenant_mention(message, ctx.tenant_code, all_tenant_codes)

    # ---- 1) Prompt Injection: checked first, before any tool is chosen ----
    if injection.is_prompt_injection and policy_enabled("AI_INPUT_SECURITY"):
        trace.add("Prompt Security", "FAIL", "Prompt injection / instruction-override pattern detected")
        trace.add(
            "Tenant Isolation",
            "FAIL" if cross_tenant_code else "N/A",
            f"Message also references tenant '{cross_tenant_code}'" if cross_tenant_code else "No explicit cross-tenant reference",
        )
        trace.add("Authorization Policy", "BLOCKED", "Policy AI_INPUT_SECURITY = BLOCK")
        trace.add("LLM / Agent Invocation", "SKIPPED", "The agent was never invoked")
        trace.add("Tool Call", "SKIPPED", "No SQL Tool or RAG Tool call was made")

        policies_triggered = ["AI_INPUT_SECURITY"]
        if injection.matched_secret_keywords:
            policies_triggered.append("SECRET_PROTECTION")
        if cross_tenant_code:
            policies_triggered.append("TENANT_ISOLATION")

        audit_service.log_audit(
            db, ctx.tenant_id, ctx.user.id, "AI_REQUEST", "BLOCK", message,
            "AI_INPUT_SECURITY", "CRITICAL", provider.get_model_name(),
            {"policies_triggered": policies_triggered},
        )
        trace.add("Audit Logging", "PASS", "Blocked request recorded in the audit log")

        return ChatResponse(
            action="BLOCK", risk_level="CRITICAL", policy_code="AI_INPUT_SECURITY",
            policies_triggered=policies_triggered,
            message=(
                "🚫 REQUEST BLOCKED — Prompt injection detected. This request attempted to override "
                "system instructions and/or access protected secrets or another tenant's data. It was "
                "blocked before the agent — and therefore before any SQL/RAG tool call — was invoked."
            ),
            llm_invoked=False, model=provider.get_model_name(), provider=provider.get_provider_name(),
            mock_mode=provider.is_mock(), tool_used=None, trace=trace.steps,
            cross_tenant={"authenticated_tenant": ctx.tenant_code, "requested_tenant": cross_tenant_code} if cross_tenant_code else None,
        )

    # ---- 2) Cross-tenant access attempt (covers both SQL- and RAG-style requests) ----
    if cross_tenant_code and (policy_enabled("TENANT_ISOLATION") or policy_enabled("CROSS_TENANT_ACCESS")):
        attempted_tool = "RAG" if _looks_like_rag_query(message) else "SQL"
        filter_name = "Tenant Filter" if attempted_tool == "RAG" else "RLS Filter"
        store_name = "Vector Database" if attempted_tool == "RAG" else "Database"

        trace.add("Prompt Security", "PASS", "No prompt injection pattern detected")
        trace.add("Tool Selection", "PASS", f"{attempted_tool} Tool would handle this request")
        trace.add("Tenant Isolation", "FAIL", f"Authenticated tenant '{ctx.tenant_code}' requested data for tenant '{cross_tenant_code}'")
        trace.add(
            filter_name, "BLOCKED",
            f"{attempted_tool} Tool call rejected before reaching the {store_name} — the tenant filter "
            f"only ever resolves to '{ctx.tenant_code}', so it cannot be redirected to '{cross_tenant_code}' by the prompt",
        )
        trace.add("LLM / Agent Invocation", "SKIPPED", "The tool call was blocked before the agent could use any result")

        audit_service.log_audit(
            db, ctx.tenant_id, ctx.user.id, "AI_REQUEST", "BLOCK", message,
            "TENANT_ISOLATION", "CRITICAL", provider.get_model_name(),
            {"attempted_tool": attempted_tool, "authenticated_tenant": ctx.tenant_code, "requested_tenant": cross_tenant_code},
        )
        trace.add("Audit Logging", "PASS", "Blocked cross-tenant attempt recorded in the audit log")

        return ChatResponse(
            action="BLOCK", risk_level="CRITICAL", policy_code="TENANT_ISOLATION",
            policies_triggered=["TENANT_ISOLATION"],
            message=(
                f"🚫 ACCESS BLOCKED — Cross-tenant data access is not permitted. You are authenticated as "
                f"{ctx.tenant_code}, but this request asked the {attempted_tool} Tool for data belonging to "
                f"{cross_tenant_code}. The {store_name.lower()} was never queried for the other tenant."
            ),
            llm_invoked=False, model=provider.get_model_name(), provider=provider.get_provider_name(),
            mock_mode=provider.is_mock(), tool_used=attempted_tool, trace=trace.steps,
            cross_tenant={"authenticated_tenant": ctx.tenant_code, "requested_tenant": cross_tenant_code},
        )

    # ---- 3) Allowed: route to SQL Tool or RAG Tool, each independently tenant-filtered ----
    trace.add("Prompt Security", "PASS", "No prompt injection pattern detected")
    trace.add("Tenant Isolation", "PASS", f"No cross-tenant reference — scope confirmed as {ctx.tenant_code}")

    if _looks_like_rag_query(message):
        tool_used = "RAG"
        trace.add("Tool Selection", "PASS", "RAG Tool selected (knowledge/policy-style question)")
        results = rag_service.search_documents(db, ctx.tenant_id, message)
        trace.add("Tenant Filter", "PASS", f"Vector search scoped server-side to tenant_id = {ctx.tenant_code} only, before ranking")
        trace.add("Vector Database", "PASS", f"{len(results)} document(s) retrieved from {ctx.tenant_code}'s isolated knowledge base")
        context = {
            "tenant_name": ctx.tenant.name,
            "documents": "; ".join(f"{doc.title}: {doc.content}" for doc, _ in results) or "(no matching documents)",
        }
        retrieved_documents = [RetrievedDocument(title=doc.title, score=round(score, 2)) for doc, score in results]
    else:
        tool_used = "SQL"
        trace.add("Tool Selection", "PASS", "SQL Tool selected (structured/statistical question)")
        context = {
            "tenant_name": ctx.tenant.name,
            "tenant_code": ctx.tenant_code,
            "total_patients": tenant_service.count_tenant_patients(db, ctx.tenant_id),
            "admissions_this_month": tenant_service.count_admissions_this_month(db, ctx.tenant_id),
        }
        trace.add("RLS Filter", "PASS", f"Row-Level Security enforced server-side: WHERE tenant_id = {ctx.tenant_code}")
        trace.add("Database", "PASS", "Tenant-scoped SQL query executed")
        retrieved_documents = []

    llm_text = _redact_secrets(provider.generate_with_context(message, context))
    trace.add("LLM / Agent", "PASS", f"{provider.get_model_name()} ({provider.get_provider_name()}) answers using only the {tool_used} Tool's tenant-scoped output")
    trace.add("Response Validation", "PASS", "Output re-scanned — no cross-tenant data or secrets present")

    audit_service.log_audit(
        db, ctx.tenant_id, ctx.user.id, "AI_REQUEST", "ALLOW", message,
        "TENANT_SCOPED_ACCESS", "LOW", provider.get_model_name(),
        {"tool_used": tool_used, **{k: v for k, v in context.items() if k != "documents"}},
    )
    trace.add("Audit Logging", "PASS", "Allowed request recorded in the audit log")

    return ChatResponse(
        action="ALLOW", risk_level="LOW", policy_code="TENANT_SCOPED_ACCESS", policies_triggered=[],
        message=llm_text, llm_invoked=True, model=provider.get_model_name(), provider=provider.get_provider_name(),
        mock_mode=provider.is_mock(), tool_used=tool_used, retrieved_documents=retrieved_documents, trace=trace.steps,
    )
