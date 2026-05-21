// key_vault.bicep - Azure Key Vault deployment

targetScope = 'resourceGroup'

param location string
param environmentName string
param namePrefix string = 'dc'

@secure()
param azureOpenAiEndpoint string

@secure()
param azureOpenAiApiKey string

param modelDeployment string

var kvName = toLower('${namePrefix}-kv-${environmentName}-${uniqueString(resourceGroup().id)}')

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: kvName
  location: location
  properties: {
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    sku: {
      family: 'A'
      name: 'standard'
    }
    enabledForDeployment: false
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    publicNetworkAccess: 'Enabled'
  }
}

// Secrets (RBAC access is required to read them)
resource secretOpenAiEndpoint 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'AZURE-OPENAI-ENDPOINT'
  parent: kv
  properties: {
    value: azureOpenAiEndpoint
  }
}

resource secretOpenAiKey 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'AZURE-OPENAI-API-KEY'
  parent: kv
  properties: {
    value: azureOpenAiApiKey
  }
}

resource secretModelDeployment 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'MODEL-DEPLOYMENT'
  parent: kv
  properties: {
    value: modelDeployment
  }
}

output vaultName string = kv.name
output vaultUri string = kv.properties.vaultUri
