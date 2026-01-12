@description('The name of the application')
param applicationName string = 'rag-system'

@description('The Azure region where resources will be deployed')
param location string = resourceGroup().location

@description('The environment (dev, staging, prod)')
param environment string = 'dev'

@description('SKU for Azure OpenAI')
param openAiSku string = 'S0'

@description('Azure OpenAI model deployment name')
param openAiDeploymentName string = 'gpt-4'

@description('Azure OpenAI embedding deployment name')
param openAiEmbeddingDeployment string = 'text-embedding-ada-002'

@description('Search service SKU')
param searchSku string = 'basic'

@description('Enable Application Insights')
param enableApplicationInsights bool = true

// Variables
var resourcePrefix = '${applicationName}-${environment}'
var tags = {
  application: applicationName
  environment: environment
  managedBy: 'bicep'
}

// Azure OpenAI Account
resource openAiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${resourcePrefix}-openai'
  location: location
  kind: 'OpenAI'
  sku: {
    name: openAiSku
  }
  tags: tags
  properties: {
    customSubDomainName: '${toLower(resourcePrefix)}-openai'
    publicNetworkAccess: 'Enabled'
  }
}

// Azure OpenAI Model Deployments
resource gpt4Deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAiAccount
  name: openAiDeploymentName
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4'
      version: '0613'
    }
    sku: {
      name: 'Standard'
      capacity: 10
    }
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAiAccount
  name: openAiEmbeddingDeployment
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-ada-002'
      version: '2'
    }
    sku: {
      name: 'Standard'
      capacity: 10
    }
  }
}

// Azure AI Search
resource searchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: '${toLower(resourcePrefix)}-search'
  location: location
  sku: {
    name: searchSku
  }
  tags: tags
  properties: {
    replicaCount: searchSku == 'free' ? 1 : searchSku == 'basic' ? 1 : 3
    partitionCount: searchSku == 'free' ? 1 : searchSku == 'basic' ? 1 : 3
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      ipRules: []
    }
  }
}

// Storage Account for Blob Storage
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${toLower(replace(resourcePrefix, '-', ''))}stor'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  tags: tags
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

// Blob Service
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

// Blob Containers
resource documentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'documents'
  properties: {
    publicAccess: 'None'
    metadata: {
      description: 'Original uploaded documents'
    }
  }
}

resource processedContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'processed'
  properties: {
    publicAccess: 'None'
    metadata: {
      description: 'Processed and chunked documents'
    }
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = if (enableApplicationInsights) {
  name: '${resourcePrefix}-insights'
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    IngestionMode: 'ApplicationInsights'
    Request_Source: 'rest'
    Flow_Type: 'Redfield'
  }
}

// Outputs
output openAiEndpoint string = openAiAccount.properties.endpoint
output openAiAccountName string = openAiAccount.name
output searchEndpoint string = 'https://${searchService.name}.search.windows.net'
output searchServiceName string = searchService.name
output storageAccountName string = storageAccount.name
output storageConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
output applicationInsightsConnectionString string = enableApplicationInsights ? applicationInsights.properties.ConnectionString : ''
output resourceGroupName string = resourceGroup().name
