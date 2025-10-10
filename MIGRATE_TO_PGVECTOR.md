# Migrate from ChromaDB to pgvector (Supabase)

## Why pgvector?

✅ **Single Cloud Database**: PostgreSQL + vectors in Supabase
✅ **No Local Storage**: Everything in cloud
✅ **Better Performance**: Native PostgreSQL indexing
✅ **Simpler Deployment**: One less service
✅ **Free Tier**: Included in Supabase

---

## Step 1: Enable pgvector Extension in Supabase

### Via Supabase Dashboard

1. Go to https://supabase.com/dashboard
2. Select your project: **qfcnomdgpcpnsibihwvm**
3. Click **Database** in left sidebar
4. Click **Extensions** tab
5. Search for **"vector"** or **"pgvector"**
6. Click **Enable** button next to pgvector

### Via SQL (Alternative)

1. In Supabase dashboard, go to **SQL Editor**
2. Run this command:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify it's enabled
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## Step 2: Create Vector Table

Run this SQL in Supabase SQL Editor:

```sql
-- Create documents table for vector embeddings
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(384),  -- 384 dimensions for all-MiniLM-L6-v2
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for vector similarity search (using HNSW)
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);

-- Create index for metadata filtering
CREATE INDEX ON documents USING gin (metadata);

-- Create function for similarity search
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(384),
    match_threshold float,
    match_count int
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
```

**What this does:**
- Creates `documents` table with vector column (384 dimensions)
- Creates HNSW index for fast similarity search
- Creates function `match_documents` for easy querying

---

## Step 3: Update .env Configuration

Update your `.env` file:

```env
# -----------------------------------------------------------------------------
# VECTOR DATABASE - pgvector (Supabase)
# -----------------------------------------------------------------------------
# Use pgvector instead of ChromaDB
USE_PGVECTOR=true
CHROMA_PERSIST_DIR="./data/vector_store"  # Not used when USE_PGVECTOR=true
CHROMA_HOST="localhost"  # Not used when USE_PGVECTOR=true
CHROMA_PORT=8001  # Not used when USE_PGVECTOR=true
CHROMA_COLLECTION_NAME="wealth_coach_knowledge"  # Not used

# Embedding Model (HuggingFace)
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION=384
EMBEDDING_BATCH_SIZE=32

# RAG Configuration (pgvector)
RAG_TOP_K=5  # Number of documents to retrieve
RAG_SIMILARITY_THRESHOLD=0.7
RAG_MAX_CONTEXT_LENGTH=2000
```

---

## Step 4: Update Database Models

Create new model in `backend/db/models.py`:

```python
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

from backend.db.database import Base


class Document(Base):
    """Document model for vector embeddings"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    metadata = Column(JSON)
    embedding = Column(Vector(384))  # 384 dimensions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## Step 5: Create pgvector Service

Create `backend/services/vector_store/pgvector_store.py`:

```python
"""
pgvector Vector Store Service
Replaces ChromaDB with Supabase pgvector
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
import numpy as np

from backend.db.database import SessionLocal
from backend.db.models import Document
from backend.services.rag.embeddings import get_embeddings
from backend.core.config import settings


class PGVectorStore:
    """pgvector-based vector store using Supabase PostgreSQL"""

    def __init__(self):
        self.embedding_model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Add documents with embeddings to vector store"""
        db = SessionLocal()
        try:
            # Generate embeddings
            embeddings = get_embeddings(texts)

            # Create document records
            documents = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                metadata = metadatas[i] if metadatas else {}
                doc = Document(
                    content=text,
                    metadata=metadata,
                    embedding=embedding.tolist()
                )
                documents.append(doc)

            # Bulk insert
            db.bulk_save_objects(documents)
            db.commit()

            # Return IDs
            return [str(doc.id) for doc in documents]

        finally:
            db.close()

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity"""
        db = SessionLocal()
        try:
            # Generate query embedding
            query_embedding = get_embeddings([query])[0]

            # Use custom match_documents function
            result = db.execute(
                text("""
                    SELECT id, content, metadata, similarity
                    FROM match_documents(:embedding, :threshold, :limit)
                """),
                {
                    "embedding": query_embedding.tolist(),
                    "threshold": threshold,
                    "limit": k
                }
            )

            # Format results
            documents = []
            for row in result:
                documents.append({
                    "id": str(row.id),
                    "content": row.content,
                    "metadata": row.metadata,
                    "similarity": float(row.similarity)
                })

            return documents

        finally:
            db.close()

    def delete_all(self):
        """Delete all documents (use with caution!)"""
        db = SessionLocal()
        try:
            db.query(Document).delete()
            db.commit()
        finally:
            db.close()

    def count(self) -> int:
        """Count total documents in vector store"""
        db = SessionLocal()
        try:
            return db.query(Document).count()
        finally:
            db.close()
```

---

## Step 6: Update RAG Retriever

Update `backend/services/rag/retriever.py`:

```python
"""
RAG Document Retriever - pgvector version
"""

from typing import List, Dict, Any
from backend.services.vector_store.pgvector_store import PGVectorStore
from backend.core.config import settings


class RAGRetriever:
    """Retrieve relevant documents for RAG"""

    def __init__(self):
        self.vector_store = PGVectorStore()
        self.top_k = settings.RAG_TOP_K
        self.similarity_threshold = settings.RAG_SIMILARITY_THRESHOLD

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        k = top_k or self.top_k
        thresh = threshold or self.similarity_threshold

        # Search vector store
        results = self.vector_store.similarity_search(
            query=query,
            k=k,
            threshold=thresh
        )

        return results

    def get_context(self, query: str) -> str:
        """Get formatted context string for LLM prompt"""
        documents = self.retrieve(query)

        if not documents:
            return "No relevant information found."

        # Format context
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.get("metadata", {}).get("source", "Unknown")
            content = doc["content"]
            context_parts.append(f"[{i}] Source: {source}\n{content}")

        return "\n\n".join(context_parts)
```

---

## Step 7: Load Knowledge Base into pgvector

Create `scripts/load_knowledge_pgvector.py`:

```python
#!/usr/bin/env python3
"""
Load Knowledge Base into pgvector
Migrates from ChromaDB to Supabase pgvector
"""

import sys
import os
sys.path.insert(0, ".")

from backend.services.vector_store.pgvector_store import PGVectorStore
from backend.core.config import settings
import glob
from pathlib import Path


def load_markdown_files(directory: str):
    """Load all markdown files from knowledge base"""
    documents = []
    metadatas = []

    md_files = glob.glob(f"{directory}/**/*.md", recursive=True)

    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into chunks (simple splitting by paragraphs)
        chunks = content.split('\n\n')
        for chunk in chunks:
            if chunk.strip():
                documents.append(chunk.strip())
                metadatas.append({
                    "source": Path(file_path).name,
                    "file_path": file_path
                })

    return documents, metadatas


def main():
    print("=" * 70)
    print("Loading Knowledge Base into pgvector (Supabase)")
    print("=" * 70)
    print()

    vector_store = PGVectorStore()

    # Clear existing documents
    print("🗑️  Clearing existing documents...")
    vector_store.delete_all()
    print("✅ Cleared")
    print()

    # Load documents
    kb_path = settings.KNOWLEDGE_BASE_PATH
    print(f"📂 Loading from: {kb_path}")
    documents, metadatas = load_markdown_files(kb_path)
    print(f"📄 Found {len(documents)} document chunks")
    print()

    # Add to vector store
    print("💾 Adding documents to pgvector...")
    doc_ids = vector_store.add_documents(documents, metadatas)
    print(f"✅ Added {len(doc_ids)} documents")
    print()

    # Verify
    count = vector_store.count()
    print(f"📊 Total documents in vector store: {count}")
    print()

    print("=" * 70)
    print("✅ Knowledge base loaded successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

---

## Step 8: Install Required Package

```bash
# Install pgvector Python client
pip install pgvector
```

Add to `requirements.txt`:
```txt
pgvector==0.2.4
```

---

## Step 9: Run Migration

```bash
# 1. Enable pgvector in Supabase (via dashboard or SQL)

# 2. Install pgvector package
source venv/bin/activate
pip install pgvector

# 3. Create documents table (run SQL in Supabase SQL Editor)

# 4. Update .env to use pgvector
# Set USE_PGVECTOR=true

# 5. Load knowledge base
python scripts/load_knowledge_pgvector.py

# 6. Test
python -c "
from backend.services.vector_store.pgvector_store import PGVectorStore
store = PGVectorStore()
print(f'Documents in vector store: {store.count()}')
results = store.similarity_search('What is a 401k?', k=3)
print(f'Found {len(results)} results')
for r in results:
    print(f'  - {r[\"content\"][:50]}... (similarity: {r[\"similarity\"]:.2f})')
"
```

---

## Step 10: Update Docker Compose (Optional)

Since you're no longer using ChromaDB, remove it from `docker-compose.yml`:

```yaml
# Comment out or remove ChromaDB service
# chromadb:
#   image: chromadb/chroma:latest
#   ...

# Remove chromadb from backend dependencies
backend:
  depends_on:
    - redis
    # - chromadb  # Remove this
```

---

## Comparison: ChromaDB vs pgvector

| Feature | ChromaDB (Local) | pgvector (Supabase) |
|---------|------------------|---------------------|
| **Storage** | Local files | Cloud database |
| **Setup** | Manual | Managed |
| **Scaling** | Manual | Automatic |
| **Backups** | Manual | Automatic (Supabase) |
| **Cost** | Free (local) | Free (Supabase tier) |
| **Deployment** | Need to deploy | Already deployed |
| **Queries** | HTTP API | SQL |
| **Performance** | Good | Excellent (HNSW index) |
| **Maintenance** | You manage | Supabase manages |

---

## Benefits Summary

✅ **Simplified Architecture**: PostgreSQL + Redis + OpenAI only
✅ **Fully Cloud**: No local dependencies
✅ **Better Performance**: Native PostgreSQL indexing
✅ **ACID Transactions**: Data consistency
✅ **Easier Deployment**: One less service
✅ **Free Tier**: Included in Supabase

---

## Next Steps

1. ✅ Enable pgvector in Supabase dashboard
2. ✅ Run SQL to create documents table
3. ✅ Install pgvector package: `pip install pgvector`
4. ✅ Update `.env`: Set `USE_PGVECTOR=true`
5. ✅ Create pgvector service code
6. ✅ Load knowledge base: `python scripts/load_knowledge_pgvector.py`
7. ✅ Test: Start backend and query

Your vector database will be fully cloud-based! 🚀
