from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tenant import Tenant
from app.security.rbac import require_any_authenticated
from app.security.tenant_context import TenantContext
from app.services import tenant_service

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


@router.get("")
def list_tenants(ctx: TenantContext = Depends(require_any_authenticated), db: Session = Depends(get_db)):
    """Demonstrates tenant separation visually. Hospital users (Doctor /
    Hospital Admin) see full detail ONLY for their own tenant; every other
    tenant is shown as a protected, data-free card to make isolation
    obvious without ever leaking another hospital's stats. Super Admin
    (platform-level, no hospital data scope) sees aggregate metadata for
    all tenants but this never bypasses per-hospital patient-data isolation.
    """
    tenants = db.query(Tenant).all()
    result = []
    for tenant in tenants:
        is_own = ctx.tenant_id == tenant.id
        is_super_admin = ctx.role == "SUPER_ADMIN"
        if is_own or is_super_admin:
            stats = tenant_service.tenant_stats(db, tenant.id)
            result.append({**stats, "accessible": True})
        else:
            result.append(
                {
                    "tenant_code": tenant.tenant_code,
                    "tenant_name": tenant.name,
                    "location": tenant.location,
                    "status": tenant.status,
                    "accessible": False,
                    "reason": "Cross-tenant access blocked by TENANT_ISOLATION policy",
                }
            )
    return {"tenants": result, "viewer_tenant_code": ctx.tenant_code, "viewer_role": ctx.role}
