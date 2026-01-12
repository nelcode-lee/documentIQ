"""Document management API endpoints."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List
from app.models.document import DocumentResponse, UploadResponse
from pydantic import BaseModel
import uuid
import os
import tempfile
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from app.config import settings
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreManager
from app.services.document_store import document_store


class LinkDocumentsRequest(BaseModel):
    """Request model for linking documents."""
    relatedDocumentIds: List[str]

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    layer: Optional[str] = Form(None),  # 'policy' | 'principle' | 'sop'
):
    """
    Upload and ingest a document.
    
    This endpoint:
    1. Saves file temporarily
    2. Uploads to Azure Blob Storage
    3. Processes document in background:
       - Extracts text content
       - Chunks the document intelligently
       - Generates embeddings
       - Stores in Azure AI Search
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_extension = '.' + (file.filename or '').split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} is not supported. Allowed types: {', '.join(allowed_extensions)}"
            )

        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Use filename as title if not provided
        document_title = title or file.filename or 'Untitled Document'
        
        # Parse tags if provided
        document_tags = []
        if tags:
            try:
                import json
                document_tags = json.loads(tags)
            except:
                # If not JSON, treat as comma-separated
                document_tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

        # Save file temporarily for processing
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"{document_id}{file_extension}")
        
        try:
            # Save uploaded file to temp location
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Validate layer if provided
            valid_layers = ['policy', 'principle', 'sop', None]
            if layer and layer not in valid_layers:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid layer '{layer}'. Must be one of: policy, principle, sop"
                )
            
            # Process document in background
            background_tasks.add_task(
                process_document_task,
                temp_file_path=temp_file_path,
                document_id=document_id,
                document_title=document_title,
                category=category,
                tags=document_tags,
                layer=layer,  # Pass layer to processing task
                file_extension=file_extension,
                original_filename=file.filename
            )
            
            return UploadResponse(
                id=document_id,
                message=f"Document '{document_title}' uploaded successfully. Processing will begin shortly.",
                status="processing"
            )
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error saving uploaded file: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )


@router.get("/")
async def list_documents(layer: Optional[str] = None) -> List[DocumentResponse]:
    """
    List all documents from Azure AI Search and Blob Storage.
    
    Fetches unique documents by grouping chunks by documentId,
    and includes metadata from both Azure AI Search and Blob Storage.
    """
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        from azure.storage.blob import BlobServiceClient
        import json
        
        # Initialize clients
        search_credential = AzureKeyCredential(settings.azure_search_api_key)
        search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=search_credential
        )
        
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        container_client = blob_service_client.get_container_client(
            settings.azure_storage_container_name
        )
        
        # Optimize: Fetch limited chunks and extract unique documents
        # This is much faster than fetching all 402 chunks
        results = search_client.search(
            search_text="*",
            top=500,  # Limit to 500 chunks for faster response (covers all documents)
            select=["documentId", "title", "category", "tags", "metadata", "uploadedAt", "layer"]
        )
        
        # Convert to list to avoid lazy iteration issues
        results_list = list(results)
        print(f"[INFO] Retrieved {len(results_list)} chunks from search index")
        
        # Group by documentId (take first chunk of each document for metadata)
        documents_dict = {}
        seen_doc_ids = set()
        
        for result in results_list:
            doc_id = result.get("documentId")
            if not doc_id:
                continue
            
            # Only process the first chunk we see for each document (they all have same metadata)
            if doc_id in seen_doc_ids:
                continue
            
            seen_doc_ids.add(doc_id)
            
            # Parse metadata
            metadata_str = result.get("metadata")
            metadata = {}
            if metadata_str:
                try:
                    metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
                except:
                    pass
            
            # Get uploadedAt from result or metadata
            uploaded_at = result.get("uploadedAt")
            if not uploaded_at and metadata.get("processed_at"):
                uploaded_at = metadata.get("processed_at")
            
            # Extract layer from result or metadata
            layer = result.get("layer")
            if not layer and metadata.get("layer"):
                layer = metadata.get("layer")
            
            documents_dict[doc_id] = {
                "id": doc_id,
                "title": result.get("title", "Untitled Document"),
                "category": result.get("category"),
                "tags": result.get("tags", []),
                "layer": layer,  # Extract layer from result or metadata
                "uploadedAt": uploaded_at.isoformat() if hasattr(uploaded_at, 'isoformat') else (
                    uploaded_at if isinstance(uploaded_at, str) else datetime.utcnow().isoformat()
                ),
                "status": "completed",
                "source": "uploaded",
                "metadata": metadata
            }
        
        # Get file information from Blob Storage
        blob_list = container_client.list_blobs()
        blob_dict = {}
        for blob in blob_list:
            blob_dict[blob.name] = {
                "fileSize": blob.size,
                "lastModified": blob.last_modified.isoformat() if hasattr(blob.last_modified, 'isoformat') else None,
                "fileType": blob.name.split('.')[-1].lower() if '.' in blob.name else None
            }
        
        # Merge blob metadata with document info
        documents_list = []
        for doc_id, doc_info in documents_dict.items():
            # Apply layer filter if specified
            if layer and doc_info.get("layer") != layer:
                continue
            
            # Try to find blob for this document
            # Blob name format: {document_id}.{extension}
            blob_info = None
            for blob_name, blob_data in blob_dict.items():
                if blob_name.startswith(doc_id):
                    blob_info = blob_data
                    break
            
            # Build document response
            doc_response = DocumentResponse(
                id=doc_info["id"],
                title=doc_info["title"],
                category=doc_info.get("category"),
                tags=doc_info.get("tags", []),
                layer=doc_info.get("layer"),  # Include layer
                uploadedAt=doc_info["uploadedAt"],
                status=doc_info["status"],
                source=doc_info.get("source", "uploaded"),
                fileType=blob_info.get("fileType") if blob_info else None,
                fileSize=blob_info.get("fileSize") if blob_info else None
            )
            
            documents_list.append(doc_response)
        
        # Also get generated documents
        generated_docs = document_store.list_documents()
        for gen_doc in generated_docs:
            doc_response = DocumentResponse(
                id=gen_doc.get("id", ""),
                title=gen_doc.get("title", "Untitled Document"),
                category=gen_doc.get("category"),
                tags=gen_doc.get("tags", []),
                uploadedAt=gen_doc.get("created_at", datetime.utcnow().isoformat()),
                status="completed",
                source="generated",
                fileType=gen_doc.get("fileType"),
                fileSize=gen_doc.get("fileSize")
            )
            documents_list.append(doc_response)
        
        # Sort by uploadedAt (newest first)
        documents_list.sort(
            key=lambda x: x.uploadedAt,
            reverse=True
        )
        
        print(f"[INFO] Returning {len(documents_list)} documents from list_documents endpoint")
        return documents_list
        
    except Exception as e:
        print(f"[ERROR] Error listing documents: {e}")
        import traceback
        traceback.print_exc()
        # Return empty list on error rather than failing completely
        return []


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document completely.
    
    This will:
    1. Remove all chunks from Azure AI Search
    2. Remove original file from Azure Blob Storage
    3. Remove from generated documents store if applicable
    """
    try:
        from app.services.vector_store import VectorStoreManager
        from app.services.document_store import document_store
        import os
        
        deleted_items = []
        errors = []
        
        # 1. Delete from Azure AI Search (all chunks)
        try:
            vector_store = VectorStoreManager()
            success = await vector_store.delete_document(document_id)
            if success:
                deleted_items.append("Azure AI Search chunks")
            else:
                errors.append("Failed to delete from Azure AI Search")
        except Exception as e:
            print(f"[ERROR] Failed to delete from Azure AI Search: {e}")
            errors.append(f"Azure AI Search: {str(e)}")
        
        # 2. Delete from Azure Blob Storage
        try:
            blob_service_client = BlobServiceClient.from_connection_string(
                settings.azure_storage_connection_string
            )
            container_client = blob_service_client.get_container_client(
                settings.azure_storage_container_name
            )
            
            # Find and delete all blobs that start with document_id
            blobs_to_delete = []
            for blob in container_client.list_blobs():
                if blob.name.startswith(document_id):
                    blobs_to_delete.append(blob.name)
            
            for blob_name in blobs_to_delete:
                try:
                    blob_client = container_client.get_blob_client(blob_name)
                    blob_client.delete_blob()
                    deleted_items.append(f"Blob: {blob_name}")
                except Exception as e:
                    errors.append(f"Blob {blob_name}: {str(e)}")
                    
        except Exception as e:
            print(f"[ERROR] Failed to delete from Blob Storage: {e}")
            errors.append(f"Blob Storage: {str(e)}")
        
        # 3. Delete from generated documents store if it exists
        try:
            document_store.delete_document(document_id)
            deleted_items.append("Generated documents metadata")
        except Exception as e:
            # Not an error if document doesn't exist in generated store
            pass
        
        if errors and not deleted_items:
            # Complete failure
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete document: {'; '.join(errors)}"
            )
        elif errors:
            # Partial success
            return {
                "message": f"Document {document_id} partially deleted",
                "status": "partial",
                "deleted_items": deleted_items,
                "errors": errors
            }
        else:
            # Complete success
            return {
                "message": f"Document {document_id} deleted successfully",
                "status": "success",
                "deleted_items": deleted_items
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )


@router.put("/{document_id}")
async def update_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
):
    """
    Update a document.
    
    This endpoint allows updating:
    1. Document metadata (title, category, tags) - if no file provided
    2. Complete document replacement - if file provided (deletes old, uploads new)
    
    If a file is provided, it will:
    1. Delete old document from Azure AI Search and Blob Storage
    2. Upload new file
    3. Re-process the document
    """
    try:
        from app.services.vector_store import VectorStoreManager
        
        # If file is provided, replace the entire document
        if file:
            # Validate file type
            allowed_extensions = ['.pdf', '.docx', '.txt']
            file_extension = '.' + (file.filename or '').split('.')[-1].lower()
            
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file_extension} is not supported. Allowed types: {', '.join(allowed_extensions)}"
                )
            
            # Delete old document first
            try:
                # Delete from Azure AI Search
                vector_store = VectorStoreManager()
                await vector_store.delete_document(document_id)
                
                # Delete from Blob Storage
                blob_service_client = BlobServiceClient.from_connection_string(
                    settings.azure_storage_connection_string
                )
                container_client = blob_service_client.get_container_client(
                    settings.azure_storage_container_name
                )
                
                for blob in container_client.list_blobs():
                    if blob.name.startswith(document_id):
                        blob_client = container_client.get_blob_client(blob.name)
                        blob_client.delete_blob()
                        print(f"[OK] Deleted old blob: {blob.name}")
            except Exception as e:
                print(f"[WARNING] Error deleting old document (continuing with update): {e}")
            
            # Save new file temporarily
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, f"{document_id}_update{file_extension}")
            
            try:
                # Save uploaded file to temp location
                with open(temp_file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                # Use provided title or filename
                document_title = title or file.filename or 'Untitled Document'
                
                # Parse tags
                document_tags = []
                if tags:
                    try:
                        import json
                        document_tags = json.loads(tags)
                    except:
                        document_tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
                
                # Validate layer if provided
                if layer and layer not in ['policy', 'principle', 'sop']:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid layer '{layer}'. Must be one of: policy, principle, sop"
                    )
                
                # Process new document in background
                background_tasks.add_task(
                    process_document_task,
                    temp_file_path=temp_file_path,
                    document_id=document_id,  # Keep same ID
                    document_title=document_title,
                    category=category,
                    tags=document_tags,
                    layer=layer,  # Pass layer to processing task
                    file_extension=file_extension,
                    original_filename=file.filename
                )
                
                return {
                    "message": f"Document '{document_title}' update started. Processing will begin shortly.",
                    "status": "processing",
                    "id": document_id
                }
            except Exception as e:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error saving updated file: {str(e)}"
                )
        else:
            # Update metadata only (no file replacement)
            # This requires updating all chunks in Azure AI Search with new metadata
            try:
                # Parse tags if provided
                document_tags = []
                if tags:
                    try:
                        import json
                        document_tags = json.loads(tags)
                    except:
                        document_tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
                
                vector_store = VectorStoreManager()
                
                # Search for all chunks of this document
                search_client = vector_store.search_client
                search_results = search_client.search(
                    search_text="*",
                    filter=f"documentId eq '{document_id}'",
                    select=["id", "content", "contentVector", "chunkIndex", "metadata", "title", "category", "tags", "uploadedAt"]
                )
                
                # Collect chunks to update
                chunks_to_update = []
                for result in search_results:
                    # Parse existing metadata
                    metadata_str = result.get("metadata")
                    existing_metadata = {}
                    if metadata_str:
                        try:
                            existing_metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
                        except:
                            pass
                    
                    # Update layer if provided, otherwise keep existing
                    updated_layer = layer if layer is not None else result.get("layer")
                    if not updated_layer and metadata.get("layer"):
                        updated_layer = metadata.get("layer")
                    
                    # Update document metadata
                    updated_doc = {
                        "id": result.get("id"),
                        "documentId": document_id,
                        "content": result.get("content"),
                        "contentVector": result.get("contentVector"),
                        "title": updated_title,
                        "category": updated_category,
                        "tags": updated_tags,
                        "layer": updated_layer,  # Include updated layer
                        "chunkIndex": result.get("chunkIndex"),
                        "uploadedAt": result.get("uploadedAt"),
                        "metadata": json.dumps({**existing_metadata, "updated_at": datetime.utcnow().isoformat()})
                    }
                    chunks_to_update.append(updated_doc)
                
                if chunks_to_update:
                    # Update chunks in batch
                    result = search_client.upload_documents(documents=chunks_to_update)
                    success = all(r.succeeded for r in result)
                    
                    if success:
                        return {
                            "message": f"Document metadata updated successfully",
                            "status": "success",
                            "id": document_id,
                            "chunks_updated": len(chunks_to_update)
                        }
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to update some document chunks"
                        )
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Document {document_id} not found"
                    )
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error updating document metadata: {str(e)}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating document: {str(e)}"
        )


@router.post("/{document_id}/link")
async def link_documents(document_id: str, request: LinkDocumentsRequest = Body(...)):
    """
    Link documents together.
    
    This creates relationships between documents for easier retrieval.
    """
    try:
        # TODO: Implement actual document linking in database
        return {
            "message": f"Document {document_id} linked to {len(request.relatedDocumentIds)} document(s)",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error linking documents: {str(e)}"
        )


@router.get("/{document_id}/related", response_model=List[DocumentResponse])
async def get_related_documents(document_id: str):
    """
    Get documents related to a specific document.
    """
    try:
        # TODO: Implement actual related documents retrieval
        return []
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving related documents: {str(e)}"
        )


async def process_document_task(
    temp_file_path: str,
    document_id: str,
    document_title: str,
    category: Optional[str],
    tags: List[str],
    layer: Optional[str],  # 'policy' | 'principle' | 'sop'
    file_extension: str,
    original_filename: Optional[str]
):
    """
    Background task to process uploaded document.
    
    This function:
    1. Uploads file to Azure Blob Storage
    2. Extracts text and chunks document
    3. Generates embeddings
    4. Stores in Azure AI Search
    """
    blob_url = None
    
    try:
        # 1. Upload to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        blob_client = blob_service_client.get_blob_client(
            container=settings.azure_storage_container_name,
            blob=f"{document_id}{file_extension}"
        )
        
        with open(temp_file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        blob_url = blob_client.url
        print(f"[OK] Uploaded {document_id} to Blob Storage: {blob_url}")
        
        # 2. Process document (extract text and chunk)
        processor = DocumentProcessor(
            chunk_size=500,  # ~500 tokens per chunk (more precise retrieval)
            chunk_overlap=125,  # ~125 token overlap (25% overlap for context)
            min_chunk_size=100  # Minimum 100 tokens
        )
        
        extracted_text, chunks, metadata = await processor.process_document(
            file_path=temp_file_path,
            file_extension=file_extension,
            title=document_title,
            category=category,
            tags=tags
        )
        
        print(f"[OK] Processed {document_id}: {len(chunks)} chunks created")
        
        if not chunks:
            print(f"[WARNING] No chunks created for document {document_id}")
            return
        
        # 3. Generate embeddings
        embedding_service = EmbeddingService()
        
        # Prepare texts for embedding (use full_content which includes section headers)
        chunk_texts = [chunk.full_content for chunk in chunks]
        
        # Generate embeddings in batches
        print(f"[INFO] Generating embeddings for {len(chunk_texts)} chunks...")
        embeddings = embedding_service.generate_embeddings_batch(
            chunk_texts,
            batch_size=100
        )
        print(f"[OK] Generated {len(embeddings)} embeddings")
        
        # 4. Store in Azure AI Search
        vector_store = VectorStoreManager()
        
        # Prepare documents for batch upload
        uploaded_at = datetime.utcnow()
        documents_to_index = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_dict = {
                "id": f"{document_id}_{chunk.chunk_index}",
                "documentId": document_id,
                "content": chunk.content,
                "contentVector": embedding,
                "title": document_title,
                "category": category,
                "tags": tags,
                "layer": layer,  # Include layer in indexed document
                "chunkIndex": chunk.chunk_index,
                "uploadedAt": uploaded_at,
                "metadata": {
                    **chunk.metadata,
                    **metadata,
                    "page_number": chunk.page_number,
                    "section_header": chunk.section_header,
                    "blob_url": blob_url,
                    "original_filename": original_filename,
                    "source": "uploaded",
                    "layer": layer  # Also store in metadata for backup
                }
            }
            documents_to_index.append(chunk_dict)
        
        # Upload to search index in batch
        success = await vector_store.add_documents_batch(documents_to_index)
        
        if success:
            print(f"[OK] Successfully indexed {len(documents_to_index)} chunks for document {document_id}")
        else:
            print(f"[WARNING] Some chunks may have failed to index for document {document_id}")
        
    except Exception as e:
        print(f"[ERROR] Failed to process document {document_id}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
