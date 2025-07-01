#!/usr/bin/env python3
"""
Redis Client Module

Handles Redis connection, caching, and session management.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

import redis
from redis.exceptions import ConnectionError, TimeoutError, RedisError

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Redis client instance
redis_client: Optional[redis.Redis] = None


def init_redis() -> redis.Redis:
    """
    Initialize Redis connection.
    
    Returns:
        redis.Redis: Redis client instance
    
    Raises:
        ConnectionError: If unable to connect to Redis
    """
    global redis_client
    
    try:
        logger.info("Initializing Redis connection...")
        
        # Parse Redis URL or use individual settings
        if settings.REDIS_URL:
            redis_client = redis.from_url(
                str(settings.REDIS_URL),
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
        else:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
        
        # Test connection
        redis_client.ping()
        logger.info("Redis connection established successfully")
        
        return redis_client
        
    except Exception as e:
        logger.error(f"Failed to initialize Redis connection: {e}")
        raise ConnectionError(f"Redis connection failed: {e}")


def get_redis() -> redis.Redis:
    """
    Get Redis client instance.
    
    Returns:
        redis.Redis: Redis client instance
    
    Raises:
        RuntimeError: If Redis is not initialized
    """
    global redis_client
    
    if redis_client is None:
        redis_client = init_redis()
    
    return redis_client


def close_redis() -> None:
    """
    Close Redis connection.
    """
    global redis_client
    
    if redis_client:
        try:
            redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
        finally:
            redis_client = None


class RedisCache:
    """
    Redis cache utility class with common caching operations.
    """
    
    def __init__(self, client: Optional[redis.Redis] = None):
        self.client = client or get_redis()
    
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Set a value in Redis cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire: Expiration time in seconds or timedelta
            namespace: Optional namespace prefix
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = self._build_key(key, namespace)
            
            # Serialize value to JSON
            if isinstance(value, (dict, list, tuple)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)
            
            # Set expiration
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            
            return self.client.set(cache_key, serialized_value, ex=expire)
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def get(
        self,
        key: str,
        namespace: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """
        Get a value from Redis cache.
        
        Args:
            key: Cache key
            namespace: Optional namespace prefix
            default: Default value if key not found
        
        Returns:
            Any: Cached value or default
        """
        try:
            cache_key = self._build_key(key, namespace)
            value = self.client.get(cache_key)
            
            if value is None:
                return default
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return default
    
    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """
        Delete a key from Redis cache.
        
        Args:
            key: Cache key
            namespace: Optional namespace prefix
        
        Returns:
            bool: True if key was deleted, False otherwise
        """
        try:
            cache_key = self._build_key(key, namespace)
            return bool(self.client.delete(cache_key))
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def exists(self, key: str, namespace: Optional[str] = None) -> bool:
        """
        Check if a key exists in Redis cache.
        
        Args:
            key: Cache key
            namespace: Optional namespace prefix
        
        Returns:
            bool: True if key exists, False otherwise
        """
        try:
            cache_key = self._build_key(key, namespace)
            return bool(self.client.exists(cache_key))
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int, namespace: Optional[str] = None) -> bool:
        """
        Set expiration time for a key.
        
        Args:
            key: Cache key
            seconds: Expiration time in seconds
            namespace: Optional namespace prefix
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = self._build_key(key, namespace)
            return bool(self.client.expire(cache_key, seconds))
        except Exception as e:
            logger.error(f"Error setting expiration for cache key {key}: {e}")
            return False
    
    def ttl(self, key: str, namespace: Optional[str] = None) -> int:
        """
        Get time to live for a key.
        
        Args:
            key: Cache key
            namespace: Optional namespace prefix
        
        Returns:
            int: TTL in seconds (-1 if no expiration, -2 if key doesn't exist)
        """
        try:
            cache_key = self._build_key(key, namespace)
            return self.client.ttl(cache_key)
        except Exception as e:
            logger.error(f"Error getting TTL for cache key {key}: {e}")
            return -2
    
    def increment(self, key: str, amount: int = 1, namespace: Optional[str] = None) -> int:
        """
        Increment a numeric value in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            namespace: Optional namespace prefix
        
        Returns:
            int: New value after increment
        """
        try:
            cache_key = self._build_key(key, namespace)
            return self.client.incr(cache_key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return 0
    
    def decrement(self, key: str, amount: int = 1, namespace: Optional[str] = None) -> int:
        """
        Decrement a numeric value in cache.
        
        Args:
            key: Cache key
            amount: Amount to decrement by
            namespace: Optional namespace prefix
        
        Returns:
            int: New value after decrement
        """
        try:
            cache_key = self._build_key(key, namespace)
            return self.client.decr(cache_key, amount)
        except Exception as e:
            logger.error(f"Error decrementing cache key {key}: {e}")
            return 0
    
    def get_keys(self, pattern: str, namespace: Optional[str] = None) -> List[str]:
        """
        Get all keys matching a pattern.
        
        Args:
            pattern: Key pattern (supports wildcards)
            namespace: Optional namespace prefix
        
        Returns:
            List[str]: List of matching keys
        """
        try:
            search_pattern = self._build_key(pattern, namespace)
            keys = self.client.keys(search_pattern)
            
            # Remove namespace prefix from returned keys
            if namespace:
                prefix = f"{namespace}:"
                return [key.replace(prefix, "", 1) for key in keys]
            
            return keys
            
        except Exception as e:
            logger.error(f"Error getting keys with pattern {pattern}: {e}")
            return []
    
    def clear_namespace(self, namespace: str) -> int:
        """
        Clear all keys in a namespace.
        
        Args:
            namespace: Namespace to clear
        
        Returns:
            int: Number of keys deleted
        """
        try:
            pattern = f"{namespace}:*"
            keys = self.client.keys(pattern)
            
            if keys:
                return self.client.delete(*keys)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error clearing namespace {namespace}: {e}")
            return 0
    
    def _build_key(self, key: str, namespace: Optional[str] = None) -> str:
        """
        Build cache key with optional namespace.
        
        Args:
            key: Base key
            namespace: Optional namespace prefix
        
        Returns:
            str: Full cache key
        """
        if namespace:
            return f"{namespace}:{key}"
        return key


# Global cache instance
cache = RedisCache()


def check_redis_connection() -> bool:
    """
    Check if Redis connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        client = get_redis()
        client.ping()
        logger.info("Redis connection successful")
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False


def get_redis_info() -> Dict[str, Any]:
    """
    Get Redis server information.
    
    Returns:
        Dict[str, Any]: Redis server information
    """
    try:
        client = get_redis()
        info = client.info()
        
        return {
            "version": info.get("redis_version"),
            "mode": info.get("redis_mode"),
            "connected_clients": info.get("connected_clients"),
            "used_memory": info.get("used_memory_human"),
            "total_commands_processed": info.get("total_commands_processed"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "uptime_in_seconds": info.get("uptime_in_seconds"),
        }
        
    except Exception as e:
        logger.error(f"Error getting Redis info: {e}")
        return {}


# Session management utilities
class SessionManager:
    """
    Redis-based session management.
    """
    
    def __init__(self, client: Optional[redis.Redis] = None, prefix: str = "session"):
        self.client = client or get_redis()
        self.prefix = prefix
        self.default_ttl = 3600  # 1 hour
    
    def create_session(self, session_id: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Create a new session.
        
        Args:
            session_id: Unique session identifier
            data: Session data
            ttl: Time to live in seconds
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"{self.prefix}:{session_id}"
            serialized_data = json.dumps(data, default=str)
            return self.client.set(key, serialized_data, ex=ttl or self.default_ttl)
        except Exception as e:
            logger.error(f"Error creating session {session_id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Optional[Dict[str, Any]]: Session data or None if not found
        """
        try:
            key = f"{self.prefix}:{session_id}"
            data = self.client.get(key)
            
            if data:
                return json.loads(data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session identifier
            data: Updated session data
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"{self.prefix}:{session_id}"
            
            # Get current TTL to preserve it
            ttl = self.client.ttl(key)
            if ttl == -2:  # Key doesn't exist
                return False
            
            serialized_data = json.dumps(data, default=str)
            
            if ttl > 0:
                return self.client.set(key, serialized_data, ex=ttl)
            else:
                return self.client.set(key, serialized_data)
                
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"{self.prefix}:{session_id}"
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    def extend_session(self, session_id: str, ttl: Optional[int] = None) -> bool:
        """
        Extend session expiration time.
        
        Args:
            session_id: Session identifier
            ttl: New time to live in seconds
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"{self.prefix}:{session_id}"
            return bool(self.client.expire(key, ttl or self.default_ttl))
        except Exception as e:
            logger.error(f"Error extending session {session_id}: {e}")
            return False


# Global session manager
session_manager = SessionManager()