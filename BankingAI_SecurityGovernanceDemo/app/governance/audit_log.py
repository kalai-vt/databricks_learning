"""Append-only, hash-chained audit log.

Every entry embeds the SHA-256 hash of the previous entry (à la a
single-node blockchain), so tampering with any historical entry — editing
a payload, reordering, or deleting one — breaks `verify_integrity()` from
that point forward. This is the standard "tamper-evident log" pattern
auditors look for in banking compliance reviews (who asked what, what was
retrieved, what was redacted, what was denied, and when), and it is a
natural live-demo moment: mutate an old entry in front of the audience and
show the verifier catch it.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from app.models import now_iso

GENESIS_HASH = "0" * 64


@dataclass
class AuditEntry:
    seq: int
    timestamp: str
    prev_hash: str
    payload: dict
    entry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        self.entry_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        base = f"{self.seq}|{self.timestamp}|{self.prev_hash}|{json.dumps(self.payload, sort_keys=True, default=str)}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()


class AuditLog:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def append(self, payload: dict) -> AuditEntry:
        prev_hash = self._entries[-1].entry_hash if self._entries else GENESIS_HASH
        entry = AuditEntry(seq=len(self._entries), timestamp=now_iso(), prev_hash=prev_hash, payload=payload)
        self._entries.append(entry)
        return entry

    @property
    def entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def verify_integrity(self) -> tuple[bool, str | None]:
        """Returns (is_valid, reason_if_invalid)."""
        expected_prev = GENESIS_HASH
        for entry in self._entries:
            if entry.prev_hash != expected_prev:
                return False, f"entry seq={entry.seq} has broken prev_hash link"
            if entry.entry_hash != entry._compute_hash():
                return False, f"entry seq={entry.seq} payload/hash mismatch (tampered)"
            expected_prev = entry.entry_hash
        return True, None

    def tail(self, n: int = 10) -> list[AuditEntry]:
        return self._entries[-n:]
