from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.security_event import SecurityEvent
from app.models.user import User
from app.security.rbac import require_any_authenticated
from app.security.tenant_context import TenantContext

router = APIRouter(prefix="/api/security", tags=["security"])


@router.get("/events")
def list_security_events(
    ctx: TenantContext = Depends(require_any_authenticated),
    db: Session = Depends(get_db),
    limit: int = 200,
):
    query = db.query(SecurityEvent)
    if ctx.tenant_id is not None:
        # Hospital users (Doctor / Hospital Admin) only ever see their own tenant.
        query = query.filter(SecurityEvent.tenant_id == ctx.tenant_id)
    # else: platform Super Admin may view cross-tenant security events
    # (this is a monitoring/reporting view — it never grants access to
    # another tenant's underlying patient data).
    rows = query.order_by(SecurityEvent.timestamp.desc()).limit(limit).all()
    return {"events": [_serialize(db, e) for e in rows]}


def _serialize(db: Session, event: SecurityEvent) -> dict:
    user = db.query(User).filter(User.id == event.user_id).first()
    tenant_code = event.tenant.tenant_code if event.tenant else None
    return {
        "id": event.id,
        "timestamp": event.timestamp.isoformat(),
        "tenant_code": tenant_code,
        "tenant_name": event.tenant.name if event.tenant else None,
        "user_name": user.name if user else "Unknown",
        "event_type": event.event_type,
        "severity": event.severity,
        "action": event.action,
        "description": event.description,
    }
