"""SecureRAGPipeline: the orchestrator that wires tenancy, security,
ethics, and RAG together into one auditable `ask()` call.

Fixed control order, every step logged, first hard-stop wins:

  1. tenant/user authorization         (multi-tenant isolation)
  2. rate limiting                     (OWASP LLM04)
  3. inbound PII redaction             (OWASP LLM06) — runs before anything
     else touches the query, including logging
  4. prompt-injection scan             (OWASP LLM01) — on the *redacted* text
  5. ethical-AI policy                 (refuse / escalate / allow)
  6. tenant+role-scoped retrieval      (multi-tenant isolation + RBAC)
  7. grounded generation               (no answer without retrieved context)
  8. outbound output guard             (OWASP LLM02, PII re-check)
  9. tamper-evident audit log entry    (Standards & Governance)

Every branch below returns through the same audit-log call so there is one
row per request no matter how it was handled — allowed, refused, or
blocked.
"""
from __future__ import annotations

import time

from app.ethics.policy import EthicsAction, evaluate as ethics_evaluate
from app.governance.audit_log import AuditLog
from app.models import QueryResult, SecurityEvent, new_id
from app.rag.generator import Generator
from app.rag.retriever import retrieve
from app.rag.vector_store import TenantVectorRegistry
from app.security.output_guard import sanitize_output
from app.security.pii import detect_and_redact
from app.security.prompt_injection import scan as scan_injection
from app.security.rate_limit import RateLimiter
from app.tenancy import TenantRegistry


class SecureRAGPipeline:
    def __init__(
        self,
        registry: TenantRegistry,
        vector_registry: TenantVectorRegistry,
        generator: Generator,
        audit_log: AuditLog | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self.registry = registry
        self.vector_registry = vector_registry
        self.generator = generator
        self.audit_log = audit_log or AuditLog()
        self.rate_limiter = rate_limiter or RateLimiter()

    def ask(self, user_id: str, claimed_tenant_id: str, raw_query: str) -> QueryResult:
        start = time.monotonic()
        query_id = new_id("qry")
        events: list[SecurityEvent] = []

        def deny(reason: str, event_type: str, severity: str = "warning", role=None) -> QueryResult:
            events.append(SecurityEvent(new_id("evt"), event_type, severity, reason))
            result = QueryResult(
                query_id=query_id,
                tenant_id=claimed_tenant_id,
                user_id=user_id,
                role=role,
                original_query="[not logged — request denied pre-processing]",
                allowed=False,
                answer=reason,
                events=events,
                latency_ms=(time.monotonic() - start) * 1000,
            )
            self._audit(result)
            return result

        # 1. Authorization: does user_id really belong to claimed_tenant_id?
        try:
            user = self.registry.authorize(user_id, claimed_tenant_id)
        except (KeyError, PermissionError) as exc:
            return deny(str(exc), "CROSS_TENANT_ACCESS_DENIED", severity="critical")

        # 2. Rate limiting
        if not self.rate_limiter.allow(claimed_tenant_id, user_id):
            return deny(
                "Request rate limit exceeded for this account. Please wait and try again.",
                "RATE_LIMITED",
                role=user.role,
            )

        # 3. Inbound PII redaction — runs before the query is used anywhere else
        redacted_query, pii_findings = detect_and_redact(raw_query)
        if pii_findings:
            labels = ", ".join(sorted({f.label for f in pii_findings}))
            events.append(SecurityEvent(
                new_id("evt"), "PII_REDACTED_INBOUND", "info",
                f"Redacted {len(pii_findings)} PII item(s) from the query before processing: {labels}",
            ))

        # 4. Prompt-injection scan (on redacted text)
        injection_findings = scan_injection(redacted_query)
        if injection_findings:
            names = ", ".join(f.pattern_name for f in injection_findings)
            reason = f"Request blocked: matched known prompt-injection pattern(s): {names}."
            events.append(SecurityEvent(new_id("evt"), "PROMPT_INJECTION_BLOCKED", "critical", reason))
            result = QueryResult(
                query_id=query_id, tenant_id=claimed_tenant_id, user_id=user_id, role=user.role,
                original_query=redacted_query, allowed=False, answer=reason, events=events,
                latency_ms=(time.monotonic() - start) * 1000,
            )
            self._audit(result)
            return result

        # 5. Ethical AI policy
        decision = ethics_evaluate(redacted_query)
        escalate = False
        if decision.action == EthicsAction.REFUSE:
            events.append(SecurityEvent(new_id("evt"), "ETHICS_REFUSED", "warning", decision.reason or ""))
            result = QueryResult(
                query_id=query_id, tenant_id=claimed_tenant_id, user_id=user_id, role=user.role,
                original_query=redacted_query, allowed=False, answer=decision.reason or "Request declined.",
                events=events, latency_ms=(time.monotonic() - start) * 1000,
            )
            self._audit(result)
            return result
        if decision.action == EthicsAction.ESCALATE:
            escalate = True
            events.append(SecurityEvent(new_id("evt"), "ETHICS_ESCALATED", "info", decision.reason or ""))

        # 6. Tenant + role scoped retrieval
        store = self.vector_registry.get(claimed_tenant_id)
        retrieved = retrieve(store, redacted_query, role=user.role)
        if not retrieved:
            events.append(SecurityEvent(
                new_id("evt"), "NO_GROUNDED_ANSWER", "info",
                "No chunk cleared the relevance threshold and/or the user's role clearance; refusing "
                "rather than answering ungrounded.",
            ))

        # 7. Grounded generation
        raw_answer = self.generator.generate(redacted_query, retrieved)

        # 8. Outbound output guard
        clean_answer, guard_notes = sanitize_output(raw_answer)
        for note in guard_notes:
            events.append(SecurityEvent(new_id("evt"), "OUTPUT_GUARD_" + note.upper(), "info", note))

        citations = sorted({r.chunk.title for r in retrieved})

        result = QueryResult(
            query_id=query_id,
            tenant_id=claimed_tenant_id,
            user_id=user_id,
            role=user.role,
            original_query=redacted_query,
            allowed=True,
            answer=clean_answer,
            citations=citations,
            events=events,
            escalate_to_human=escalate,
            latency_ms=(time.monotonic() - start) * 1000,
        )
        self._audit(result)
        return result

    def _audit(self, result: QueryResult) -> None:
        self.audit_log.append({
            "query_id": result.query_id,
            "tenant_id": result.tenant_id,
            "user_id": result.user_id,
            "role": result.role.value if result.role else None,
            "query": result.original_query,
            "allowed": result.allowed,
            "citations": result.citations,
            "escalate_to_human": result.escalate_to_human,
            "events": [
                {"type": e.event_type, "severity": e.severity, "detail": e.detail} for e in result.events
            ],
            "latency_ms": round(result.latency_ms, 2),
        })
