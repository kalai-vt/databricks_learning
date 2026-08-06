# Architecture

## Request flow through the guardrail pipeline

```
                                   ┌─────────────────────────────────────────┐
                                   │            SecureRAGPipeline.ask()        │
                                   └─────────────────────────────────────────┘
 user_id, claimed_tenant_id, raw_query
              │
              ▼
   ┌─────────────────────┐   fail  ┌──────────────────────────────────┐
   │ 1. TenantRegistry    │ ──────▶ │ DENY: CROSS_TENANT_ACCESS_DENIED  │──┐
   │    .authorize()      │         └──────────────────────────────────┘  │
   └─────────────────────┘                                                │
              │ ok                                                        │
              ▼                                                           │
   ┌─────────────────────┐   fail  ┌──────────────────────────────────┐   │
   │ 2. RateLimiter       │ ──────▶ │ DENY: RATE_LIMITED                │──┤
   │    .allow()          │         └──────────────────────────────────┘  │
   └─────────────────────┘                                                │
              │ ok                                                        │
              ▼                                                           │
   ┌─────────────────────┐         ┌──────────────────────────────────┐   │
   │ 3. PII detect+redact │ ──────▶ │ EVENT: PII_REDACTED_INBOUND       │   │
   │    (always runs)     │         │ (redacted text flows onward)      │   │
   └─────────────────────┘         └──────────────────────────────────┘   │
              │                                                           │
              ▼                                                           │
   ┌─────────────────────┐   hit   ┌──────────────────────────────────┐   │
   │ 4. Prompt-injection  │ ──────▶ │ DENY: PROMPT_INJECTION_BLOCKED    │──┤
   │    scan              │         └──────────────────────────────────┘  │
   └─────────────────────┘                                                │
              │ clean                                                     │
              ▼                                                           │
   ┌─────────────────────┐  refuse ┌──────────────────────────────────┐   │
   │ 5. Ethics policy     │ ──────▶ │ DENY: ETHICS_REFUSED              │──┤
   │    evaluate()        │         └──────────────────────────────────┘  │
   └─────────────────────┘                                                │
              │ allow / escalate                                          │
              ▼                                                           │
   ┌─────────────────────────────────────────┐                            │
   │ 6. TenantVectorRegistry.get(tenant_id)   │  ← structural isolation:   │
   │    .search(query, role, top_k)           │    one store per tenant,  │
   │    RBAC-filtered by sensitivity clearance│    RBAC filters candidates│
   └─────────────────────────────────────────┘                            │
              │ retrieved chunks (or none → NO_GROUNDED_ANSWER)            │
              ▼                                                           │
   ┌─────────────────────┐                                                │
   │ 7. Generator         │  extractive template, or a hosted LLM under   │
   │    .generate()       │  the same guardrails via a pluggable interface│
   └─────────────────────┘                                                │
              │                                                           │
              ▼                                                           │
   ┌─────────────────────┐                                                │
   │ 8. output_guard      │  strip markup, cap length, re-scan for PII    │
   │    .sanitize_output()│                                               │
   └─────────────────────┘                                                │
              │                                                           │
              ▼                                                           ▼
   ┌───────────────────────────────────────────────────────────────────────┐
   │ 9. AuditLog.append()  — hash-chained, tamper-evident, ONE row per      │
   │    request no matter which branch above it took                       │
   └───────────────────────────────────────────────────────────────────────┘
              │
              ▼
        QueryResult returned to caller (CLI / demo script)
```

## Multi-tenant isolation, structurally

```
TenantRegistry                         TenantVectorRegistry
┌─────────────────────────┐            ┌─────────────────────────────────┐
│ northstar_bank  → users │            │ northstar_bank  → VectorStore A  │
│ meridian_bank   → users │            │ meridian_bank   → VectorStore B  │
│ retail_banking… → users │            │ retail_banking… → VectorStore C  │
│ risk_compliance…→ users │            │ risk_compliance…→ VectorStore D  │
└─────────────────────────┘            └─────────────────────────────────┘
        ▲                                          ▲
        │ authorize(user_id, claimed_tenant_id)     │ get(tenant_id) — only reachable
        │ rejects if user.tenant_id mismatches       │ with a tenant_id the caller
        │ the claimed tenant                         │ already had to be authorized for
        └───────────────────┬────────────────────────┘
                             │
                    SecureRAGPipeline.ask()
```

Each `VectorStore` instance owns exactly one tenant's chunks and its own
TF-IDF index — there is no shared, globally-queryable index anywhere in
the codebase. `VectorStore.add_chunks()` raises `ValueError` if handed a
chunk for a different tenant, so isolation is enforced at ingestion time
too, not only at query time. RBAC (role → sensitivity clearance) is
enforced inside the same `search()` call, restricting the TF-IDF candidate
set before ranking — a low-privilege role's query never even scores
against a chunk it isn't cleared to see.

## Two demo scenarios, one engine

```
                     app/  (security + governance + ethics + rag)
                       │
          ┌────────────┴─────────────┐
          ▼                          ▼
 Demo 1: Internal Compliance   Demo 2: Multi-Brand Customer
 Co-Pilot                      Support Assistant
 tenants: retail_banking_dept, tenants: northstar_bank,
          risk_compliance_dept          meridian_bank
 roles:   teller, risk_analyst,  role:  customer
          compliance_officer
 focus:   RBAC within a tenant,  focus: brand isolation, PII in
          restricted docs,             free-text chat, prompt
          discrimination refusal       injection, rate limiting,
                                        advice/fraud ethics
```
