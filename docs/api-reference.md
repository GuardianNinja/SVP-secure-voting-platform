# API reference (baseline)

## Core API

- `POST /api/auth/login`
- `POST /api/auth/mfa`
- `POST /api/auth/token`
- `POST /api/ballot/submit`
- `GET /api/verify/{ballotId}`
- `GET /api/arkchain/chain/head?electionId=...`
- `GET /api/arkchain/entries?electionId=...`

## ArkChain service API

- `GET /healthz`
- `POST /api/v1/arkchain/append`
- `GET /api/v1/arkchain/blocks`
- `GET /api/v1/arkchain/entries?electionId=...`

