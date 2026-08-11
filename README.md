# databricks_learning
Learning Demos and Documents

## Projects

- [`UnityCatalogDemo/`](./UnityCatalogDemo/) — a complete, hands-on Databricks Unity Catalog demo
  built around a fictional retail company (RetailCorp) with Sales, HR, and Finance departments.
  Includes 13 SQL notebooks, standalone SQL scripts, sample CSV datasets, a security/RBAC demo, a
  data lineage walkthrough, ASCII architecture diagrams, interview questions, a presenter script,
  and PowerPoint slide content — everything needed for a 45–60 minute live technical session.
  Start at [`UnityCatalogDemo/README.md`](./UnityCatalogDemo/README.md).

- [`securemed-ai/`](./securemed-ai/) — SecureMed AI, a runnable Ethical AI & Multi-Tenant Security
  Governance demo: a fictional healthcare SaaS platform (React/Vite/TypeScript frontend, FastAPI
  backend) showing two hospital tenants (H1, H2) sharing an AI assistant while a governance gateway
  enforces JWT auth, RBAC, server-side tenant isolation, PII/PHI masking, prompt-injection detection,
  risk-based human review, and full audit logging — all before any request reaches the LLM. Uses only
  synthetic data; ships with a Mock LLM mode so the demo works with no OpenAI API key. Start at
  [`securemed-ai/README.md`](./securemed-ai/README.md).
