"""PII / sensitive-data detection and redaction.

Maps to OWASP LLM06: Sensitive Information Disclosure. We scan text
*before* it is sent to the retriever/generator ("inbound") and again on the
model's answer before it leaves the trust boundary ("outbound") — a model
can echo back PII a user pasted in, so both directions must be checked.

This is a regex/checksum-based demo detector, intentionally dependency-free
so the walkthrough needs no `pip install`. Call out in the live demo that a
production deployment would swap this for a proper DLP/PII engine (e.g.
Microsoft Presidio, AWS Comprehend PII, GCP DLP) behind the exact same
`detect_and_redact()` interface — the guardrail *pipeline* doesn't change,
only the detector implementation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PIIFinding:
    label: str
    value: str
    start: int
    end: int


def _luhn_valid(digits: str) -> bool:
    total = 0
    parity = len(digits) % 2
    for i, ch in enumerate(digits):
        d = int(ch)
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


_PATTERNS: dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "SSN_US": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "PAN_IN": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),  # Indian income-tax PAN
    "IFSC_IN": re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),  # Indian bank branch code
    "CARD_CANDIDATE": re.compile(r"\b\d(?:[ -]?\d){12,18}\b"),
    "ACCOUNT_NUMBER": re.compile(r"\b(?:acc(?:oun)?t\.?\s*#?\s*)(\d{8,17})\b", re.IGNORECASE),
    "PHONE": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"),
}


def find_pii(text: str) -> list[PIIFinding]:
    findings: list[PIIFinding] = []
    claimed_spans: list[tuple[int, int]] = []

    for label, pattern in _PATTERNS.items():
        for m in pattern.finditer(text):
            value = m.group(1) if pattern.groups else m.group(0)
            start, end = m.span()

            if label == "CARD_CANDIDATE":
                digits = re.sub(r"[ -]", "", m.group(0))
                if not (13 <= len(digits) <= 19 and _luhn_valid(digits)):
                    continue
                label_final, value = "CARD_NUMBER", m.group(0)
            else:
                label_final = label

            # Skip overlaps with a span we've already claimed (e.g. don't
            # let PHONE re-match digits already tagged as CARD_NUMBER).
            if any(not (end <= s or start >= e) for s, e in claimed_spans):
                continue

            claimed_spans.append((start, end))
            findings.append(PIIFinding(label_final, value, start, end))

    findings.sort(key=lambda f: f.start)
    return findings


def redact(text: str, findings: list[PIIFinding] | None = None) -> str:
    findings = findings if findings is not None else find_pii(text)
    if not findings:
        return text
    out = []
    cursor = 0
    for f in findings:
        out.append(text[cursor:f.start])
        out.append(f"[REDACTED:{f.label}]")
        cursor = f.end
    out.append(text[cursor:])
    return "".join(out)


def detect_and_redact(text: str) -> tuple[str, list[PIIFinding]]:
    findings = find_pii(text)
    return redact(text, findings), findings
