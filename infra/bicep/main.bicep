// main.bicep - Entry point for all infrastructure deployments

targetScope = 'resourceGroup'

@description('Deployment location')
param location string = resourceGroup().location

@description('Environment name (dev/test/prod)')
param environmentName string

@description('Optional resource name prefix to ensure global uniqueness')
param namePrefix string = 'dc'

@description('Container image to deploy for the API (can be public for dev if ACR is disabled)')
param apiImage string = ''

@description('Whether to deploy Azure Container Registry (ACR). Some subscriptions/policies disallow ACR creation.')
param deployAcr bool = true

@description('ACR SKU. Some subscriptions/regions only support specific tiers; some disallow ACR entirely.')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param acrSku string = 'Basic'

@description('Azure OpenAI endpoint (for initial bootstrap; will be stored in Key Vault)')
@secure()
param azureOpenAiEndpoint string

@description('Azure OpenAI API key (for initial bootstrap; will be stored in Key Vault)')
@secure()
param azureOpenAiApiKey string

@description('Azure OpenAI model deployment name (for initial bootstrap; will be stored in Key Vault)')
param modelDeployment string = 'gpt-4o'

// Resource name helpers
var suffix = toLower('${namePrefix}-${environmentName}-${uniqueString(resourceGroup().id)}')

module keyVault './key_vault.bicep' = {
  name: 'kv-${suffix}'
  params: {
    location: location
    environmentName: environmentName
    namePrefix: namePrefix
    azureOpenAiEndpoint: azureOpenAiEndpoint
    azureOpenAiApiKey: azureOpenAiApiKey
    modelDeployment: modelDeployment
  }
}

// When deployAcr=false, we avoid referencing acr module outputs altogether to keep bicep warnings clean.
module acr './acr.bicep' = if (deployAcr) {
  name: 'acr-${suffix}'
  params: {
    location: location
    environmentName: environmentName
    namePrefix: namePrefix
    acrSku: acrSku
  }
}

module containerAppsWithAcr './container_apps.bicep' = if (deployAcr) {
  name: 'ca-${suffix}-with-acr'
  params: {
    location: location
    environmentName: environmentName
    namePrefix: namePrefix
    apiImage: apiImage
    keyVaultUri: keyVault.outputs.vaultUri
    keyVaultName: keyVault.outputs.vaultName
    deployAcr: true
    acrLoginServer: acr.outputs.loginServer
    acrId: acr.outputs.acrId
  }
}

module containerAppsNoAcr './container_apps.bicep' = if (!deployAcr) {
  name: 'ca-${suffix}-no-acr'
  params: {
    location: location
    environmentName: environmentName
    namePrefix: namePrefix
    apiImage: apiImage
    keyVaultUri: keyVault.outputs.vaultUri
    keyVaultName: keyVault.outputs.vaultName
    deployAcr: false
  }
}

output acrLoginServer string = deployAcr ? acr.outputs.loginServer : ''
output keyVaultName string = keyVault.outputs.vaultName
output containerAppName string = deployAcr ? containerAppsWithAcr.outputs.containerAppName : containerAppsNoAcr.outputs.containerAppName
