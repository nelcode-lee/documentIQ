# Update Your .env File with Admin Key

## You Already Have the Variable!

Your `.env` file already has:
```env
AZURE_SEARCH_API_KEY=your-query-key-here
```

## The Issue

The current value appears to be a **Query Key**, not an **Admin Key**. You need to **replace the value** with an admin key.

## Steps to Fix

### 1. Get Your Admin Key

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to: **Your Azure AI Search service** → **Keys**
3. Find **"Admin Key (primary)"**
4. Click **"Show"** and copy the entire key

### 2. Update Your .env File

Open `backend/.env` and **replace** the existing value:

**Before:**
```env
AZURE_SEARCH_API_KEY=your-query-key-here
```

**After:**
```env
AZURE_SEARCH_API_KEY=your-admin-key-from-azure-portal
```

**Important:**
- Keep the variable name `AZURE_SEARCH_API_KEY` (don't change it!)
- Only replace the value after the `=` sign
- Make sure there are no spaces around the `=` sign

### 3. Save and Test

After updating, save the file and run:
```bash
cd backend
python create_search_index.py
```

## Quick Visual Guide

In Azure Portal, you'll see something like:

```
Keys
├── Admin Keys
│   ├── Admin Key (primary)     ← COPY THIS ONE!
│   └── Admin Key (secondary)
│
└── Query Keys
    └── (Don't use these)
```

## Key Differences

- **Admin Key**: Long string, can create/delete indexes, full access
- **Query Key**: Usually shorter, can only search, read-only

The variable name is correct - you just need to use an admin key value instead of a query key value!
