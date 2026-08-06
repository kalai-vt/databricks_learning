"""Pure-Python TF-IDF vectorizer + cosine similarity.

No numpy/scikit-learn dependency on purpose: the whole demo runs with a
bare `python3` interpreter, which matters when you're presenting live and
cannot risk a `pip install` failing on a conference-room wifi network.
For a real deployment, swap this module for embeddings from a hosted model
(same `TfidfIndex.search()` shape: text in, ranked (id, score) out).
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class TfidfIndex:
    def __init__(self) -> None:
        self._doc_tokens: dict[str, list[str]] = {}
        self._doc_freq: Counter[str] = Counter()
        self._idf: dict[str, float] = {}
        self._vectors: dict[str, dict[str, float]] = {}
        self._dirty = True

    def add(self, item_id: str, text: str) -> None:
        self._doc_tokens[item_id] = tokenize(text)
        self._dirty = True

    def remove(self, item_id: str) -> None:
        self._doc_tokens.pop(item_id, None)
        self._dirty = True

    def _rebuild(self) -> None:
        n_docs = len(self._doc_tokens)
        self._doc_freq = Counter()
        for tokens in self._doc_tokens.values():
            for term in set(tokens):
                self._doc_freq[term] += 1

        self._idf = {
            term: math.log((1 + n_docs) / (1 + df)) + 1.0
            for term, df in self._doc_freq.items()
        }

        self._vectors = {}
        for item_id, tokens in self._doc_tokens.items():
            tf = Counter(tokens)
            total = max(1, len(tokens))
            vec: dict[str, float] = {}
            for term, count in tf.items():
                vec[term] = (count / total) * self._idf.get(term, 0.0)
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            self._vectors[item_id] = {k: v / norm for k, v in vec.items()}

        self._dirty = False

    def _vectorize_query(self, text: str) -> dict[str, float]:
        tokens = tokenize(text)
        if not tokens:
            return {}
        tf = Counter(tokens)
        total = len(tokens)
        vec = {term: (count / total) * self._idf.get(term, 0.0) for term, count in tf.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {k: v / norm for k, v in vec.items()}

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        if len(b) < len(a):
            a, b = b, a
        return sum(v * b.get(k, 0.0) for k, v in a.items())

    def search(self, query: str, top_k: int = 5, candidate_ids: set[str] | None = None) -> list[tuple[str, float]]:
        if self._dirty:
            self._rebuild()
        q_vec = self._vectorize_query(query)
        if not q_vec:
            return []

        scores: list[tuple[str, float]] = []
        for item_id, vec in self._vectors.items():
            if candidate_ids is not None and item_id not in candidate_ids:
                continue
            score = self._cosine(q_vec, vec)
            if score > 0:
                scores.append((item_id, score))

        scores.sort(key=lambda pair: pair[1], reverse=True)
        return scores[:top_k]
