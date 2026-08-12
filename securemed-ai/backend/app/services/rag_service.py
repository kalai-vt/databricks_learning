"""RAG Tool: tenant-scoped retrieval over unstructured knowledge documents.

This is a deliberately dependency-free stand-in for a real vector database
(e.g. pgvector, Pinecone, a namespaced Chroma/Qdrant collection): documents
are turned into simple term-frequency vectors and ranked by cosine
similarity. The mechanism a production system would use to embed and
search is irrelevant to the security property being demonstrated here —
what matters is the SAME rule as the SQL Tool: the tenant filter is applied
in this function, server-side, from the authenticated tenant_id, and the
query text itself is never trusted to name which tenant's partition to
search.

Correct pattern used below:
    db.query(KnowledgeDocument).filter(KnowledgeDocument.tenant_id == tenant_id)
A real vector DB would express the equivalent as a per-tenant namespace/
collection or a metadata filter (e.g. `filter={"tenant_id": tenant_id}`)
applied before the similarity search runs — never as a post-hoc filter on
results the model already saw.
"""
import math
import re
from collections import Counter

from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _vectorize(text: str) -> Counter:
    return Counter(_TOKEN_RE.findall(text.lower()))


def _cosine_similarity(a: Counter, b: Counter) -> float:
    shared_terms = set(a) & set(b)
    dot_product = sum(a[t] * b[t] for t in shared_terms)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def search_documents(db: Session, tenant_id: int, query: str, top_k: int = 2) -> list[tuple[KnowledgeDocument, float]]:
    # Tenant filter applied here, server-side, before any similarity ranking.
    documents = db.query(KnowledgeDocument).filter(KnowledgeDocument.tenant_id == tenant_id).all()
    query_vector = _vectorize(query)

    scored = [
        (doc, _cosine_similarity(query_vector, _vectorize(f"{doc.title} {doc.content}")))
        for doc in documents
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    ranked = [(doc, score) for doc, score in scored if score > 0][:top_k]

    # Fall back to the top documents even with weak lexical overlap, so a
    # generic "what's our policy?" question still returns this tenant's
    # documents rather than nothing.
    if not ranked and documents:
        ranked = [(doc, 0.0) for doc in documents[:top_k]]
    return ranked
