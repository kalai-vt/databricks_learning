"""Prompt-injection / jailbreak detection.

Maps to OWASP LLM01: Prompt Injection. This is an input-side heuristic
scanner: pattern-match on known instruction-override phrasing, role-tag
smuggling, and encoding tricks used to hide a payload from a naive filter.

Heuristic scanners like this catch *known* attack phrasing, not everything —
say so explicitly in the walkthrough. The defense-in-depth point is that
this is one layer among several (RBAC-scoped retrieval, output guarding,
grounded-only generation, audit logging); no single layer is assumed
sufficient on its own.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class InjectionFinding:
    pattern_name: str
    matched_text: str


_INJECTION_PATTERNS: dict[str, re.Pattern] = {
    "instruction_override": re.compile(
        r"\b(ignore|disregard|forget)\s+(all\s+|any\s+)?(the\s+|your\s+)?"
        r"(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?)\b",
        re.IGNORECASE,
    ),
    "new_instructions": re.compile(r"\bnew\s+instructions?\s*:", re.IGNORECASE),
    "role_override": re.compile(
        r"\byou\s+are\s+now\s+(a|an)\b|\bact\s+as\s+(an?\s+)?(unfiltered|jailbroken|dan)\b",
        re.IGNORECASE,
    ),
    "system_prompt_exfiltration": re.compile(
        r"\b(reveal|show|print|leak|output)\s+(your|the)\s+(system|hidden|initial)\s+prompt\b",
        re.IGNORECASE,
    ),
    "guardrail_override": re.compile(
        r"\boverride\s+(your|the)\s+(guardrails?|rules?|policy|policies|filters?)\b",
        re.IGNORECASE,
    ),
    "fake_role_tag": re.compile(r"</?\s*(system|assistant|user)\s*>", re.IGNORECASE),
    "dan_jailbreak": re.compile(r"\bDAN\b"),
    "encoded_payload_hint": re.compile(r"\bbase64\s*:", re.IGNORECASE),
    "delimiter_escape": re.compile(r"(-{3,}|`{3,})\s*(end|stop|system)\b", re.IGNORECASE),
}


def scan(text: str) -> list[InjectionFinding]:
    findings: list[InjectionFinding] = []
    for name, pattern in _INJECTION_PATTERNS.items():
        m = pattern.search(text)
        if m:
            findings.append(InjectionFinding(name, m.group(0)))
    return findings


def is_suspicious(text: str) -> bool:
    return len(scan(text)) > 0
