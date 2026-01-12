"""Script to create Azure Blob Storage containers."""

import os
from dotenv import load_dotenv

load_dotenv()

def create_containers():
    """Create required blob storage containers."""
    try:
        from azure.storage.blob import BlobServiceClient
        
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
        
        if not connection_string:
            print("[ERROR] AZURE_STORAGE_CONNECTION_STRING not found in .env")
            return False
        
        print(f"Connecting to Azure Blob Storage...")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Create documents container
        containers_to_create = [
            container_name,  # Main documents container
            "processed"      # Optional: for processed chunks
        ]
        
        for container in containers_to_create:
            try:
                print(f"\nCreating container: {container}...")
                container_client = blob_service_client.create_container(container)
                print(f"[OK] Container '{container}' created successfully!")
            except Exception as e:
                if "ContainerAlreadyExists" in str(e) or "already exists" in str(e).lower():
                    print(f"[OK] Container '{container}' already exists")
                else:
                    print(f"[ERROR] Failed to create container '{container}': {str(e)}")
                    return False
        
        print("\n" + "=" * 50)
        print("[SUCCESS] All containers are ready!")
        return True
        
    except ImportError:
        print("[ERROR] azure-storage-blob not installed")
        print("Run: pip install azure-storage-blob")
        return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

if __name__ == "__main__":
    success = create_containers()
    exit(0 if success else 1)
