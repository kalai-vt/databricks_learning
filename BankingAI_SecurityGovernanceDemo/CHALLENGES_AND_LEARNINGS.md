# Challenges, Key Learnings & Best Practices

Agenda item 3. These are real obstacles hit while building this demo, not
generic advice — each one changed a design decision in the code.

## 1. "Access denied" and "no relevant information" look identical to a user — but they must not be the same code path

**Problem encountered:** Early on, retrieval used a single relevance
threshold, and RBAC filtering happened by shrinking the candidate set
*before* scoring. That's correct in principle, but with TF-IDF (not
semantic embeddings), a low-clearance role's query would sometimes score a
weak, topically-wrong match against a document it *was* allowed to read
(e.g. a teller's underwriting question weakly matching an unrelated KYC
paragraph), producing a low-confidence "grounded" answer that was actually
noise — while a correctly-scoped, high-clearance query landed a strong
match on the right document.

**How it was addressed:** Tuned `MIN_RELEVANCE_SCORE`
(`app/config.py`) using measured scores across the real demo corpus rather
than a guessed constant, and wrote `tests/test_rag_grounding.py` to pin
the behavior: a role without clearance must get `NO_GROUNDED_ANSWER`, not
a low-confidence guess. This is caught automatically now, not by eyeballing
demo output.

**Recommendation:** Never treat "refuse due to no permission" and "refuse
due to no data" as cosmetically different UI states built on the same
fuzzy-match logic. Test the boundary explicitly, and prefer a system that
says "I don't know" over one that answers timidly.

## 2. Shared mutable state (rate limiter, audit log) breaks a scripted demo in ways that look like real bugs

**Problem encountered:** The rate-limit token bucket is per-`(tenant,
user)`, which is correct for production — but a demo/test harness that
reuses one pipeline instance and one user across many calls silently
drains that same bucket. The attack-simulation script hit this directly:
by the sixth `ask()` call for `cust_ns_01`, requests were being denied by
the rate limiter *before* the prompt-injection scan ever ran, making a
working detector look broken.

**How it was addressed:** Made the rate limiter resettable
per test/demo section (`pipeline.rate_limiter = RateLimiter()`) and were
explicit in each script's narration about *why* a fresh bucket is used —
so the fix is visible, not silently masking the real production behavior.

**Recommendation:** When you build stateful guardrails (rate limits,
session counters, circuit breakers), give your test/demo tooling an
explicit way to reset them. Otherwise your test suite's pass rate depends
on execution order, which is a much worse bug to chase in CI than in a
five-minute local run.

## 3. Regex-based PII/injection detection is a real, bounded tool — say so explicitly, don't oversell it

**Problem encountered:** It's tempting to present a prompt-injection
scanner as "the" defense. It isn't — it's a pattern matcher. Two paraphrased
jailbreak attempts in `scripts/run_attack_simulation.py`
("set aside whatever rules normally apply...", "kindly disregard prior
guidance...") deliberately don't match any of the known patterns, and are
left in the corpus *unscored* rather than quietly excluded.

**How it was addressed:** Rather than expanding the regex list until every
demo case passes (which produces false confidence and an overfit filter),
the gap is documented in the code, the README, and the model card as a
known limitation, with the mitigation being architectural: injection
detection is one layer among several — RBAC-scoped retrieval, grounded-only
generation, and output sanitization all still apply even if a jailbreak
phrase gets past the input filter.

**Recommendation:** In a regulated domain, an undisclosed gap in a control
is worse than the gap itself. Ship the limitation in the model card, not
just in your own head.

## 4. Small regex bugs matter more in redaction than almost anywhere else

**Problem encountered:** An early card-number pattern (`(?:\d[ -]?){13,19}`)
could greedily consume a trailing separator character, so redacting
"card 4111 1111 1111 1111 wants..." produced "card
[REDACTED:CARD_NUMBER]wants..." — cosmetically wrong, and in a real system
a sign that the redaction boundary doesn't precisely match the sensitive
span, which matters if downstream code ever needs to reason about exact
offsets (e.g. for a compliance export).

**How it was addressed:** Tightened the pattern to
`\b\d(?:[ -]?\d){12,18}\b` so the match always starts and ends on a digit.
Added a Luhn-validity check as a second gate so a random 16-digit
reference number isn't mistaken for a card number in the first place
(`tests/test_pii_redaction.py::test_does_not_flag_luhn_invalid_digit_sequence`).

**Recommendation:** Redaction correctness deserves the same span-level
testing rigor as a parser, not just "does the word REDACTED show up
somewhere in the output."

## 5. Tenant isolation is only real if it's structural, not a query filter

**Key learning (validated, not a bug found):** The design choice that
paid off most was giving each tenant its own `VectorStore` instance with
its own index (`app/rag/vector_store.py`), and making
`VectorStore.add_chunks()` raise `ValueError` on a tenant mismatch at
*ingestion* time — plus `TenantRegistry.authorize()` rejecting a mismatched
`(user_id, claimed_tenant_id)` pair before any retrieval code runs at all.
A single shared index with a `WHERE tenant_id = ?`-style filter would have
been fewer lines of code, but a single missed filter anywhere in the
codebase becomes a cross-tenant data leak. With separate store instances,
that class of bug requires two independent mistakes to happen at once.

**Recommendation:** For multi-tenant AI systems in banking, prefer
isolation enforced by *object boundaries* (separate store instances,
separate indexes) over isolation enforced by *query discipline* (a filter
clause someone has to remember to add every time). The former fails
loudly (wrong tenant, empty results, or an explicit exception); the latter
fails silently.

## Recommendations for future projects

1. **Build the audit log first, not last.** It ended up being the cheapest
   part of the system (hash-chained append-only log, ~70 lines) and the
   highest-leverage governance artifact — every other guardrail's behavior
   becomes provable rather than asserted once it logs through one place.
2. **Make guardrail coverage measurable.** A pass/fail table
   (`scripts/run_attack_simulation.py`) over a small, versioned attack
   corpus turns "we have security" into a number that can regress and be
   tracked, and it doubles as a regression test.
3. **Keep the model swappable, keep the controls fixed.** Putting the
   generator behind one small interface (`app/rag/generator.py`) means the
   security/governance/ethics layers don't change when the underlying
   model does — which is the actual governance requirement model-risk
   teams ask for (SR 11-7 style: know what changed, and confirm the
   controls still hold).
4. **Zero-dependency demo code is worth the extra design effort.** Writing
   a from-scratch TF-IDF index instead of pulling in scikit-learn cost
   maybe 30 extra minutes and meant the live demo never depended on
   network access or a `pip install` succeeding in front of an audience.
