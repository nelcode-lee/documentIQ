"""Test script to debug documents endpoint."""
import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_API_KEY")
search_index = os.getenv("AZURE_SEARCH_INDEX_NAME")

print(f"Connecting to: {search_endpoint}")
print(f"Index: {search_index}")
print()

client = SearchClient(
    endpoint=search_endpoint,
    index_name=search_index,
    credential=AzureKeyCredential(search_key)
)

# Test 1: What check_documents.py does (works)
print("[TEST 1] Using check_documents.py fields:")
try:
    results1 = list(client.search(
        search_text="*",
        top=10,
        select=["documentId", "title", "category", "chunkIndex", "content"]
    ))
    print(f"✅ Found {len(results1)} chunks")
except Exception as e:
    print(f"❌ Error: {e}")

print()

# Test 2: What API endpoint tries (might fail)
print("[TEST 2] Using API endpoint fields:")
try:
    results2 = list(client.search(
        search_text="*",
        top=10,
        select=["documentId", "title", "category", "tags", "metadata", "uploadedAt"]
    ))
    print(f"✅ Found {len(results2)} chunks")
except Exception as e:
    print(f"❌ Error: {e}")

print()

# Test 3: Try without uploadedAt
print("[TEST 3] Without uploadedAt:")
try:
    results3 = list(client.search(
        search_text="*",
        top=10,
        select=["documentId", "title", "category", "tags", "metadata"]
    ))
    print(f"✅ Found {len(results3)} chunks")
except Exception as e:
    print(f"❌ Error: {e}")

print()

# Test 4: Try with just basic fields
print("[TEST 4] Just basic fields:")
try:
    results4 = list(client.search(
        search_text="*",
        top=10,
        select=["documentId", "title", "category"]
    ))
    print(f"✅ Found {len(results4)} chunks")
    if results4:
        print(f"Sample: {results4[0].get('title', 'No title')}")
except Exception as e:
    print(f"❌ Error: {e}")
