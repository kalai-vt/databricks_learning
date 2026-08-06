"""Per-(tenant, user) token-bucket rate limiter.

Maps to OWASP LLM04: Unbounded Resource Consumption (model-DoS / cost
exhaustion). Each tenant's users draw from their own bucket, so one noisy
or malicious user cannot starve another tenant's request budget — another
facet of multi-tenant isolation, applied to *capacity* rather than data.
"""
from __future__ import annotations

import time

from app import config


class _Bucket:
    __slots__ = ("tokens", "last_refill")

    def __init__(self, tokens: float, last_refill: float) -> None:
        self.tokens = tokens
        self.last_refill = last_refill


class RateLimiter:
    def __init__(
        self,
        max_tokens: int = config.RATE_LIMIT_MAX_TOKENS,
        refill_per_sec: float = config.RATE_LIMIT_REFILL_PER_SEC,
    ) -> None:
        self.max_tokens = max_tokens
        self.refill_per_sec = refill_per_sec
        self._buckets: dict[str, _Bucket] = {}

    def _key(self, tenant_id: str, user_id: str) -> str:
        return f"{tenant_id}:{user_id}"

    def allow(self, tenant_id: str, user_id: str) -> bool:
        key = self._key(tenant_id, user_id)
        now = time.monotonic()
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=float(self.max_tokens), last_refill=now)
            self._buckets[key] = bucket

        elapsed = now - bucket.last_refill
        bucket.tokens = min(self.max_tokens, bucket.tokens + elapsed * self.refill_per_sec)
        bucket.last_refill = now

        if bucket.tokens >= 1.0:
            bucket.tokens -= 1.0
            return True
        return False
