# Azure AI Search Index Setup

## Important: Admin Key Required

To create an index, you need an **ADMIN KEY**, not a query key.

### Get Your Admin Key:

1. **Go to Azure Portal:**
   - Navigate to your Azure AI Search service
   - Or go directly: https://portal.azure.com → Your Search Service

2. **Go to Keys Section:**
   - In the left menu, click "Keys"
   - You'll see:
     - **Admin Key (primary)** - Use this one
     - **Admin Key (secondary)** - Alternative
     - Query keys - These won't work for creating indexes

3. **Copy the Admin Key:**
   - Click "Show" next to Admin Key (primary)
   - Copy the full key

4. **Update Your .env File:**
   ```env
   AZURE_SEARCH_API_KEY=your-admin-key-here
   ```

5. **Run the Script Again:**
   ```bash
   cd backend
   python create_search_index.py
   ```

## Key Types Explained

- **Admin Key**: Can create/delete indexes, manage everything (what you need now)
- **Query Key**: Can only search, cannot modify indexes (for production apps)

## After Creating the Index

Once the index is created, you can optionally switch to a query key for your application (more secure), or keep using the admin key for simplicity.
