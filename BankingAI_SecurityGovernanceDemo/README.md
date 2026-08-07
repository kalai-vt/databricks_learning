# Banking AI Security, Governance & Compliance Demo

**Pillar 4 — Security, Governance & Compliance**
Covers: Standards & Governance · RAG Patterns · Security (OWASP, PII) · Ethical AI · Multi-tenant Isolation

A dependency-free (stdlib-only) Python application that demonstrates what
those five topics look like as working code, not slides, in a banking
context. Everything in this folder runs with a bare `python3` interpreter
— no `pip install`, no API keys, no external services — which matters when
you're presenting live and can't risk a flaky network.

## The two technical solutions

### 1. Internal Compliance & Policy Co-Pilot
**Problem:** Compliance officers, risk analysts, and tellers across
different internal departments need fast, accurate answers to policy
questions (KYC/AML, loan underwriting, data privacy, fraud response)
without emailing the compliance team — and a wrong or hallucinated answer
to "what triggers enhanced due diligence" is a real regulatory risk, not
just an annoyance.

**Approach:** A grounded RAG assistant scoped per department (tenant),
with role-based access control down to individual documents (PUBLIC →
INTERNAL → CONFIDENTIAL → RESTRICTED), a tamper-evident audit log of every
question asked and every access decision made, and an ethics layer that
refuses discrimination-adjacent underwriting questions outright.

**Business impact:** Cuts policy-lookup time from "email compliance, wait
a day" to seconds, while making the system auditable by design — every
answer traces to a specific, access-controlled source document, and every
denial is logged with a reason.

### 2. Multi-Brand Customer Support Assistant
**Problem:** A bank licenses the same AI support platform to multiple
white-label brands (here: NorthStar Bank and Meridian Bank). Each brand's
customers must only ever see that brand's fees and policies, and real
customers paste real account numbers, card numbers, and fraud complaints
directly into chat — putting the assistant squarely on the attack surface
described by the OWASP Top 10 for LLM Applications.

**Approach:** The same secure pipeline, configured with two isolated
tenants. Demonstrates hard tenant-boundary enforcement (a brand-A customer
literally cannot query brand-B's data even if the client is compromised or
buggy), inbound/outbound PII redaction, prompt-injection blocking,
per-tenant rate limiting, and ethical-AI refusal/escalation for
unlicensed-advice and high-stakes fraud requests.

**Business impact:** Lets one platform serve multiple brands/subsidiaries
safely — a real commercial requirement for banking-as-a-service and
white-label banking — without a data leak or a jailbroken customer bot
becoming a headline.

## How the five Pillar-4 topics map to code

| Topic | Where it lives | What to look at live |
|---|---|---|
| Standards & Governance | `app/governance/` | `model_card.py`, `compliance_map.py`, `audit_log.py` |
| RAG Patterns | `app/rag/` | `chunking.py` → `tfidf.py` → `vector_store.py` → `retriever.py` → `generator.py` → `pipeline.py` |
| Security (OWASP, PII) | `app/security/` | `pii.py`, `prompt_injection.py`, `rate_limit.py`, `output_guard.py` |
| Ethical AI | `app/ethics/policy.py` | non-discrimination, unlicensed-advice refusal, human-in-the-loop escalation |
| Multi-tenant Isolation | `app/tenancy.py`, `app/rag/vector_store.py` | one `VectorStore` per tenant, `TenantRegistry.authorize()` |

See [`diagrams/architecture.md`](diagrams/architecture.md) for the full
request-flow and isolation diagrams, and
[`WALKTHROUGH.md`](WALKTHROUGH.md) for the live-demo script.

## Browser console (no install, no server)

[`web/banking_ai_console.html`](web/banking_ai_console.html) is a self-contained, dependency-free
reimplementation of the same guardrail pipeline (tenancy, PII redaction, prompt-injection
detection, ethics policy, TF-IDF RAG, tamper-evident audit log) as a single HTML file with
inline CSS/JS — open it directly in any browser, nothing to install and no server to start.
It mirrors `app/` line-for-line in behavior and is useful when you want an interactive,
clickable walkthrough (persona switcher, scenario chips, live audit-log tamper demo, a
Governance tab with the model card and compliance matrix, and an Attack Simulation tab)
instead of a terminal session. The Python code in `app/` remains the reference
implementation — this is a second, presentation-friendly surface over the same logic.

```bash
# macOS
open BankingAI_SecurityGovernanceDemo/web/banking_ai_console.html
# Linux
xdg-open BankingAI_SecurityGovernanceDemo/web/banking_ai_console.html
# or just drag the file into any browser window
```

## Quick start

```bash
cd BankingAI_SecurityGovernanceDemo

# No install required for the core app. Optional, for the test suite:
pip install -r requirements.txt

# Run either scripted demo (recommended for the live walkthrough):
python3 scripts/demo_1_internal_compliance_copilot.py
python3 scripts/demo_2_customer_support_assistant.py

# Or drive it interactively:
python3 -m app.cli --list-users
python3 -m app.cli --user cust_ns_01 --tenant northstar_bank

# Run the OWASP-style attack simulation harness:
python3 scripts/run_attack_simulation.py

# Run the automated test suite:
python3 -m pytest tests/ -v
```

By default the app uses a zero-dependency, hallucination-proof extractive
generator (`TemplateGenerator`). Set `ANTHROPIC_API_KEY` and
`pip install anthropic` to swap in a real LLM behind the exact same
guardrail pipeline (`app/rag/generator.py`) — nothing else in the codebase
changes, which is itself the governance point: the model is swappable, the
controls are not.

## Repository layout

```
BankingAI_SecurityGovernanceDemo/
├── app/
│   ├── models.py            # shared dataclasses (Tenant, User, Chunk, QueryResult, ...)
│   ├── config.py             # tunables (chunk size, relevance threshold, rate limits)
│   ├── tenancy.py            # TenantRegistry — the multi-tenant identity boundary
│   ├── bootstrap.py           # wires everything together for CLI/demo scripts
│   ├── cli.py                 # interactive REPL for live demos
│   ├── display.py             # pretty-prints a QueryResult with its guardrail trace
│   ├── security/
│   │   ├── pii.py             # PII detection & redaction (OWASP LLM06)
│   │   ├── prompt_injection.py# prompt-injection/jailbreak scanner (OWASP LLM01)
│   │   ├── rate_limit.py       # per-(tenant,user) token bucket (OWASP LLM04)
│   │   └── output_guard.py     # output sanitization (OWASP LLM02)
│   ├── governance/
│   │   ├── audit_log.py        # hash-chained, tamper-evident audit log
│   │   ├── model_card.py        # model card (SR 11-7 / EU AI Act style)
│   │   └── compliance_map.py    # control → regulation matrix
│   ├── ethics/
│   │   └── policy.py            # non-discrimination, advice-refusal, escalation
│   └── rag/
│       ├── chunking.py, tfidf.py, vector_store.py, retriever.py,
│       └── generator.py, ingest.py, pipeline.py
├── data/                      # synthetic banking knowledge bases, one folder per tenant
│   ├── tenant_northstar_bank/       (public, customer-facing FAQ)
│   ├── tenant_meridian_bank/        (public, customer-facing FAQ)
│   ├── tenant_retail_banking_dept/  (internal + confidential policy docs)
│   └── tenant_risk_compliance_dept/ (internal + confidential + restricted policy docs)
├── scripts/
│   ├── demo_1_internal_compliance_copilot.py
│   ├── demo_2_customer_support_assistant.py
│   └── run_attack_simulation.py
├── tests/                     # pytest — PII, injection, isolation, ethics, audit integrity
├── diagrams/architecture.md
├── WALKTHROUGH.md              # live-demo script with timing and talking points
└── CHALLENGES_AND_LEARNINGS.md # obstacles, how they were addressed, recommendations
```

## Honest limitations (see also `app/governance/model_card.py`)

- Retrieval is TF-IDF cosine similarity, not semantic embeddings — it
  misses paraphrased queries. Good enough to demonstrate the guardrail
  architecture; a production system would use a real embedding model
  behind the same `VectorStore.search()` interface.
- The PII and prompt-injection detectors are regex/heuristic demo
  implementations, not certified DLP/safety engines. `scripts/run_attack_simulation.py`
  includes two intentionally-unblocked "known gap" cases to make this
  limitation visible rather than hidden.
- Authentication is simulated (`--user`/`--tenant` flags); there's no real
  login flow. The tenant-isolation guarantees this demo makes are about
  the *data and retrieval layer*, not about credential security.
