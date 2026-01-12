# Azure Infrastructure Deployment

This directory contains Bicep templates for deploying the Enterprise RAG System infrastructure to Azure.

## Prerequisites

- Azure CLI installed and configured
- Azure subscription with appropriate permissions
- PowerShell (for deployment script)

## Resources Deployed

The Bicep template deploys the following Azure resources:

1. **Azure OpenAI Service**
   - GPT-4 deployment
   - Text Embedding Ada 002 deployment

2. **Azure AI Search**
   - Vector search enabled
   - Basic SKU (configurable)

3. **Azure Blob Storage**
   - Documents container (original files)
   - Processed container (chunked documents)

4. **Application Insights** (optional)
   - Application monitoring and analytics

## Deployment Options

### Option 1: Using PowerShell Script (Recommended)

```powershell
cd infrastructure
.\deploy.ps1 -ResourceGroupName "rg-rag-system-dev" -Location "uksouth" -Environment "dev"
```

### Option 2: Using Azure CLI Directly

```bash
# Create resource group
az group create --name rg-rag-system-dev --location uksouth

# Deploy Bicep template
az deployment group create \
  --resource-group rg-rag-system-dev \
  --template-file main.bicep \
  --parameters azuredeploy.parameters.json \
  --parameters environment=dev
```

### Option 3: Using Azure Portal

1. Navigate to Azure Portal
2. Create a new resource group
3. Go to "Deploy a custom template"
4. Upload `main.bicep` and `azuredeploy.parameters.json`

## Parameters

Edit `azuredeploy.parameters.json` to customize deployment:

- `applicationName`: Base name for resources
- `location`: Azure region
- `environment`: Environment name (dev, staging, prod)
- `openAiSku`: Azure OpenAI SKU (S0, S1, etc.)
- `searchSku`: Azure AI Search SKU (free, basic, standard)
- `enableApplicationInsights`: Enable Application Insights

## Post-Deployment Steps

After deployment, you need to:

1. **Get OpenAI API Keys:**
   ```bash
   az cognitiveservices account keys list \
     --name <openai-account-name> \
     --resource-group <resource-group-name>
   ```

2. **Get Search Admin Keys:**
   ```bash
   az search admin-key show \
     --service-name <search-service-name> \
     --resource-group <resource-group-name>
   ```

3. **Create Search Index:**
   The search index needs to be created separately. Use the Azure Portal or Azure CLI:
   ```bash
   az search index create \
     --service-name <search-service-name> \
     --resource-group <resource-group-name> \
     --name documents-index \
     --schema @search-index.json
   ```

4. **Update Environment Variables:**
   Copy the output values to your `.env` files in backend and frontend directories.

## Cost Considerations

- **Free Tier**: Use `free` SKU for Azure AI Search (limited to 50MB storage, 2 indexes)
- **Basic Tier**: Recommended for development ($75/month for Search, plus OpenAI usage)
- **Production**: Consider Standard SKU for better performance and scalability

## Cleanup

To delete all resources:

```bash
az group delete --name <resource-group-name> --yes --no-wait
```

## Troubleshooting

- If OpenAI deployment fails, check if OpenAI is available in your region
- Some SKUs may require approval for your subscription
- Ensure you have sufficient quotas for the selected SKUs
