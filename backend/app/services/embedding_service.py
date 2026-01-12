"""Service for generating embeddings using OpenAI API."""

from openai import OpenAI
from app.config import settings
from typing import List
import time
from app.services.cache_service import cache_service


class EmbeddingService:
    """Service to generate embeddings using OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model
        self.use_cache = settings.enable_embedding_cache
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Uses caching to avoid regenerating embeddings for the same text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        # Check cache first
        if self.use_cache:
            cached_embedding = cache_service.get_embedding(text)
            if cached_embedding is not None:
                print(f"[CACHE HIT] Embedding for query: {text[:50]}...")
                return cached_embedding
        
        # Generate new embedding
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            embedding = response.data[0].embedding
            
            # Cache the embedding
            if self.use_cache:
                cache_service.set_embedding(
                    text=text,
                    embedding=embedding,
                    ttl=settings.cache_embedding_ttl
                )
            
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process per batch
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                # Sort by index to maintain order
                sorted_data = sorted(response.data, key=lambda x: x.index)
                batch_embeddings = [item.embedding for item in sorted_data]
                embeddings.extend(batch_embeddings)
                
                # Rate limiting - small delay between batches
                if i + batch_size < len(texts):
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Error generating batch embeddings: {e}")
                raise
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for this model."""
        # text-embedding-ada-002: 1536 dimensions
        # text-embedding-3-small: 1536 dimensions
        # text-embedding-3-large: 3072 dimensions
        if "ada-002" in self.model:
            return 1536
        elif "3-small" in self.model:
            return 1536
        elif "3-large" in self.model:
            return 3072
        else:
            return 1536  # Default
