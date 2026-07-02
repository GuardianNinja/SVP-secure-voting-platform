from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .service import store


class AppendRequest(BaseModel):
    entryType: str = Field(min_length=1, max_length=64)
    electionId: str = Field(min_length=1, max_length=64)
    payload: dict[str, Any]
    originService: str = Field(min_length=1, max_length=64)


app = FastAPI(title="SVP ArkChain Node (Scaffold)")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/arkchain/append")
def append_entry(body: AppendRequest) -> dict[str, Any]:
    entry, block = store.append(body.entryType, body.electionId, body.payload, body.originService)
    return {
        "accepted": True,
        "entry": asdict(entry),
        "block": {"blockId": block.block_id, "blockHash": block.block_hash, "merkleRoot": block.merkle_root},
    }


@app.get("/api/v1/arkchain/blocks")
def list_blocks() -> dict[str, Any]:
    return {"blocks": [asdict(block) for block in store.list_blocks()]}

