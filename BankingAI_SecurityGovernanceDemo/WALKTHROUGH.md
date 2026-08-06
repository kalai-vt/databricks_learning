# Live Walkthrough Script (~20 minutes, code only, no slides)

Terminal setup: two panes/tabs — one for running commands, one you keep
free to open source files (`app/security/pii.py`, `app/ethics/policy.py`,
etc.) when you want to show the code behind a behavior the audience just
saw.

## 0. Orient (1 min)

> "This is Pillar 4 — Security, Governance & Compliance. Instead of
> slides, we built a real AI application for a banking domain that
> demonstrates all five of our topics as running code: standards &
> governance, RAG patterns, OWASP/PII security, ethical AI, and
> multi-tenant isolation. Two solutions, one shared engine."

```bash
cd BankingAI_SecurityGovernanceDemo
python3 -m pytest tests/ -q   # 32 tests, zero dependencies beyond pytest itself
```

> "That's our safety net for the rest of this walkthrough — if I break
> something live, this is what would catch it."

## 1. Solution 1 — Internal Compliance & Policy Co-Pilot (8 min)

```bash
python3 scripts/demo_1_internal_compliance_copilot.py
```

Talking points as each section prints:

- **Sections 1–2 (Governance):** "This is the model card and the
  compliance matrix — not documentation we wrote separately, but data
  structures in `app/governance/` the system can render on demand. Every
  control maps to a named regulation: GDPR, PCI-DSS, ECOA, SOX."
- **Section 3 (RAG):** "A grounded answer with a citation. Open
  `app/rag/pipeline.py` for a second — chunk, embed with TF-IDF, retrieve,
  generate, sanitize, log. No hallucination risk because the generator is
  extractive by default."
- **Sections 4–7 (RBAC / multi-tenant):** "Same question, three different
  roles, three different outcomes — and it's not a permission *filter*
  bolted on top, it's structural: a teller's query never even scores
  against a confidential chunk." Pause on section 6 vs 7 — restricted-tier
  document, only the compliance officer gets it.
- **Section 8 (tenant isolation):** "This is the one to remember: a user
  from one department cannot even *claim* to be another department. It's
  rejected before a single row of data is touched."
- **Section 9 (PII):** "A raw SSN and card number in the query — watch
  what gets logged." Open `app/security/pii.py` briefly, point at the
  Luhn check for card numbers.
- **Section 10 (prompt injection):** "Classic injection attempt, blocked
  before it reaches retrieval or generation."
- **Section 11 (ethical AI):** "This is the one banks actually get sued
  over — refusing a discrimination-adjacent underwriting question outright."
- **Section 12 (audit log):** live-tamper the log in front of the room —
  this is the moment that lands. "I'm mutating history. Watch the
  integrity check flip to invalid."

## 2. Solution 2 — Multi-Brand Customer Support Assistant (7 min)

```bash
python3 scripts/demo_2_customer_support_assistant.py
```

- **Sections 1–2:** same question, two brands, two *correct* different
  answers (different fee schedules) — proves isolation isn't just "deny
  access," it's "serve the right data."
- **Section 3:** brand-spoofing attempt, denied.
- **Section 4:** a customer pastes a real card number mid-conversation —
  this is the realistic case, not a contrived attack.
- **Section 5:** jailbreak attempt (DAN persona), blocked.
- **Section 6:** "Should I invest in crypto?" — refused, out of scope for
  an unlicensed assistant.
- **Section 7:** a fraud report — answered informationally *and* flagged
  for human escalation. "The bot never says 'yes that's fraud, you're
  covered.' That's a human decision, always."
- **Section 8:** rate limiting — burst 7 requests, watch the bucket empty.
- **Section 9:** the full session, still one clean audit trail.

## 3. Attack simulation / measurable coverage (2 min)

```bash
python3 scripts/run_attack_simulation.py
```

> "This is how we made 'we have guardrails' into something measurable
> instead of a claim — a small attack corpus, pass/fail per case. Note the
> two cases marked as a known gap at the bottom — we'll get to those in
> lessons learned."

## 4. Q&A / open the code (2 min)

Good files to have ready if asked "how does X actually work":
- `app/rag/pipeline.py` — the whole orchestration in one place
- `app/security/pii.py` — Luhn check, regex patterns
- `app/governance/audit_log.py` — hash chaining
- `app/ethics/policy.py` — the refusal/escalation rules

## Fallback if live demo fails

Every script's expected output is deterministic and was captured during
development — if something breaks live, say so, then either re-run the
narrower `run_attack_simulation.py` (smaller blast radius) or fall back to
walking through `app/rag/pipeline.py` and `diagrams/architecture.md`
directly. Do not skip the audit-log tamper demo — it's low-risk (12 lines
of deterministic code) and it's the moment that best makes the governance
point.
