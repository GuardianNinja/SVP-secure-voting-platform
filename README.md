# SVP-secure-voting-platform

SVP is a secure voting platform scaffold with multi-role portals, a core API, and an ArkChain append-only service.

## Repository structure

```text
backend/
  api/
  auth/
  token/
  ballot/
  verify/
  arkchain/
    node/
    consensus/
    storage/
    crypto/
    keys/
    homomorphic/
    threshold/
  common/
    models/
    utils/
frontend/
  voter/
  admin/
  observer/
  trustee/
infra/
  docker/
  k8s/
  helm/
docs/
scripts/
```

## Current runnable demo

Legacy demo pages and API remain at the repository root for compatibility:

- `main.py`, `index.html`, `vote.html`, `totp.html`, `observer.html`

Run locally:

1. `pip install -r requirements.txt`
2. `uvicorn main:app --reload`
3. Open `http://127.0.0.1:8000/index.html`

## ArkChain service

ArkChain now exists as a separate service scaffold under:

- `backend/arkchain/node/models.py` (block and entry models)
- `backend/arkchain/node/api.py` (append/read APIs)
- `backend/arkchain/consensus/raft.py` (Raft scaffolding)

## Infra and CI/CD

- Docker: `infra/docker/`
- Kubernetes: `infra/k8s/`
- Helm: `infra/helm/`
- GitHub Actions pipeline: `.github/workflows/ci.yml`
