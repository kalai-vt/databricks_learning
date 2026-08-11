from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ai import ChatRequest, ChatResponse
from app.security.rbac import require_hospital_user
from app.security.tenant_context import TenantContext
from app.services.governance_service import process_ai_request

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    ctx: TenantContext = Depends(require_hospital_user),
    db: Session = Depends(get_db),
):
    """Every AI request passes through the SecureMed AI Governance Gateway.
    tenant_id is taken exclusively from `ctx` (derived server-side from the
    JWT) — the request body only ever carries the free-text message.
    """
    return process_ai_request(db, ctx, payload.message)
