# Live Walkthrough Script (~20–25 minutes, no slides)

Two surfaces, one engine — use both, don't pick one:

- **Browser console** (`web/banking_ai_console.html`, or the published artifact link) — what
  the room *watches*. Click a scenario chip, the guardrail trace and audit log update live.
  No terminal typing, no risk of a typo mid-sentence.
- **Python source / editor** (`app/`) — what makes it a *code walkthrough*, not a UI demo.
  Every behavior the console shows is ~10–20 lines of real code; open the file right after
  the click that triggered it.

## Setup (before the room fills up)

- Browser: console open, **Console tab**, persona = "Alex — NorthStar customer", tenant =
  NorthStar Bank. Zoom the browser to ~125% so trace text reads from the back row.
- Editor: `BankingAI_SecurityGovernanceDemo/app/` open, with tabs pre-opened for
  `rag/pipeline.py`, `tenancy.py`, `security/pii.py`, `security/prompt_injection.py`,
  `ethics/policy.py`, `governance/audit_log.py` — so you switch tabs, not search files, live.
  If you're worried about the internet, use the local `web/banking_ai_console.html` file
  (double-click it, works with zero install) instead of the hosted artifact link.
- Terminal: idle, `cd BankingAI_SecurityGovernanceDemo`, ready for the pytest fallback.

## 0. Orient (1 min)

> "This is Pillar 4 — Security, Governance & Compliance. Instead of slides, this is a real
> banking AI application: two solutions, one shared guardrail engine, covering all five of
> our topics as running code. We'll drive it live — every click on screen is backed by
> Python you can read right after."

## 1. The two solutions — problem, approach, impact (3–4 min, spoken over the console)

Point at the **Governance tab** (model card) while you say this — it's your only "slide,"
and it's real data, not a deck.

- **Solution 1 — Internal Compliance & Policy Co-Pilot.** Compliance officers, risk
  analysts, and tellers need instant, trustworthy answers to policy questions (KYC/AML,
  underwriting, fraud response) without emailing compliance and without risking a
  hallucinated answer being treated as policy. Impact: seconds instead of a day, and every
  answer is traceable and auditable by design.
- **Solution 2 — Multi-Brand Customer Support Assistant.** One platform serving multiple
  white-label bank brands (NorthStar, Meridian) — customers paste real account/card numbers
  and fraud complaints straight into chat, so this sits directly on the OWASP LLM attack
  surface. Impact: one platform can safely serve multiple brands/subsidiaries without a
  cross-tenant leak or a jailbroken bot becoming a headline.

## 2. Live console walkthrough + code (12–15 min)

Work down the **scenario chips** in this order. After each click, say the one-liner, then
(for the starred ⭐ ones) flip to the matching file for 15–20 seconds — don't read code
line by line, just point at the function name and the one line that matters.

| # | Chip / action | What it proves | ⭐ Code to flash |
|---|---|---|---|
| 1 | **Overdraft fee** (as NorthStar customer) | Grounded RAG answer with a citation — no hallucination | ⭐ `rag/generator.py` — extractive, cites the chunk |
| 2 | Switch persona to Jamie (Meridian), click **Overdraft fee** again | Same question, two brands, two *correct* different answers — isolation serves the right data, not just denies | — |
| 3 | **Cross-tenant impersonation** chip | Denied outright, before any data is touched | ⭐ `tenancy.py` → `authorize()` |
| 4 | Switch persona to Sam (Teller), click **Underwriting factors (RBAC test)** | Refuses — not because of a bug, because of clearance | ⭐ `models.py` → `role_can_read()` |
| 5 | Switch persona to Dana (Retail risk analyst), same chip again | Same tenant, same document, different role → grounded answer | — |
| 6 | Switch to Morgan (Compliance officer @ Risk & Compliance dept), click **Exam findings (restricted tier)** | Only the top clearance tier can read a RESTRICTED doc | — |
| 7 | **Prompt injection attempt** chip | Blocked before it reaches retrieval or generation | ⭐ `security/prompt_injection.py` |
| 8 | **Paste sensitive info (PII)** chip | SSN + card number redacted *before* being used or logged — point at the "Rate budget" ticking down too, that's the OWASP LLM04 control | ⭐ `security/pii.py` — Luhn check on the card |
| 9 | **Discrimination question** chip | Refused outright — the one banks actually get sued over | ⭐ `ethics/policy.py` |
| 10 | **Fraud report (escalation)** chip | Answered informationally *and* flagged for a human — the bot never confirms fraud itself | — |
| 11 | Open the **Audit log** drawer, click the most recent entry, hit **"Tamper: flip allowed,"** then **Verify integrity** | The moment that lands: mutate history live, watch the hash chain catch it | ⭐ `governance/audit_log.py` — hash-chain in ~25 lines |

Then:
- **Governance tab** — scroll the compliance matrix: "every control on the left maps to a
  named regulation on the right — GDPR, PCI-DSS, ECOA, SOX, EU AI Act."
- **Attack Simulation tab** — click **Run attack simulation**: "this is how 'we have
  guardrails' becomes measurable instead of a claim. 7/7 known cases, and two intentionally
  left unblocked — we'll get to those in a second."

## 3. Challenges, learnings, best practices (3–5 min)

Don't read `CHALLENGES_AND_LEARNINGS.md` — pick three real ones and tell them as stories:

1. **RBAC vs. TF-IDF false positives.** A teller's ungrounded query was weakly matching the
   *wrong* internal document instead of cleanly refusing — tuned the relevance threshold
   against measured scores, then wrote a test to pin the boundary so it can't regress.
2. **The two intentionally-unblocked injection cases.** A regex/heuristic scanner catches
   *known* attack phrasing, not everything — say so in the model card instead of hiding it.
   The mitigation is architectural (RBAC-scoped retrieval, grounded-only generation, output
   guard), not "add more regexes until the demo passes."
3. **Structural isolation beat query-filter isolation.** Each tenant gets its own store
   instance, not a shared index with a `WHERE tenant_id = ?` filter — a missed filter
   anywhere becomes a leak; a missing store instance just fails loudly.

Best-practice takeaway: **build the audit log first, not last** — it ended up being the
cheapest part of the system and the highest-leverage governance artifact, because every
other guardrail's behavior becomes provable, not just asserted.

## 4. Close (1 min)

> "Five topics, one afternoon of clicking: standards & governance in the model card and
> compliance matrix, RAG patterns in the citation-backed answers, OWASP/PII in the redaction
> and injection blocks, ethical AI in the refusals and escalations, and multi-tenant
> isolation in every impersonation attempt that got denied. Questions?"

## Fallback if something breaks live

- Browser console frozen/won't load → open the local file directly
  (`web/banking_ai_console.html`) instead of the hosted link; it's fully self-contained.
- Browser unusable at all → fall back to the terminal:
  `python3 scripts/demo_1_internal_compliance_copilot.py` and
  `python3 scripts/demo_2_customer_support_assistant.py` print the identical scenarios as
  formatted text, plus `python3 -m pytest tests/ -q` as your "it actually works" safety net.
- Don't skip the audit-log tamper demo even under time pressure — it's the single moment
  that best makes the governance point, and it's ~10 seconds either way.
