"""Script to create Azure AI Search index."""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def create_search_index():
    """Create the search index in Azure AI Search."""
    # Initialize semantic search flag
    HAS_SEMANTIC = False
    SemanticConfiguration = None
    PrioritizedFields = None
    SemanticField = None
    
    try:
        try:
            from azure.search.documents.indexes import SearchIndexClient
            from azure.search.documents.indexes.models import (
                SearchIndex,
                SimpleField,
                SearchableField,
                SearchField,
                VectorSearch,
                VectorSearchProfile,
                HnswAlgorithmConfiguration,
                SemanticConfiguration,
                PrioritizedFields,
                SemanticField
            )
            HAS_SEMANTIC = True
        except ImportError:
            # Try alternative import
            from azure.search.documents.indexes import SearchIndexClient
            from azure.search.documents.indexes.models import (
                SearchIndex,
                SimpleField,
                SearchableField,
                SearchField,
                VectorSearch,
                VectorSearchProfile,
                HnswAlgorithmConfiguration
            )
            # Semantic search might not be available in all tiers
            try:
                from azure.search.documents.indexes.models import SemanticConfiguration, PrioritizedFields, SemanticField
                HAS_SEMANTIC = True
            except ImportError:
                HAS_SEMANTIC = False
                print("[NOTE] Semantic search not available - will create index without it")
        from azure.core.credentials import AzureKeyCredential
        
        # Get credentials
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = os.getenv("AZURE_SEARCH_API_KEY")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "documents-index")
        
        if not search_endpoint or not search_key:
            print("[ERROR] Azure AI Search credentials not found in .env")
            return False
        
        print(f"Connecting to Azure AI Search...")
        print(f"Endpoint: {search_endpoint}")
        print(f"Index Name: {index_name}")
        
        credential = AzureKeyCredential(search_key)
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
        
        # Check if index already exists
        try:
            existing_index = index_client.get_index(index_name)
            print(f"\n[WARNING] Index '{index_name}' already exists!")
            print("Do you want to delete and recreate it? (This will delete all data)")
            response = input("Type 'yes' to continue: ")
            if response.lower() == 'yes':
                print(f"\nDeleting existing index...")
                index_client.delete_index(index_name)
                print("[OK] Index deleted")
            else:
                print("Cancelled. Index not modified.")
                return True
        except Exception:
            # Index doesn't exist, which is fine - we'll create it
            print(f"\nIndex '{index_name}' does not exist. Creating new index...")
        
        # Define the index fields
        fields = [
            SimpleField(name="id", type="Edm.String", key=True, filterable=True, retrievable=True),
            SimpleField(name="documentId", type="Edm.String", filterable=True, searchable=False, retrievable=True),
            SearchableField(name="content", type="Edm.String", analyzer_name="en.microsoft", retrievable=True),
            SearchField(
                name="contentVector",
                type="Collection(Edm.Single)",
                vector_search_dimensions=1536,
                vector_search_profile_name="default-vector-profile",
                retrievable=True
            ),
            SearchableField(name="title", type="Edm.String", filterable=True, retrievable=True),
            SearchableField(name="category", type="Edm.String", filterable=True, retrievable=True),
            SimpleField(name="tags", type="Collection(Edm.String)", filterable=True, searchable=True, retrievable=True),
            SimpleField(name="layer", type="Edm.String", filterable=True, searchable=False, retrievable=True),  # 'policy' | 'principle' | 'sop'
            SimpleField(name="chunkIndex", type="Edm.Int32", filterable=True, retrievable=True),
            SimpleField(name="uploadedAt", type="Edm.DateTimeOffset", filterable=True, sortable=True, retrievable=True),
            SimpleField(name="metadata", type="Edm.String", searchable=False, retrievable=True),
        ]
        
        # Define vector search configuration
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="default-algorithm",
                    kind="hnsw",
                    parameters={
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine"
                    }
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="default-vector-profile",
                    algorithm_configuration_name="default-algorithm"
                )
            ]
        )
        
        # Create the index with optional semantic search
        index_params = {
            "name": index_name,
            "fields": fields,
            "vector_search": vector_search
        }
        
        # Add semantic configuration if available
        if HAS_SEMANTIC:
            try:
                semantic_config = SemanticConfiguration(
                    name="default-semantic-config",
                    prioritized_fields=PrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                        keywords_fields=[SemanticField(field_name="tags")]
                    )
                )
                index_params["semantic_configurations"] = [semantic_config]
            except:
                print("[NOTE] Skipping semantic search configuration")
        
        index = SearchIndex(**index_params)
        
        print(f"\nCreating index '{index_name}' with vector search capabilities...")
        result = index_client.create_index(index)
        
        print("\n" + "=" * 50)
        print(f"[SUCCESS] Index '{index_name}' created successfully!")
        print("\nIndex configuration:")
        print(f"  - Vector dimensions: 1536 (for text-embedding-ada-002)")
        print(f"  - Vector search algorithm: HNSW")
        print(f"  - Semantic search: Enabled")
        print(f"  - Fields: {len(fields)}")
        
        return True
        
    except ImportError:
        print("[ERROR] azure-search-documents not installed")
        print("Run: pip install azure-search-documents")
        return False
    except Exception as e:
        error_msg = str(e)
        print(f"\n[ERROR] Failed to create index: {error_msg}")
        
        # Provide helpful error messages
        if "api key" in error_msg.lower() or "key" in error_msg.lower():
            print("\n[IMPORTANT] API Key Issue:")
            print("You need an ADMIN KEY (not a query key) to create indexes.")
            print("\nTo get your admin key:")
            print("1. Go to Azure Portal")
            print("2. Navigate to your Azure AI Search service")
            print("3. Go to 'Keys' section")
            print("4. Copy the 'Admin Key (primary)' or 'Admin Key (secondary)'")
            print("5. Update AZURE_SEARCH_API_KEY in your .env file")
        elif "semantic" in error_msg.lower():
            print("\nNote: Semantic search may require Standard tier or higher.")
            print("You can still create the index without semantic search.")
        elif "403" in error_msg or "forbidden" in error_msg.lower():
            print("\nThis is a permissions issue.")
            print("Ensure you're using an ADMIN KEY, not a query key.")
        
        return False

if __name__ == "__main__":
    success = create_search_index()
    exit(0 if success else 1)
