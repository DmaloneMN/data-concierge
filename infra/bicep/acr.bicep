// acr.bicep - Azure Container Registry

targetScope = 'resourceGroup'

param location string
param environmentName string
param namePrefix string = 'dc'

@allowed([
  'Basic'
  'Standard'
  'Premium'
])
@description('ACR SKU. Some subscriptions/regions only support Basic.')
param acrSku string = 'Basic'

// ACR name must be globally unique, 5-50 alphanumeric
var acrName = toLower(replace('${namePrefix}${environmentName}${uniqueString(resourceGroup().id)}', '-', ''))

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: acrSku
  }
  properties: {
    adminUserEnabled: false
    policies: {
      retentionPolicy: {
        status: 'enabled'
        days: 7
      }
    }
  }
}

output acrId string = acr.id
output loginServer string = acr.properties.loginServer
output acrName string = acr.name
