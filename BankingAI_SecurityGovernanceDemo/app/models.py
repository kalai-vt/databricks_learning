"""Core data models shared across the demo application.

Kept dependency-free (stdlib only) so the whole demo runs with a bare
`python3` interpreter during a live walkthrough.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


class Role(str, Enum):
    CUSTOMER = "customer"
    TELLER = "teller"
    RISK_ANALYST = "risk_analyst"
    COMPLIANCE_OFFICER = "compliance_officer"
    ADMIN = "admin"


class SensitivityLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


# Role hierarchy used for simple RBAC checks: a role may read content
# classified at its own sensitivity level or below.
_SENSITIVITY_CLEARANCE = {
    Role.CUSTOMER: {SensitivityLevel.PUBLIC},
    Role.TELLER: {SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL},
    Role.RISK_ANALYST: {SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL, SensitivityLevel.CONFIDENTIAL},
    Role.COMPLIANCE_OFFICER: {
        SensitivityLevel.PUBLIC,
        SensitivityLevel.INTERNAL,
        SensitivityLevel.CONFIDENTIAL,
        SensitivityLevel.RESTRICTED,
    },
    Role.ADMIN: {
        SensitivityLevel.PUBLIC,
        SensitivityLevel.INTERNAL,
        SensitivityLevel.CONFIDENTIAL,
        SensitivityLevel.RESTRICTED,
    },
}


def role_can_read(role: Role, sensitivity: SensitivityLevel) -> bool:
    return sensitivity in _SENSITIVITY_CLEARANCE.get(role, set())


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    display_name: str
    tenant_type: str  # "white_label_brand" (customer-facing) | "internal_department"


@dataclass(frozen=True)
class User:
    user_id: str
    tenant_id: str
    role: Role
    display_name: str


@dataclass
class Document:
    doc_id: str
    tenant_id: str
    title: str
    source_path: str
    sensitivity: SensitivityLevel
    text: str


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    tenant_id: str
    title: str
    sensitivity: SensitivityLevel
    text: str
    position: int


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


@dataclass
class SecurityEvent:
    event_id: str
    event_type: str  # e.g. PROMPT_INJECTION_BLOCKED, PII_REDACTED, RBAC_DENIED
    severity: str  # info | warning | critical
    detail: str


@dataclass
class QueryResult:
    query_id: str
    tenant_id: str
    user_id: str
    original_query: str
    allowed: bool
    answer: str
    role: Role | None = None
    citations: list[str] = field(default_factory=list)
    events: list[SecurityEvent] = field(default_factory=list)
    escalate_to_human: bool = False
    latency_ms: float = 0.0
