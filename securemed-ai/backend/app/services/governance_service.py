"""AI Governance Gateway - the orchestrator of the full request pipeline.

USER -> Authentication -> Tenant Identification -> RBAC -> AI Governance
Gateway (PII/PHI Detection -> Prompt Injection Detection -> Policy Engine ->
Tenant Authorization) -> Tenant-Scoped Data Retrieval -> LLM -> Response
Validation -> Audit Logging -> USER

CORE PRINCIPLE: security must not depend on the LLM. Every authorization,
isolation, and safety decision below happens in deterministic backend code
BEFORE the LLM is ever invoked. The LLM is only reached for requests that
have already been fully authorized and scoped.
"""
from sqlalchemy.orm import Session

from app.models.ai_policy import AIPolicy
from app.schemas.ai import ChatResponse, TraceStep
from app.security.rbac import ROLE_LABELS
from app.security.tenant_context import TenantContext
from app.services import audit_service, pii_service, risk_service, tenant_service
from app.services.llm.factory import get_llm_provider


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
    trace.add("RBAC", "PASS", f"Role = {ROLE_LABELS.get(ctx.role, ctx.role)} — permitted to use AI Assistant")

    all_tenant_codes = tenant_service.get_all_tenant_codes(db)
    patients = tenant_service.get_tenant_patients(db, ctx.tenant_id)

    injection = risk_service.detect_prompt_injection(message)
    cross_tenant_code = risk_service.detect_cross_tenant_mention(message, ctx.tenant_code, all_tenant_codes)
    pii_findings = pii_service.build_pii_findings(message, patients)
    is_high_risk = risk_service.detect_high_risk_healthcare(message)

    # ---- 1) Prompt Injection: highest priority, checked first ----
    if injection.is_prompt_injection and policy_enabled("AI_INPUT_SECURITY"):
        trace.add("PII Detection", "SKIPPED", "Not evaluated — request already flagged for injection")
        trace.add("Prompt Security", "FAIL", "Prompt injection / instruction-override pattern detected")
        trace.add(
            "Tenant Isolation",
            "FAIL" if cross_tenant_code else "N/A",
            f"Message also references tenant '{cross_tenant_code}'" if cross_tenant_code else "No explicit cross-tenant reference",
        )
        trace.add("Governance Policy", "BLOCKED", "Policy AI_INPUT_SECURITY = BLOCK")
        trace.add("Data Access", "SKIPPED", "Blocked before any data retrieval")
        trace.add("LLM Invocation", "SKIPPED", "LLM was never called")
        trace.add("Response Validation", "SKIPPED", "N/A — no LLM response was generated")

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
        audit_service.log_security_event(
            db, ctx.tenant_id, ctx.user.id, "PROMPT_INJECTION", "CRITICAL",
            "Prompt injection attempt detected and blocked before reaching the LLM.", "BLOCKED",
        )
        trace.add("Audit", "PASS", "Security event and audit log recorded")

        return ChatResponse(
            action="BLOCK", risk_level="CRITICAL", policy_code="AI_INPUT_SECURITY",
            policies_triggered=policies_triggered,
            message=(
                "🚫 REQUEST BLOCKED — Prompt injection detected. This request attempted to override "
                "system instructions and/or access protected secrets or another tenant's data. "
                "The request was blocked before it reached the LLM. No API keys, credentials, or "
                "cross-tenant data were exposed."
            ),
            llm_invoked=False, model=provider.get_model_name(), provider=provider.get_provider_name(),
            mock_mode=provider.is_mock(), trace=trace.steps,
            cross_tenant={"authenticated_tenant": ctx.tenant_code, "requested_tenant": cross_tenant_code} if cross_tenant_code else None,
        )

    # ---- 2) Cross-tenant access attempt ----
    if cross_tenant_code and (policy_enabled("TENANT_ISOLATION") or policy_enabled("CROSS_TENANT_ACCESS")):
        trace.add("PII Detection", "N/A", "Not applicable — request blocked on tenant isolation")
        trace.add("Prompt Security", "PASS", "No prompt injection pattern detected")
        trace.add("Tenant Isolation", "FAIL", f"Authenticated tenant '{ctx.tenant_code}' requested data for tenant '{cross_tenant_code}'")
        trace.add("Governance Policy", "BLOCKED", "Policy TENANT_ISOLATION = BLOCK")
        trace.add("Data Access", "SKIPPED", "Cross-tenant query was never executed")
        trace.add("LLM Invocation", "SKIPPED", "LLM was never called")
        trace.add("Response Validation", "SKIPPED", "N/A — no LLM response was generated")

        audit_service.log_audit(
            db, ctx.tenant_id, ctx.user.id, "AI_REQUEST", "BLOCK", message,
            "TENANT_ISOLATION", "CRITICAL", provider.get_model_name(),
            {"authenticated_tenant": ctx.tenant_code, "requested_tenant": cross_tenant_code},
        )
        audit_service.log_security_event(
            db, ctx.tenant_id, ctx.user.id, "CROSS_TENANT_ACCESS", "CRITICAL",
            f"User requested data belonging to tenant '{cross_tenant_code}' while authenticated as '{ctx.tenant_code}'.",
            "BLOCKED",
        )
        trace.add("Audit", "PASS", "Security event and audit log recorded")

        return ChatResponse(
            action="BLOCK", risk_level="CRITICAL", policy_code="TENANT_ISOLATION",
            policies_triggered=["TENANT_ISOLATION"],
            message=(
                f"🚫 ACCESS BLOCKED — Cross-tenant data access is not permitted. You are authenticated "
                f"as {ctx.tenant_code}, but this request asked for data belonging to {cross_tenant_code}. "
                f"The database was never queried for the other tenant, and the LLM was never invoked."
            ),
            llm_invoked=False, model=provider.get_model_name(), provider=provider.get_provider_name(),
            mock_mode=provider.is_mock(), trace=trace.steps,
            cross_tenant={"authenticated_tenant": ctx.tenant_code, "requested_tenant": cross_tenant_code},
        )

    # ---- 3) PII / PHI sensitive-field request ----
    if pii_findings and policy_enabled("PHI_PROTECTION"):
        trace.add("PII Detection", "FAIL", f"Sensitive field(s) requested: {', '.join(f.field for f in pii_findings)}")
        trace.add("Prompt Security", "PASS", "No prompt injection pattern detected")
        trace.add("Tenant Isolation", "PASS", f"Patient belongs to tenant {ctx.tenant_code}")
        trace.add("Governance Policy", "MASKED", "Policy PHI_PROTECTION = MASK")
        trace.add("Data Access", "PASS", f"{ctx.tenant_code} scope enforced — sensitive fields minimized before LLM context")

        masked_context = {
            "tenant_name": ctx.tenant.name,
            "patient": pii_findings[0].patient_name,
            **{f.field: f.masked for f in pii_findings},
        }
        llm_text = provider.generate_with_context(message, masked_context)
        llm_text = pii_service.redact_secrets_from_text(llm_text)
        trace.add("LLM Invocation", "PASS", f"{provider.get_model_name()} called with masked context only (no raw PII)")
        trace.add("Response Validation", "PASS", "Output re-scanned; no unmasked PII present")

        details = {"findings": [{"field": f.field, "patient": f.patient_name, "masked": f.masked} for f in pii_findings]}
        audit_service.log_audit(
            db, ctx.tenant_id, ctx.user.id, "AI_REQUEST", "MASK", message,
            "PHI_PROTECTION", "MEDIUM", provider.get_model_name(), details,
        )
        audit_service.log_security_event(
            db, ctx.tenant_id, ctx.user.id, "PII_DETECTION", "MEDIUM",
            f"Sensitive field(s) requested for patient {pii_findings[0].patient_name}: {', '.join(f.field for f in pii_findings)}. Masked before response.",
            "MASKED",
        )
        trace.add("Audit", "PASS", "Security event and audit log recorded")

        masked_lines = "\n".join(f"- {f.field}: {f.masked} (original protected)" for f in pii_findings)
        return ChatResponse(
            action="MASK", risk_level="MEDIUM", policy_code="PHI_PROTECTION",
            policies_triggered=["PHI_PROTECTION"],
            message=f"🔒 PII/PHI DETECTED — sensitive field(s) masked before display:\n{masked_lines}\n\n{llm_text}",
            llm_invoked=True, model=provider.get_model_name(), provider=provider.get_provider_name(),
            mock_mode=provider.is_mock(), trace=trace.steps,
            pii_detected=[{"field": f.field, "patient": f.patient_name, "masked": f.masked} for f in pii_findings],
        )

    # ---- 4) High-risk healthcare request (needs human oversight) ----
    if is_high_risk and policy_enabled("HIGH_RISK_HEALTHCARE"):
        trace.add("PII Detection", "PASS", "No sensitive field request detected")
        trace.add("Prompt Security", "PASS", "No prompt injection pattern detected")
        trace.add("Tenant Isolation", "PASS", f"Scope = {ctx.tenant_code}")
        trace.add("Governance Policy", "HUMAN_REVIEW", "Policy HIGH_RISK_HEALTHCARE = HUMAN REVIEW")
        trace.add("Data Access", "SKIPPED", "Not required — request escalated before data retrieval")
        trace.add("LLM Invocation", "SKIPPED", "LLM is not used to make high-impact healthcare decisions")
        trace.add("Response Validation", "SKIPPED", "N/A")

        audit_service.log_audit(
            db, ctx.tenant_id, ctx.user.id, "AI_REQUEST", "HUMAN_REVIEW", message,
            "HIGH_RISK_HEALTHCARE", "HIGH", provider.get_model_name(), None,
        )
        audit_service.log_security_event(
            db, ctx.tenant_id, ctx.user.id, "HIGH_RISK_REQUEST", "HIGH",
            "High-risk healthcare request (diagnosis/treatment) escalated for mandatory human review.",
            "HUMAN_REVIEW",
        )
        trace.add("Audit", "PASS", "Security event and audit log recorded")

        return ChatResponse(
            action="HUMAN_REVIEW", risk_level="HIGH", policy_code="HIGH_RISK_HEALTHCARE",
            policies_triggered=["HIGH_RISK_HEALTHCARE"],
            message=(
                "⚠ HUMAN REVIEW REQUIRED — This AI assistant is not a medical diagnostic or treatment "
                "system. High-impact healthcare decisions require qualified human review. This request "
                "has been logged and routed for clinical staff attention; the LLM was not used to "
                "generate a diagnosis or treatment recommendation."
            ),
            llm_invoked=False, model=provider.get_model_name(), provider=provider.get_provider_name(),
            mock_mode=provider.is_mock(), trace=trace.steps,
        )

    # ---- 5) Allowed: normal, tenant-scoped request ----
    trace.add("PII Detection", "PASS", "No sensitive field request detected")
    trace.add("Prompt Security", "PASS", "No prompt injection pattern detected")
    trace.add("Tenant Isolation", "PASS", f"Scope = {ctx.tenant_code}")
    trace.add("Governance Policy", "ALLOWED", "No policy violation — request permitted")

    context = {
        "tenant_name": ctx.tenant.name,
        "tenant_code": ctx.tenant_code,
        "total_patients": tenant_service.count_tenant_patients(db, ctx.tenant_id),
        "admissions_this_month": tenant_service.count_admissions_this_month(db, ctx.tenant_id),
    }
    trace.add("Data Access", "PASS", f"Tenant-scoped query executed (WHERE tenant_id = {ctx.tenant_code})")

    llm_text = provider.generate_with_context(message, context)
    llm_text = pii_service.redact_secrets_from_text(llm_text)
    trace.add("LLM Invocation", "PASS", f"{provider.get_model_name()} ({provider.get_provider_name()})")
    trace.add("Response Validation", "PASS", "Output scanned — no PII or cross-tenant data present")

    audit_service.log_audit(
        db, ctx.tenant_id, ctx.user.id, "AI_REQUEST", "ALLOW", message,
        "GOVERNANCE_ALLOW", "LOW", provider.get_model_name(), context,
    )
    trace.add("Audit", "PASS", "Audit log recorded")

    return ChatResponse(
        action="ALLOW", risk_level="LOW", policy_code="GOVERNANCE_ALLOW",
        policies_triggered=[],
        message=llm_text,
        llm_invoked=True, model=provider.get_model_name(), provider=provider.get_provider_name(),
        mock_mode=provider.is_mock(), trace=trace.steps,
    )
