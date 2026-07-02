# SVP Architecture

SVP is organized as a multi-service secure voting platform with role-separated frontends and a verifiable append-only ledger.

## Core services

- **Backend API**: authentication, token issuance, ballot submission, verification
- **ArkChain**: separate append-only ledger service for election events
- **Postgres/Redis**: operational data and short-lived controls

## Trust boundaries

- voter-facing operations remain isolated from admin and trustee operations
- all election operations are scoped by `election_id`
- observer APIs are read-only

## Repository structure

- `backend/` service-oriented backend modules
- `frontend/` role-separated portal surfaces
- `infra/` deployment artifacts (Docker, Kubernetes, Helm)
- `docs/` architecture and security documentation

