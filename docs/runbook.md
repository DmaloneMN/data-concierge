## Week 2 – Infrastructure Deployment (Enterprise-first)

This runbook covers deploying the core infrastructure needed for Data Concierge:

- Azure Key Vault + secrets
- Log Analytics Workspace
- Azure Container Apps Environment
- Container App (internal ingress only)

Optionally:
- Azure Container Registry (ACR)

> Note: With internal ingress, you will not be able to hit the app directly from the public internet.
> In Week 3/4, we typically add API Management (and optionally VNet integration) as the secure front door.

### Prerequisites

- Azure CLI installed
- Bicep installed (`az bicep version`)
- Logged in: `az login`

### 0) IMPORTANT: rotate secrets if leaked

If you ever paste an API key into chat logs or terminals that are recorded, rotate it immediately in Azure.

### 1) Create a resource group

```bash
az group create --name rg-data-concierge-dev --location eastus
```

### 2) What-if deployment (recommended)

Set these in your shell (do not commit secrets):

```bash
export AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com/"
export AZURE_OPENAI_API_KEY="<your-api-key>"
```

Run what-if:

```bash
az deployment group create \
  --resource-group rg-data-concierge-dev \
  --template-file infra/bicep/main.bicep \
  --parameters @infra/environments/dev.parameters.json \
  --parameters azureOpenAiEndpoint="$AZURE_OPENAI_ENDPOINT" azureOpenAiApiKey="$AZURE_OPENAI_API_KEY" \
  --what-if
```

### 3) Deploy

```bash
az deployment group create \
  --resource-group rg-data-concierge-dev \
  --template-file infra/bicep/main.bicep \
  --parameters @infra/environments/dev.parameters.json \
  --parameters azureOpenAiEndpoint="$AZURE_OPENAI_ENDPOINT" azureOpenAiApiKey="$AZURE_OPENAI_API_KEY"
```

### 4) Image strategy

This repo supports two paths:

#### Path A: No ACR (for restricted subscriptions)

If your subscription/policies disallow ACR creation, set `deployAcr=false` and use a public image (e.g. MCR)
for the first deploy. This validates Key Vault, managed identity, role assignments, Container Apps environment, etc.

Later, when you have an approved registry (central ACR or GHCR), switch `apiImage` and (optionally) enable ACR.

#### Path B: ACR

If ACR is allowed, set `deployAcr=true`, deploy, then build/push your API image and re-run deployment with `apiImage`.

```bash
# Example (replace values)
ACR_LOGIN_SERVER="<acr>.azurecr.io"
az acr login --name "${ACR_LOGIN_SERVER%%.*}"

docker build -t data-concierge-api .
docker tag data-concierge-api $ACR_LOGIN_SERVER/data-concierge-api:latest
docker push $ACR_LOGIN_SERVER/data-concierge-api:latest
```
