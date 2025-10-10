-- ================================================================
-- pgvector Setup for Wealth Warriors
-- Run this in Supabase SQL Editor
-- ================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- ================================================================
-- Create documents table for vector embeddings
-- ================================================================
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(384),  -- 384 dimensions for all-MiniLM-L6-v2
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- Create indexes for fast similarity search
-- ================================================================

-- HNSW index for vector similarity search (fast approximate search)
CREATE INDEX IF NOT EXISTS documents_embedding_idx
ON documents USING hnsw (embedding vector_cosine_ops);

-- GIN index for metadata filtering
CREATE INDEX IF NOT EXISTS documents_metadata_idx
ON documents USING gin (metadata);

-- Index for created_at (useful for sorting)
CREATE INDEX IF NOT EXISTS documents_created_at_idx
ON documents (created_at DESC);

-- ================================================================
-- Create similarity search function
-- ================================================================
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        id,
        content,
        metadata,
        1 - (embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- ================================================================
-- Create helper functions
-- ================================================================

-- Function to count total documents
CREATE OR REPLACE FUNCTION count_documents()
RETURNS bigint
LANGUAGE sql STABLE
AS $$
    SELECT COUNT(*) FROM documents;
$$;

-- Function to delete all documents (for testing)
CREATE OR REPLACE FUNCTION delete_all_documents()
RETURNS void
LANGUAGE sql
AS $$
    DELETE FROM documents;
$$;

-- ================================================================
-- Verification queries
-- ================================================================

-- Show table structure
\d documents

-- Show indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'documents';

-- Show functions
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_name LIKE '%document%';

-- ================================================================
-- Test queries (optional)
-- ================================================================

-- Insert a test document (uncomment to test)
-- INSERT INTO documents (content, metadata, embedding)
-- VALUES (
--     'Test document about 401k retirement accounts',
--     '{"source": "test.md", "category": "retirement"}'::jsonb,
--     array_fill(0.1, ARRAY[384])::vector
-- );

-- Count documents
-- SELECT count_documents();

-- Delete all (use with caution!)
-- SELECT delete_all_documents();

-- ================================================================
-- Success message
-- ================================================================
DO $$
BEGIN
    RAISE NOTICE 'pgvector setup complete! ✅';
    RAISE NOTICE 'Table "documents" created with vector(384) column';
    RAISE NOTICE 'Indexes created for fast similarity search';
    RAISE NOTICE 'Helper functions created';
END $$;
