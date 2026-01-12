# Document Control Features

## Overview

The Documents tab now includes comprehensive document control features to ensure information accuracy and proper document management.

---

## Features Implemented

### 1. **Delete Documents** 🗑️

**Complete Deletion:**
- Removes document from Azure Blob Storage (original file)
- Removes all chunks from Azure AI Search (indexed content + embeddings)
- Removes from generated documents metadata store
- **Permanent action** - cannot be undone

**User Experience:**
- Confirmation modal with clear warning
- Lists what will be deleted (file, indexed content, metadata)
- Prevents accidental deletions

**Usage:**
1. Click the trash icon (🗑️) on any document card
2. Review the confirmation dialog
3. Confirm deletion

### 2. **Update Documents** ✏️

**Two Update Modes:**

#### A. **Metadata Update** (No File Upload)
- Update title, category, and tags
- Changes are reflected immediately
- Updates all document chunks in Azure AI Search
- No re-processing required

#### B. **Complete Document Replacement** (File Upload)
- Replace the entire document file
- Automatically:
  1. Deletes old document from Azure Blob Storage
  2. Deletes old chunks from Azure AI Search
  3. Uploads new file to Blob Storage
  4. Re-processes document (extraction, chunking, embeddings)
  5. Re-indexes in Azure AI Search
- **Ensures latest information** is always available

**User Experience:**
- Edit button (✏️) on each document card
- Modal form with all document fields
- Optional file replacement
- Clear warning when replacing file
- Loading state during update

**Usage:**
1. Click the Edit button (✏️) on any document card
2. Modify title, category, or tags
3. Optionally upload a new file to replace the document
4. Click "Save Changes"
5. Document is updated and re-indexed if file was replaced

---

## Backend Implementation

### Delete Endpoint

**Endpoint:** `DELETE /api/documents/{document_id}`

**Process:**
1. Delete all chunks from Azure AI Search
2. Delete blob(s) from Azure Blob Storage
3. Delete from generated documents store (if applicable)

**Response:**
```json
{
  "message": "Document {id} deleted successfully",
  "status": "success",
  "deleted_items": ["Azure AI Search chunks", "Blob: {filename}"]
}
```

### Update Endpoint

**Endpoint:** `PUT /api/documents/{document_id}`

**Request Format:**
- `multipart/form-data`
- Fields: `file` (optional), `title`, `category`, `tags`

**Process (Metadata Only):**
1. Find all chunks for document in Azure AI Search
2. Update metadata fields (title, category, tags)
3. Update all chunks in batch

**Process (File Replacement):**
1. Delete old document from Azure AI Search
2. Delete old blob from Azure Blob Storage
3. Upload new file to Blob Storage
4. Process document (same as upload flow)
5. Index new chunks

**Response:**
```json
{
  "message": "Document updated successfully",
  "status": "success",
  "id": "{document_id}"
}
```

---

## Frontend Implementation

### Document Card Actions

**Actions Available:**
- **Edit** (✏️) - Open update modal
- **Link** (🔗) - Link related documents (future feature)
- **Delete** (🗑️) - Delete document with confirmation

**Removed Actions:**
- ❌ Download button (not needed per requirements)
- ❌ Preview button (can be added later if needed)

### Edit Modal

**Fields:**
- Document Title (required)
- Category (optional, with autocomplete from existing categories)
- Tags (comma-separated, optional)
- File Replacement (optional file upload)

**Features:**
- Form validation
- Clear warnings for file replacement
- Loading state during update
- Error handling

### Delete Confirmation Modal

**Features:**
- Clear warning message
- Lists what will be deleted
- Document title display
- Cancel and Delete buttons
- Cannot be undone warning

---

## Use Cases

### Scenario 1: Fix Typo in Document Title
1. Click Edit on document
2. Fix title
3. Click Save
4. ✅ Done - title updated immediately

### Scenario 2: Update Document Content
1. Click Edit on document
2. Upload new file
3. Click Save
4. ⏳ Document is re-processed in background
5. ✅ New content available after processing

### Scenario 3: Re-categorize Document
1. Click Edit on document
2. Change category
3. Click Save
4. ✅ Category updated immediately

### Scenario 4: Remove Obsolete Document
1. Click Delete on document
2. Review confirmation
3. Confirm deletion
4. ✅ Document completely removed

---

## Benefits

### Information Accuracy
- **Update outdated documents** with latest versions
- **Remove obsolete documents** to prevent confusion
- **Fix metadata errors** (title, category, tags)
- **Ensure consistency** across document library

### Data Integrity
- **Complete deletion** ensures no orphaned data
- **Proper indexing** after updates
- **Consistent metadata** across all chunks

### User Experience
- **Simple, intuitive controls**
- **Clear warnings** for destructive actions
- **Fast metadata updates** (no re-processing)
- **Background processing** for file replacements

---

## Technical Details

### Cache Invalidation

**After Update:**
- Query cache should be cleared for updated documents
- Consider implementing automatic cache invalidation by document ID

**After Delete:**
- Queries for deleted documents will return no results (expected behavior)
- Cache entries may contain outdated references (acceptable)

### Error Handling

**Partial Failures:**
- Delete operation reports partial success if some operations fail
- Update operation fails completely if any step fails
- Clear error messages returned to frontend

**Recovery:**
- Failed deletions can be retried
- Failed updates can be retried
- System maintains consistency even with partial failures

---

## Future Enhancements

### Potential Additions:

1. **Bulk Operations**
   - Select multiple documents
   - Bulk delete
   - Bulk category update

2. **Version History**
   - Track document versions
   - View change history
   - Revert to previous version

3. **Document Status**
   - Mark documents as "Under Review"
   - Archive documents instead of deleting
   - Draft/Published status

4. **Audit Trail**
   - Log who updated/deleted documents
   - Track when changes were made
   - Reason for deletion/update

5. **Approval Workflow**
   - Require approval for deletions
   - Multi-step approval for major updates

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/documents` | List all documents |
| `POST` | `/api/documents/upload` | Upload new document |
| `PUT` | `/api/documents/{id}` | Update document (metadata or file) |
| `DELETE` | `/api/documents/{id}` | Delete document completely |
| `POST` | `/api/documents/{id}/link` | Link related documents |
| `GET` | `/api/documents/{id}/related` | Get related documents |

---

## Testing Checklist

- [x] Delete removes from Azure Blob Storage
- [x] Delete removes from Azure AI Search
- [x] Delete confirmation modal works
- [x] Update metadata without file works
- [x] Update with file replacement works
- [x] Update re-processes document correctly
- [x] Error handling for failed operations
- [x] UI feedback during operations
- [x] Form validation in edit modal

---

**Last Updated:** January 2025
