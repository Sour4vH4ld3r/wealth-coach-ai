"""
LLM Client Service

Provides a unified interface for interacting with Large Language Models (OpenAI).
Includes token counting, cost tracking, error handling, and rate limiting.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, AsyncIterator
from dataclasses import dataclass, field

import tiktoken
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from tenacity import (
  retry,
  stop_after_attempt,
  wait_exponential,
  retry_if_exception_type,
)

from backend.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
  """Token usage tracking for a single request."""
  prompt_tokens: int = 0
  completion_tokens: int = 0
  total_tokens: int = 0

  @property
  def estimated_cost(self) -> float:
    """
    Estimate cost based on token usage (OpenAI pricing).

    Note: Prices are approximations for gpt-3.5-turbo.
    Update for different models or current pricing.
    """
    # GPT-3.5-turbo pricing (as of 2024)
    prompt_cost_per_1k = 0.0015
    completion_cost_per_1k = 0.002

    prompt_cost = (self.prompt_tokens / 1000) * prompt_cost_per_1k
    completion_cost = (self.completion_tokens / 1000) * completion_cost_per_1k

    return prompt_cost + completion_cost


@dataclass
class LLMResponse:
  """Structured response from LLM."""
  content: str
  model: str
  usage: TokenUsage
  finish_reason: str
  response_time: float
  cached: bool = False

  def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary representation."""
    return {
      "content": self.content,
      "model": self.model,
      "usage": {
        "prompt_tokens": self.usage.prompt_tokens,
        "completion_tokens": self.usage.completion_tokens,
        "total_tokens": self.usage.total_tokens,
        "estimated_cost": self.usage.estimated_cost,
      },
      "finish_reason": self.finish_reason,
      "response_time": self.response_time,
      "cached": self.cached,
    }


@dataclass
class LLMStats:
  """Global statistics for LLM usage."""
  total_requests: int = 0
  total_tokens: int = 0
  total_cost: float = 0.0
  cache_hits: int = 0
  cache_misses: int = 0
  errors: int = 0
  average_response_time: float = 0.0
  _response_times: List[float] = field(default_factory=list, repr=False)

  def add_request(self, response: LLMResponse) -> None:
    """Update statistics with a new request."""
    self.total_requests += 1
    self.total_tokens += response.usage.total_tokens
    self.total_cost += response.usage.estimated_cost

    if response.cached:
      self.cache_hits += 1
    else:
      self.cache_misses += 1

    self._response_times.append(response.response_time)
    self.average_response_time = sum(self._response_times) / len(self._response_times)

  def add_error(self) -> None:
    """Record an error."""
    self.errors += 1

  @property
  def cache_hit_rate(self) -> float:
    """Calculate cache hit rate."""
    total = self.cache_hits + self.cache_misses
    return self.cache_hits / total if total > 0 else 0.0


class LLMClient:
  """
  Client for interacting with Large Language Models.

  Provides:
  - Async and sync interfaces
  - Token counting and cost tracking
  - Automatic retries with exponential backoff
  - Response caching
  - Error handling
  """

  def __init__(
    self,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    timeout: Optional[int] = None,
    cache_client=None,
  ):
    """
    Initialize the LLM client.

    Args:
      api_key: OpenAI API key
      model: Model name to use
      max_tokens: Maximum tokens per completion
      temperature: Sampling temperature
      timeout: Request timeout in seconds
      cache_client: Optional Redis cache client
    """
    self.api_key = api_key or settings.OPENAI_API_KEY
    self.model = model or settings.OPENAI_MODEL
    self.max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS
    self.temperature = temperature or settings.OPENAI_TEMPERATURE
    self.timeout = timeout or settings.OPENAI_TIMEOUT
    self.cache_client = cache_client

    # Initialize OpenAI clients
    self.client = OpenAI(api_key=self.api_key, timeout=self.timeout)
    self.async_client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout)

    # Initialize token encoder for the model
    try:
      self.encoder = tiktoken.encoding_for_model(self.model)
    except KeyError:
      logger.warning(f"No encoder found for {self.model}, using cl100k_base")
      self.encoder = tiktoken.get_encoding("cl100k_base")

    # Statistics
    self.stats = LLMStats()

    logger.info(
      f"LLMClient initialized: model={self.model}, "
      f"max_tokens={self.max_tokens}, temperature={self.temperature}"
    )

  def count_tokens(self, text: str) -> int:
    """
    Count tokens in a text string.

    Args:
      text: Input text

    Returns:
      Number of tokens
    """
    try:
      return len(self.encoder.encode(text))
    except Exception as e:
      logger.error(f"Token counting error: {e}")
      # Fallback: rough estimate (1 token ≈ 4 chars)
      return len(text) // 4

  def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
    """
    Count tokens in a list of messages.

    Args:
      messages: List of message dictionaries

    Returns:
      Total number of tokens
    """
    # Tokens per message overhead
    tokens_per_message = 3
    tokens_per_name = 1

    num_tokens = 0
    for message in messages:
      num_tokens += tokens_per_message
      for key, value in message.items():
        num_tokens += self.count_tokens(str(value))
        if key == "name":
          num_tokens += tokens_per_name

    num_tokens += 3  # Every reply is primed with assistant
    return num_tokens

  async def _get_from_cache(self, cache_key: str) -> Optional[str]:
    """Retrieve response from cache."""
    if not self.cache_client or not settings.CACHE_ENABLED:
      return None

    try:
      return await self.cache_client.get(cache_key)
    except Exception as e:
      logger.warning(f"Cache retrieval error: {e}")
      return None

  async def _store_in_cache(self, cache_key: str, response: str) -> None:
    """Store response in cache."""
    if not self.cache_client or not settings.CACHE_ENABLED:
      return

    try:
      await self.cache_client.set(
        cache_key,
        response,
        ex=settings.QUERY_CACHE_TTL,
      )
    except Exception as e:
      logger.warning(f"Cache storage error: {e}")

  def _generate_cache_key(self, messages: List[Dict[str, str]]) -> str:
    """Generate cache key for a conversation."""
    import hashlib
    import json

    # Create deterministic string from messages
    messages_str = json.dumps(messages, sort_keys=True)
    hash_obj = hashlib.sha256(messages_str.encode())
    return f"llm:{self.model}:{hash_obj.hexdigest()}"

  @retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
  )
  async def chat(
    self,
    messages: List[Dict[str, str]],
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    use_cache: bool = True,
  ) -> LLMResponse:
    """
    Generate a chat completion (async with retries).

    Args:
      messages: List of message dictionaries with 'role' and 'content'
      max_tokens: Override default max tokens
      temperature: Override default temperature
      use_cache: Whether to use caching

    Returns:
      LLMResponse object with completion and metadata
    """
    start_time = time.time()
    cache_key = self._generate_cache_key(messages) if use_cache else None

    # Check cache
    if cache_key:
      cached_response = await self._get_from_cache(cache_key)
      if cached_response:
        response_time = time.time() - start_time
        usage = TokenUsage(
          prompt_tokens=self.count_messages_tokens(messages),
          completion_tokens=self.count_tokens(cached_response),
          total_tokens=0,  # Will be recalculated
        )
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens

        llm_response = LLMResponse(
          content=cached_response,
          model=self.model,
          usage=usage,
          finish_reason="stop",
          response_time=response_time,
          cached=True,
        )
        self.stats.add_request(llm_response)
        logger.info(f"Cache hit for LLM request (tokens: {usage.total_tokens})")
        return llm_response

    # Make API call
    try:
      response: ChatCompletion = await self.async_client.chat.completions.create(
        model=self.model,
        messages=messages,
        max_tokens=max_tokens or self.max_tokens,
        temperature=temperature or self.temperature,
      )

      response_time = time.time() - start_time
      content = response.choices[0].message.content or ""

      usage = TokenUsage(
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
        total_tokens=response.usage.total_tokens,
      )

      llm_response = LLMResponse(
        content=content,
        model=response.model,
        usage=usage,
        finish_reason=response.choices[0].finish_reason,
        response_time=response_time,
        cached=False,
      )

      # Cache the response
      if cache_key:
        await self._store_in_cache(cache_key, content)

      # Update statistics
      self.stats.add_request(llm_response)

      logger.info(
        f"LLM request completed: {usage.total_tokens} tokens, "
        f"${usage.estimated_cost:.4f}, {response_time:.2f}s"
      )

      return llm_response

    except Exception as e:
      self.stats.add_error()
      logger.error(f"LLM request failed: {e}")
      raise

  async def chat_stream(
    self,
    messages: List[Dict[str, str]],
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
  ) -> AsyncIterator[str]:
    """
    Generate a streaming chat completion (async generator).

    Args:
      messages: List of message dictionaries with 'role' and 'content'
      max_tokens: Override default max tokens
      temperature: Override default temperature

    Yields:
      Content chunks as they arrive from the API
    """
    try:
      stream = await self.async_client.chat.completions.create(
        model=self.model,
        messages=messages,
        max_tokens=max_tokens or self.max_tokens,
        temperature=temperature or self.temperature,
        stream=True,
      )

      async for chunk in stream:
        if chunk.choices[0].delta.content:
          yield chunk.choices[0].delta.content

    except Exception as e:
      self.stats.add_error()
      logger.error(f"LLM streaming request failed: {e}")
      raise

  def chat_sync(
    self,
    messages: List[Dict[str, str]],
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
  ) -> LLMResponse:
    """
    Generate a chat completion (synchronous).

    Args:
      messages: List of message dictionaries
      max_tokens: Override default max tokens
      temperature: Override default temperature

    Returns:
      LLMResponse object
    """
    start_time = time.time()

    try:
      response: ChatCompletion = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        max_tokens=max_tokens or self.max_tokens,
        temperature=temperature or self.temperature,
      )

      response_time = time.time() - start_time
      content = response.choices[0].message.content or ""

      usage = TokenUsage(
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
        total_tokens=response.usage.total_tokens,
      )

      llm_response = LLMResponse(
        content=content,
        model=response.model,
        usage=usage,
        finish_reason=response.choices[0].finish_reason,
        response_time=response_time,
        cached=False,
      )

      self.stats.add_request(llm_response)

      return llm_response

    except Exception as e:
      self.stats.add_error()
      logger.error(f"LLM request failed: {e}")
      raise

  async def chat_stream(
    self,
    messages: List[Dict[str, str]],
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
  ) -> AsyncIterator[str]:
    """
    Generate a streaming chat completion (async).

    Args:
      messages: List of message dictionaries
      max_tokens: Override default max tokens
      temperature: Override default temperature

    Yields:
      Content chunks as they arrive
    """
    try:
      stream = await self.async_client.chat.completions.create(
        model=self.model,
        messages=messages,
        max_tokens=max_tokens or self.max_tokens,
        temperature=temperature or self.temperature,
        stream=True,
      )

      async for chunk in stream:
        if chunk.choices[0].delta.content:
          yield chunk.choices[0].delta.content

    except Exception as e:
      self.stats.add_error()
      logger.error(f"LLM streaming request failed: {e}")
      raise

  def get_stats(self) -> Dict[str, Any]:
    """
    Get usage statistics.

    Returns:
      Dictionary with usage statistics
    """
    return {
      "total_requests": self.stats.total_requests,
      "total_tokens": self.stats.total_tokens,
      "total_cost": round(self.stats.total_cost, 4),
      "cache_hit_rate": round(self.stats.cache_hit_rate, 3),
      "errors": self.stats.errors,
      "average_response_time": round(self.stats.average_response_time, 2),
      "model": self.model,
    }

  def reset_stats(self) -> None:
    """Reset statistics."""
    self.stats = LLMStats()
    logger.info("LLM statistics reset")


# Global instance for dependency injection
_llm_client_instance: Optional[LLMClient] = None


def get_llm_client(cache_client=None) -> LLMClient:
  """
  Get or create the global LLMClient instance.

  Args:
    cache_client: Optional Redis cache client

  Returns:
    LLMClient instance
  """
  global _llm_client_instance

  if _llm_client_instance is None:
    _llm_client_instance = LLMClient(cache_client=cache_client)

  return _llm_client_instance


def reset_llm_client() -> None:
  """
  Reset the global LLMClient instance.

  Useful for testing or reinitialization.
  """
  global _llm_client_instance
  _llm_client_instance = None
