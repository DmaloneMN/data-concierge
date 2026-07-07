#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  export RG="rg-data-concierge-dev"
  export ACR_NAME="<optional-acr-name>"
  export IMAGE_NAME="data-concierge-api"   # optional
  export IMAGE_TAG="dev"                   # optional

If ACR_NAME is not set, the script resolves it with:
  az acr list -g "$RG" --query "[0].name" -o tsv
USAGE
}

require_command() {
  local command_name=$1
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Error: required command '$command_name' is not installed or not on PATH." >&2
    exit 1
  fi
}

require_command az

IMAGE_NAME="${IMAGE_NAME:-data-concierge-api}"
IMAGE_TAG="${IMAGE_TAG:-dev}"
ACR_NAME="${ACR_NAME:-}"

if [[ -z "$ACR_NAME" ]]; then
  if [[ -z "${RG:-}" ]]; then
    echo "Error: set ACR_NAME directly or provide RG so the registry can be auto-discovered." >&2
    usage >&2
    exit 1
  fi

  echo "Resolving ACR_NAME from resource group '$RG'"
  ACR_NAME="$(az acr list -g "$RG" --query '[0].name' -o tsv)"
fi

if [[ -z "$ACR_NAME" ]]; then
  echo "Error: unable to resolve an Azure Container Registry name." >&2
  usage >&2
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
image_ref="${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building $image_ref with az acr build from $repo_root"
az acr build \
  --registry "$ACR_NAME" \
  --image "${IMAGE_NAME}:${IMAGE_TAG}" \
  "$repo_root"

echo "Fully qualified image: $image_ref"
