from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_code = Column(String, unique=True, index=True, nullable=False)  # e.g. "H1"
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="PROTECTED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="tenant")
    patients = relationship("Patient", back_populates="tenant")
    policies = relationship("AIPolicy", back_populates="tenant")
