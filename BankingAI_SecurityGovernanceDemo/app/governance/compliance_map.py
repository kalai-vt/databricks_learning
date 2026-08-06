"""Maps each engineering control in this demo to the regulatory/standards
driver it satisfies. This table is the artifact a compliance reviewer
actually wants to see: not "we have security," but "control X maps to
requirement Y, implemented in file Z."
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ControlMapping:
    control: str
    implementation: str
    regulations: list[str]
    description: str


COMPLIANCE_MATRIX: list[ControlMapping] = [
    ControlMapping(
        control="Tenant & role-scoped retrieval (multi-tenant isolation)",
        implementation="app/rag/vector_store.py, app/tenancy.py",
        regulations=["GDPR Art. 5(1)(f) — integrity & confidentiality", "PCI-DSS Req. 7 — need-to-know access", "SOC 2 CC6"],
        description="A query can never retrieve chunks belonging to another tenant, and RBAC further "
        "restricts by document sensitivity within a tenant.",
    ),
    ControlMapping(
        control="PII detection & redaction (inbound + outbound)",
        implementation="app/security/pii.py, app/security/output_guard.py",
        regulations=["GDPR Art. 5(1)(c) — data minimization", "PCI-DSS Req. 3.4 — PAN masking", "GLBA Safeguards Rule"],
        description="Card numbers, account numbers, SSNs, and similar identifiers are masked before "
        "being used in retrieval/generation and again before leaving the system.",
    ),
    ControlMapping(
        control="Prompt-injection detection",
        implementation="app/security/prompt_injection.py",
        regulations=["OWASP Top 10 for LLM Applications — LLM01", "NIST AI RMF — Manage 2.1"],
        description="Blocks known instruction-override / jailbreak phrasing before it reaches the "
        "retriever or generator.",
    ),
    ControlMapping(
        control="Output sanitization",
        implementation="app/security/output_guard.py",
        regulations=["OWASP Top 10 for LLM Applications — LLM02"],
        description="Strips markup, caps response length, and re-scans generated text for PII before "
        "it is returned to the caller.",
    ),
    ControlMapping(
        control="Per-tenant rate limiting",
        implementation="app/security/rate_limit.py",
        regulations=["OWASP Top 10 for LLM Applications — LLM04", "SOC 2 CC7 — availability"],
        description="Token-bucket limiter keyed by (tenant, user) so one tenant cannot exhaust shared "
        "inference capacity.",
    ),
    ControlMapping(
        control="Grounded-only generation with refusal on low relevance",
        implementation="app/rag/generator.py",
        regulations=["EU AI Act Art. 13 — transparency", "NIST AI RMF — Govern 1.1"],
        description="If retrieval confidence is below threshold, the system declines to answer rather "
        "than fabricating a policy statement — no hallucinated banking guidance.",
    ),
    ControlMapping(
        control="Ethical-AI refusal & escalation policy",
        implementation="app/ethics/policy.py",
        regulations=["ECOA / Regulation B (US) — non-discrimination in lending", "EU AI Act Art. 5/9 — prohibited & high-risk practices", "RBI Fair Practices Code"],
        description="Refuses discrimination-adjacent lending queries and unlicensed financial-advice "
        "requests; flags high-stakes categories (fraud, credit decisions) for human review.",
    ),
    ControlMapping(
        control="Tamper-evident audit log",
        implementation="app/governance/audit_log.py",
        regulations=["SOX Section 404 — internal controls", "GLBA Safeguards Rule", "PCI-DSS Req. 10"],
        description="Hash-chained, append-only log of every query, retrieval, redaction, refusal, and "
        "escalation decision.",
    ),
    ControlMapping(
        control="Model card & risk classification",
        implementation="app/governance/model_card.py",
        regulations=["SR 11-7 (US model risk management)", "EU AI Act Art. 13"],
        description="Documents intended use, out-of-scope uses, data sources, limitations, and human "
        "oversight requirements for the deployed system.",
    ),
]


def render_markdown() -> str:
    lines = ["| Control | Implementation | Regulations / Standards |", "|---|---|---|"]
    for c in COMPLIANCE_MATRIX:
        lines.append(f"| {c.control} | `{c.implementation}` | {', '.join(c.regulations)} |")
    return "\n".join(lines)
