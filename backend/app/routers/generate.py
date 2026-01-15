"""Document generation API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
import uuid
from datetime import datetime

from app.services.document_generator import DocumentGenerator
from app.services.document_store import DocumentStore
from app.services.embedding_service import EmbeddingService

router = APIRouter()

class DocumentGenerationRequest(BaseModel):
    documentType: Literal[
        'principle', 'risk-assessment', 'method-statement', 'safe-work-procedure',
        'quality-control-plan', 'inspection-checklist', 'training-record',
        'incident-report'
    ] = Field(..., description="Type of document to generate")
    format: Literal['docx', 'pdf', 'markdown'] = Field('docx', description="Output file format")
    title: str = Field(..., min_length=1, max_length=200, description="Document title")
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    projectReference: Optional[str] = Field(None, max_length=100)
    siteLocation: Optional[str] = Field(None, max_length=200)
    author: str = Field(..., min_length=1, max_length=100, description="Document author")
    reviewDate: Optional[str] = None
    version: Optional[str] = Field("1.0", pattern=r'^\d+\.\d+$')
    documentReference: Optional[str] = Field(None, max_length=100, description="Document reference number/code")
    issueDate: Optional[str] = Field(None, description="Issue date in YYYY-MM-DD format")
    layer: Optional[Literal['policy', 'principle', 'sop']] = Field(None, description="Document layer: policy, principle, or sop")
    useStandards: bool = True
    data: dict = Field(..., description="Document-specific data")

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Tags must be 50 characters or less')
        return v

    @validator('data')
    def validate_data(cls, v, values):
        """Validate document-specific data based on document type."""
        doc_type = values.get('documentType')
        if not doc_type:
            return v

        if doc_type == 'principle':
            required_fields = ['brcClause', 'intent', 'riskOfNonCompliance']
            for field in required_fields:
                if field not in v or not v[field]:
                    raise ValueError(f'Missing required field for principle: {field}')

        elif doc_type == 'risk-assessment':
            required_fields = ['activityDescription', 'location']
            for field in required_fields:
                if field not in v or not v[field]:
                    raise ValueError(f'Missing required field for risk assessment: {field}')

        elif doc_type == 'method-statement':
            required_fields = ['activity', 'scope', 'location']
            for field in required_fields:
                if field not in v or not v[field]:
                    raise ValueError(f'Missing required field for method statement: {field}')

        return v

class DocumentGenerationResponse(BaseModel):
    documentId: str
    content: str
    downloadUrl: Optional[str] = None
    message: str
    status: str

@router.post("/document", response_model=DocumentGenerationResponse)
async def generate_document(
    request: DocumentGenerationRequest,
    background_tasks: BackgroundTasks
) -> DocumentGenerationResponse:
    """Generate a document using AI with optional standards integration."""

    try:
        # Generate unique document ID
        document_id = str(uuid.uuid4())

        # Initialize services
        doc_generator = DocumentGenerator()
        doc_store = DocumentStore()

        # Generate the document content
        result = await doc_generator.generate_document(
            document_type=request.documentType,
            title=request.title,
            author=request.author,
            data=request.data,
            use_standards=request.useStandards,
            format=request.format,
            document_reference=request.documentReference,
            issue_date=request.issueDate,
            layer=request.layer
        )

        # Create metadata for storage
        metadata = {
            "id": document_id,
            "title": request.title,
            "documentType": request.documentType,
            "source": "generated",
            "author": request.author,
            "category": request.category,
            "tags": request.tags,
            "projectReference": request.projectReference,
            "siteLocation": request.siteLocation,
            "version": request.version,
            "reviewDate": request.reviewDate,
            "documentReference": request.documentReference,
            "issueDate": request.issueDate,
            "layer": request.layer,
            "uploadedAt": datetime.utcnow().isoformat(),
            "fileType": request.format.lower(),
            "status": "completed"
        }

        # Generate and store the file in background
        background_tasks.add_task(
            doc_store.store_generated_document,
            document_id=document_id,
            content=result["content"],
            metadata=metadata,
            format=request.format
        )

        return DocumentGenerationResponse(
            documentId=document_id,
            content=result["content"],
            message="Document generated successfully",
            status="success"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate document: {str(e)}"
        )

@router.post("/risk-assessment", response_model=DocumentGenerationResponse)
async def generate_risk_assessment(
    request: DocumentGenerationRequest,
    background_tasks: BackgroundTasks
) -> DocumentGenerationResponse:
    """Generate a risk assessment document."""

    if request.documentType != "risk-assessment":
        raise HTTPException(
            status_code=400,
            detail="Document type must be 'risk-assessment' for this endpoint"
        )

    return await generate_document(request, background_tasks)

@router.get("/download/{document_id}")
async def download_generated_document(document_id: str):
    """Download a generated document file."""
    try:
        doc_store = DocumentStore()
        download_url = await doc_store.get_download_url(document_id)

        if not download_url:
            raise HTTPException(status_code=404, detail="Document not found")

        return {"downloadUrl": download_url}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get download URL: {str(e)}"
        )
