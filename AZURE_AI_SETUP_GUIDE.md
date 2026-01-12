# Azure AI Setup Guide for RAG System

## Architecture Overview

### Do you need a separate vector database?

**No!** Azure AI Search provides everything you need in one service:
- ✅ **Vector storage** - Stores embeddings/vectors
- ✅ **Vector search** - Performs similarity search on vectors
- ✅ **Hybrid search** - Combines keyword + vector search
- ✅ **Semantic search** - Advanced semantic understanding (optional)

### Complete Architecture Flow

```
1. Document Upload
   ↓
2. Backend Processing (Python)
   ├─ Extract text (PyMuPDF, python-docx)
   ├─ Chunk documents (LangChain or custom)
   └─ Generate embeddings (Azure OpenAI)
   ↓
3. Azure AI Search
   ├─ Store vectors + metadata
   ├─ Index for search
   └─ Hybrid search capabilities
   ↓
4. Query Time
   ├─ Generate query embedding (Azure OpenAI)
   ├─ Vector search in Azure AI Search
   ├─ Retrieve top-k chunks
   └─ Send to GPT-4 with context
```

## Azure Services You Need

### 1. Azure OpenAI Service (Required)
**Purpose:** Generate embeddings and LLM responses

**What it provides:**
- `text-embedding-ada-002` - Converts text to vectors (1536 dimensions)
- `gpt-4` or `gpt-35-turbo` - Generates responses

**Cost:** Pay-per-use (tokens used)

### 2. Azure AI Search (Required)
**Purpose:** Vector database + search engine (all-in-one)

**What it provides:**
- Vector storage (no separate DB needed!)
- Vector similarity search
- Keyword search
- Hybrid search (vector + keyword)
- Semantic search (optional)

**Cost:** 
- Free tier: 50MB storage, 3 indexes
- Basic tier: ~$75/month, 2GB storage
- Standard tier: ~$250/month, 25GB storage

### 3. Azure Blob Storage (Required)
**Purpose:** Store original document files

**What it provides:**
- File storage for PDFs, DOCX, etc.
- SAS tokens for secure access

**Cost:** Very low (~$0.02/GB/month)

## Step-by-Step Setup

### Phase 1: Request Access (If Needed)

1. **Check Azure OpenAI Access**
   - Go to https://portal.azure.com
   - Navigate to "Azure OpenAI"
   - If unavailable, submit request at: https://aka.ms/oai/access
   - Approval can take 1-3 business days

### Phase 2: Create Azure Resources

#### A. Azure OpenAI Service

1. **Create Resource:**
   ```
   Azure Portal → Create Resource → "Azure OpenAI"
   ```
   - **Resource Group:** Create new or use existing
   - **Region:** Choose closest (e.g., UK South, East US)
   - **Pricing Tier:** Standard S0 (pay-per-use)
   - **Name:** e.g., `cranswick-openai`

2. **Deploy Models:**
   - Go to Azure OpenAI Studio: https://oai.azure.com
   - Navigate to "Deployments"
   - Click "Create new deployment"
   
   **Deployment 1 - GPT-4:**
   - Model: `gpt-4` or `gpt-4-turbo`
   - Deployment name: `gpt-4` (must match config)
   - Version: Latest
   
   **Deployment 2 - Embeddings:**
   - Model: `text-embedding-ada-002`
   - Deployment name: `text-embedding-ada-002` (must match config)
   - Version: 2

3. **Get Keys:**
   - Azure Portal → Your OpenAI Resource → "Keys and Endpoint"
   - Copy:
     - Endpoint: `https://your-resource.openai.azure.com/`
     - Key 1 or Key 2

#### B. Azure AI Search

1. **Create Resource:**
   ```
   Azure Portal → Create Resource → "Azure AI Search"
   ```
   - **Resource Group:** Same as OpenAI
   - **Region:** Same region as OpenAI (for lower latency)
   - **Pricing Tier:** 
     - **Dev/Testing:** Basic ($75/month)
     - **Production:** Standard ($250/month)
   - **Name:** e.g., `cranswick-search`

2. **Create Index:**
   - Go to Azure Portal → Your Search Service → "Indexes"
   - Click "Add index"
   - Use the schema from `infrastructure/search-index.json`
   - Key fields:
     - `id` - Unique identifier
     - `contentVector` - Vector field (1536 dimensions)
     - `content` - Text content
     - Metadata fields (title, category, etc.)

3. **Configure Semantic Search (Optional but Recommended):**
   - In index creation, enable "Semantic ranking"
   - Requires Standard tier

4. **Get Keys:**
   - Azure Portal → Your Search Service → "Keys"
   - Copy:
     - Endpoint: `https://your-service.search.windows.net`
     - Admin Key (primary or secondary)

#### C. Azure Blob Storage

1. **Create Storage Account:**
   ```
   Azure Portal → Create Resource → "Storage account"
   ```
   - **Resource Group:** Same as above
   - **Performance:** Standard
   - **Redundancy:** LRS (Locally Redundant Storage)
   - **Name:** e.g., `cranswickstorage`

2. **Create Containers:**
   - Go to Storage Account → "Containers"
   - Create: `documents` (for uploaded files)
   - Create: `processed` (for processed chunks, optional)

3. **Get Connection String:**
   - Storage Account → "Access keys"
   - Copy "Connection string" (Key 1)

### Phase 3: Configure Backend

1. **Update Environment Variables:**
   ```bash
   # backend/.env
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-key-here
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
   
   AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
   AZURE_SEARCH_API_KEY=your-admin-key
   AZURE_SEARCH_INDEX_NAME=documents-index
   
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
   AZURE_STORAGE_CONTAINER_NAME=documents
   ```

2. **Test Connections:**
   - Use the Bicep deployment script OR
   - Manually verify in Azure Portal

### Phase 4: Implement Backend Services

The backend services need to be implemented:

1. **DocumentProcessor** (`backend/app/services/document_processor.py`)
   - Extract text from PDF/DOCX
   - Chunk text (512-1024 tokens, 50-100 overlap)
   - Use LangChain's RecursiveCharacterTextSplitter

2. **EmbeddingService** (`backend/app/services/vector_store.py`)
   - Generate embeddings using Azure OpenAI
   - Handle batch requests for efficiency

3. **VectorStoreManager** (`backend/app/services/vector_store.py`)
   - Upload vectors to Azure AI Search
   - Implement search/retrieval methods
   - Handle metadata storage

4. **ChatService** (`backend/app/services/chat_service.py`)
   - Generate query embedding
   - Search Azure AI Search
   - Retrieve top-k chunks
   - Send to GPT-4 with context

## Important Notes

### Vector Database = Azure AI Search
- **No separate vector DB needed!** Azure AI Search handles everything
- It supports up to 30,000 dimensions (we use 1536)
- Provides similarity search with configurable algorithms (HNSW)

### Chunking Happens in Your Code
- Azure AI Search doesn't chunk for you
- Use LangChain or implement custom chunking in Python
- Recommended: 512-1024 tokens per chunk with overlap

### Embedding Generation
- Happens via Azure OpenAI API calls
- Each chunk = 1 API call (or batch calls)
- Cost: ~$0.0001 per 1K tokens

## Cost Estimation (Monthly)

**Development/Testing:**
- Azure OpenAI: ~$50-100 (depending on usage)
- Azure AI Search Basic: $75
- Azure Blob Storage: ~$1-5
- **Total: ~$125-180/month**

**Production:**
- Azure OpenAI: ~$200-500 (higher usage)
- Azure AI Search Standard: $250
- Azure Blob Storage: ~$5-20
- **Total: ~$455-770/month**

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Use Managed Identity** - For production, prefer Azure AD authentication
3. **Enable Private Endpoints** - For production deployments
4. **Rotate keys regularly** - Every 90 days recommended
5. **Use separate keys** - Different keys for dev/prod

## Troubleshooting

### "Resource not found" errors
- Check endpoint URLs are correct (no trailing slashes)
- Verify deployments are created in Azure OpenAI Studio

### "Model not found" errors
- Ensure deployment names match exactly
- Check model is deployed in the correct region

### Search index errors
- Verify index schema matches your code
- Check vector field dimensions (1536 for ada-002)

## Next Steps

1. ✅ Complete the todo list items
2. ✅ Implement backend services (use placeholder code as starting point)
3. ✅ Test with a single document first
4. ✅ Verify embeddings are stored correctly
5. ✅ Test search and retrieval
6. ✅ Integrate with chat interface

## Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/cognitive-services/openai/)
- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)
- [Vector Search in Azure AI Search](https://learn.microsoft.com/azure/search/vector-search-overview)
- [LangChain Azure Integration](https://python.langchain.com/docs/integrations/platforms/azure)
