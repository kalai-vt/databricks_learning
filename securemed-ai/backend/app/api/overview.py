from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.security_event import SecurityEvent
from app.models.tenant import Tenant
from app.security.rbac import require_any_authenticated
from app.security.tenant_context import TenantContext

router = APIRouter(prefix="/api/overview", tags=["overview"])


@router.get("/stats")
def overview_stats(ctx: TenantContext = Depends(require_any_authenticated), db: Session = Depends(get_db)):
    audit_query = db.query(AuditLog).filter(AuditLog.event_type == "AI_REQUEST")
    event_query = db.query(SecurityEvent)
    if ctx.tenant_id is not None:
        audit_query = audit_query.filter(AuditLog.tenant_id == ctx.tenant_id)
        event_query = event_query.filter(SecurityEvent.tenant_id == ctx.tenant_id)

    logs = audit_query.all()
    events = event_query.all()

    action_counts = Counter(l.action for l in logs)
    total = len(logs)
    allowed = action_counts.get("ALLOW", 0)
    blocked = action_counts.get("BLOCK", 0)
    masked = action_counts.get("MASK", 0)
    human_review = action_counts.get("HUMAN_REVIEW", 0)

    cross_tenant_attempts = sum(1 for e in events if e.event_type == "CROSS_TENANT_ACCESS")
    security_events_by_type = Counter(e.event_type for e in events)
    policy_violations = Counter(l.policy_code for l in logs if l.action != "ALLOW")

    tenant_activity = []
    tenants = db.query(Tenant).all()
    for t in tenants:
        if ctx.tenant_id is not None and t.id != ctx.tenant_id:
            continue
        tenant_activity.append({
            "tenant_code": t.tenant_code,
            "tenant_name": t.name,
            "ai_requests": db.query(AuditLog).filter(AuditLog.tenant_id == t.id, AuditLog.event_type == "AI_REQUEST").count(),
        })

    return {
        "current_tenant": ctx.tenant_code,
        "cards": {
            "ai_requests": total,
            "allowed": allowed,
            "blocked": blocked,
            "pii_protected": masked,
            "human_review": human_review,
            "security_events": len(events),
            "cross_tenant_attempts": cross_tenant_attempts,
        },
        "charts": {
            "requests_by_status": [{"name": k, "value": v} for k, v in action_counts.items()],
            "security_events_by_type": [{"name": k, "value": v} for k, v in security_events_by_type.items()],
            "tenant_activity": tenant_activity,
            "policy_violations": [{"name": k, "value": v} for k, v in policy_violations.items()],
        },
        "governance_active": {
            "authentication": True,
            "rbac": True,
            "tenant_isolation": True,
            "pii_protection": True,
            "prompt_security": True,
            "audit_logging": True,
            "response_validation": True,
        },
    }
