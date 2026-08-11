from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.ai_policy import AIPolicy
from app.security.rbac import require_admin, require_hospital_user
from app.security.tenant_context import TenantContext
from app.services.audit_service import log_audit

router = APIRouter(prefix="/api/governance", tags=["governance"])

ETHICAL_AI_PILLARS = [
    {"pillar": "Privacy", "implementation": "PII/PHI detection and masking before data reaches the LLM", "status": "ACTIVE"},
    {"pillar": "Fairness", "implementation": "Protected attributes are kept out of inappropriate automated decision-making workflows", "status": "ACTIVE"},
    {"pillar": "Transparency", "implementation": "Every request shows a full security trace and decision explanation", "status": "ACTIVE"},
    {"pillar": "Accountability", "implementation": "Immutable audit logs for every allowed and blocked request", "status": "ACTIVE"},
    {"pillar": "Safety", "implementation": "Risk classification with automatic high-risk escalation", "status": "ACTIVE"},
    {"pillar": "Human Oversight", "implementation": "High-risk healthcare requests require qualified human review", "status": "ACTIVE"},
    {"pillar": "Security", "implementation": "RBAC, tenant isolation, and prompt-injection defenses enforced server-side", "status": "ACTIVE"},
]


@router.get("/ethical-ai")
def ethical_ai(ctx: TenantContext = Depends(require_hospital_user)):
    return {"pillars": ETHICAL_AI_PILLARS}


@router.get("/policies")
def list_policies(ctx: TenantContext = Depends(require_hospital_user), db: Session = Depends(get_db)):
    rows = db.query(AIPolicy).filter(AIPolicy.tenant_id == ctx.tenant_id).all()
    return {
        "tenant_code": ctx.tenant_code,
        "demo_mode": settings.demo_mode,
        "policies": [
            {
                "policy_code": r.policy_code,
                "policy_name": r.policy_name,
                "action": r.action,
                "enabled": r.enabled,
                "risk_level": r.risk_level,
            }
            for r in rows
        ],
    }


@router.post("/policies/{policy_code}/toggle")
def toggle_policy(
    policy_code: str,
    ctx: TenantContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not settings.demo_mode:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Policy changes are disabled outside demo mode")

    if ctx.tenant_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super Admin views governance read-only across tenants")

    row = db.query(AIPolicy).filter(AIPolicy.tenant_id == ctx.tenant_id, AIPolicy.policy_code == policy_code).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    row.enabled = not row.enabled
    db.commit()

    log_audit(
        db, ctx.tenant_id, ctx.user.id, "POLICY_CHANGE", "LOG",
        request_text=f"Policy '{policy_code}' toggled to {'ENABLED' if row.enabled else 'DISABLED'}",
        policy_code=policy_code, risk_level=row.risk_level, details={"enabled": row.enabled},
    )

    return {"policy_code": row.policy_code, "enabled": row.enabled}
