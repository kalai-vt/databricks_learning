"""Ethical AI decisioning.

Three concerns, each with a distinct failure mode a banking AI assistant
must not have:

1. Non-discrimination — never let the assistant reason about, or appear to
   condition an outcome on, a protected attribute (ECOA/Reg B in the US,
   RBI Fair Practices Code, EU AI Act Art. 5 prohibited-practice framing).
2. Unlicensed financial advice — a support/policy assistant is not a
   registered investment adviser; it must not give personalized buy/sell/
   invest guidance.
3. Human-in-the-loop for high-stakes topics — credit decisions and fraud
   allegations affect real financial outcomes, so the assistant answers
   informationally and *always* routes to a human for the actual decision.

The policy runs on the *query*, before retrieval, so a refusal never even
touches tenant data — and again conceptually applies to the answer via the
"always disclose AI + escalate" rule enforced in the pipeline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class EthicsAction(str, Enum):
    ALLOW = "allow"
    REFUSE = "refuse"
    ESCALATE = "escalate"  # answer informationally, but flag for human follow-up


@dataclass(frozen=True)
class EthicsDecision:
    action: EthicsAction
    reason: str | None = None


_PROTECTED_ATTR_TERMS = [
    "religion", "religious", "caste", "race", "ethnicity", "national origin",
    "gender", "sex", "sexual orientation", "disability", "age", "marital status",
]

_DISCRIMINATION_PATTERNS = [
    re.compile(
        r"\b(deny|reject|decline|approve|favor)\b.{0,40}\b(loan|credit|account|mortgage|card)\b.{0,40}\b("
        + "|".join(_PROTECTED_ATTR_TERMS) + r")\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bonly\s+(approve|lend|offer)\b.{0,40}\b(" + "|".join(_PROTECTED_ATTR_TERMS) + r")\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(" + "|".join(_PROTECTED_ATTR_TERMS) + r")\b.{0,40}\b(credit\s*score|loan\s*eligibility|interest\s*rate)\b",
        re.IGNORECASE,
    ),
]

_FINANCIAL_ADVICE_PATTERNS = [
    re.compile(r"\bshould\s+i\s+(invest|buy|sell|short)\b", re.IGNORECASE),
    re.compile(r"\b(guaranteed|guarantee)\s+returns?\b", re.IGNORECASE),
    re.compile(r"\bbest\s+(stock|crypto|fund|coin)\s+to\s+buy\b", re.IGNORECASE),
    re.compile(r"\bwhich\s+stock\s+should\s+i\s+pick\b", re.IGNORECASE),
]

_HIGH_STAKES_PATTERNS = {
    "credit_decision": re.compile(r"\b(loan|credit|mortgage)\s+(denied|rejection|decline)\b", re.IGNORECASE),
    "fraud_allegation": re.compile(r"\bfraud(ulent)?\b|\bunauthorized\s+(transaction|charge)\b", re.IGNORECASE),
    "account_closure": re.compile(r"\bclose\s+my\s+account\b|\baccount\s+(frozen|suspended)\b", re.IGNORECASE),
}


def evaluate(query: str) -> EthicsDecision:
    for pattern in _DISCRIMINATION_PATTERNS:
        if pattern.search(query):
            return EthicsDecision(
                EthicsAction.REFUSE,
                "Request appears to condition a banking decision on a protected attribute; "
                "refusing per non-discrimination policy (ECOA/Reg B, RBI Fair Practices Code).",
            )

    for pattern in _FINANCIAL_ADVICE_PATTERNS:
        if pattern.search(query):
            return EthicsDecision(
                EthicsAction.REFUSE,
                "Request asks for personalized investment/trading advice, which is out of scope "
                "for an unlicensed policy/support assistant.",
            )

    for label, pattern in _HIGH_STAKES_PATTERNS.items():
        if pattern.search(query):
            return EthicsDecision(
                EthicsAction.ESCALATE,
                f"High-stakes topic detected ({label}); answer will be informational only and "
                "routed to a human for the actual decision/action.",
            )

    return EthicsDecision(EthicsAction.ALLOW)
