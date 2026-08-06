"""One place that wires the whole demo system together: tenants, users,
document ingestion into isolated vector stores, the generator, and the
secure pipeline. Both the CLI and the demo scripts import from here so
there is exactly one source of truth for "how the system is assembled."
"""
from __future__ import annotations

from app.governance.audit_log import AuditLog
from app.rag.generator import get_generator
from app.rag.ingest import ingest_all
from app.rag.pipeline import SecureRAGPipeline
from app.rag.vector_store import TenantVectorRegistry
from app.tenancy import TenantRegistry, build_demo_registry

ALL_TENANT_IDS = [
    "northstar_bank",
    "meridian_bank",
    "retail_banking_dept",
    "risk_compliance_dept",
]


def build_pipeline() -> tuple[SecureRAGPipeline, TenantRegistry]:
    registry = build_demo_registry()
    vector_registry = TenantVectorRegistry()
    counts = ingest_all(vector_registry, ALL_TENANT_IDS)

    generator = get_generator()
    audit_log = AuditLog()
    pipeline = SecureRAGPipeline(registry, vector_registry, generator, audit_log)

    pipeline.ingested_chunk_counts = counts  # attached for display purposes
    return pipeline, registry
