# Enterprise RAG System Design Prompt for Cursor

## Project Overview
Design and implement a complete enterprise-grade RAG (Retrieval-Augmented Generation) system for company technical standards using Microsoft Azure technologies.

## System Requirements

### Technology Stack
- **Backend**: Python (FastAPI or Flask)
- **Frontend**: React with TypeScript, responsive design (Tailwind CSS or Material-UI)
- **Vector Database**: Azure AI Search (formerly Cognitive Search) with vector search capabilities
- **LLM Service**: Azure OpenAI Service
- **Document Storage**: Azure Blob Storage
- **Authentication**: Azure Active Directory (Entra ID)
- **Analytics**: Azure Application Insights
- **Infrastructure**: Azure Container Apps or Azure App Service

## Core Features to Implement

### 1. Backend API (Python)
Create a FastAPI backend with the following components:

**Dependencies to include:**
```
fastapi
uvicorn
azure-search-documents
azure-storage-blob
azure-identity
openai (Azure OpenAI SDK)
langchain
langchain-community
pypdf2 or pymupdf
python-docx
pandas
pydantic
python-multipart
```

**API Endpoints:**
- `POST /api/chat` - Handle chat queries with RAG
- `POST /api/documents/upload` - Upload and ingest documents
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{id}` - Remove documents
- `POST /api/generate/risk-assessment` - Generate risk assessments
- `POST /api/generate/document` - Generate other document types
- `GET /api/analytics` - Retrieve usage analytics
- `GET /api/health` - Health check endpoint

**Key Backend Classes:**
- `VectorStoreManager` - Manage Azure AI Search vector operations
- `DocumentProcessor` - Parse and chunk documents (PDF, DOCX, TXT)
- `EmbeddingService` - Generate embeddings using Azure OpenAI
- `ChatService` - Handle RAG queries with context retrieval
- `DocumentGenerator` - Generate templated documents using LLM
- `AnalyticsService` - Track and aggregate usage metrics

### 2. Frontend Application (React + TypeScript)

**Required Pages/Components:**

**a) Chat Interface (`/chat`)**
- Clean, responsive chat UI with message history
- Streaming responses support
- Source citations display (show which documents were referenced)
- Copy/export conversation feature
- Loading states and error handling

**b) Document Upload/Ingestion (`/documents/upload`)**
- Drag-and-drop file upload
- Support for PDF, DOCX, TXT files
- Batch upload capability
- Upload progress indicators
- Document metadata input (title, category, tags)
- Processing status display

**c) Document Management (`/documents`)**
- Searchable/filterable document list
- Document preview capability
- Delete/archive documents
- View document metadata
- Ingestion status indicators

**d) Document Generation (`/generate`)**
- Template selection dropdown (Risk Assessment, Method Statement, etc.)
- Form-based input for document parameters
- AI-assisted document generation
- Live preview of generated document
- Export to DOCX/PDF
- Save as template option

**e) Analytics Dashboard (`/analytics`)**
- Query volume metrics (daily/weekly/monthly)
- Most queried topics/documents
- User engagement metrics
- Average response time
- Document usage statistics
- Interactive charts (use Recharts or Chart.js)
- Export analytics reports

**f) Navigation & Layout**
- Responsive sidebar navigation
- User profile dropdown (Azure AD integration)
- Dark/light mode toggle
- Mobile-friendly hamburger menu

### 3. Azure Integration Details

**Azure AI Search Setup:**
- Create search index with vector fields
- Configure semantic ranking
- Set up custom analyzers for technical terminology
- Implement hybrid search (keyword + vector)

**Azure OpenAI Integration:**
- Use `text-embedding-ada-002` for embeddings
- Use `gpt-4` or `gpt-35-turbo` for chat completions
- Implement proper error handling and rate limiting
- Add conversation memory/context management

**Azure Blob Storage:**
- Container for original documents
- Container for processed/chunked documents
- Implement SAS token generation for secure access

**Authentication Flow:**
- Implement Azure AD OAuth2 flow
- Protect all API endpoints
- Role-based access control (Admin, User roles)

### 4. RAG Implementation Specifics

**Document Processing Pipeline:**
1. Upload document to Azure Blob Storage
2. Extract text and metadata
3. Chunk documents (chunk size: 512-1024 tokens, overlap: 50-100 tokens)
4. Generate embeddings for each chunk
5. Store in Azure AI Search with metadata
6. Create document index entry

**Query Processing:**
1. Generate embedding for user query
2. Perform vector search in Azure AI Search
3. Retrieve top-k relevant chunks (k=5-10)
4. Construct prompt with retrieved context
5. Send to Azure OpenAI with system prompt
6. Stream response back to frontend
7. Log query and response for analytics

**System Prompt Template:**
```
You are an AI assistant specializing in company technical standards. 
Use the provided context to answer questions accurately. 
If the answer isn't in the context, say so clearly.
Always cite the source documents used.
```

### 5. Document Generation Features

**Risk Assessment Template:**
- Activity description
- Hazard identification
- Risk rating (likelihood × severity)
- Control measures
- Residual risk
- Generated using retrieved relevant standards

**Output Formats:**
- Markdown preview
- Export to DOCX using python-docx
- Export to PDF using reportlab or weasyprint

### 6. Configuration & Environment

**Required Environment Variables:**
```
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT_NAME=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
AZURE_SEARCH_INDEX_NAME=
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_CONTAINER_NAME=
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
```

### 7. Project Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── services/
│   │   │   ├── vector_store.py
│   │   │   ├── document_processor.py
│   │   │   ├── chat_service.py
│   │   │   ├── analytics.py
│   │   │   └── document_generator.py
│   │   ├── routers/
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   ├── generate.py
│   │   │   └── analytics.py
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── tsconfig.json
├── infrastructure/
│   └── azure-deploy.bicep
└── README.md
```

## Implementation Instructions

### Phase 1: Setup & Infrastructure
1. Set up Azure resources (AI Search, OpenAI, Storage, Container Apps)
2. Initialize backend FastAPI project with Azure SDK integrations
3. Initialize React + TypeScript frontend with routing
4. Implement Azure AD authentication

### Phase 2: Core RAG Functionality
1. Build document ingestion pipeline
2. Implement vector search with Azure AI Search
3. Create chat API with context retrieval
4. Build responsive chat interface

### Phase 3: Document Management
1. Implement document upload UI
2. Create document listing and management
3. Add document preview capabilities
4. Implement delete/archive functionality

### Phase 4: Document Generation
1. Create document generation templates
2. Build form-based generation UI
3. Implement AI-assisted content generation
4. Add export functionality (DOCX/PDF)

### Phase 5: Analytics & Monitoring
1. Implement analytics tracking backend
2. Build analytics dashboard with visualizations
3. Add Azure Application Insights integration
4. Create export and reporting features

## Best Practices to Follow

1. **Error Handling**: Implement comprehensive error handling and user-friendly error messages
2. **Loading States**: Show loading indicators for all async operations
3. **Responsive Design**: Ensure all pages work on mobile, tablet, and desktop
4. **Security**: Use Azure Managed Identity where possible, never expose API keys in frontend
5. **Performance**: Implement caching for embeddings and frequently accessed documents
6. **Logging**: Use structured logging for debugging and monitoring
7. **Testing**: Write unit tests for critical backend services
8. **Documentation**: Add inline comments and API documentation (OpenAPI/Swagger)

## Deliverables

1. Fully functional backend API with all endpoints
2. Responsive React frontend with all required pages
3. Docker configuration for both frontend and backend
4. Azure deployment configuration (Bicep or ARM templates)
5. README with setup instructions
6. Environment variable template file
7. Basic unit tests for core services

## Additional Features to Consider

- Multi-language support for documents
- Document versioning
- Collaborative features (comments, sharing)
- Advanced search filters
- Export chat conversations
- Scheduled document re-indexing
- Audit logging for compliance
- Custom document templates management

---

**Start by creating the project structure, setting up the Azure resources, and implementing the core RAG functionality first. Then progressively add features in the order listed above.**