"""Test script to verify Azure services configuration."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_azure_search():
    """Test Azure AI Search connection."""
    print("Testing Azure AI Search...")
    print("=" * 50)
    
    # Check credentials
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "documents-index")
    
    if not search_endpoint:
        print("[ERROR] AZURE_SEARCH_ENDPOINT not found")
        return False
    
    if not search_key:
        print("[ERROR] AZURE_SEARCH_API_KEY not found")
        return False
    
    if "your-" in search_endpoint.lower() or "placeholder" in search_endpoint.lower():
        print("[ERROR] Search endpoint appears to be a placeholder")
        print("   Please update .env with your real Azure AI Search endpoint")
        return False
    
    print(f"[OK] Search Endpoint: {search_endpoint}")
    print(f"[OK] Search Key: {search_key[:10]}...{search_key[-4:]}")
    print(f"[OK] Index Name: {index_name}")
    
    # Test connection
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        credential = AzureKeyCredential(search_key)
        client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=credential
        )
        
        # Test connection by checking if index exists
        print("\n  Testing connection to Azure AI Search...")
        print(f"  Service: {search_endpoint.split('//')[1].split('.')[0]}")
        
        # Try to check if index exists by attempting a search
        print(f"\n  Checking if index '{index_name}' exists...")
        try:
            # Try a simple search to verify index exists
            results = client.search(search_text="*", top=1)
            result_count = len(list(results))
            print(f"  [OK] Connected successfully!")
            print(f"  [OK] Index '{index_name}' exists and is accessible")
            print(f"  [OK] Test search returned {result_count} result(s)")
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "404" in error_msg or "index" in error_msg:
                print(f"  [WARNING] Index '{index_name}' not found or not accessible")
                print(f"     Connection to Azure AI Search is OK, but index needs to be created")
                print(f"     Use the search-index.json schema from infrastructure/ folder")
                print(f"     This is OK if you haven't created the index yet")
                # Connection is OK, just index missing
                return True
            else:
                print(f"  [ERROR] Connection failed: {str(e)}")
                return False
        
        return True
        
    except ImportError:
        print("  [ERROR] azure-search-documents package not installed")
        print("     Run: pip install azure-search-documents")
        return False
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        print("\n  Common issues:")
        print("    - Invalid endpoint URL")
        print("    - Invalid API key")
        print("    - Network connectivity")
        print("    - Index doesn't exist yet")
        return False

def test_azure_storage():
    """Test Azure Blob Storage connection."""
    print("\n\nTesting Azure Blob Storage...")
    print("=" * 50)
    
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
    
    if not connection_string:
        print("[ERROR] AZURE_STORAGE_CONNECTION_STRING not found")
        return False
    
    if "your-" in connection_string.lower() or "placeholder" in connection_string.lower():
        print("[ERROR] Storage connection string appears to be a placeholder")
        print("   Please update .env with your real Azure Storage connection string")
        return False
    
    print(f"[OK] Container Name: {container_name}")
    
    # Test connection
    try:
        from azure.storage.blob import BlobServiceClient
        
        print("\n  Testing connection to Azure Blob Storage...")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Try to list containers
        containers = list(blob_service_client.list_containers())
        print(f"  [OK] Connected successfully!")
        print(f"  [OK] Found {len(containers)} container(s)")
        
        # Check if our container exists
        container_exists = any(c.name == container_name for c in containers)
        if container_exists:
            print(f"  [OK] Container '{container_name}' exists")
        else:
            print(f"  [WARNING] Container '{container_name}' not found")
            print(f"     You may need to create it")
        
        return True
        
    except ImportError:
        print("  [ERROR] azure-storage-blob package not installed")
        print("     Run: pip install azure-storage-blob")
        return False
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        print("\n  Common issues:")
        print("    - Invalid connection string")
        print("    - Storage account doesn't exist")
        print("    - Network connectivity")
        return False

def main():
    """Run all Azure connection tests."""
    print("Azure Services Connection Test")
    print("=" * 50)
    print()
    
    results = []
    
    # Test Azure AI Search
    search_ok = test_azure_search()
    results.append(("Azure AI Search", search_ok))
    
    # Test Azure Blob Storage
    storage_ok = test_azure_storage()
    results.append(("Azure Blob Storage", storage_ok))
    
    # Summary
    print("\n\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    for service, status in results:
        status_icon = "[OK]" if status else "[FAIL]"
        print(f"{status_icon} {service}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n[SUCCESS] All Azure services are configured correctly!")
    else:
        print("\n[WARNING] Some services need configuration. Check the errors above.")
        print("\nNext steps:")
        print("  1. Update .env file with your Azure credentials")
        print("  2. Ensure Azure resources are created in Azure Portal")
        print("  3. Run this test again to verify")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
