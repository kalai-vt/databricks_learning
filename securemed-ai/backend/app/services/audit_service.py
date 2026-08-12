"""Audit logging.

RULE 8: Log security violations. Every AI request — ALLOW or BLOCK —
generates an audit_logs row, giving a single, complete record of what the
governance gateway decided and why.
"""
import json
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_audit(
    db: Session,
    tenant_id: int,
    user_id: int,
    event_type: str,
    action: str,
    request_text: str | None = None,
    policy_code: str | None = None,
    risk_level: str | None = None,
    model: str | None = None,
    details: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        event_type=event_type,
        request_text=request_text,
        policy_code=policy_code,
        risk_level=risk_level,
        action=action,
        model=model,
        details=json.dumps(details) if details else None,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
