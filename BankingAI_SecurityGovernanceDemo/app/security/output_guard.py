"""Output-side guardrail.

Maps to OWASP LLM02: Insecure Output Handling. Even a fully grounded,
template-based answer must not be trusted blindly downstream (e.g. if the
answer is later rendered in a web UI or an internal ticketing system) — so
we strip markup/script-bearing content, cap length, and re-run PII
detection in case retrieved context or a plugged-in LLM echoed something
sensitive back.
"""
from __future__ import annotations

import re

from app.security.pii import find_pii, redact

_TAG_RE = re.compile(r"<[^>]+>")
_MAX_ANSWER_CHARS = 4000


def sanitize_output(text: str) -> tuple[str, list[str]]:
    """Returns (clean_text, notes) where notes describes what was changed."""
    notes: list[str] = []

    stripped = _TAG_RE.sub("", text)
    if stripped != text:
        notes.append("stripped_html_or_markup_tags")
    text = stripped

    if len(text) > _MAX_ANSWER_CHARS:
        text = text[:_MAX_ANSWER_CHARS] + " …[truncated]"
        notes.append("truncated_over_length_cap")

    findings = find_pii(text)
    if findings:
        text = redact(text, findings)
        notes.append(f"redacted_{len(findings)}_pii_item(s)_in_output")

    return text, notes
