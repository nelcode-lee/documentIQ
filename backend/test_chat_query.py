"""Test the actual chat service with the specific query."""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

async def test_chat_query():
    """Test the chat service with the specific query."""
    from app.services.chat_service import ChatService
    
    query = "How does Issue 9 expect the HACCP team to validate critical limits before implementing changes?"
    
    print("=" * 70)
    print(f"Testing Chat Service Query")
    print("=" * 70)
    print(f"\nQuery: {query}\n")
    
    chat_service = ChatService()
    
    try:
        print("[Step 1] Generating embedding and searching...")
        result = await chat_service.chat(query=query, top_k=10)
        
        print(f"\n[Response]")
        print("-" * 70)
        print(result["response"])
        print("-" * 70)
        
        print(f"\n[Sources Found: {len(result['sources'])}]")
        for source in result['sources']:
            print(f"  - {source}")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_query())
