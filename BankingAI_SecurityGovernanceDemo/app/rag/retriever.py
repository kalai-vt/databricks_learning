"""Thin retrieval wrapper that applies the minimum-relevance grounding
threshold. Below the threshold we treat the query as "not answerable from
the knowledge base" — this is the mechanism behind "refuse rather than
hallucinate."
"""
from __future__ import annotations

from app import config
from app.models import Role, RetrievedChunk
from app.rag.vector_store import VectorStore


def retrieve(store: VectorStore, query: str, role: Role, top_k: int = config.TOP_K) -> list[RetrievedChunk]:
    hits = store.search(query, role=role, top_k=top_k)
    return [h for h in hits if h.score >= config.MIN_RELEVANCE_SCORE]
