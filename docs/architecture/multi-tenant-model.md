# Multi-Tenant Election Model (SVP)

## Status
Draft (PR-ready skeleton)

## Objective

Define a safe, auditable multi-tenant model where each election is an isolated tenant with independent configuration, cryptographic context, and verification surface.

## Tenant definition

A tenant is an `election` and owns:

- Ballot schema
- District map / jurisdiction metadata
- Token policy
- Cryptographic key references
- Audit and chain views
- Election lifecycle state

## Core principles

1. **Strict isolation by `election_id`**
2. **No cross-tenant token or ballot reuse**
3. **Deterministic auditability**
4. **Public verifiability via read-only observer interfaces**
5. **Least-privilege role separation**

## Domain model (logical)

- `elections`
- `districts`
- `ballot_definitions`
- `voters` (global identity with election-scoped eligibility links)
- `voter_eligibility` (joins voter ↔ election)
- `tokens` (election-scoped, one-time)
- `ballots` (election-scoped immutable submissions)
- `audit_log` (election-scoped events)
- `election_keys` (key references/version metadata)
- `trustees` (per-election trustee assignments)

## Required schema constraints

- Every tenant-owned row includes non-null `election_id`
- Composite uniqueness where appropriate:
  - `tokens(election_id, token_id)` unique
  - `ballots(election_id, ballot_id)` unique
- Foreign keys enforce tenant consistency
- No mutable update path for submitted ballots (append-only semantics)

## API tenancy rules (normative skeleton)

- Mutating endpoints MUST require `election_id` context.
- `election_id` can come from:
  - URL path segment, or
  - signed token claim
- If both are present, they MUST match.
- All service-to-service calls propagate `election_id`.
- Observer endpoints are read-only and explicitly election-scoped.

## Role separation model

### Voter
- Authenticate, obtain token, submit ballot, retrieve receipt verification data.

### Admin
- Create/configure/open/close elections.
- Publish election config hash and policy metadata.

### Observer
- Read chain state, verify inclusion, download audit bundles.

### Trustee
- Manage key ceremony metadata and decryption-share workflows (future phases).

### Registration
- Manage voter onboarding/eligibility for election scope.

## Lifecycle states

Proposed election states:

- `DRAFT`
- `CONFIGURED`
- `OPEN`
- `CLOSED`
- `TALLIED`
- `ARCHIVED`

Transition rules:
- Only specific roles may transition states.
- All transitions emit auditable events.
- Invalid transitions return deterministic errors.

## Request flow (reference)

1. User authenticates and satisfies MFA.
2. User requests election-scoped voting token.
3. Token service validates eligibility in election scope.
4. Ballot submission consumes token atomically.
5. Ballot write + chain append + audit event are correlated by request ID.
6. Observer verifies inclusion via receipt/proof APIs.

## Isolation and security controls

- Tenant-aware authorization checks at API boundary.
- Query filters enforce `WHERE election_id = :election_id`.
- Defense-in-depth:
  - app-level guards
  - DB constraints
  - audit reconciliation jobs
- Cross-tenant access attempts are logged as security events.

## Operational model

- API nodes: stateless, horizontally scalable
- Postgres: operational data with election-scoped indexing
- ArkChain: integrity log for election/audit events
- Observer APIs: cache-friendly read replicas where possible

## Indexing guidance

Recommended indexes:
- `tokens (election_id, voter_id, status, expires_at)`
- `ballots (election_id, created_at)`
- `audit_log (election_id, created_at, event_type)`
- `voter_eligibility (election_id, voter_id)`

## Backward compatibility and migration

- Add `election_id` nullable initially for migration.
- Backfill legacy records into a bootstrap/default election tenant.
- Flip to non-null + constraints after backfill verification.
- Maintain migration audit report artifact.

## Non-goals (current phase)

- Full cryptographic tally decryption workflows
- Inter-jurisdiction federation between separate platforms
- Policy DSL completeness

## Acceptance criteria checklist

- [ ] Every ballot/token/audit record includes valid `election_id`
- [ ] API integration tests for cross-tenant denial
- [ ] Election lifecycle transitions audited
- [ ] Observer can query election-scoped chain state
- [ ] Migration/backfill completed without orphan records

## Open questions

- [ ] Global user identity model vs per-election pseudonymous identities
- [ ] Tenant-specific encryption key rotation cadence
- [ ] Election data retention and legal hold policies
- [ ] Public data redaction policy for observer endpoints
