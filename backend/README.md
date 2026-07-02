# Backend layout

This directory contains service-oriented backend modules for SVP:

- `api/` core API composition and app wiring
- `auth/` authentication and MFA service layer
- `token/` election-scoped token issuance and validation
- `ballot/` ballot submission and integrity handling
- `verify/` read-only verification endpoints and response models
- `arkchain/` separate append-only ledger service
- `common/` shared models and helpers

