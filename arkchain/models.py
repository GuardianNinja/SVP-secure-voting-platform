from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ArkEntry:
    entry_id: str
    entry_type: str
    election_id: str
    payload: dict[str, Any]
    created_at: int
    origin_service: str
    service_signature: str | None = None


@dataclass(frozen=True)
class ArkBlock:
    block_id: int
    prev_hash: str
    merkle_root: str
    block_hash: str
    timestamp: int
    entries: list[ArkEntry] = field(default_factory=list)

