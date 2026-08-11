"""Tenant-scoped data access.

RULE 7: Always apply tenant filters server-side. Every function here takes
an explicit tenant_id sourced from the authenticated TenantContext - never
from a caller-supplied argument that traces back to the request body/URL.

Correct pattern used throughout:
    db.query(Patient).filter(Patient.tenant_id == authenticated_tenant_id)
Never:
    db.query(Patient)                      # missing tenant filter
    db.query(Patient).filter(Patient.tenant_id == request.tenant_id)  # trusts client input
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import extract

from app.models.patient import Patient
from app.models.tenant import Tenant
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.security_event import SecurityEvent


def get_tenant_patients(db: Session, tenant_id: int) -> list[Patient]:
    return db.query(Patient).filter(Patient.tenant_id == tenant_id).all()


def count_tenant_patients(db: Session, tenant_id: int) -> int:
    return db.query(Patient).filter(Patient.tenant_id == tenant_id).count()


def count_admissions_this_month(db: Session, tenant_id: int) -> int:
    now = datetime.now(timezone.utc)
    return (
        db.query(Patient)
        .filter(
            Patient.tenant_id == tenant_id,
            extract("year", Patient.admission_date) == now.year,
            extract("month", Patient.admission_date) == now.month,
        )
        .count()
    )


def get_all_tenant_codes(db: Session) -> list[str]:
    return [t.tenant_code for t in db.query(Tenant).all()]


def tenant_stats(db: Session, tenant_id: int) -> dict:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    return {
        "tenant_code": tenant.tenant_code if tenant else None,
        "tenant_name": tenant.name if tenant else None,
        "location": tenant.location if tenant else None,
        "users": db.query(User).filter(User.tenant_id == tenant_id).count(),
        "patients": count_tenant_patients(db, tenant_id),
        "ai_requests": db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id, AuditLog.event_type == "AI_REQUEST").count(),
        "security_events": db.query(SecurityEvent).filter(SecurityEvent.tenant_id == tenant_id).count(),
        "status": tenant.status if tenant else None,
    }
