#!/usr/bin/env bash
set -euo pipefail

kubectl apply -f infra/k8s/api-deployment.yaml
kubectl apply -f infra/k8s/arkchain-statefulset.yaml

