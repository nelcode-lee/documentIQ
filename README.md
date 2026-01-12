# Enterprise RAG System

An enterprise-grade Retrieval-Augmented Generation (RAG) system for company technical standards using Microsoft Azure technologies.

## 🚀 Project Overview

This system enables organizations to:
- Upload and manage technical standards documents (PDF, DOCX, TXT)
- Query documents using natural language with AI-powered responses
- Generate templated documents (Risk Assessments, Method Statements, etc.)
- Track usage analytics and document engagement
- Maintain secure, scalable document management

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.11+ with FastAPI
- Azure AI Search (vector search)
- Azure OpenAI Service (GPT-4, embeddings)
- Azure Blob Storage
- LangChain for RAG orchestration

**Frontend:**
- React 19 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- React Router for navigation
- Recharts for analytics visualization

**Infrastructure:**
- Docker & Docker Compose for local development
- Azure Container Apps / App Service for hosting
- Azure Application Insights for monitoring

## 📋 Prerequisites

- **Python 3.11+** (for backend development)
- **Node.js 20+** (for frontend development)
- **Docker & Docker Compose** (for containerized deployment)
- **Azure CLI** (for Azure deployments)
- **Azure Subscription** with:
  - Azure OpenAI Service access
  - Azure AI Search
  - Azure Blob Storage
  - Azure Container Apps (optional)

## 🔧 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Cranswick Technical Standards Agent"
```

### 2. Set Up Azure Resources

Deploy Azure infrastructure using Bicep templates:

```powershell
cd infrastructure
.\deploy.ps1 -ResourceGroupName "rg-rag-system-dev" -Location "uksouth" -Environment "dev"
```

Follow the post-deployment steps to retrieve API keys and connection strings.

See [infrastructure/README.md](infrastructure/README.md) for detailed instructions.

### 3. Configure Environment Variables

**Backend:**
```bash
cd backend
copy .env.example .env
```

Edit `backend/.env` with your Azure credentials:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-key
AZURE_SEARCH_INDEX_NAME=documents-index
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER_NAME=documents
```

**Frontend:**
```bash
cd frontend
copy .env.example .env
```

Edit `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 4. Local Development Setup

#### Option A: Using Docker Compose (Recommended)

**Development mode with hot-reload:**
```bash
docker-compose -f docker-compose.dev.yml up
```

**Production-like mode:**
```bash
docker-compose up
```

#### Option B: Native Development

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 📁 Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── config.py       # Configuration settings
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic services
│   │   │   ├── vector_store.py
│   │   │   ├── document_processor.py
│   │   │   ├── chat_service.py
│   │   │   ├── analytics.py
│   │   │   └── document_generator.py
│   │   ├── routers/        # API route handlers
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   ├── generate.py
│   │   │   └── analytics.py
│   │   └── utils/          # Utility functions
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container image
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   │   ├── Chat.tsx
│   │   │   ├── Documents.tsx
│   │   │   ├── Upload.tsx
│   │   │   ├── Generate.tsx
│   │   │   └── Analytics.tsx
│   │   ├── services/       # API client
│   │   ├── hooks/          # Custom React hooks
│   │   ├── types/          # TypeScript definitions
│   │   └── App.tsx         # Main app component
│   ├── package.json        # Node dependencies
│   └── Dockerfile          # Frontend container image
│
├── infrastructure/         # Azure infrastructure as code
│   ├── main.bicep          # Main Bicep template
│   ├── deploy.ps1          # Deployment script
│   └── search-index.json   # Azure AI Search index schema
│
├── docker-compose.yml      # Production-like compose file
├── docker-compose.dev.yml  # Development compose file
└── README.md              # This file
```

## 🔑 Key Features

### 1. Document Ingestion
- Upload PDF, DOCX, and TXT files
- Automatic text extraction and chunking
- Embedding generation using Azure OpenAI
- Vector storage in Azure AI Search
- Metadata indexing

### 2. Chat Interface
- Natural language queries
- Context-aware responses using RAG
- Source document citations
- Conversation history
- Streaming responses

### 3. Document Management
- Browse and search documents
- View document metadata
- Delete/archive documents
- Document preview

### 4. Document Generation
- AI-assisted document creation
- Templates (Risk Assessments, Method Statements)
- Export to DOCX/PDF
- Preview before export

### 5. Analytics Dashboard
- Query volume metrics
- Most queried documents
- User engagement tracking
- Response time analytics
- Exportable reports

## 🔐 Security

- Azure AD (Entra ID) integration for authentication
- Secure API key management via environment variables
- Private blob storage access
- CORS configuration
- Role-based access control (RBAC) ready

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Building for Production

### Backend
```bash
cd backend
docker build -t rag-backend:latest .
```

### Frontend
```bash
cd frontend
npm run build
docker build -t rag-frontend:latest .
```

## 🚢 Deployment

### Azure Container Apps (Recommended)

1. Build and push images to Azure Container Registry:
```bash
az acr build --registry <acr-name> --image rag-backend:latest backend/
az acr build --registry <acr-name> --image rag-frontend:latest frontend/
```

2. Deploy using Azure Container Apps
3. Configure environment variables
4. Set up custom domains

See Azure documentation for detailed deployment steps.

### Alternative: Azure App Service

Deploy as containerized apps to Azure App Service using the Dockerfiles provided.

## 📊 Monitoring

- **Application Insights**: Integrated for application monitoring
- **Health Checks**: Available at `/api/health`
- **Logging**: Structured logging for debugging

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## 📝 API Documentation

Once the backend is running, access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🐛 Troubleshooting

### Backend won't start
- Check environment variables are set correctly
- Verify Azure credentials are valid
- Ensure Python 3.11+ is installed

### Frontend can't connect to backend
- Verify `VITE_API_BASE_URL` in frontend `.env`
- Check CORS settings in backend `config.py`
- Ensure backend is running on the correct port

### Azure AI Search index issues
- Verify the index is created (use `search-index.json`)
- Check index name matches configuration
- Ensure vector fields are configured correctly

### Docker build failures
- Clear Docker cache: `docker system prune -a`
- Check Dockerfile syntax
- Verify all required files are present

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/cognitive-services/openai/)
- [LangChain Documentation](https://python.langchain.com/)

## 📄 License

[Specify your license here]

## 👥 Authors

[Your name/team]

## 🙏 Acknowledgments

- Azure OpenAI Service
- LangChain framework
- FastAPI community
- React community

---

**Note**: This is an enterprise application. Ensure proper security configurations and compliance measures are in place before production deployment.
