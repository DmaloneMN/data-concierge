// container_apps.bicep - Azure Container Apps environment and app deployment

targetScope = 'resourceGroup'

param location string
param environmentName string
param namePrefix string = 'dc'

@description('ACR login server, e.g. myacr.azurecr.io')
param acrLoginServer string

@description('ACR resource id')
param acrId string

@description('API container image full reference')
param apiImage string

@description('Key Vault URI (https://<name>.vault.azure.net/)')
param keyVaultUri string

@description('Key Vault name')
param keyVaultName string

var lawName = toLower('${namePrefix}-law-${environmentName}-${uniqueString(resourceGroup().id)}')
var caeName = toLower('${namePrefix}-cae-${environmentName}-${uniqueString(resourceGroup().id)}')
var appName = toLower('${namePrefix}-api-${environmentName}-${uniqueString(resourceGroup().id)}')

resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: lawName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource cae 'Microsoft.App/managedEnvironments@2023-08-01-preview' = {
  name: caeName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: law.properties.customerId
        sharedKey: law.listKeys().primarySharedKey
      }
    }
  }
}

// Managed identity for the app (for Key Vault access and ACR pull)
resource appIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${appName}-id'
  location: location
}

// Existing resources for RBAC scopes (scope must be a resource object, not a string)
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: last(split(acrId, '/'))
}

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

// Role assignment name must be computed from stable values known at deployment start.
// (principalId is not available at compile-time, but identity resourceId is.)
var acrPullAssignmentName = guid(acr.id, appIdentity.id, 'acrpull')
var kvSecretsUserAssignmentName = guid(kv.id, appIdentity.id, 'kv-secrets-user')

// RBAC: allow Container Apps identity to pull from ACR
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: acrPullAssignmentName
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: appIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC: allow identity to read Key Vault secrets
resource kvSecretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: kvSecretsUserAssignmentName
  scope: kv
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: appIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource app 'Microsoft.App/containerApps@2023-08-01-preview' = {
  name: appName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${appIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: cae.id
    configuration: {
      ingress: {
        // enterprise-friendly: internal only; APIM will be front door later
        external: false
        targetPort: 8000
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: appIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: apiImage
          env: [
            {
              name: 'ENVIRONMENT'
              value: environmentName
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: '@Microsoft.KeyVault(SecretUri=${keyVaultUri}secrets/AZURE-OPENAI-ENDPOINT)'
            }
            {
              name: 'AZURE_OPENAI_API_KEY'
              value: '@Microsoft.KeyVault(SecretUri=${keyVaultUri}secrets/AZURE-OPENAI-API-KEY)'
            }
            {
              name: 'MODEL_DEPLOYMENT'
              value: '@Microsoft.KeyVault(SecretUri=${keyVaultUri}secrets/MODEL-DEPLOYMENT)'
            }
          ]
          resources: {
            cpu: '0.5'
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
  dependsOn: [
    acrPullRole
    kvSecretsUserRole
  ]
}

output containerAppName string = app.name
output managedEnvironmentName string = cae.name
