"""Diagnostic script to identify Azure resource naming issues after project rename.

This script helps identify if your .env file is pointing to the wrong Azure resources
after the project name changed.
"""

import os
import sys
from dotenv import load_dotenv

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def extract_resource_name_from_endpoint(endpoint: str) -> str:
    """Extract resource name from Azure endpoint URL."""
    if not endpoint:
        return None
    # Example: https://rag-system-dev-search.search.windows.net -> rag-system-dev-search
    try:
        # Remove protocol
        if endpoint.startswith('https://'):
            endpoint = endpoint[8:]
        elif endpoint.startswith('http://'):
            endpoint = endpoint[7:]
        
        # Extract service name (before first dot)
        parts = endpoint.split('.')
        if len(parts) > 0:
            return parts[0]
    except:
        pass
    return None

def extract_storage_account_from_connection_string(conn_str: str) -> str:
    """Extract storage account name from connection string."""
    if not conn_str:
        return None
    try:
        # Format: DefaultEndpointsProtocol=https;AccountName=ragsystemdevstor;AccountKey=...
        parts = conn_str.split(';')
        for part in parts:
            if part.startswith('AccountName='):
                return part.split('=')[1]
    except:
        pass
    return None

def diagnose_azure_resources():
    """Diagnose Azure resource configuration issues."""
    print("=" * 80)
    print("Azure Resource Configuration Diagnostic")
    print("=" * 80)
    print()
    
    # Get environment variables
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_index = os.getenv("AZURE_SEARCH_INDEX_NAME")
    storage_conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    storage_container = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
    
    print("[1] Current Environment Configuration")
    print("-" * 80)
    print(f"Search Endpoint:     {search_endpoint}")
    print(f"Search Index Name:   {search_index}")
    print(f"Storage Container:   {storage_container}")
    
    if storage_conn_str:
        # Hide the key part for security
        masked_conn = storage_conn_str[:50] + "..." if len(storage_conn_str) > 50 else storage_conn_str
        print(f"Storage Conn String: {masked_conn}")
    else:
        print("Storage Conn String: NOT SET")
    
    print()
    
    # Extract resource names from config
    search_service_name = extract_resource_name_from_endpoint(search_endpoint) if search_endpoint else None
    storage_account_name = extract_storage_account_from_connection_string(storage_conn_str) if storage_conn_str else None
    
    print("[2] Extracted Resource Names")
    print("-" * 80)
    print(f"Search Service Name (from endpoint):  {search_service_name}")
    print(f"Storage Account Name (from conn str): {storage_account_name}")
    print()
    
    # Try to connect and verify resources exist
    print("[3] Verifying Resource Accessibility")
    print("-" * 80)
    
    # Test Search Service
    if search_endpoint and search_index:
        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential
            
            search_key = os.getenv("AZURE_SEARCH_API_KEY")
            if not search_key:
                print("❌ AZURE_SEARCH_API_KEY not set - cannot test Search Service")
            else:
                try:
                    search_client = SearchClient(
                        endpoint=search_endpoint,
                        index_name=search_index,
                        credential=AzureKeyCredential(search_key)
                    )
                    # Try to get index stats
                    stats = search_client.get_document_count()
                    print(f"✅ Search Service: CONNECTED")
                    print(f"   - Index '{search_index}' exists")
                    print(f"   - Document count: {stats}")
                    
                    # Try a quick search
                    results = list(search_client.search(search_text="*", top=1))
                    if results:
                        print(f"   - Index contains documents")
                    else:
                        print(f"   - ⚠️  Index is empty (no documents found)")
                        
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg or "not found" in error_msg.lower():
                        print(f"❌ Search Service: INDEX NOT FOUND")
                        print(f"   - Index '{search_index}' does not exist in service '{search_service_name}'")
                        print(f"   - This suggests the index name might be wrong")
                    elif "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg.lower():
                        print(f"❌ Search Service: AUTHENTICATION FAILED")
                        print(f"   - Check your AZURE_SEARCH_API_KEY")
                    elif "NameResolutionFailure" in error_msg or "could not resolve" in error_msg.lower():
                        print(f"❌ Search Service: SERVICE NOT FOUND")
                        print(f"   - Service '{search_service_name}' does not exist")
                        print(f"   - The endpoint URL might be incorrect (old project name?)")
                    else:
                        print(f"❌ Search Service: ERROR - {error_msg}")
        except Exception as e:
            print(f"❌ Search Service: FAILED TO CONNECT - {str(e)}")
    else:
        print("⚠️  Search configuration incomplete - missing endpoint or index name")
    
    print()
    
    # Test Storage Account
    if storage_conn_str:
        try:
            from azure.storage.blob import BlobServiceClient
            
            blob_service = BlobServiceClient.from_connection_string(storage_conn_str)
            try:
                container_client = blob_service.get_container_client(storage_container)
                # Try to list blobs (use iterator, not max_results parameter)
                blob_iterator = container_client.list_blobs()
                first_blob = next(blob_iterator, None)
                if first_blob:
                    print(f"✅ Storage Account: CONNECTED")
                    print(f"   - Container '{storage_container}' exists")
                    
                    # Get full blob count (iterate through all)
                    all_blobs = list(container_client.list_blobs())
                    print(f"   - Blob count: {len(all_blobs)}")
                else:
                    print(f"⚠️  Storage Account: CONNECTED but container is empty")
                    print(f"   - Container '{storage_container}' exists but has no blobs")
                
            except Exception as e:
                error_msg = str(e)
                if "ContainerNotFound" in error_msg or "does not exist" in error_msg.lower():
                    print(f"❌ Storage Account: CONTAINER NOT FOUND")
                    print(f"   - Container '{storage_container}' does not exist")
                    print(f"   - Check AZURE_STORAGE_CONTAINER_NAME in .env")
                elif "AuthenticationFailed" in error_msg or "unauthorized" in error_msg.lower():
                    print(f"❌ Storage Account: AUTHENTICATION FAILED")
                    print(f"   - Check your AZURE_STORAGE_CONNECTION_STRING")
                else:
                    print(f"❌ Storage Account: ERROR - {error_msg}")
        except Exception as e:
            error_msg = str(e)
            if "InvalidConnectionString" in error_msg:
                print(f"❌ Storage Account: INVALID CONNECTION STRING")
                print(f"   - Check your AZURE_STORAGE_CONNECTION_STRING format")
            elif "AccountNotFound" in error_msg or "does not exist" in error_msg.lower():
                print(f"❌ Storage Account: ACCOUNT NOT FOUND")
                print(f"   - Storage account '{storage_account_name}' does not exist")
                print(f"   - The connection string might point to old resources")
            else:
                print(f"❌ Storage Account: FAILED TO CONNECT - {error_msg}")
    else:
        print("⚠️  Storage configuration incomplete - missing connection string")
    
    print()
    print("[4] Recommendations")
    print("-" * 80)
    
    recommendations = []
    
    # Check for common issues
    if search_service_name and ("rag-system" in search_service_name.lower() or "ragsystem" in search_service_name.lower()):
        recommendations.append(
            "⚠️  Search service name contains 'rag-system' - this suggests old project name.\n"
            "   If you renamed the project, you may need to:\n"
            "   1. Find your new search service in Azure Portal\n"
            "   2. Update AZURE_SEARCH_ENDPOINT in .env\n"
            "   3. Get new admin key and update AZURE_SEARCH_API_KEY"
        )
    
    if storage_account_name and ("ragsystem" in storage_account_name.lower() or "rag-system" in storage_account_name.lower()):
        recommendations.append(
            "⚠️  Storage account name contains 'rag-system' - this suggests old project name.\n"
            "   If you renamed the project, you may need to:\n"
            "   1. Find your new storage account in Azure Portal\n"
            "   2. Get new connection string from Azure Portal\n"
            "   3. Update AZURE_STORAGE_CONNECTION_STRING in .env"
        )
    
    if not recommendations:
        if search_service_name and storage_account_name:
            recommendations.append(
                "✅ Resource names don't contain obvious old project references.\n"
                "   If documents aren't loading, check:\n"
                "   1. Index name matches exactly (case-sensitive)\n"
                "   2. Container name is correct\n"
                "   3. Admin keys are up to date"
            )
        else:
            recommendations.append(
                "⚠️  Could not extract resource names. Please verify:\n"
                "   1. AZURE_SEARCH_ENDPOINT is correct\n"
                "   2. AZURE_STORAGE_CONNECTION_STRING is correct"
            )
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
        print()
    
    print("=" * 80)
    print()
    print("To find your Azure resources:")
    print("1. Go to Azure Portal: https://portal.azure.com")
    print("2. Search for 'Search services' - find your search service")
    print("3. Search for 'Storage accounts' - find your storage account")
    print("4. Copy the correct endpoints and connection strings")
    print()

if __name__ == "__main__":
    try:
        diagnose_azure_resources()
    except Exception as e:
        print(f"\n❌ Diagnostic script failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
