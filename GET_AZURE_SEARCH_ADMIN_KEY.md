# How to Get Azure AI Search Admin Key

## Important: Different from Blob Storage!

- **Azure Blob Storage** = Storage service (has its own keys)
- **Azure AI Search** = Search service (has DIFFERENT keys)

You need the **Azure AI Search** admin key, NOT the Blob Storage key!

## Step-by-Step

1. **Go to Azure Portal:**
   - https://portal.azure.com

2. **Find Your Azure AI Search Service:**
   - In the search bar at the top, type: `techstandards` or `Azure AI Search`
   - Click on your Azure AI Search service
   - **Service name should be:** `techstandards` or similar
   - **Resource type:** Should say "Azure AI Search" or "Search service"

3. **Get the Admin Key:**
   - In the left menu, click **"Keys"**
   - You'll see:
     ```
     Keys
     ├── Admin Keys
     │   ├── Admin Key (primary)    ← USE THIS ONE!
     │   └── Admin Key (secondary)
     └── Query Keys
         └── (Don't use these)
     ```
   - Click **"Show"** next to **"Admin Key (primary)"**
   - **Copy the entire key**

4. **Update Your .env File:**
   - Open `backend/.env`
   - Find: `AZURE_SEARCH_API_KEY=...`
   - Replace with: `AZURE_SEARCH_API_KEY=your-azure-search-admin-key-here`
   - Save the file

5. **Verify:**
   - Run: `python backend/test_admin_key.py`
   - Should say "[SUCCESS] Admin key is working correctly!"

## Visual Difference

- **Blob Storage Keys**: Usually start with something like `DefaultEndpointsProtocol=...` or are shorter
- **Azure AI Search Keys**: Usually longer strings, base64 encoded (often end with `==`)

## Both Services You Need

Your `.env` should have keys for BOTH services:

```env
# Azure AI Search (for vector search)
AZURE_SEARCH_ENDPOINT=https://techstandards.search.windows.net
AZURE_SEARCH_API_KEY=<Azure AI Search Admin Key - GET THIS NOW>

# Azure Blob Storage (for document storage)
AZURE_STORAGE_CONNECTION_STRING=<Blob Storage Connection String - You already have this>
```
