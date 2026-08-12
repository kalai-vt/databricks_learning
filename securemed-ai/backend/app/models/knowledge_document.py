from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class KnowledgeDocument(Base):
    """A tenant-scoped unstructured document (policy/guideline) used by the
    RAG Tool. Represents rows in a per-tenant partition of a vector
    database — retrieval always filters by tenant_id server-side, the same
    way SQL Tool queries enforce row-level security."""

    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)  # POLICY | GUIDELINE | PROTOCOL
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant")
