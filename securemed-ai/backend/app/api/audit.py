import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.security.rbac import require_any_authenticated, require_hospital_user
from app.security.tenant_context import TenantContext

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs")
def list_audit_logs(
    ctx: TenantContext = Depends(require_any_authenticated),
    db: Session = Depends(get_db),
    risk: str | None = None,
    policy_code: str | None = None,
    action: str | None = None,
    limit: int = 300,
):
    query = db.query(AuditLog)
    if ctx.tenant_id is not None:
        query = query.filter(AuditLog.tenant_id == ctx.tenant_id)
    if risk:
        query = query.filter(AuditLog.risk_level == risk.upper())
    if policy_code:
        query = query.filter(AuditLog.policy_code == policy_code)
    if action:
        query = query.filter(AuditLog.action == action.upper())

    rows = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return {"logs": [_serialize(db, r) for r in rows]}


@router.delete("/logs")
def clear_audit_logs(
    ctx: TenantContext = Depends(require_hospital_user),
    db: Session = Depends(get_db),
):
    """Demo-mode reset: clears this tenant's audit log so a presenter can
    start the scripted narrative from a clean slate. Scoped to the
    authenticated tenant like every other query in this app — it can never
    touch another tenant's history."""
    deleted = db.query(AuditLog).filter(AuditLog.tenant_id == ctx.tenant_id).delete(synchronize_session=False)
    db.commit()
    return {"deleted": deleted}


def _serialize(db: Session, entry: AuditLog) -> dict:
    user = db.query(User).filter(User.id == entry.user_id).first()
    tool_used = None
    if entry.details:
        try:
            tool_used = json.loads(entry.details).get("tool_used") or json.loads(entry.details).get("attempted_tool")
        except (json.JSONDecodeError, AttributeError):
            tool_used = None
    return {
        "id": entry.id,
        "timestamp": entry.timestamp.isoformat(),
        "tenant_code": entry.tenant.tenant_code if entry.tenant else None,
        "user_name": user.name if user else "Unknown",
        "role": user.role if user else None,
        "event_type": entry.event_type,
        "request_text": entry.request_text,
        "policy_code": entry.policy_code,
        "risk_level": entry.risk_level,
        "action": entry.action,
        "model": entry.model,
        "tool_used": tool_used,
    }
