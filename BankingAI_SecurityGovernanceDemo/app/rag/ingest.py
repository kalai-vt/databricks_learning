"""Loads sample banking documents from data/tenant_<id>/ into tenant-scoped
vector stores.

Sensitivity is inferred from a front-matter line at the top of each
document (`sensitivity: internal`, etc.) so the demo corpus can express
RBAC without a separate manifest file. Defaults to PUBLIC if omitted.
"""
from __future__ import annotations

from pathlib import Path

from app.models import Document, SensitivityLevel, new_id
from app.rag.chunking import chunk_document
from app.rag.vector_store import TenantVectorRegistry

DATA_ROOT = Path(__file__).resolve().parent.parent.parent / "data"

_FRONT_MATTER_PREFIX = "sensitivity:"


def _parse_document(path: Path, tenant_id: str) -> Document:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    sensitivity = SensitivityLevel.PUBLIC

    if lines and lines[0].lower().startswith(_FRONT_MATTER_PREFIX):
        value = lines[0].split(":", 1)[1].strip().lower()
        try:
            sensitivity = SensitivityLevel(value)
        except ValueError:
            sensitivity = SensitivityLevel.PUBLIC
        body = "\n".join(lines[1:])
    else:
        body = raw

    title_line = next((l.lstrip("# ").strip() for l in body.splitlines() if l.strip()), path.stem)

    return Document(
        doc_id=new_id("doc"),
        tenant_id=tenant_id,
        title=title_line,
        source_path=str(path.relative_to(DATA_ROOT)),
        sensitivity=sensitivity,
        text=body,
    )


def load_tenant_documents(tenant_id: str) -> list[Document]:
    tenant_dir = DATA_ROOT / f"tenant_{tenant_id}"
    if not tenant_dir.is_dir():
        raise FileNotFoundError(f"No data directory for tenant '{tenant_id}': {tenant_dir}")
    docs = []
    for path in sorted(tenant_dir.glob("*.md")):
        docs.append(_parse_document(path, tenant_id))
    return docs


def ingest_tenant(vector_registry: TenantVectorRegistry, tenant_id: str) -> int:
    """Loads, chunks, and indexes one tenant's documents. Returns chunk count."""
    store = vector_registry.get_or_create(tenant_id)
    total = 0
    for doc in load_tenant_documents(tenant_id):
        chunks = chunk_document(doc)
        store.add_chunks(chunks)
        total += len(chunks)
    return total


def ingest_all(vector_registry: TenantVectorRegistry, tenant_ids: list[str]) -> dict[str, int]:
    return {tenant_id: ingest_tenant(vector_registry, tenant_id) for tenant_id in tenant_ids}
