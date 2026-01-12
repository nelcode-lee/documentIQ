# How to Get Azure AI Search Admin Key

## What is an Admin Key?

Azure AI Search has two types of keys:
- **Admin Key** - Full access (can create/delete indexes, manage everything)
- **Query Key** - Read-only (can only search, safer for production apps)

You need the **Admin Key** to create indexes.

## Step-by-Step: Get Your Admin Key

### Method 1: Azure Portal

1. **Login to Azure Portal:**
   - Go to https://portal.azure.com
   - Sign in with your Azure account

2. **Navigate to Your Search Service:**
   - Click "All resources" in the left menu (or search in the top bar)
   - Find and click on your Azure AI Search service (e.g., `techstandards`)
   - Or search for "Azure AI Search" → Select your service

3. **Go to Keys:**
   - In the left menu under "Settings", click **"Keys"**
   - You'll see a page with keys displayed

4. **Copy the Admin Key:**
   - You'll see:
     - **Admin Key (primary)** - Use this one! 
     - **Admin Key (secondary)** - Alternative (use if primary doesn't work)
     - **Query Keys** - Don't use these for creating indexes
   - Click "Show" next to "Admin Key (primary)"
   - **Copy the entire key** (it's a long string)

5. **Update Your .env File:**
   - Open `backend/.env`
   - Find the line: `AZURE_SEARCH_API_KEY=...`
   - Replace it with: `AZURE_SEARCH_API_KEY=your-admin-key-here` (paste your copied key)
   - Save the file

### Method 2: Azure CLI

If you have Azure CLI installed:

```bash
az search admin-key show \
  --service-name techstandards \
  --resource-group your-resource-group-name
```

This will show your admin keys.

## Visual Guide

When you're in Azure Portal → Your Search Service → Keys, you'll see something like:

```
Keys and connection strings

Admin Keys
├── Admin Key (primary)
│   Show | Copy
│   Key: ************************************
│   
└── Admin Key (secondary)
    Show | Copy

Query Keys
└── (These are for searching only)
```

## Important Notes

- **Keep your admin key secure** - Don't share it or commit it to git
- The admin key looks like a long random string (e.g., `ABC123XYZ789...`)
- You can regenerate keys if needed (but this will break existing connections)
- For production, consider using query keys for the application after setup

## Verify You Have the Right Key

After updating your `.env` file, run:

```bash
cd backend
python create_search_index.py
```

If it works, you have the right key! ✅

If you get "API key doesn't match", you might have:
- Used a query key instead of admin key
- Copied the key incorrectly
- Used the wrong search service
