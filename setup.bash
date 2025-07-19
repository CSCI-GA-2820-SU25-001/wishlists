#!/usr/bin/env bash
#
# deploy.sh — teardown/create cluster, build & push image, deploy app, and verify
#

set -euo pipefail
IFS=$'\n\t'

# Utility for logging
log() {
  local type="$1"; shift
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] ${type}: $*"
}

# 1. Tear down existing cluster
log INFO "Tearing down any existing cluster..."
make cluster-rm

# 2. Create a fresh cluster
log INFO "Creating new k3d cluster..."
make cluster

# 3. Build your image
log INFO "Building the Docker image..."
make build

# 4. Push it to the registry
log INFO "Pushing image to registry..."
make push

# 5. Deploy into Kubernetes
log INFO "Deploying application..."
make deploy

# 6. Show cluster resources
log INFO "Current cluster resources:"
kubectl get all

log INFO "✅ Deployment pipeline complete!"
