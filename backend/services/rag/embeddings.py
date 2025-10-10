"""
Embedding Service for RAG Pipeline

Generates text embeddings using SentenceTransformers with caching support
for improved performance and cost optimization.
"""

import os
import hashlib
import logging
from typing import List, Optional, Union
import asyncio

# Set tokenizers parallelism to false to avoid fork warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from sentence_transformers import SentenceTransformer

from backend.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
  """
  Service for generating text embeddings with caching.

  Uses SentenceTransformers for efficient local embedding generation.
  Integrates with Redis cache to avoid redundant computations.
  """

  def __init__(
    self,
    model_name: Optional[str] = None,
    cache_client=None,
  ):
    """
    Initialize the embedding service.

    Args:
      model_name: Name of the SentenceTransformer model to use
      cache_client: Optional Redis cache client for caching embeddings
    """
    self.model_name = model_name or settings.EMBEDDING_MODEL
    self.cache_client = cache_client
    self.cache_ttl = settings.EMBEDDING_CACHE_TTL

    # Load the model
    logger.info(f"Loading embedding model: {self.model_name}")
    try:
      self.model = SentenceTransformer(self.model_name)
      self.embedding_dimension = self.model.get_sentence_embedding_dimension()
      logger.info(
        f"Embedding model loaded successfully. Dimension: {self.embedding_dimension}"
      )
    except Exception as e:
      logger.error(f"Failed to load embedding model: {e}")
      raise

    # Statistics
    self.cache_hits = 0
    self.cache_misses = 0

  def _get_cache_key(self, text: str) -> str:
    """
    Generate a cache key for a text string.

    Args:
      text: Input text

    Returns:
      Cache key string
    """
    # Use hash of text as cache key for consistent lookup
    text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    return f"embedding:{self.model_name}:{text_hash}"

  async def _get_from_cache(self, text: str) -> Optional[List[float]]:
    """
    Retrieve embedding from cache if available.

    Args:
      text: Input text

    Returns:
      Cached embedding vector or None
    """
    if not self.cache_client or not settings.CACHE_ENABLED:
      return None

    try:
      cache_key = self._get_cache_key(text)
      cached = await self.cache_client.get(cache_key)

      if cached:
        self.cache_hits += 1
        logger.debug(f"Cache hit for text (length: {len(text)})")
        # Parse cached embedding (stored as comma-separated string)
        return [float(x) for x in cached.split(',')]

      self.cache_misses += 1
      return None

    except Exception as e:
      logger.warning(f"Cache retrieval error: {e}")
      return None

  async def _store_in_cache(self, text: str, embedding: List[float]) -> None:
    """
    Store embedding in cache.

    Args:
      text: Input text
      embedding: Embedding vector to cache
    """
    if not self.cache_client or not settings.CACHE_ENABLED:
      return

    try:
      cache_key = self._get_cache_key(text)
      # Store as comma-separated string for efficiency
      embedding_str = ','.join(map(str, embedding))
      await self.cache_client.set(
        cache_key,
        embedding_str,
        ex=self.cache_ttl,
      )
      logger.debug(f"Cached embedding for text (length: {len(text)})")

    except Exception as e:
      logger.warning(f"Cache storage error: {e}")

  def embed_sync(self, text: str) -> List[float]:
    """
    Generate embedding for a single text (synchronous).

    Args:
      text: Input text to embed

    Returns:
      Embedding vector as list of floats
    """
    try:
      embedding = self.model.encode(text, convert_to_numpy=True)
      return embedding.tolist()
    except Exception as e:
      logger.error(f"Failed to generate embedding: {e}")
      raise

  async def embed(self, text: str) -> List[float]:
    """
    Generate embedding for a single text with caching (async).

    Args:
      text: Input text to embed

    Returns:
      Embedding vector as list of floats
    """
    # Check cache first
    cached_embedding = await self._get_from_cache(text)
    if cached_embedding is not None:
      return cached_embedding

    # Generate new embedding in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    embedding = await loop.run_in_executor(None, self.embed_sync, text)

    # Cache the result
    await self._store_in_cache(text, embedding)

    return embedding

  def embed_batch_sync(
    self,
    texts: List[str],
    batch_size: Optional[int] = None,
    show_progress: bool = False,
  ) -> List[List[float]]:
    """
    Generate embeddings for multiple texts (synchronous, batched).

    Args:
      texts: List of texts to embed
      batch_size: Batch size for processing
      show_progress: Whether to show progress bar

    Returns:
      List of embedding vectors
    """
    batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE

    try:
      embeddings = self.model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
      )
      return [emb.tolist() for emb in embeddings]
    except Exception as e:
      logger.error(f"Failed to generate batch embeddings: {e}")
      raise

  async def embed_batch(
    self,
    texts: List[str],
    batch_size: Optional[int] = None,
    show_progress: bool = False,
  ) -> List[List[float]]:
    """
    Generate embeddings for multiple texts with caching (async).

    Args:
      texts: List of texts to embed
      batch_size: Batch size for processing
      show_progress: Whether to show progress bar

    Returns:
      List of embedding vectors
    """
    # Check cache for all texts
    cached_results = {}
    uncached_texts = []
    text_indices = {}

    for idx, text in enumerate(texts):
      cached = await self._get_from_cache(text)
      if cached is not None:
        cached_results[idx] = cached
      else:
        text_indices[len(uncached_texts)] = idx
        uncached_texts.append(text)

    # Generate embeddings for uncached texts
    if uncached_texts:
      loop = asyncio.get_event_loop()
      new_embeddings = await loop.run_in_executor(
        None,
        self.embed_batch_sync,
        uncached_texts,
        batch_size,
        show_progress,
      )

      # Cache new embeddings
      for uncached_idx, embedding in enumerate(new_embeddings):
        original_idx = text_indices[uncached_idx]
        cached_results[original_idx] = embedding
        await self._store_in_cache(uncached_texts[uncached_idx], embedding)

    # Return embeddings in original order
    return [cached_results[i] for i in range(len(texts))]

  def embed_documents(
    self,
    documents: List[str],
    show_progress: bool = True,
  ) -> List[List[float]]:
    """
    Generate embeddings for documents (convenience method).

    Args:
      documents: List of document texts
      show_progress: Whether to show progress bar

    Returns:
      List of embedding vectors
    """
    logger.info(f"Generating embeddings for {len(documents)} documents")
    return self.embed_batch_sync(documents, show_progress=show_progress)

  def embed_query(self, query: str) -> List[float]:
    """
    Generate embedding for a search query (convenience method).

    Args:
      query: Query text

    Returns:
      Query embedding vector
    """
    return self.embed_sync(query)

  async def embed_query_async(self, query: str) -> List[float]:
    """
    Generate embedding for a search query with caching (async).

    Args:
      query: Query text

    Returns:
      Query embedding vector
    """
    return await self.embed(query)

  def get_cache_stats(self) -> dict:
    """
    Get cache performance statistics.

    Returns:
      Dictionary with cache statistics
    """
    total_requests = self.cache_hits + self.cache_misses
    hit_rate = (
      self.cache_hits / total_requests if total_requests > 0 else 0.0
    )

    return {
      "cache_hits": self.cache_hits,
      "cache_misses": self.cache_misses,
      "total_requests": total_requests,
      "hit_rate": hit_rate,
      "cache_enabled": settings.CACHE_ENABLED and self.cache_client is not None,
    }

  def reset_cache_stats(self) -> None:
    """Reset cache statistics counters."""
    self.cache_hits = 0
    self.cache_misses = 0
    logger.info("Cache statistics reset")

  def get_model_info(self) -> dict:
    """
    Get information about the embedding model.

    Returns:
      Dictionary with model information
    """
    return {
      "model_name": self.model_name,
      "embedding_dimension": self.embedding_dimension,
      "max_seq_length": self.model.max_seq_length,
    }


# Global instance for dependency injection
_embedding_service_instance: Optional[EmbeddingService] = None


def get_embedding_service(cache_client=None) -> EmbeddingService:
  """
  Get or create the global EmbeddingService instance.

  Args:
    cache_client: Optional Redis cache client

  Returns:
    EmbeddingService instance
  """
  global _embedding_service_instance

  if _embedding_service_instance is None:
    _embedding_service_instance = EmbeddingService(cache_client=cache_client)

  return _embedding_service_instance


def reset_embedding_service() -> None:
  """
  Reset the global EmbeddingService instance.

  Useful for testing or reinitialization.
  """
  global _embedding_service_instance
  _embedding_service_instance = None
