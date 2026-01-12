# Using Standard OpenAI API Instead of Azure OpenAI

## Overview

You can use the standard OpenAI API (openai.com) instead of Azure OpenAI to reduce costs. This guide shows you how to configure the system to use OpenAI directly while still using Azure AI Search for vector storage.

## Cost Comparison

### Azure OpenAI
- Requires Azure subscription
- Typically more expensive
- Enterprise features (private endpoints, etc.)

### Standard OpenAI API
- Direct API access
- More cost-effective for most use cases
- Pay-per-use pricing
- No Azure subscription required for OpenAI

## Architecture

```
Document → Backend (Chunking) → OpenAI API (Embeddings) → Azure AI Search (Vector Storage)
                                                           ↓
Query → OpenAI API (Query Embedding) → Azure AI Search → OpenAI API (GPT-4 with context)
```

## Setup Instructions

### 1. Get OpenAI API Key

1. Go to https://platform.openai.com
2. Sign up or log in
3. Navigate to API Keys: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)
6. **Important:** Save it immediately - you can't view it again!

### 2. Check Your API Limits

- Go to https://platform.openai.com/usage
- Ensure you have access to:
  - GPT-4 models (may require approval)
  - Embedding models (text-embedding-ada-002)

### 3. Update Backend Configuration

The configuration has been updated to use standard OpenAI API. Update your `backend/.env`:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4  # or gpt-4-turbo, gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Azure AI Search (still required)
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-key
AZURE_SEARCH_INDEX_NAME=documents-index

# Azure Blob Storage (still required)
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER_NAME=documents
```

### 4. Implementation Changes Needed

The backend services need to be updated to use OpenAI SDK instead of Azure OpenAI SDK. Here's what needs to change:

#### A. Embedding Service

**Before (Azure OpenAI):**
```python
from openai import AzureOpenAI
client = AzureOpenAI(
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    api_version="2024-02-15-preview"
)
```

**After (Standard OpenAI):**
```python
from openai import OpenAI
client = OpenAI(api_key=settings.openai_api_key)

# Generate embedding
response = client.embeddings.create(
    model=settings.openai_embedding_model,
    input=text
)
```

#### B. Chat/Completion Service

**Before (Azure OpenAI):**
```python
response = client.chat.completions.create(
    model=settings.azure_openai_deployment_name,  # This is a deployment name
    messages=messages
)
```

**After (Standard OpenAI):**
```python
response = client.chat.completions.create(
    model=settings.openai_model,  # This is the model name directly
    messages=messages
)
```

### 5. Model Availability

**Embeddings:**
- `text-embedding-ada-002` - Available, cost-effective
- `text-embedding-3-small` - Newer, better performance
- `text-embedding-3-large` - Best quality, higher cost

**Chat Models:**
- `gpt-3.5-turbo` - Cheapest, good for simple queries
- `gpt-4` - Better quality, more expensive
- `gpt-4-turbo` - Latest, best performance

## Cost Estimation (OpenAI API)

### Embeddings
- `text-embedding-ada-002`: $0.0001 per 1K tokens
- `text-embedding-3-small`: $0.00002 per 1K tokens (cheaper!)

### Chat Completions
- `gpt-3.5-turbo`: $0.0015 per 1K input tokens, $0.002 per 1K output tokens
- `gpt-4`: $0.03 per 1K input tokens, $0.06 per 1K output tokens
- `gpt-4-turbo`: $0.01 per 1K input tokens, $0.03 per 1K output tokens

### Example Monthly Costs (1000 queries/month)

**Using gpt-4-turbo + text-embedding-ada-002:**
- Embeddings: ~$1-5
- Chat completions: ~$50-150
- **Total: ~$51-155/month** (much cheaper than Azure OpenAI!)

## Implementation Checklist

- [x] Updated `config.py` to use `OPENAI_API_KEY` instead of Azure OpenAI settings
- [ ] Update `services/vector_store.py` to use standard OpenAI client
- [ ] Update `services/chat_service.py` to use standard OpenAI client  
- [ ] Update `services/document_processor.py` if it uses embeddings
- [ ] Update `.env.example` file
- [ ] Test embedding generation
- [ ] Test chat completions
- [ ] Verify Azure AI Search integration still works

## Key Differences

| Feature | Azure OpenAI | Standard OpenAI |
|---------|-------------|----------------|
| Authentication | Endpoint + Key | API Key only |
| Model Reference | Deployment name | Model name directly |
| Rate Limits | Configurable | Tier-based |
| Data Residency | Azure regions | US/EU options |
| Pricing | Higher | Lower |
| API Version | Required parameter | Latest by default |

## Security Considerations

1. **API Key Storage:**
   - Never commit API keys to git
   - Use environment variables
   - Rotate keys regularly

2. **Rate Limits:**
   - Monitor usage at https://platform.openai.com/usage
   - Implement retry logic with exponential backoff
   - Consider rate limiting in your application

3. **Data Privacy:**
   - Standard OpenAI may use data for training (check terms)
   - For sensitive data, consider Azure OpenAI or use data opt-out
   - Review OpenAI's data usage policy

## Migration Steps

1. ✅ Get OpenAI API key
2. ✅ Update environment variables
3. ⏳ Update backend service implementations
4. ⏳ Test embedding generation
5. ⏳ Test chat functionality
6. ⏳ Verify end-to-end flow

## Next Steps

Once you have your OpenAI API key, update your `backend/.env` file and we can update the service implementations to use the standard OpenAI API instead of Azure OpenAI.
