# Threat model (baseline)

## Threats

- credential theft and session replay
- token replay and duplicate ballot submission
- unauthorized cross-tenant data access
- ledger tampering or deletion attempts

## Mitigations

- MFA and short-lived session/token controls
- election-scoped authorization and query filters
- append-only integrity logging with hash-linking and Merkle roots
- auditable admin and key events

