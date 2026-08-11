"""Server-side tenant context derivation.

RULE 1: Never trust a tenant_id supplied by the frontend, a URL, a request
body, a query parameter, or a user prompt.

The ONLY source of truth for "which tenant is this request allowed to
touch" is the authenticated User row loaded from the verified JWT. This
module is the single choke point every data-access path must go through.
"""
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.security.auth import get_current_user


@dataclass
class TenantContext:
    user: User
    tenant: Tenant | None  # None only for platform-level SUPER_ADMIN
    tenant_id: int | None
    tenant_code: str | None
    role: str


def get_tenant_context(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TenantContext:
    if user.role == "SUPER_ADMIN":
        return TenantContext(user=user, tenant=None, tenant_id=None, tenant_code=None, role=user.role)

    if user.tenant_id is None:
        # Defensive: a non-super-admin user must always belong to a tenant.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no tenant assignment")

    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not found")

    return TenantContext(user=user, tenant=tenant, tenant_id=tenant.id, tenant_code=tenant.tenant_code, role=user.role)


def require_tenant_scope(ctx: TenantContext = Depends(get_tenant_context)) -> TenantContext:
    """Use for endpoints that operate on hospital data and therefore require
    a concrete tenant (i.e. excludes the platform-level Super Admin)."""
    if ctx.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform Super Admin has no hospital data scope; this endpoint requires a hospital tenant user",
        )
    return ctx
