from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict
from typing import Any
from uuid import uuid4

from .models import ArkBlock, ArkEntry


class ArkChainStore:
    """In-memory append-only ArkChain scaffold."""

    def __init__(self) -> None:
        self._blocks: list[ArkBlock] = []

    @staticmethod
    def _sha256(payload: str) -> str:
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _merkle_root(self, entries: list[ArkEntry]) -> str:
        if not entries:
            return self._sha256("")
        level = [self._sha256(json.dumps(asdict(entry), sort_keys=True, separators=(",", ":"))) for entry in entries]
        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])
            level = [self._sha256(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
        return level[0]

    def append(self, entry_type: str, election_id: str, payload: dict[str, Any], origin_service: str) -> tuple[ArkEntry, ArkBlock]:
        entry = ArkEntry(
            entry_id=str(uuid4()),
            entry_type=entry_type,
            election_id=election_id,
            payload=payload,
            created_at=int(time.time()),
            origin_service=origin_service,
        )
        prev_hash = self._blocks[-1].block_hash if self._blocks else ""
        block_id = len(self._blocks) + 1
        merkle_root = self._merkle_root([entry])
        block_hash = self._sha256(f"{block_id}:{prev_hash}:{merkle_root}:{entry.entry_id}")
        block = ArkBlock(
            block_id=block_id,
            prev_hash=prev_hash,
            merkle_root=merkle_root,
            block_hash=block_hash,
            timestamp=int(time.time()),
            entries=[entry],
        )
        self._blocks.append(block)
        return entry, block

    def list_blocks(self) -> list[ArkBlock]:
        return self._blocks


store = ArkChainStore()

