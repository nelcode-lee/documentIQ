"""Document store for tracking and storing generated documents."""

from typing import List, Dict, Optional
from datetime import datetime
import json
import os
import io
from app.config import settings

try:
    from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
    from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("Azure Storage libraries not available. Using local storage only.")

try:
    from docx import Document as DocxDocument
    from docx.shared import Inches
    import markdown
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("python-docx not available. DOCX generation disabled.")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("reportlab not available. PDF generation disabled.")


class DocumentStore:
    """Document store for tracking and storing generated documents with Azure Blob Storage support."""

    def __init__(self, store_file: str = "generated_documents.json"):
        """Initialize document store."""
        self.store_file = store_file
        self.store_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            store_file
        )

        # Azure Blob Storage setup
        self.blob_service_client = None
        self.generated_container = "generated-documents"

        if AZURE_AVAILABLE and settings.azure_storage_connection_string:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    settings.azure_storage_connection_string
                )
                # Ensure container exists
                self._ensure_container_exists()
            except Exception as e:
                print(f"Failed to initialize Azure Blob Storage: {e}")
                self.blob_service_client = None
    
    def _load_documents(self) -> List[Dict]:
        """Load documents from file."""
        if not os.path.exists(self.store_path):
            return []
        
        try:
            with open(self.store_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading document store: {e}")
            return []
    
    def _save_documents(self, documents: List[Dict]):
        """Save documents to file."""
        try:
            with open(self.store_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving document store: {e}")
    
    def add_document(self, document: Dict) -> bool:
        """Add a generated document to the store."""
        try:
            documents = self._load_documents()
            
            # Check if document already exists
            doc_id = document.get("id")
            documents = [d for d in documents if d.get("id") != doc_id]
            
            # Add new document
            document["created_at"] = datetime.utcnow().isoformat()
            documents.append(document)
            
            self._save_documents(documents)
            return True
        except Exception as e:
            print(f"Error adding document to store: {e}")
            return False
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """Get a document by ID."""
        documents = self._load_documents()
        for doc in documents:
            if doc.get("id") == document_id:
                return doc
        return None
    
    def list_documents(self) -> List[Dict]:
        """List all generated documents."""
        return self._load_documents()
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the store."""
        try:
            documents = self._load_documents()
            documents = [d for d in documents if d.get("id") != document_id]
            self._save_documents(documents)

            # Also delete from blob storage if available
            if self.blob_service_client:
                try:
                    blob_client = self.blob_service_client.get_blob_client(
                        container=self.generated_container,
                        blob=f"{document_id}.docx"
                    )
                    blob_client.delete_blob()
                except Exception as e:
                    print(f"Warning: Could not delete blob for {document_id}: {e}")

            return True
        except Exception as e:
            print(f"Error deleting document from store: {e}")
            return False

    def _ensure_container_exists(self):
        """Ensure the generated documents container exists."""
        if not self.blob_service_client:
            return

        try:
            self.blob_service_client.create_container(self.generated_container)
        except ResourceExistsError:
            pass  # Container already exists
        except Exception as e:
            print(f"Warning: Could not create container {self.generated_container}: {e}")

    async def store_generated_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict,
        format: str = "docx"
    ) -> Optional[str]:
        """
        Store a generated document in blob storage and return download URL.

        Args:
            document_id: Unique document identifier
            content: Document content (markdown text)
            metadata: Document metadata
            format: File format (docx, pdf, markdown)

        Returns:
            Download URL if successful, None otherwise
        """
        try:
            # Generate the file content
            if format.lower() == "docx" and DOCX_AVAILABLE:
                file_content = self._generate_docx(content, metadata)
                filename = f"{document_id}.docx"
                content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif format.lower() == "pdf" and PDF_AVAILABLE:
                file_content = self._generate_pdf(content, metadata)
                filename = f"{document_id}.pdf"
                content_type = "application/pdf"
            else:
                # Default to markdown
                file_content = content.encode('utf-8')
                filename = f"{document_id}.md"
                content_type = "text/markdown"

            # Store in Azure Blob Storage if available
            if self.blob_service_client:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.generated_container,
                    blob=filename
                )

                blob_client.upload_blob(
                    file_content,
                    blob_type="BlockBlob",
                    content_type=content_type,
                    metadata={
                        "document_id": document_id,
                        "title": metadata.get("title", ""),
                        "author": metadata.get("author", ""),
                        "document_type": metadata.get("documentType", ""),
                        "created_at": metadata.get("uploadedAt", datetime.utcnow().isoformat())
                    },
                    overwrite=True
                )

                # Generate SAS URL for download
                download_url = self._generate_download_url(filename)
            else:
                # Fallback to local storage
                local_path = os.path.join(
                    os.path.dirname(self.store_path),
                    "generated_docs",
                    filename
                )
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                if isinstance(file_content, bytes):
                    with open(local_path, 'wb') as f:
                        f.write(file_content)
                else:
                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)

                download_url = f"/api/documents/download/{document_id}"

            # Store metadata locally
            doc_record = {
                "id": document_id,
                "title": metadata.get("title", ""),
                "filename": filename,
                "download_url": download_url,
                "format": format,
                "created_at": datetime.utcnow().isoformat(),
                **metadata
            }
            self.add_document(doc_record)

            return download_url

        except Exception as e:
            print(f"Error storing generated document {document_id}: {e}")
            return None

    def _generate_docx(self, content: str, metadata: Dict) -> bytes:
        """Generate a DOCX file from markdown content."""
        if not DOCX_AVAILABLE:
            raise Exception("python-docx not available")

        doc = DocxDocument()

        # Add title
        title = metadata.get("title", "Generated Document")
        doc.add_heading(title, 0)

        # Add metadata
        doc.add_paragraph(f"Author: {metadata.get('author', 'Unknown')}")
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.add_paragraph(f"Type: {metadata.get('documentType', 'Document')}")

        # Convert markdown to docx
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            elif line.startswith('# '):
                doc.add_heading(line[2:], 1)
            elif line.startswith('## '):
                doc.add_heading(line[3:], 2)
            elif line.startswith('### '):
                doc.add_heading(line[4:], 3)
            elif line.startswith('- ') or line.startswith('* '):
                doc.add_paragraph(line[2:], style='List Bullet')
            elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
                doc.add_paragraph(line, style='List Number')
            else:
                doc.add_paragraph(line)

        # Save to bytes
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def _generate_pdf(self, content: str, metadata: Dict) -> bytes:
        """Generate a PDF file from markdown content."""
        if not PDF_AVAILABLE:
            raise Exception("reportlab not available")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title = metadata.get("title", "Generated Document")
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 12))

        # Metadata
        story.append(Paragraph(f"Author: {metadata.get('author', 'Unknown')}", styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Type: {metadata.get('documentType', 'Document')}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Content
        lines = content.split('\n')
        current_paragraph = ""
        in_list = False

        for line in lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, styles['Normal']))
                    story.append(Spacer(1, 6))
                    current_paragraph = ""
                continue
            elif line.startswith('# '):
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, styles['Normal']))
                    current_paragraph = ""
                story.append(Paragraph(line[2:], styles['Heading1']))
                story.append(Spacer(1, 6))
            elif line.startswith('## '):
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, styles['Normal']))
                    current_paragraph = ""
                story.append(Paragraph(line[3:], styles['Heading2']))
                story.append(Spacer(1, 6))
            elif line.startswith('- ') or line.startswith('* '):
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, styles['Normal']))
                    current_paragraph = ""
                story.append(Paragraph(f"• {line[2:]}", styles['Normal']))
                story.append(Spacer(1, 3))
            elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, styles['Normal']))
                    current_paragraph = ""
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 3))
            else:
                current_paragraph += line + " "

        if current_paragraph:
            story.append(Paragraph(current_paragraph, styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _generate_download_url(self, filename: str) -> str:
        """Generate a SAS URL for downloading the blob."""
        if not self.blob_service_client:
            return f"/api/generate/download/{filename}"

        try:
            from datetime import datetime, timedelta
            from azure.storage.blob import BlobSasPermissions, generate_blob_sas

            # Generate SAS token valid for 24 hours
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=self.generated_container,
                blob_name=filename,
                account_key=self.blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=24)
            )

            return f"{self.blob_service_client.primary_endpoint}{self.generated_container}/{filename}?{sas_token}"

        except Exception as e:
            print(f"Error generating SAS URL: {e}")
            return f"/api/generate/download/{filename}"

    async def get_download_url(self, document_id: str) -> Optional[str]:
        """Get download URL for a generated document."""
        # First check local store
        doc = self.get_document(document_id)
        if doc and doc.get("download_url"):
            return doc["download_url"]

        # If not found locally and blob storage available, try to generate URL
        if self.blob_service_client:
            try:
                # Check if blob exists
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.generated_container,
                    blob=f"{document_id}.docx"
                )

                if blob_client.exists():
                    return self._generate_download_url(f"{document_id}.docx")

                # Try other formats
                for ext in ['.pdf', '.md']:
                    blob_client = self.blob_service_client.get_blob_client(
                        container=self.generated_container,
                        blob=f"{document_id}{ext}"
                    )
                    if blob_client.exists():
                        return self._generate_download_url(f"{document_id}{ext}")

            except Exception as e:
                print(f"Error checking blob existence: {e}")

        return None


# Global instance
document_store = DocumentStore()
