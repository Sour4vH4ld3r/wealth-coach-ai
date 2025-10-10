"""
RAG Retriever Service

Retrieves relevant context from the knowledge base using vector similarity search.
Handles query embedding, result ranking, and source attribution.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from backend.core.config import settings
from backend.services.vector_store.pgvector_store import PGVectorStore, get_vector_store
from backend.services.rag.embeddings import EmbeddingService, get_embedding_service

logger = logging.getLogger(__name__)


@dataclass
class RetrievedDocument:
  """
  Container for a retrieved document with metadata.
  """
  content: str
  metadata: Dict
  score: float
  source: str
  chunk_id: Optional[str] = None

  def to_dict(self) -> Dict:
    """Convert to dictionary representation."""
    return {
      "content": self.content,
      "metadata": self.metadata,
      "score": self.score,
      "source": self.source,
      "chunk_id": self.chunk_id,
    }


@dataclass
class RetrievalResult:
  """
  Container for retrieval results with context.
  """
  query: str
  documents: List[RetrievedDocument]
  total_found: int
  context: str
  sources: List[str]

  def to_dict(self) -> Dict:
    """Convert to dictionary representation."""
    return {
      "query": self.query,
      "documents": [doc.to_dict() for doc in self.documents],
      "total_found": self.total_found,
      "context": self.context,
      "sources": self.sources,
    }


class RAGRetriever:
  """
  Retrieval-Augmented Generation (RAG) retriever.

  Combines vector database search with embedding service to retrieve
  relevant context for answering user queries.
  """

  def __init__(
    self,
    vector_db: Optional[PGVectorStore] = None,
    embedding_service: Optional[EmbeddingService] = None,
    top_k: Optional[int] = None,
    similarity_threshold: Optional[float] = None,
    max_context_length: Optional[int] = None,
  ):
    """
    Initialize the RAG retriever.

    Args:
      vector_db: PGVectorStore instance
      embedding_service: Embedding service instance
      top_k: Number of documents to retrieve
      similarity_threshold: Minimum similarity score for results
      max_context_length: Maximum combined context length in characters
    """
    self.vector_db = vector_db or get_vector_store()
    self.embedding_service = embedding_service or get_embedding_service()

    self.top_k = top_k or settings.RAG_TOP_K
    self.similarity_threshold = similarity_threshold or settings.RAG_SIMILARITY_THRESHOLD
    self.max_context_length = max_context_length or settings.RAG_MAX_CONTEXT_LENGTH

    logger.info(
      f"RAGRetriever initialized: top_k={self.top_k}, "
      f"threshold={self.similarity_threshold}, "
      f"max_context={self.max_context_length}"
    )

  async def retrieve(
    self,
    query: str,
    top_k: Optional[int] = None,
    filters: Optional[Dict] = None,
  ) -> RetrievalResult:
    """
    Retrieve relevant documents for a query.

    Args:
      query: User query text
      top_k: Number of documents to retrieve (overrides default)
      filters: Optional metadata filters for search

    Returns:
      RetrievalResult with retrieved documents and context
    """
    k = top_k or self.top_k

    try:
      # Generate query embedding
      logger.debug(f"Generating embedding for query: {query[:100]}...")
      query_embedding = await self.embedding_service.embed_query_async(query)

      # Search vector database using pgvector
      logger.debug(f"Searching vector DB for top {k} results")
      search_results = self.vector_db.similarity_search(
        query_embedding=query_embedding,
        k=k * 2,  # Get more results for filtering
        threshold=self.similarity_threshold,
      )

      # Process and filter results
      documents = self._process_results(search_results)

      # Rank and deduplicate
      documents = self._rank_and_filter(documents)[:k]

      # Build context string
      context = self._build_context(documents)

      # Extract sources
      sources = self._extract_sources(documents)

      return RetrievalResult(
        query=query,
        documents=documents,
        total_found=len(documents),
        context=context,
        sources=sources,
      )

    except Exception as e:
      logger.error(f"Retrieval failed for query '{query}': {e}")
      # Return empty result on error
      return RetrievalResult(
        query=query,
        documents=[],
        total_found=0,
        context="",
        sources=[],
      )

  def retrieve_sync(
    self,
    query: str,
    top_k: Optional[int] = None,
    filters: Optional[Dict] = None,
  ) -> RetrievalResult:
    """
    Retrieve relevant documents for a query (synchronous version).

    Args:
      query: User query text
      top_k: Number of documents to retrieve
      filters: Optional metadata filters

    Returns:
      RetrievalResult with retrieved documents and context
    """
    k = top_k or self.top_k

    try:
      # Generate query embedding (sync)
      query_embedding = self.embedding_service.embed_query(query)

      # Search vector database using pgvector
      search_results = self.vector_db.similarity_search(
        query_embedding=query_embedding,
        k=k * 2,
        threshold=self.similarity_threshold,
      )

      # Process results
      documents = self._process_results(search_results)
      documents = self._rank_and_filter(documents)[:k]
      context = self._build_context(documents)
      sources = self._extract_sources(documents)

      return RetrievalResult(
        query=query,
        documents=documents,
        total_found=len(documents),
        context=context,
        sources=sources,
      )

    except Exception as e:
      logger.error(f"Retrieval failed for query '{query}': {e}")
      return RetrievalResult(
        query=query,
        documents=[],
        total_found=0,
        context="",
        sources=[],
      )

  def _process_results(self, search_results: List[Dict]) -> List[RetrievedDocument]:
    """
    Process raw search results into RetrievedDocument objects.

    Args:
      search_results: Raw results from pgvector (List of dicts)

    Returns:
      List of RetrievedDocument objects
    """
    documents = []

    for result in search_results:
      # pgvector returns similarity score (cosine similarity, 0-1 range)
      similarity = result.get("similarity", 0.0)

      # Similarity threshold already applied by pgvector, but double-check
      if similarity < self.similarity_threshold:
        continue

      metadata = result.get("metadata", {})
      source = metadata.get("source", "Unknown")

      documents.append(
        RetrievedDocument(
          content=result.get("content", ""),
          metadata=metadata,
          score=similarity,
          source=source,
          chunk_id=result.get("id"),
        )
      )

    return documents

  def _rank_and_filter(self, documents: List[RetrievedDocument]) -> List[RetrievedDocument]:
    """
    Rank documents by score and remove duplicates.

    Args:
      documents: List of retrieved documents

    Returns:
      Filtered and ranked list of documents
    """
    # Sort by score (descending)
    documents.sort(key=lambda d: d.score, reverse=True)

    # Remove near-duplicates based on content similarity
    seen_contents = set()
    filtered = []

    for doc in documents:
      # Use first 200 chars as duplicate check
      content_key = doc.content[:200].strip()

      if content_key not in seen_contents:
        seen_contents.add(content_key)
        filtered.append(doc)

    return filtered

  def _build_context(self, documents: List[RetrievedDocument]) -> str:
    """
    Build combined context string from retrieved documents.

    Args:
      documents: List of retrieved documents

    Returns:
      Combined context string, truncated to max length
    """
    if not documents:
      return ""

    context_parts = []
    current_length = 0

    for i, doc in enumerate(documents, 1):
      # Format: [Source 1] Content...
      part = f"[Source {i}: {doc.source}]\n{doc.content}\n"

      # Check if adding this would exceed max length
      if current_length + len(part) > self.max_context_length:
        # Truncate to fit
        remaining = self.max_context_length - current_length
        if remaining > 100:  # Only add if meaningful amount remains
          part = part[:remaining] + "..."
          context_parts.append(part)
        break

      context_parts.append(part)
      current_length += len(part)

    return "\n".join(context_parts)

  def _extract_sources(self, documents: List[RetrievedDocument]) -> List[str]:
    """
    Extract unique sources from documents.

    Args:
      documents: List of retrieved documents

    Returns:
      List of unique source identifiers
    """
    sources = []
    seen = set()

    for doc in documents:
      if doc.source not in seen:
        sources.append(doc.source)
        seen.add(doc.source)

    return sources

  async def retrieve_with_scores(
    self,
    query: str,
    top_k: Optional[int] = None,
  ) -> List[Tuple[str, float]]:
    """
    Retrieve documents with their similarity scores.

    Args:
      query: User query text
      top_k: Number of results to return

    Returns:
      List of (document_content, score) tuples
    """
    result = await self.retrieve(query, top_k=top_k)
    return [(doc.content, doc.score) for doc in result.documents]

  def get_retrieval_stats(self) -> Dict:
    """
    Get retrieval statistics.

    Returns:
      Dictionary with retrieval statistics
    """
    return {
      "top_k": self.top_k,
      "similarity_threshold": self.similarity_threshold,
      "max_context_length": self.max_context_length,
      "total_documents_in_db": self.vector_db.count(),
      "embedding_cache_stats": self.embedding_service.get_cache_stats(),
    }


# Global instance for dependency injection
_retriever_instance: Optional[RAGRetriever] = None


def get_retriever(
  vector_db: Optional[PGVectorStore] = None,
  embedding_service: Optional[EmbeddingService] = None,
) -> RAGRetriever:
  """
  Get or create the global RAGRetriever instance.

  Args:
    vector_db: Optional PGVectorStore instance
    embedding_service: Optional embedding service instance

  Returns:
    RAGRetriever instance
  """
  global _retriever_instance

  if _retriever_instance is None:
    _retriever_instance = RAGRetriever(
      vector_db=vector_db,
      embedding_service=embedding_service,
    )

  return _retriever_instance


def reset_retriever() -> None:
  """
  Reset the global RAGRetriever instance.

  Useful for testing or reinitialization.
  """
  global _retriever_instance
  _retriever_instance = None
