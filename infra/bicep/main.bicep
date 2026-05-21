// main.bicep - Entry point for all infrastructure deployments

targetScope = 'resourceGroup'

@description('Deployment location')
param location string = resourceGroup().location

@description('Environment name (dev/test/prod)')
param environmentName string

@description('Optional resource name prefix to ensure global uniqueness')
param namePrefix string = 'dc'

@description('Container image to deploy for the API (e.g. myacr.azurecr.io/data-concierge-api:latest)')
param apiImage string = ''

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

module acr './acr.bicep' = {
  name: 'acr-${suffix}'
  params: {
    location: location
    environmentName: environmentName
    namePrefix: namePrefix
  }
}

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

module containerApps './container_apps.bicep' = {
  name: 'ca-${suffix}'
  params: {
    location: location
    environmentName: environmentName
    namePrefix: namePrefix
    acrLoginServer: acr.outputs.loginServer
    acrId: acr.outputs.acrId
    apiImage: apiImage
    keyVaultUri: keyVault.outputs.vaultUri
    keyVaultName: keyVault.outputs.vaultName
  }
  dependsOn: [
    acr
    keyVault
  ]
}

output acrLoginServer string = acr.outputs.loginServer
output keyVaultName string = keyVault.outputs.vaultName
output containerAppName string = containerApps.outputs.containerAppName
output containerAppFqdn string = containerApps.outputs.containerAppFqdn
