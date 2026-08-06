"""Sliding-window word chunking with overlap.

Simple by design: this demo's point is the *guardrail pipeline* around
retrieval, not chunking sophistication. Swap in a semantic/structure-aware
chunker for production without touching anything downstream — chunks just
need a `chunk_id`, `tenant_id`, `sensitivity`, and `text`.
"""
from __future__ import annotations

from app import config
from app.models import Chunk, Document, new_id


def chunk_document(doc: Document, size_words: int = config.CHUNK_SIZE_WORDS,
                    overlap_words: int = config.CHUNK_OVERLAP_WORDS) -> list[Chunk]:
    words = doc.text.split()
    if not words:
        return []

    chunks: list[Chunk] = []
    step = max(1, size_words - overlap_words)
    position = 0
    for start in range(0, len(words), step):
        window = words[start:start + size_words]
        if not window:
            break
        text = " ".join(window)
        chunks.append(
            Chunk(
                chunk_id=new_id("chunk"),
                doc_id=doc.doc_id,
                tenant_id=doc.tenant_id,
                title=doc.title,
                sensitivity=doc.sensitivity,
                text=text,
                position=position,
            )
        )
        position += 1
        if start + size_words >= len(words):
            break
    return chunks
