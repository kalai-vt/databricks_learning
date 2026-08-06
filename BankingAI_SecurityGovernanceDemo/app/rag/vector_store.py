"""Tenant-isolated vector stores.

Each `VectorStore` instance owns exactly one tenant's chunks and its own
`TfidfIndex`. `TenantVectorRegistry` maps tenant_id -> VectorStore, and
that mapping is the *only* way to reach a store — there is no global
"search everything" index anywhere in this codebase. Combined with
`TenantRegistry.authorize()` (app/tenancy.py) validating that the caller's
user_id truly belongs to the claimed tenant_id, cross-tenant retrieval
requires a bug in two independent places at once, not one.

RBAC (role -> sensitivity clearance) is enforced *inside* the same
`search()` call, before ranking, by restricting the TF-IDF candidate set —
a low-privilege role's query never even scores against a chunk it isn't
cleared to see.
"""
from __future__ import annotations

from app.models import Chunk, Role, RetrievedChunk, role_can_read
from app.rag.tfidf import TfidfIndex


class VectorStore:
    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        self._chunks: dict[str, Chunk] = {}
        self._index = TfidfIndex()

    def add_chunks(self, chunks: list[Chunk]) -> None:
        for chunk in chunks:
            if chunk.tenant_id != self.tenant_id:
                raise ValueError(
                    f"Refusing to add chunk for tenant '{chunk.tenant_id}' into "
                    f"'{self.tenant_id}' store — this is the isolation boundary."
                )
            self._chunks[chunk.chunk_id] = chunk
            self._index.add(chunk.chunk_id, chunk.text)

    def search(self, query: str, role: Role, top_k: int) -> list[RetrievedChunk]:
        readable_ids = {cid for cid, c in self._chunks.items() if role_can_read(role, c.sensitivity)}
        hits = self._index.search(query, top_k=top_k, candidate_ids=readable_ids)
        return [RetrievedChunk(chunk=self._chunks[cid], score=score) for cid, score in hits]

    def __len__(self) -> int:
        return len(self._chunks)


class TenantVectorRegistry:
    def __init__(self) -> None:
        self._stores: dict[str, VectorStore] = {}

    def get_or_create(self, tenant_id: str) -> VectorStore:
        if tenant_id not in self._stores:
            self._stores[tenant_id] = VectorStore(tenant_id)
        return self._stores[tenant_id]

    def get(self, tenant_id: str) -> VectorStore:
        if tenant_id not in self._stores:
            raise KeyError(f"No vector store for tenant_id: {tenant_id}")
        return self._stores[tenant_id]
