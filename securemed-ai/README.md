# SecureMed AI

**Ethical AI & Multi-Tenant Security Governance Platform — Demonstration**

> DEMO ENVIRONMENT — SYNTHETIC HEALTHCARE DATA — NOT FOR MEDICAL USE

This is a **Security Governance & Ethical AI Demonstration using synthetic healthcare data.**
It is not a medical device, not a diagnostic tool, and is not claimed to be HIPAA, GDPR, or
DPDP compliant, or medically certified.

---

## 1. Product Overview

SecureMed AI is a fictional multi-hospital healthcare SaaS platform used to demonstrate how a
**shared AI system can safely serve multiple tenants** (hospitals) without ever leaking one
tenant's data to another, while remaining transparent, auditable, and governed.

Two demo tenants are pre-seeded:

| Tenant | Name | Location | Users |
|---|---|---|---|
| `H1` | H1 Hospital | Chennai | Dr. Arun (Doctor), Priya / Kumar (Hospital Admin) |
| `H2` | H2 Hospital | Bengaluru | Dr. Meera (Doctor), Ravi (Hospital Admin) |

Plus one platform-level `Super Admin` with no hospital data scope.

## 2. Business Problem

*"How can a healthcare SaaS platform safely provide AI capabilities to multiple hospitals while
preventing unauthorized access, protecting sensitive patient information, detecting unsafe AI
requests, enforcing governance policies, and maintaining complete auditability?"*

H1 must never be able to see H2's data, and vice versa — even though both hospitals share the
same application, database, and LLM.

## 3. Ethical AI

The **Governance** page's "Ethical AI Pillars" tab demonstrates seven pillars, each backed by a
concrete implementation, not just a policy statement:

| Pillar | Implementation |
|---|---|
| Privacy | PII/PHI detection and masking before any data reaches the LLM |
| Fairness | Protected attributes kept out of inappropriate automated decisions |
| Transparency | Every request shows a full security trace + decision explanation |
| Accountability | Immutable audit logs for every allowed and blocked request |
| Safety | Risk classification with automatic high-risk escalation |
| Human Oversight | High-risk healthcare requests require qualified human review |
| Security | RBAC, tenant isolation, and prompt-injection defenses, enforced server-side |

## 4. Multi-Tenant Isolation

**Core principle: security must not depend on the LLM.** Tenant identity is derived exclusively
from the authenticated user's JWT — never from the frontend, a URL, a request body, a query
parameter, or (critically) the free-text AI prompt itself. Every patient-data query is filtered
server-side with `WHERE tenant_id = authenticated_tenant_id`. See the **Architecture** page for a
side-by-side "Bad Approach vs. Secure Approach" diagram.

## 5. Architecture

```
USER
  |
Authentication / JWT
  |
Tenant Context (server-derived, never client-supplied)
  |
RBAC
  |
AI GOVERNANCE GATEWAY
  +-- PII/PHI Detection
  +-- Prompt Injection Detection
  +-- Risk Classification
  +-- Policy Engine
  +-- Tenant Isolation
  |
Tenant-Scoped Database
  |
Minimum Required Context
  |
LLM PROVIDER (model-agnostic)
  |
Response Validation
  |
Audit Log
  |
USER
```

Every one of these stages runs in deterministic backend code **before** the LLM is ever called.
Blocked and human-review requests never reach the LLM at all.

## 6. Technology Stack

**Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide React icons, Recharts, React Router.
**Backend:** Python, FastAPI, Pydantic, SQLAlchemy, python-jose (JWT), Passlib/bcrypt, SQLite.

## 7. Database Schema

- `tenants` — id, tenant_code, name, location, status, created_at
- `users` — id, tenant_id (nullable for Super Admin), name, email, role, password_hash, status, created_at
- `patients` — id, tenant_id, patient_code, name, age, gender, email, phone, city, condition, admission_date, created_at
- `ai_policies` — id, tenant_id, policy_code, policy_name, action, enabled, risk_level
- `audit_logs` — id, tenant_id, user_id, event_type, request_text, policy_code, risk_level, action, model, details, timestamp
- `security_events` — id, tenant_id, user_id, event_type, severity, description, action, timestamp

SQLite is used for this local demo; the schema uses portable SQLAlchemy constructs so migrating to
PostgreSQL/MySQL later is a connection-string change, not a rewrite.

## 8. Security Model

- **RULE 1–2:** Never trust `tenant_id` from the frontend, URL, request body, query params, or prompt.
- **RULE 3:** The LLM never determines authorization — every ALLOW/BLOCK/MASK/HUMAN_REVIEW decision
  is made by deterministic backend code before the LLM is invoked.
- **RULE 4–5:** API keys and database credentials are never exposed to the frontend or the LLM prompt.
- **RULE 6–7:** System prompts are not a security boundary; tenant filters are applied server-side on
  every query.
- **RULE 8–10:** Security violations are logged; sensitive data is minimized before reaching the LLM;
  LLM output is re-validated before being shown to the user.
- **RULE 11–12:** Only synthetic data is used; high-risk healthcare requests require human review.

See the **Security Center** page for the full control list and live security event feed.

## 9. Governance Model

Each tenant has seven independently toggleable policies (`TENANT_ISOLATION`, `PHI_PROTECTION`,
`AI_INPUT_SECURITY`, `HIGH_RISK_HEALTHCARE`, `CROSS_TENANT_ACCESS`, `AUDIT_LOGGING`,
`SENSITIVE_EXPORT`). Hospital Admins can toggle policies in demo mode; every change is itself an
audited event. Doctors have read-only visibility.

## 10. LLM Architecture

`backend/app/services/llm/base.py` defines the model-agnostic `LLMProvider` interface
(`generate_response`, `generate_with_context`, `get_model_name`, `get_provider_name`, `is_mock`).
`openai_provider.py` implements it for GPT-4o-mini via the OpenAI API. Nothing in governance, RBAC,
tenant isolation, PII protection, or audit logging imports an LLM SDK directly — everything goes
through this interface, so adding `ClaudeProvider`, `GeminiProvider`, or `LocalProvider` later never
touches security code.

## 11. Why GPT-4o-mini for the Prototype

Cost-effective, fast, sufficient capability for a structured conversational workflow, and a good fit
for a local proof-of-concept that gets run repeatedly during demos. **This is not a claim that
GPT-4o-mini is the most secure or best LLM on the market** — it is simply a practical choice for this
prototype. The governance architecture is model-agnostic.

## 12. Future LLM Replacement

Set `LLM_PROVIDER=anthropic|gemini|local` in `.env` once those providers are implemented (only
`openai` is implemented today). Swapping providers requires no changes to tenant isolation, RBAC,
PII protection, audit logging, or any other security control.

## 13. Installation

### Prerequisites
- Python 3.11+
- Node.js 18+

### Clone / navigate
```
cd securemed-ai
```

## 14. Environment Setup

```
cp .env.example backend/.env
```
Edit `backend/.env` if you have a real OpenAI API key. If you leave `OPENAI_API_KEY` blank (or set
`MOCK_LLM=true`), the app runs in deterministic **Mock/Demo LLM mode** — the full governance and
security pipeline still runs and blocks/masks/escalates exactly the same way; only the final
natural-language answer is a canned demo string instead of a real GPT-4o-mini completion. This
guarantees a live presentation never fails due to a missing key, network issue, or quota problem.

## 15. Backend Startup

**Windows:**
```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**macOS / Linux:**
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The database is created and seeded automatically on first startup (SQLite file `securemed.db`).
API docs: http://localhost:8000/docs

## 16. Frontend Startup

```
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 — the Vite dev server proxies `/api` to the backend on port 8000.

## 17. Demo Credentials

| Hospital | Email | Password | Role |
|---|---|---|---|
| H1 Hospital | `arun@h1.demo` | `Demo@123` | Doctor |
| H2 Hospital | `meera@h2.demo` | `Demo@123` | Doctor |
| H1 Admin | `priya@h1.demo` | `Demo@123` | Hospital Admin |
| Platform Admin | `admin@securemed.demo` | `Demo@123` | Super Admin |

(Additional seeded accounts: `kumar@h1.demo` and `ravi@h2.demo`, both Hospital Admin, `Demo@123`.)

Passwords are stored using bcrypt hashing — never in plaintext.

## 18. Guided Demo

The **Guided Demo** page runs five one-click scenarios end-to-end (request → governance decision →
security trace → audit record):

1. Normal Request → **ALLOW**
2. Cross-Tenant Request → **BLOCK**
3. PII Request → **MASK**
4. Prompt Injection → **BLOCK**
5. High-Risk Healthcare Request → **HUMAN REVIEW**

Use **Presentation Mode** (top bar) to hide the sidebar and enlarge text for projector use.

## 19. Security Limitations (this demo)

This is a local demonstration, not a production system. Known limitations:
- Single shared JWT secret, no MFA/SSO/OAuth
- No rate limiting, WAF, or DLP
- SQLite, no encryption at rest
- PII/PHI and prompt-injection detection are deterministic pattern/keyword based, not ML-based —
  sufficient to reliably demonstrate the five scripted scenarios, not exhaustive real-world coverage
- No centralized logging/SIEM integration
- Single-process app, no horizontal scaling / multi-region considerations

## 20. Production Recommendations

For a real deployment, evaluate: enterprise identity provider, MFA, OAuth/OIDC, a secrets manager,
encryption at rest and in transit, PostgreSQL with row-level security where appropriate, an API
gateway, WAF, rate limiting, DLP, centralized logging, SIEM, security monitoring, model evaluation,
red-team testing, prompt-injection testing, vulnerability scanning, backup, disaster recovery,
incident response, compliance review, vendor risk assessment, and a data residency assessment.

## 21. SaaS Use Cases

See the in-app **SaaS Use Cases** page for the "Prototype → SaaS" tenant model (each hospital gets
its own users, roles, patient data, AI conversations, policies, audit logs, and usage metrics on a
shared platform providing AI Gateway, Governance, Model Management, Security Monitoring, Audit,
Billing, and Tenant Management).

## 22. India Use Cases

Primary: healthcare (hospital AI assistants, hospital analytics, patient support, medical
documentation assistance, healthcare operations). Also applicable to banking, insurance, education,
HR, and general enterprise SaaS (CRM/ERP/BI/customer support AI). **This prototype is not itself
legally compliant** — any production deployment in India must evaluate applicable DPDP Act,
sector-specific, contractual, security, data residency, and governance requirements.

---

## Project Structure

```
securemed-ai/
  frontend/          React + Vite + TypeScript + Tailwind
    src/components/  Layout, TopBar, NavSidebar, SecurityTrace, ActionBadge, StatCard
    src/pages/        Login, Overview, AIAssistant, Tenants, Governance, SecurityCenter,
                       AuditLogs, ModelPage, Architecture, GuidedDemo, SaaSUseCases
    src/services/     api.ts (fetch wrapper, JWT header injection)
    src/hooks/        useAuth, usePresentationMode
  backend/
    app/
      main.py, config.py, database.py, seed.py
      models/          SQLAlchemy models
      schemas/         Pydantic request/response schemas
      security/        auth.py, rbac.py, tenant_context.py
      services/
        llm/           base.py (LLMProvider), openai_provider.py, factory.py
        governance_service.py, pii_service.py, risk_service.py,
        tenant_service.py, audit_service.py
      api/             auth, ai, tenants, governance, security_center, audit,
                        model_config, overview routers
    tests/             pytest suite (auth, RBAC, tenant isolation, PII, prompt
                        injection, governance, audit, LLM)
  .env.example
  .gitignore
```

## Running Tests

```
cd backend
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
python -m pytest -v
```

All 38 tests cover: valid/invalid login, H1↔H2 tenant isolation, RBAC per role, PII detection and
masking, prompt-injection detection and blocking, policy enable/disable behavior, audit logging for
both allowed and blocked requests, and LLM provider loading (including mock mode).
