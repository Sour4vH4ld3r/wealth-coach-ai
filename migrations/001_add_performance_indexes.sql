-- Performance Optimization Migration
-- Adds indexes to improve query performance for chat sessions and messages
-- Run this on existing databases to add indexes

-- Add indexes to chat_sessions table
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at);

-- Add indexes to chat_messages table
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

-- Add composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_role ON chat_messages(session_id, role);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created ON chat_messages(session_id, created_at DESC);

-- Verify indexes were created
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
  AND (tablename = 'chat_sessions' OR tablename = 'chat_messages')
ORDER BY tablename, indexname;
