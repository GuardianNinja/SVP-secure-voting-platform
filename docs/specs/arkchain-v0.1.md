# Space LEAF ArkChain Specification (v0.1)

## Status
Draft (PR-ready skeleton)

## Purpose

ArkChain is a governance-grade bulletin board: an append-only, hash-linked ledger for elections, designed to be publicly inspectable and understandable.

It records:

- Ballot submissions
- Token issuance
- Tally publication
- Key and system events

## Scope

### In scope (v0.1)
- Append-only election event ledger
- Hash-linked blocks
- Basic read APIs
- Entry and block signing interfaces
- Merkle inclusion proofs per block

### Out of scope (v0.1)
- Full homomorphic ballot encryption
- Production threshold decryption ceremonies
- Geo-distributed consensus across jurisdictions

## Data model

### Block
- `blockId` — sequential height or UUID
- `prevHash` — hash of previous block
- `timestamp` — block creation time
- `entries[]` — list of ledger entries
- `merkleRoot` — root hash over entry leaves
- `blockHash` — hash over canonical block header + entries metadata
- `nodeSignature` — signature by ArkChain node

### Entry
Common fields:
- `entryId` — unique identifier
- `type` — event type
- `electionId`
- `payload` — JSON payload
- `createdAt`
- `originService`
- `serviceSignature`

Entry types:
- `BALLOT_SUBMITTED`
- `TOKEN_ISSUED`
- `TALLY_PUBLISHED`
- `KEY_EVENT`
- `SYSTEM_EVENT`

## Canonical hashing rules (normative skeleton)

- Canonical JSON serialization required before hashing.
- UTF-8 encoding.
- Stable key ordering.
- No insignificant whitespace.
- `blockHash` includes `prevHash`, `timestamp`, `merkleRoot`, and block metadata.
- Exact canonicalization profile: **TBD in ADR-ARK-001**.

## Consensus

ArkChain uses a Raft-style consensus model:

- One leader, multiple followers
- Linearizable append operations
- Followers replicate the log
- Leader rotates on failure

This keeps the system simple, inspectable, and suitable for local-first deployments.

## API contracts (v0.1 skeleton)

### Append entry
`POST /api/v1/arkchain/append`

Request:
- `idempotencyKey`
- `entry.type`
- `entry.electionId`
- `entry.payload`
- `entry.createdAt`
- `entry.originService`
- `entry.serviceSignature`

Response:
- `accepted: boolean`
- `entryId`
- `blockId` (optional if queued)
- `chainHead`

### Read blocks
`GET /api/v1/arkchain/blocks?from=<height>&limit=<n>`

### Read block by id/height
`GET /api/v1/arkchain/blocks/{blockId}`

### Read entries by election
`GET /api/v1/arkchain/entries?electionId=<id>&type=<optional>&cursor=<optional>`

### Inclusion proof
`GET /api/v1/arkchain/proofs/{entryId}`

Response:
- `entryHash`
- `leafIndex`
- `proof[]`
- `merkleRoot`
- `blockId`
- `blockHash`

## Integration points

### Ballot service → ArkChain

On successful ballot submission:

1. Store ballot in `ballots` table.
2. Append `BALLOT_SUBMITTED` entry with:
   - `ballotId`
   - `ballotHash`
   - `districtId`
   - `timestamp`

### Token service → ArkChain

On token issuance:

1. Store token in `tokens` table.
2. Append `TOKEN_ISSUED` entry with:
   - `tokenId`
   - `voterId` (opaque/pseudonymous)
   - `electionId`
   - `expiresAt`

### Audit service → ArkChain

Every significant event (auth, config changes, tally publication) is:

1. Written to `audit_log`.
2. Mirrored as a `SYSTEM_EVENT` or `KEY_EVENT`.

## Failure handling and idempotency

- Append endpoints MUST support idempotency keys.
- Duplicate idempotency keys return original accepted result.
- On downstream failure, services must emit structured error audit events.
- No silent drops of append attempts.

## Security and trust assumptions

- Service private keys are rotated and versioned.
- Public keys are discoverable for signature verification.
- Observer endpoints are read-only and non-mutating.
- Raw ballot secrecy rules remain enforced outside ArkChain payload design.

## Verifiability

### Inclusion proofs

Each block maintains a Merkle tree over its entries:

- Leaf: `hash(entry)`
- Root: stored in block header (`merkleRoot`)

A verifier can prove inclusion by:

- Providing `entryId` / `ballotId`
- Receiving proof path
- Verifying proof against `merkleRoot`, then against `blockHash` chain

### Public explorer compatibility

ArkChain read APIs support:

- Listing blocks
- Filtering by election
- Fetching proofs
- Downloading election audit bundle manifest

## Rollout plan

### v0.1
- Single-node append/read + Merkle proof baseline

### v0.2
- Multi-node Raft replication, operational failover

### v0.3+
- Governance modules, threshold key events, advanced cryptographic proofs

## Open questions

- [ ] Canonical JSON profile finalization
- [ ] Signature algorithm and key distribution format
- [ ] Retention/archive strategy for old elections
- [ ] Maximum payload size per entry
- [ ] Backpressure behavior under append spikes
