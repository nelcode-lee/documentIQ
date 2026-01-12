"""Test the documents endpoint directly."""

import asyncio
import sys
sys.path.insert(0, '.')

from app.routers.documents import list_documents

async def test():
    print("Testing list_documents endpoint...")
    result = await list_documents()
    print(f"\nFound {len(result)} documents:")
    for doc in result:
        print(f"  - {doc.title} (ID: {doc.id[:8]}...)")
    
    # Try to serialize to JSON
    import json
    try:
        json_str = json.dumps([doc.dict() for doc in result], default=str, indent=2)
        print(f"\nJSON serialization successful: {len(json_str)} characters")
    except Exception as e:
        print(f"\nJSON serialization error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
