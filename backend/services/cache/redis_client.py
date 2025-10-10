"""
Redis Cache Client Service

Provides async interface for Redis caching with connection pooling,
error handling, and common cache operations.
"""

import logging
import json
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError, ConnectionError, TimeoutError

from backend.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
  """
  Async Redis client wrapper with connection pooling and error handling.

  Provides:
  - Connection pooling for efficient resource usage
  - Automatic retries and error handling
  - Type-safe get/set operations with JSON serialization
  - TTL management
  - Health checks
  """

  def __init__(
    self,
    url: Optional[str] = None,
    password: Optional[str] = None,
    max_connections: Optional[int] = None,
    decode_responses: bool = True,
  ):
    """
    Initialize Redis client with connection pool.

    Args:
      url: Redis connection URL
      password: Redis password
      max_connections: Maximum connections in pool
      decode_responses: Whether to decode responses to strings
    """
    self.url = url or settings.REDIS_URL
    self.password = password or settings.REDIS_PASSWORD
    self.max_connections = max_connections or settings.REDIS_MAX_CONNECTIONS
    self.decode_responses = decode_responses

    # Create connection pool
    self.pool: Optional[ConnectionPool] = None
    self.client: Optional[Redis] = None
    self._connected = False

    # Statistics
    self.hits = 0
    self.misses = 0
    self.errors = 0

    logger.info(f"RedisClient initialized: {self.url}")

  async def connect(self) -> None:
    """
    Establish connection to Redis.

    Creates connection pool and Redis client instance.
    """
    if self._connected:
      logger.debug("Redis already connected")
      return

    try:
      self.pool = ConnectionPool.from_url(
        self.url,
        password=self.password,
        max_connections=self.max_connections,
        decode_responses=self.decode_responses,
      )

      self.client = Redis(connection_pool=self.pool)

      # Test connection
      await self.client.ping()
      self._connected = True

      logger.info("Redis connection established")

    except Exception as e:
      logger.error(f"Failed to connect to Redis: {e}")
      self._connected = False
      raise

  async def disconnect(self) -> None:
    """
    Close Redis connection and cleanup resources.
    """
    if not self._connected:
      return

    try:
      if self.client:
        await self.client.close()

      if self.pool:
        await self.pool.disconnect()

      self._connected = False
      logger.info("Redis connection closed")

    except Exception as e:
      logger.error(f"Error disconnecting from Redis: {e}")

  async def ensure_connected(self) -> None:
    """
    Ensure Redis connection is established.

    Attempts to reconnect if connection is lost.
    """
    if not self._connected:
      await self.connect()

  @asynccontextmanager
  async def _handle_errors(self, operation: str):
    """
    Context manager for consistent error handling.

    Args:
      operation: Name of the operation for logging
    """
    try:
      yield
    except (ConnectionError, TimeoutError) as e:
      self.errors += 1
      logger.error(f"Redis connection error during {operation}: {e}")
      # Attempt reconnection
      self._connected = False
      raise
    except RedisError as e:
      self.errors += 1
      logger.error(f"Redis error during {operation}: {e}")
      raise
    except Exception as e:
      self.errors += 1
      logger.error(f"Unexpected error during {operation}: {e}")
      raise

  async def get(self, key: str, default: Any = None) -> Optional[str]:
    """
    Get value for a key.

    Args:
      key: Cache key
      default: Default value if key not found

    Returns:
      Cached value or default
    """
    await self.ensure_connected()

    async with self._handle_errors("get"):
      value = await self.client.get(key)

      if value is not None:
        self.hits += 1
        logger.debug(f"Cache hit: {key}")
        return value
      else:
        self.misses += 1
        logger.debug(f"Cache miss: {key}")
        return default

  async def get_json(self, key: str, default: Any = None) -> Any:
    """
    Get JSON value for a key.

    Args:
      key: Cache key
      default: Default value if key not found

    Returns:
      Deserialized JSON value or default
    """
    value = await self.get(key)

    if value is None:
      return default

    try:
      return json.loads(value)
    except json.JSONDecodeError as e:
      logger.error(f"Failed to decode JSON for key {key}: {e}")
      return default

  async def set(
    self,
    key: str,
    value: str,
    ex: Optional[int] = None,
    nx: bool = False,
    xx: bool = False,
  ) -> bool:
    """
    Set a key-value pair.

    Args:
      key: Cache key
      value: Value to store
      ex: Expiration time in seconds
      nx: Only set if key doesn't exist
      xx: Only set if key exists

    Returns:
      True if successful
    """
    await self.ensure_connected()

    async with self._handle_errors("set"):
      result = await self.client.set(key, value, ex=ex, nx=nx, xx=xx)
      logger.debug(f"Cache set: {key} (TTL: {ex}s)")
      return bool(result)

  async def set_json(
    self,
    key: str,
    value: Any,
    ex: Optional[int] = None,
  ) -> bool:
    """
    Set a key with JSON-serialized value.

    Args:
      key: Cache key
      value: Value to serialize and store
      ex: Expiration time in seconds

    Returns:
      True if successful
    """
    try:
      json_value = json.dumps(value)
      return await self.set(key, json_value, ex=ex)
    except (TypeError, ValueError) as e:
      logger.error(f"Failed to serialize value for key {key}: {e}")
      return False

  async def delete(self, *keys: str) -> int:
    """
    Delete one or more keys.

    Args:
      keys: Keys to delete

    Returns:
      Number of keys deleted
    """
    await self.ensure_connected()

    async with self._handle_errors("delete"):
      count = await self.client.delete(*keys)
      logger.debug(f"Deleted {count} keys")
      return count

  async def exists(self, *keys: str) -> int:
    """
    Check if keys exist.

    Args:
      keys: Keys to check

    Returns:
      Number of existing keys
    """
    await self.ensure_connected()

    async with self._handle_errors("exists"):
      return await self.client.exists(*keys)

  async def expire(self, key: str, seconds: int) -> bool:
    """
    Set expiration time for a key.

    Args:
      key: Cache key
      seconds: Expiration time in seconds

    Returns:
      True if successful
    """
    await self.ensure_connected()

    async with self._handle_errors("expire"):
      result = await self.client.expire(key, seconds)
      return bool(result)

  async def ttl(self, key: str) -> int:
    """
    Get remaining TTL for a key.

    Args:
      key: Cache key

    Returns:
      Remaining seconds (-1 if no expiry, -2 if key doesn't exist)
    """
    await self.ensure_connected()

    async with self._handle_errors("ttl"):
      return await self.client.ttl(key)

  async def incr(self, key: str, amount: int = 1) -> int:
    """
    Increment a counter.

    Args:
      key: Counter key
      amount: Amount to increment

    Returns:
      New value after increment
    """
    await self.ensure_connected()

    async with self._handle_errors("incr"):
      return await self.client.incrby(key, amount)

  async def decr(self, key: str, amount: int = 1) -> int:
    """
    Decrement a counter.

    Args:
      key: Counter key
      amount: Amount to decrement

    Returns:
      New value after decrement
    """
    await self.ensure_connected()

    async with self._handle_errors("decr"):
      return await self.client.decrby(key, amount)

  async def get_many(self, *keys: str) -> List[Optional[str]]:
    """
    Get multiple values at once.

    Args:
      keys: Keys to retrieve

    Returns:
      List of values (None for missing keys)
    """
    await self.ensure_connected()

    async with self._handle_errors("mget"):
      values = await self.client.mget(*keys)

      # Update statistics
      for value in values:
        if value is not None:
          self.hits += 1
        else:
          self.misses += 1

      return values

  async def set_many(self, mapping: Dict[str, str]) -> bool:
    """
    Set multiple key-value pairs at once.

    Args:
      mapping: Dictionary of key-value pairs

    Returns:
      True if successful
    """
    await self.ensure_connected()

    async with self._handle_errors("mset"):
      result = await self.client.mset(mapping)
      return bool(result)

  async def clear_pattern(self, pattern: str) -> int:
    """
    Delete all keys matching a pattern.

    Args:
      pattern: Key pattern (e.g., 'user:*')

    Returns:
      Number of keys deleted
    """
    await self.ensure_connected()

    async with self._handle_errors("clear_pattern"):
      keys = []
      async for key in self.client.scan_iter(match=pattern):
        keys.append(key)

      if keys:
        return await self.client.delete(*keys)
      return 0

  async def ping(self) -> bool:
    """
    Check if Redis is responsive.

    Returns:
      True if Redis responds to ping
    """
    try:
      await self.ensure_connected()
      result = await self.client.ping()
      return result
    except Exception as e:
      logger.error(f"Redis ping failed: {e}")
      return False

  async def info(self, section: Optional[str] = None) -> Dict[str, Any]:
    """
    Get Redis server information.

    Args:
      section: Optional section name (e.g., 'memory', 'stats')

    Returns:
      Dictionary with server information
    """
    await self.ensure_connected()

    async with self._handle_errors("info"):
      info = await self.client.info(section)
      return info

  async def flushdb(self) -> bool:
    """
    Delete all keys in current database.

    Warning: This is a destructive operation.

    Returns:
      True if successful
    """
    await self.ensure_connected()

    async with self._handle_errors("flushdb"):
      result = await self.client.flushdb()
      logger.warning("Redis database flushed")
      return bool(result)

  def get_stats(self) -> Dict[str, Any]:
    """
    Get cache statistics.

    Returns:
      Dictionary with cache statistics
    """
    total = self.hits + self.misses
    hit_rate = self.hits / total if total > 0 else 0.0

    return {
      "hits": self.hits,
      "misses": self.misses,
      "total_requests": total,
      "hit_rate": round(hit_rate, 3),
      "errors": self.errors,
      "connected": self._connected,
    }

  def reset_stats(self) -> None:
    """Reset statistics counters."""
    self.hits = 0
    self.misses = 0
    self.errors = 0
    logger.info("Redis statistics reset")

  async def health_check(self) -> Dict[str, Any]:
    """
    Perform comprehensive health check.

    Returns:
      Dictionary with health status and metrics
    """
    try:
      # Ping test
      ping_success = await self.ping()

      # Get server info
      info = await self.info("stats") if ping_success else {}

      # Get stats
      stats = self.get_stats()

      return {
        "status": "healthy" if ping_success else "unhealthy",
        "connected": self._connected,
        "ping": ping_success,
        "stats": stats,
        "server_info": {
          "total_connections": info.get("total_connections_received", 0),
          "total_commands": info.get("total_commands_processed", 0),
        },
      }

    except Exception as e:
      logger.error(f"Health check failed: {e}")
      return {
        "status": "unhealthy",
        "connected": False,
        "error": str(e),
      }


# Global instance for dependency injection
_redis_client_instance: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
  """
  Get or create the global RedisClient instance.

  Returns:
    RedisClient instance (connected)
  """
  global _redis_client_instance

  if _redis_client_instance is None:
    _redis_client_instance = RedisClient()
    await _redis_client_instance.connect()

  return _redis_client_instance


async def close_redis_client() -> None:
  """
  Close the global RedisClient instance.

  Useful for cleanup on application shutdown.
  """
  global _redis_client_instance

  if _redis_client_instance is not None:
    await _redis_client_instance.disconnect()
    _redis_client_instance = None


def reset_redis_client() -> None:
  """
  Reset the global RedisClient instance.

  Note: Does not disconnect. Use close_redis_client() for cleanup.
  Useful for testing.
  """
  global _redis_client_instance
  _redis_client_instance = None
