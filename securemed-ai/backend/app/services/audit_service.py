"""Audit and security-event logging.

RULE 8: Log security violations. Every AI request - ALLOW or BLOCK -
generates an audit_logs row. Anything risk-worthy (block, mask, human
review, cross-tenant attempt) also generates a security_events row that
feeds the Security Center.
"""
import json
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.security_event import SecurityEvent


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


def log_security_event(
    db: Session,
    tenant_id: int,
    user_id: int,
    event_type: str,
    severity: str,
    description: str,
    action: str,
) -> SecurityEvent:
    entry = SecurityEvent(
        tenant_id=tenant_id,
        user_id=user_id,
        event_type=event_type,
        severity=severity,
        description=description,
        action=action,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
