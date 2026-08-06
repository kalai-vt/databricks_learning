"""Central configuration for the demo. Values are intentionally small/simple
so behavior is easy to reason about live in front of an audience.
"""

# RAG
CHUNK_SIZE_WORDS = 90
CHUNK_OVERLAP_WORDS = 20
TOP_K = 3
MIN_RELEVANCE_SCORE = 0.20  # below this we refuse rather than hallucinate

# Rate limiting (token bucket): per (tenant_id, user_id)
RATE_LIMIT_MAX_TOKENS = 5
RATE_LIMIT_REFILL_PER_SEC = 1.0  # 1 request budget regained per second

# Governance
MODEL_NAME = "banking-secure-rag-demo"
MODEL_VERSION = "1.0.0"
