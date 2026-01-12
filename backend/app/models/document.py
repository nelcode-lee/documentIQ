"""Document-related data models."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentResponse(BaseModel):
    """Response model for document operations."""
    id: str
    title: str
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    uploadedAt: str
    status: str  # 'processing' | 'completed' | 'error'
    source: Optional[str] = "uploaded"  # 'uploaded' | 'generated'
    fileType: Optional[str] = None  # 'pdf' | 'docx' | 'txt'
    fileSize: Optional[int] = None  # in bytes
    layer: Optional[str] = None  # 'policy' | 'principle' | 'sop'


class UploadResponse(BaseModel):
    """Response model for document upload."""
    id: str
    message: str
    status: str  # 'success' | 'error'
