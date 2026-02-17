-- =============================================
-- SUPABASE MIGRATION FOR CRANSWICK TECH STANDARDS
-- Run this in your Supabase SQL Editor
-- =============================================

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- =============================================
-- DOCUMENTS TABLE (Vector Store)
-- =============================================
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI ada-002 embeddings are 1536 dimensions
    title TEXT,
    category TEXT,
    tags TEXT[] DEFAULT '{}',
    layer TEXT,  -- 'policy', 'principle', 'sop'
    chunk_index INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster document_id lookups
CREATE INDEX IF NOT EXISTS idx_documents_document_id ON documents(document_id);

-- Create index for vector similarity search (IVFFlat for faster approximate search)
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- =============================================
-- CONVERSATIONS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT DEFAULT 'New Conversation',
    language TEXT DEFAULT 'en',
    message_count INTEGER DEFAULT 0,
    total_response_time_ms FLOAT DEFAULT 0,
    average_response_time_ms FLOAT DEFAULT 0,
    total_queries INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- MESSAGES TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    sources JSONB,
    response_time_ms FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster conversation message lookups
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- =============================================
-- RATINGS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS ratings (
    id TEXT PRIMARY KEY,
    message_id TEXT REFERENCES messages(id) ON DELETE CASCADE,
    conversation_id TEXT REFERENCES conversations(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- FEEDBACK TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS feedback (
    id TEXT PRIMARY KEY,
    message_id TEXT REFERENCES messages(id) ON DELETE CASCADE,
    conversation_id TEXT REFERENCES conversations(id) ON DELETE CASCADE,
    feedback_type TEXT,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- GENERATED DOCUMENTS TABLE (for PDF/DOCX generation)
-- =============================================
CREATE TABLE IF NOT EXISTS generated_documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    document_type TEXT,  -- 'principle', 'risk-assessment', etc.
    format TEXT,  -- 'pdf', 'docx', 'markdown'
    content TEXT,
    storage_path TEXT,  -- Path in Supabase Storage
    download_url TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- VECTOR SIMILARITY SEARCH FUNCTION
-- =============================================
CREATE OR REPLACE FUNCTION match_documents (
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    filter_category TEXT DEFAULT NULL
)
RETURNS TABLE (
    id TEXT,
    document_id TEXT,
    content TEXT,
    title TEXT,
    category TEXT,
    tags TEXT[],
    chunk_index INTEGER,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.document_id,
        d.content,
        d.title,
        d.category,
        d.tags,
        d.chunk_index,
        d.metadata,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM documents d
    WHERE 
        (filter_category IS NULL OR d.category = filter_category)
        AND d.embedding IS NOT NULL
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- =============================================
-- ROW LEVEL SECURITY (Optional - enable if needed)
-- =============================================
-- For now, we're using service_role key which bypasses RLS
-- Uncomment below if you want to enable RLS later

-- ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ratings ENABLE ROW LEVEL SECURITY;

-- =============================================
-- STORAGE BUCKET (Run separately or via dashboard)
-- =============================================
-- Create a storage bucket named 'documents' via Supabase Dashboard
-- Settings > Storage > New Bucket > Name: "documents" > Private

-- =============================================
-- VERIFICATION QUERIES
-- =============================================
-- Run these to verify setup:

-- Check tables exist:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Check pgvector extension:
-- SELECT * FROM pg_extension WHERE extname = 'vector';

-- Test vector function:
-- SELECT * FROM match_documents(
--     '[0.1, 0.2, ...]'::vector(1536),  -- Your 1536-dim vector
--     5,
--     NULL
-- );
