"""Test if the admin key works with the search service."""

import os
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

def test_admin_key():
    """Test the admin key by trying to list indexes."""
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    
    print("=" * 50)
    print("Testing Admin Key Connection")
    print("=" * 50)
    
    if not search_endpoint or not search_key:
        print("[ERROR] Missing credentials in .env")
        return False
    
    print(f"\nEndpoint: {search_endpoint}")
    print(f"Key: {search_key[:15]}...{search_key[-10:]}")
    
    try:
        credential = AzureKeyCredential(search_key)
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
        
        # Try to get service statistics (requires admin key)
        print("\n[1] Testing connection...")
        stats = index_client.get_service_statistics()
        print(f"[OK] Connected successfully!")
        print(f"    Service: {stats.service_name if hasattr(stats, 'service_name') else 'Connected'}")
        
        # Try to list indexes
        print("\n[2] Listing existing indexes...")
        indexes = list(index_client.list_indexes())
        print(f"[OK] Found {len(indexes)} index(es):")
        for idx in indexes:
            print(f"    - {idx.name}")
        
        print("\n" + "=" * 50)
        print("[SUCCESS] Admin key is working correctly!")
        print("You should be able to create the index now.")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n[ERROR] {error_msg}")
        
        if "api key" in error_msg.lower() or "key" in error_msg.lower():
            print("\n[DIAGNOSIS]")
            print("The key you're using might be:")
            print("  1. A query key instead of admin key")
            print("  2. From a different search service")
            print("  3. Regenerated (old key no longer works)")
            print("\n[SOLUTION]")
            print("1. Go to Azure Portal")
            print("2. Navigate to: Your Resource Group -> Your Search Service")
            print(f"3. Verify the service name matches: {search_endpoint}")
            print("4. Go to 'Keys' section")
            print("5. Copy 'Admin Key (primary)' again (make sure it's admin, not query)")
            print("6. Update your .env file")
        elif "endpoint" in error_msg.lower():
            print("\n[DIAGNOSIS]")
            print("Endpoint might be incorrect or doesn't match the key.")
            print(f"\nVerify your endpoint: {search_endpoint}")
            print("It should look like: https://your-service-name.search.windows.net")
        
        return False

if __name__ == "__main__":
    success = test_admin_key()
    exit(0 if success else 1)
