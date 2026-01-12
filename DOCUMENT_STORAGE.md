# Document Storage Architecture

## Overview

This document explains where uploaded and generated documents are stored in the Cranswick Technical Standards Agent system.

---

## Storage Locations

### 1. **Uploaded Documents** 📄

Uploaded documents are stored in **two places** for different purposes:

#### A. **Original Files → Azure Blob Storage**

**Location:** Azure Blob Storage Container  
**Container Name:** `documents` (configurable via `AZURE_STORAGE_CONTAINER_NAME`)  
**Blob Name Format:** `{document_id}.{file_extension}`  
**Example:** `a1b2c3d4-e5f6-7890-abcd-ef1234567890.pdf`

**Purpose:**
- Stores the original uploaded file (PDF, DOCX, TXT)
- Used for:
  - Downloading/viewing the original document
  - Backup/archival
  - Re-processing if needed

**Storage Details:**
- **Service:** Azure Blob Storage
- **Access Tier:** Hot (frequently accessed)
- **Cost:** ~$0.018 per GB/month
- **Connection:** Configured via `AZURE_STORAGE_CONNECTION_STRING` in `.env`

**Code Location:**
```python
# backend/app/routers/documents.py, line 349-362
blob_client = blob_service_client.get_blob_client(
    container=settings.azure_storage_container_name,  # "documents"
    blob=f"{document_id}{file_extension}"
)
blob_client.upload_blob(data, overwrite=True)
```

#### B. **Processed Chunks & Embeddings → Azure AI Search**

**Location:** Azure AI Search Index  
**Index Name:** Configured via `AZURE_SEARCH_INDEX_NAME`  
**Document ID Format:** `{document_id}_{chunk_index}`  
**Example:** `a1b2c3d4-e5f6-7890-abcd-ef1234567890_0`, `a1b2c3d4-e5f6-7890-abcd-ef1234567890_1`, etc.

**Purpose:**
- Stores document chunks (text split into ~500 token pieces)
- Stores vector embeddings for semantic search
- Stores metadata (title, category, tags, page numbers, etc.)
- Used for:
  - Vector similarity search
  - Hybrid search (vector + keyword)
  - Retrieving relevant content for RAG queries

**Storage Details:**
- **Service:** Azure AI Search (formerly Azure Cognitive Search)
- **Content:** 
  - Text chunks (searchable)
  - Vector embeddings (1536 dimensions for `text-embedding-ada-002`)
  - Metadata (JSON format)
- **Index Fields:**
  - `id`: Unique chunk ID
  - `documentId`: Original document ID
  - `content`: Chunk text content
  - `contentVector`: Embedding vector (1536 floats)
  - `title`: Document title
  - `category`: Document category
  - `tags`: Array of tags
  - `chunkIndex`: Chunk position in document
  - `uploadedAt`: Upload timestamp
  - `metadata`: Additional metadata (JSON string)

**Code Location:**
```python
# backend/app/routers/documents.py, line 399-429
# Chunks are uploaded to Azure AI Search index
vector_store.add_documents_batch(documents_to_index)
```

**Processing Flow:**
1. Upload file → Temporary storage
2. Upload original → Azure Blob Storage
3. Extract text → Document processor
4. Chunk text → ~500 token chunks with 125 token overlap
5. Generate embeddings → OpenAI API (`text-embedding-ada-002`)
6. Index chunks → Azure AI Search with vectors

---

### 2. **Generated Documents** 🤖

Generated documents currently store **metadata only** in a local file.

#### A. **Metadata → Local File System**

**Location:** `backend/generated_documents.json`  
**Format:** JSON array of document metadata

**Purpose:**
- Tracks generated document metadata (ID, title, category, tags, creation date)
- **Note:** The actual generated document files are NOT currently stored
- This is a placeholder for future implementation

**Storage Details:**
- **Service:** Local file system (JSON file)
- **Path:** `{backend_directory}/generated_documents.json`
- **Cost:** Free (local storage)
- **Limitation:** Only stores metadata, not actual generated files

**Code Location:**
```python
# backend/app/services/document_store.py
# Simple file-based store for generated document metadata
```

**Example JSON Structure:**
```json
[
  {
    "id": "generated-doc-123",
    "title": "Generated Technical Standard",
    "category": "Safety",
    "tags": ["AI-generated", "2025"],
    "created_at": "2025-01-15T10:30:00",
    "fileType": "pdf",
    "fileSize": 52480
  }
]
```

**Current Limitation:**
- Generated documents are not stored as actual files
- Only metadata is tracked
- Generated documents are shown in the UI but cannot be downloaded
- **Future Enhancement:** Should store generated documents in Azure Blob Storage similar to uploaded documents

---

## Storage Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT UPLOAD FLOW                      │
└─────────────────────────────────────────────────────────────┘

User Uploads File (PDF/DOCX/TXT)
            │
            ▼
    [Temporary Storage]  ← System temp directory
            │
            ├─► [Azure Blob Storage]  ← Original file
            │    Container: "documents"
            │    Blob: "{document_id}.pdf"
            │
            └─► [Processing Pipeline]
                    │
                    ├─► Extract Text
                    ├─► Chunk Text (~500 tokens/chunk)
                    ├─► Generate Embeddings (OpenAI)
                    └─► [Azure AI Search]  ← Processed chunks
                         Index: "{index_name}"
                         Documents: "{document_id}_{chunk_index}"
                         Fields: content, contentVector, metadata


┌─────────────────────────────────────────────────────────────┐
│                 DOCUMENT RETRIEVAL FLOW                      │
└─────────────────────────────────────────────────────────────┘

User Query
    │
    ▼
[Generate Query Embedding]  ← OpenAI API
    │
    ▼
[Azure AI Search]  ← Vector similarity + keyword search
    │              Returns top matching chunks
    ▼
[Build Context]  ← Combine chunks
    │
    ▼
[OpenAI GPT]  ← Generate answer with context
    │
    ▼
[Return Response]  ← With source citations
```

---

## Accessing Stored Documents

### Viewing Documents in Azure Blob Storage

**Option 1: Azure Portal**
1. Go to Azure Portal → Storage Accounts
2. Select your storage account
3. Navigate to Containers → `documents`
4. View/download blobs

**Option 2: Azure Storage Explorer**
- Download Azure Storage Explorer (free desktop app)
- Connect using connection string
- Browse container and download files

**Option 3: Programmatic Access**
```python
from azure.storage.blob import BlobServiceClient

blob_service_client = BlobServiceClient.from_connection_string(
    settings.azure_storage_connection_string
)
blob_client = blob_service_client.get_blob_client(
    container="documents",
    blob=f"{document_id}.pdf"
)

# Download blob
with open("downloaded_file.pdf", "wb") as download_file:
    download_file.write(blob_client.download_blob().readall())
```

### Viewing Documents in Azure AI Search

**Option 1: Azure Portal**
1. Go to Azure Portal → Azure AI Search service
2. Select your search service
3. Navigate to Indexes → Select your index
4. Use "Search explorer" to query documents

**Option 2: API Access**
- Use Search REST API or SDK
- Query by `documentId` to get all chunks for a document
- Use vector search for semantic similarity

**Option 3: Backend API**
- `GET /api/documents` - Lists all documents (reads from both Azure AI Search and Blob Storage)

---

## Storage Configuration

### Environment Variables

**Azure Blob Storage:**
```env
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER_NAME=documents
```

**Azure AI Search:**
```env
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_SEARCH_INDEX_NAME=documents-index
```

### Verifying Storage

**Check Blob Storage:**
```bash
cd backend
python check_documents.py
```

**Check Azure AI Search:**
```python
# Use the backend API
GET http://localhost:8000/api/documents
```

---

## Cost Implications

### Azure Blob Storage
- **Storage:** $0.018/GB/month (Hot tier)
- **Example:** 100 documents @ 5 MB each = 500 MB = ~$0.009/month
- **Very cheap** for document storage

### Azure AI Search
- **Tier:** Basic ($75/month) or higher
- **Storage:** Included in tier (2-200 GB depending on tier)
- **Cost:** Fixed monthly fee + optional overage charges

See `COST_BREAKDOWN.md` for detailed pricing information.

---

## Future Enhancements

### Generated Documents Storage
**Recommended Implementation:**

1. **Store Generated Files in Azure Blob Storage**
   - Save generated PDF/DOCX files to Blob Storage
   - Use separate container: `generated-documents`
   - Maintain metadata in JSON (as currently done) + file reference

2. **Index Generated Documents in Azure AI Search**
   - Process generated documents same as uploaded documents
   - Enable searching/finding generated documents
   - Store embeddings for semantic search

3. **Download Functionality**
   - Add endpoint: `GET /api/documents/{id}/download`
   - Return original file from Blob Storage
   - Works for both uploaded and generated documents

### Suggested Code Changes:

```python
# Store generated document file in Blob Storage
async def save_generated_document(document_id: str, file_content: bytes, file_type: str):
    blob_service_client = BlobServiceClient.from_connection_string(
        settings.azure_storage_connection_string
    )
    blob_client = blob_service_client.get_blob_client(
        container="generated-documents",  # Separate container
        blob=f"{document_id}.{file_type}"
    )
    blob_client.upload_blob(file_content, overwrite=True)
    
    # Also process and index like uploaded documents
    # ... (same processing pipeline as uploaded documents)
```

---

## Summary

| Document Type | Original File Storage | Processed Data Storage | Metadata Storage |
|--------------|---------------------|----------------------|------------------|
| **Uploaded Documents** | ✅ Azure Blob Storage<br>`documents/{id}.pdf` | ✅ Azure AI Search<br>Index with chunks & embeddings | ✅ Azure AI Search<br>In index metadata |
| **Generated Documents** | ❌ Not stored yet | ❌ Not indexed yet | ✅ Local JSON file<br>`generated_documents.json` |

**Key Takeaways:**
1. **Uploaded documents** are fully stored and indexed (original + processed)
2. **Generated documents** only store metadata (future enhancement needed)
3. All storage is in Azure cloud services (except generated doc metadata)
4. Very cost-effective storage (~$0.01-0.10/month for typical usage)
5. Scalable architecture ready for thousands of documents

---

**Last Updated:** January 2025
