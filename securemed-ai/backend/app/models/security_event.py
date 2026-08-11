from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)  # CROSS_TENANT_ACCESS, PROMPT_INJECTION, ...
    severity = Column(String, nullable=False)  # LOW | MEDIUM | HIGH | CRITICAL
    description = Column(Text, nullable=False)
    action = Column(String, nullable=False)  # BLOCKED | MASKED | HUMAN_REVIEW | LOGGED
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    tenant = relationship("Tenant")
    user = relationship("User")
