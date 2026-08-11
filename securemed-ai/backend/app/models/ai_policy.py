from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class AIPolicy(Base):
    __tablename__ = "ai_policies"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    policy_code = Column(String, nullable=False)  # e.g. TENANT_ISOLATION
    policy_name = Column(String, nullable=False)
    action = Column(String, nullable=False)  # BLOCK | MASK | HUMAN_REVIEW | LOG
    enabled = Column(Boolean, default=True)
    risk_level = Column(String, nullable=False)  # LOW | MEDIUM | HIGH | CRITICAL

    tenant = relationship("Tenant", back_populates="policies")
