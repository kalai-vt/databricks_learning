from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)  # AI_REQUEST, POLICY_CHANGE, LOGIN, ...
    request_text = Column(Text, nullable=True)
    policy_code = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)
    action = Column(String, nullable=False)  # ALLOW | BLOCK | MASK | HUMAN_REVIEW | LOG
    model = Column(String, nullable=True)
    details = Column(Text, nullable=True)  # JSON-serialized extra context
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    tenant = relationship("Tenant")
    user = relationship("User")
