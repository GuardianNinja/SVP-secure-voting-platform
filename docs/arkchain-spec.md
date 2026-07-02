# ArkChain Specification (Scaffold)

ArkChain is the election transparency and integrity ledger for SVP.

## Data model

- `ArkEntry`: typed election event payload
- `ArkBlock`: hash-linked container of entries with Merkle root

## APIs

- `POST /api/v1/arkchain/append`
- `GET /api/v1/arkchain/blocks`
- `GET /api/v1/arkchain/entries?electionId=...`

## Consensus

Raft consensus scaffolding exists under `backend/arkchain/consensus/raft.py` with role and term lifecycle boundaries for leader/follower transitions.

