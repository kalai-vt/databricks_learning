"""Role-Based Access Control.

Authorization decisions live here and only here - never in the LLM, never
implied by prompt content. Each route dependency explicitly declares which
roles may call it.
"""
from fastapi import Depends, HTTPException, status

from app.security.tenant_context import TenantContext, get_tenant_context

SUPER_ADMIN = "SUPER_ADMIN"
HOSPITAL_ADMIN = "HOSPITAL_ADMIN"
DOCTOR = "DOCTOR"

ROLE_LABELS = {
    SUPER_ADMIN: "Super Admin",
    HOSPITAL_ADMIN: "Hospital Admin",
    DOCTOR: "Doctor",
}


def require_roles(*allowed_roles: str):
    def dependency(ctx: TenantContext = Depends(get_tenant_context)) -> TenantContext:
        if ctx.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{ROLE_LABELS.get(ctx.role, ctx.role)}' is not permitted to perform this action",
            )
        return ctx

    return dependency


require_any_authenticated = require_roles(SUPER_ADMIN, HOSPITAL_ADMIN, DOCTOR)
require_hospital_user = require_roles(HOSPITAL_ADMIN, DOCTOR)
require_admin = require_roles(SUPER_ADMIN, HOSPITAL_ADMIN)
require_super_admin = require_roles(SUPER_ADMIN)
