# Troubleshooting Document Loading Issues After Project Rename

## Problem

After renaming the project (from "rag-system" to "Cranswick Technical Standards Agent"), document loading may fail because the Azure resources still use the old project name, or the `.env` file is pointing to the wrong resources.

## Root Cause

Azure resources are named based on the `applicationName` parameter in the Bicep deployment. The naming convention is:
- **Search Service**: `{applicationName}-{environment}-search` (e.g., `rag-system-dev-search`)
- **Storage Account**: `{applicationName}{environment}stor` (e.g., `ragsystemdevstor`)
- **Search Index**: Named separately (usually `documents-index`)

When you renamed the project, either:
1. The Azure resources still have the old names, OR
2. New resources were created with new names, but your `.env` file wasn't updated

## Diagnostic Steps

### Step 1: Run the Diagnostic Script

```bash
cd backend
python diagnose_azure_resources.py
```

This script will:
- Show your current environment configuration
- Extract resource names from your endpoints
- Test connections to Azure resources
- Identify if you're pointing to old resources
- Provide specific recommendations

### Step 2: Verify Azure Resources in Portal

1. **Find Your Search Service:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Search for "Search services"
   - Look for services with names containing your project name patterns
   - Note the endpoint URL (e.g., `https://your-service-name.search.windows.net`)

2. **Find Your Storage Account:**
   - Go to Azure Portal
   - Search for "Storage accounts"
   - Look for accounts matching your project
   - Check which container has your documents (usually `documents`)

3. **Verify the Search Index:**
   - Open your Search Service
   - Go to "Indexes"
   - Check the index name (usually `documents-index` or similar)
   - Verify it contains documents

## Solution Options

### Option A: Update .env to Point to Existing Resources (Recommended)

If your Azure resources already exist with the **correct** names:

1. **Get Search Service Details:**
   ```bash
   # In Azure Portal:
   # 1. Open your Search Service
   # 2. Go to "Keys and endpoints"
   # 3. Copy:
   #    - Query endpoint (e.g., https://your-service.search.windows.net)
   #    - Admin key (primary or secondary)
   ```

2. **Get Storage Account Connection String:**
   ```bash
   # In Azure Portal:
   # 1. Open your Storage Account
   # 2. Go to "Access keys"
   # 3. Click "Show" next to key1
   # 4. Copy the "Connection string"
   ```

3. **Update backend/.env file:**
   ```env
   # Update these values:
   AZURE_SEARCH_ENDPOINT=https://your-actual-search-service.search.windows.net
   AZURE_SEARCH_API_KEY=your-actual-admin-key
   AZURE_SEARCH_INDEX_NAME=documents-index  # or your actual index name
   
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-actual-storage;AccountKey=...
   AZURE_STORAGE_CONTAINER_NAME=documents  # or your actual container name
   ```

4. **Test the connection:**
   ```bash
   cd backend
   python check_documents.py
   ```

### Option B: Find Resources Using Azure CLI

If you prefer command line:

```bash
# List all search services
az search service list --query "[].{Name:name, Endpoint:searchServiceName}" --output table

# List all storage accounts
az storage account list --query "[].{Name:name, ResourceGroup:resourceGroup}" --output table

# Get storage connection string
az storage account show-connection-string --name <storage-account-name> --resource-group <resource-group-name>
```

### Option C: Use Existing Resources with Old Names (Quick Fix)

If you want to keep using existing resources with old names:

1. **Keep your current .env file** (if it's pointing to old resources that still work)
2. **OR update .env to point back to old resources:**
   - Get the endpoint/connection string for the OLD resources
   - Update .env accordingly

**Note:** This is fine if the old resources are still working and contain your documents.

## Common Issues and Fixes

### Issue 1: "Index not found" or "404 error"

**Cause:** Index name doesn't match exactly (case-sensitive)

**Fix:**
1. Check exact index name in Azure Portal
2. Update `AZURE_SEARCH_INDEX_NAME` in `.env` to match exactly

### Issue 2: "Service not found" or "NameResolutionFailure"

**Cause:** Search service endpoint points to a service that doesn't exist (old project name)

**Fix:**
1. Find your actual search service in Azure Portal
2. Copy the correct endpoint URL
3. Update `AZURE_SEARCH_ENDPOINT` in `.env`

### Issue 3: "Container not found"

**Cause:** Container name mismatch

**Fix:**
1. Check container name in Azure Portal (Storage Account → Containers)
2. Update `AZURE_STORAGE_CONTAINER_NAME` in `.env`

### Issue 4: "Authentication failed" or "401/403 error"

**Cause:** API key is invalid or expired

**Fix:**
1. Go to Azure Portal → Your Search Service → Keys and endpoints
2. Copy a fresh admin key (primary or secondary)
3. Update `AZURE_SEARCH_API_KEY` in `.env`

### Issue 5: "Storage account not found"

**Cause:** Connection string points to account that doesn't exist (old project name)

**Fix:**
1. Find your actual storage account in Azure Portal
2. Get new connection string (Storage Account → Access keys)
3. Update `AZURE_STORAGE_CONNECTION_STRING` in `.env`

## Verification Checklist

After updating your `.env` file, verify everything works:

- [ ] Run `python backend/diagnose_azure_resources.py` - should show ✅ for all connections
- [ ] Run `python backend/check_documents.py` - should list your documents
- [ ] Test document listing in the frontend - should show documents
- [ ] Test document upload - should work end-to-end
- [ ] Test chat query - should retrieve documents

## Prevention for Future Renames

If you need to rename the project again:

1. **Before renaming:** Document all Azure resource names
2. **After renaming:**
   - Either update `.env` to point to existing resources, OR
   - Redeploy infrastructure with new names and update `.env` accordingly
3. **Test thoroughly:** Verify all endpoints work before deploying

## Getting Help

If you're still having issues:

1. **Check backend logs:**
   - Look for specific error messages
   - Check what endpoints/resources are being accessed

2. **Use the diagnostic script:**
   ```bash
   python backend/diagnose_azure_resources.py
   ```

3. **Check Azure Portal:**
   - Verify resources exist
   - Check resource health
   - Verify you have access permissions

4. **Review environment variables:**
   ```bash
   # Make sure all required variables are set
   cat backend/.env | grep AZURE
   ```

## Quick Reference: Environment Variables

Required variables in `backend/.env`:

```env
# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-admin-key-here
AZURE_SEARCH_INDEX_NAME=documents-index

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=documents
```

**Important:** All values must match your actual Azure resources exactly.
