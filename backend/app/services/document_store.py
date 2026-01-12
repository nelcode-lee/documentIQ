"""Simple document store for tracking generated documents."""

from typing import List, Dict, Optional
from datetime import datetime
import json
import os
from app.config import settings


class DocumentStore:
    """Simple file-based store for tracking generated documents."""
    
    def __init__(self, store_file: str = "generated_documents.json"):
        """Initialize document store."""
        self.store_file = store_file
        self.store_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            store_file
        )
    
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
            return True
        except Exception as e:
            print(f"Error deleting document from store: {e}")
            return False


# Global instance
document_store = DocumentStore()
