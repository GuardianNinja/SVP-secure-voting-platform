from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from backend.arkchain.consensus.raft import RaftNode
from backend.arkchain.storage.store import ArkChainStore


class AppendRequest(BaseModel):
    entryType: str = Field(min_length=1, max_length=64)
    electionId: str = Field(min_length=1, max_length=64)
    payload: dict[str, Any]
    originService: str = Field(min_length=1, max_length=64)


store = ArkChainStore()
raft_node = RaftNode(node_id="arkchain-node-1")
app = FastAPI(title="SVP ArkChain Service")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "role": raft_node.role.value}


@app.post("/api/v1/arkchain/append")
def append_entry(body: AppendRequest) -> dict[str, Any]:
    if raft_node.role.value != "leader":
        raft_node.become_leader()
    entry, block = store.append(
        entry_type=body.entryType,
        election_id=body.electionId,
        payload=body.payload,
        origin_service=body.originService,
    )
    return {
        "accepted": True,
        "entry": asdict(entry),
        "block": {"blockId": block.block_id, "blockHash": block.block_hash, "merkleRoot": block.merkle_root},
        "raft": {"term": raft_node.current_term, "role": raft_node.role.value},
    }


@app.get("/api/v1/arkchain/blocks")
def get_blocks(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
    blocks = [asdict(block) for block in store.list_blocks()]
    return {"blocks": blocks[-limit:], "count": min(limit, len(blocks))}


@app.get("/api/v1/arkchain/entries")
def get_entries(electionId: str = Query(min_length=1, max_length=64), limit: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
    blocks = store.list_blocks()
    entries: list[dict[str, Any]] = []
    for block in blocks:
        for entry in block.entries:
            if entry.election_id == electionId:
                entries.append(asdict(entry))
    return {"electionId": electionId, "entries": entries[-limit:], "count": min(limit, len(entries))}

