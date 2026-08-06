"""Terminal pretty-printing for QueryResult, used by both the CLI and the
demo scripts so a live walkthrough shows a consistent, readable trace of
every guardrail that fired.
"""
from __future__ import annotations

from app.models import QueryResult

_SEVERITY_ICON = {"info": "ℹ️ ", "warning": "⚠️ ", "critical": "🚫"}
_WIDTH = 78


def _rule(char: str = "─") -> str:
    return char * _WIDTH


def print_result(result: QueryResult, actor_label: str) -> None:
    print(_rule("═"))
    print(f"[{actor_label}] tenant={result.tenant_id}  user={result.user_id}  "
          f"role={result.role.value if result.role else '—'}")
    print(f"Query: {result.original_query}")
    print(_rule())

    if result.events:
        print("Guardrail trace:")
        for e in result.events:
            icon = _SEVERITY_ICON.get(e.severity, "•")
            print(f"  {icon} [{e.event_type}] {e.detail}")
        print(_rule())

    status = "ALLOWED" if result.allowed else "BLOCKED/REFUSED"
    print(f"Status: {status}" + ("  |  ⤴ ESCALATED TO HUMAN REVIEW" if result.escalate_to_human else ""))
    print()
    print(result.answer)
    if result.citations:
        print()
        print("Sources: " + ", ".join(result.citations))
    print(f"\n(latency: {result.latency_ms:.1f} ms)")
    print(_rule("═"))
    print()
