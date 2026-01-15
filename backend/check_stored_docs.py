#!/usr/bin/env python3
"""Check stored documents for download URLs."""

from app.services.document_store import document_store

docs = document_store.list_documents()
print(f'Found {len(docs)} stored documents')

for i, doc in enumerate(docs[:3]):
    print(f'Document {i+1}: {doc.get("title")}')
    print(f'  download_url: {bool(doc.get("download_url"))}')
    if doc.get('download_url'):
        url = doc['download_url']
        print(f'  URL: {url[:80]}...')
    print()