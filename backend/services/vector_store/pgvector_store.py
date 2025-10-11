"""
pgvector Vector Store Service
Manages document embeddings and semantic search using Supabase pgvector
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import text
import numpy as np
import logging

from backend.db.database import SessionLocal, engine
from backend.db.models import Document

logger = logging.getLogger(__name__)


class PGVectorStore:
    """Vector store using Supabase PostgreSQL with pgvector extension"""

    def __init__(self):
        self.dimension = 384  # all-MiniLM-L6-v2 embedding dimension

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> List[str]:
        """
        Add documents with embeddings to vector store

        Args:
            texts: List of document texts
            metadatas: Optional metadata for each document
            embeddings: Pre-computed embeddings (if None, caller must compute)

        Returns:
            List of document IDs
        """
        if not embeddings:
            raise ValueError("Embeddings must be provided")

        db = SessionLocal()
        try:
            doc_ids = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                metadata = metadatas[i] if metadatas and i < len(metadatas) else {}

                doc = Document(
                    content=text,
                    meta=metadata,
                    embedding=embedding
                )
                db.add(doc)
                doc_ids.append(str(doc.id))

            db.commit()
            logger.info(f"Added {len(doc_ids)} documents to pgvector")
            return doc_ids

        except Exception as e:
            db.rollback()
            logger.error(f"Error adding documents: {e}")
            raise
        finally:
            db.close()

    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity

        Args:
            query_embedding: Query vector embedding
            k: Number of results to return
            threshold: Minimum similarity threshold (0-1)

        Returns:
            List of matching documents with similarity scores
        """
        db = SessionLocal()
        try:
            # Use the match_documents function we created
            # Cast the embedding array to vector type
            result = db.execute(
                text("""
                    SELECT id, content, metadata, similarity
                    FROM match_documents(CAST(:embedding AS vector), :threshold, :limit)
                """),
                {
                    "embedding": str(query_embedding),
                    "threshold": threshold,
                    "limit": k
                }
            )

            documents = []
            for row in result:
                documents.append({
                    "id": str(row.id),
                    "content": row.content,
                    "metadata": row.metadata or {},
                    "similarity": float(row.similarity)
                })

            logger.info(f"Found {len(documents)} similar documents (threshold={threshold})")
            return documents

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
        finally:
            db.close()

    def delete_all(self):
        """Delete all documents (use with caution!)"""
        db = SessionLocal()
        try:
            count = db.query(Document).count()
            db.query(Document).delete()
            db.commit()
            logger.info(f"Deleted {count} documents from pgvector")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting documents: {e}")
            raise
        finally:
            db.close()

    def count(self) -> int:
        """Count total documents in vector store"""
        db = SessionLocal()
        try:
            return db.query(Document).count()
        finally:
            db.close()

    def get_by_metadata(
        self,
        metadata_filter: Dict[str, Any],
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get documents by metadata filter

        Args:
            metadata_filter: JSONB filter (e.g., {"source": "sample.md"})
            limit: Maximum number of results

        Returns:
            List of matching documents
        """
        db = SessionLocal()
        try:
            # Use JSONB containment operator
            import json

            result = db.execute(
                text("""
                    SELECT id, content, metadata, created_at
                    FROM documents
                    WHERE metadata @> :filter::jsonb
                    ORDER BY created_at DESC
                    LIMIT :limit
                """),
                {
                    "filter": json.dumps(metadata_filter),
                    "limit": limit
                }
            )

            documents = []
            for row in result:
                documents.append({
                    "id": str(row.id),
                    "content": row.content,
                    "metadata": row.metadata or {},
                    "created_at": row.created_at.isoformat()
                })

            return documents

        finally:
            db.close()


# Singleton instance
_vector_store = None


def get_vector_store() -> PGVectorStore:
    """Get or create vector store singleton"""
    global _vector_store
    if _vector_store is None:
        _vector_store = PGVectorStore()
    return _vector_store
