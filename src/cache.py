"""
Redis cache module for Email System.
Provides caching decorators and cache invalidation utilities.
"""
import os
import json
import redis
from functools import wraps
from typing import Optional, Any, Callable
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache handler with serialization support."""
    
    def __init__(self):
        host = os.environ.get('REDIS_HOST', 'localhost')
        port = int(os.environ.get('REDIS_PORT', 6379))
        db = int(os.environ.get('REDIS_DB', 0))
        
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            socket_connect_timeout=5
        )
        self._connected = None
    
    def is_connected(self) -> bool:
        """Check if Redis is available."""
        if self._connected is not None:
            return self._connected
        
        try:
            self.redis.ping()
            self._connected = True
            logger.info("Connected to Redis")
        except redis.ConnectionError:
            self._connected = False
            logger.warning("Redis not available, caching disabled")
        
        return self._connected
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.is_connected():
            return None
        
        try:
            value = self.redis.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except (json.JSONDecodeError, redis.RedisError) as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL (seconds)."""
        if not self.is_connected():
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except (TypeError, redis.RedisError) as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.is_connected():
            return False
        
        try:
            self.redis.delete(key)
            logger.debug(f"Cache delete: {key}")
            return True
        except redis.RedisError as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> bool:
        """Delete keys matching pattern."""
        if not self.is_connected():
            return False
        
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                logger.debug(f"Cache delete pattern: {pattern} ({len(keys)} keys)")
            return True
        except redis.RedisError as e:
            logger.error(f"Cache delete pattern error: {e}")
            return False
    
    def invalidate_user(self, user_id: int):
        """Invalidate all caches for a user."""
        self.delete(f"user:id:{user_id}")
        self.delete_pattern(f"user:{user_id}:folders")
    
    def invalidate_folder(self, folder_id: int):
        """Invalidate cache for a folder and its messages."""
        self.delete(f"folder:{folder_id}:messages")
    
    def invalidate_message(self, message_id: int):
        """Invalidate cache for a message."""
        self.delete(f"message:{message_id}")


# Global cache instance
cache = RedisCache()


def cached(key_prefix: str, ttl: int = 300):
    """
    Decorator for caching function results.
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            key = f"{key_prefix}:{func.__name__}:"
            
            # Add positional args
            for arg in args:
                key += f"{arg}:"
            
            # Add keyword args
            for k, v in sorted(kwargs.items()):
                key += f"{k}={v}:"
            
            # Remove trailing colon
            key = key.rstrip(':')
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            
            # Cache the result
            cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
