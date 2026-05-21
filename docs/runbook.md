## Week 2 – Infrastructure Deployment (Enterprise-first)

This runbook covers deploying the core infrastructure needed for Data Concierge:

- Azure Container Registry (ACR)
- Azure Key Vault + secrets
- Log Analytics Workspace
- Azure Container Apps Environment
- Container App (internal ingress only)

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

### 4) Build + push the API image

After deployment completes, get the ACR login server from outputs.

```bash
# Example (replace values)
ACR_LOGIN_SERVER="<acr>.azurecr.io"
az acr login --name "${ACR_LOGIN_SERVER%%.*}"

docker build -t data-concierge-api .
docker tag data-concierge-api $ACR_LOGIN_SERVER/data-concierge-api:latest
docker push $ACR_LOGIN_SERVER/data-concierge-api:latest
```

### 5) Update the Container App with image

Re-run the deployment passing `apiImage`:

```bash
az deployment group create \
  --resource-group rg-data-concierge-dev \
  --template-file infra/bicep/main.bicep \
  --parameters @infra/environments/dev.parameters.json \
  --parameters apiImage="$ACR_LOGIN_SERVER/data-concierge-api:latest" \
  --parameters azureOpenAiEndpoint="$AZURE_OPENAI_ENDPOINT" azureOpenAiApiKey="$AZURE_OPENAI_API_KEY"
```
