#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  export RG="rg-data-concierge-dev"
  export AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com/"
  export AZURE_OPENAI_API_KEY="<your-api-key>"
  export API_IMAGE="<acr>.azurecr.io/data-concierge-api:dev"

Optional environment variables:
  LOCATION          Azure region (default: eastus)
  ENVIRONMENT_NAME  Environment name passed to Bicep (default: dev)
  NAME_PREFIX       Resource name prefix (default: dc)
  MODEL_DEPLOYMENT  Azure OpenAI model deployment (default: gpt-4o)
  ACR_SKU           ACR SKU (default: Premium, because some subscriptions reject Basic/Standard with SkuNotSupported)

Runs:
  az deployment group create --template-file infra/bicep/main.bicep
USAGE
}

require_command() {
  local command_name=$1
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Error: required command '$command_name' is not installed or not on PATH." >&2
    exit 1
  fi
}

require_env() {
  local variable_name=$1
  if [[ -z "${!variable_name:-}" ]]; then
    echo "Error: required environment variable '$variable_name' is not set." >&2
    return 1
  fi
}

require_command az

LOCATION="${LOCATION:-eastus}"
ENVIRONMENT_NAME="${ENVIRONMENT_NAME:-dev}"
NAME_PREFIX="${NAME_PREFIX:-dc}"
MODEL_DEPLOYMENT="${MODEL_DEPLOYMENT:-gpt-4o}"
ACR_SKU="${ACR_SKU:-Premium}"

missing=0
require_env RG || missing=1
require_env AZURE_OPENAI_ENDPOINT || missing=1
require_env AZURE_OPENAI_API_KEY || missing=1
require_env API_IMAGE || missing=1

if [[ "$missing" -ne 0 ]]; then
  usage >&2
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
template_file="$repo_root/infra/bicep/main.bicep"

if [[ ! -f "$template_file" ]]; then
  echo "Error: template file not found at $template_file" >&2
  exit 1
fi

echo "Deploying infrastructure to resource group '$RG' from $template_file"
echo "Using LOCATION=$LOCATION ENVIRONMENT_NAME=$ENVIRONMENT_NAME NAME_PREFIX=$NAME_PREFIX MODEL_DEPLOYMENT=$MODEL_DEPLOYMENT ACR_SKU=$ACR_SKU"
echo "Using API_IMAGE=$API_IMAGE"

az deployment group create \
  --resource-group "$RG" \
  --template-file "$template_file" \
  --parameters \
    environmentName="$ENVIRONMENT_NAME" \
    location="$LOCATION" \
    namePrefix="$NAME_PREFIX" \
    modelDeployment="$MODEL_DEPLOYMENT" \
    azureOpenAiEndpoint="$AZURE_OPENAI_ENDPOINT" \
    azureOpenAiApiKey="$AZURE_OPENAI_API_KEY" \
    acrSku="$ACR_SKU" \
    apiImage="$API_IMAGE"
