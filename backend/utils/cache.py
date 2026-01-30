"""
Simple in-memory cache with TTL and size limit support.
For production, consider using Redis or a persistent cache.
"""

import time
from typing import Any
from functools import wraps
import hashlib
from collections import OrderedDict

from config import CACHE_TTL_DEFAULT, CACHE_MAX_SIZE


class SimpleCache:
    """
    In-memory cache with TTL and LRU eviction.

    Features:
    - TTL (time-to-live) for automatic expiration
    - Max size limit with LRU (Least Recently Used) eviction
    - Thread-safe for single-threaded async code
    """

    def __init__(self, default_ttl: int = CACHE_TTL_DEFAULT, max_size: int = CACHE_MAX_SIZE):
        """
        Initialize cache.

        Args:
            default_ttl: Default TTL in seconds (default from config)
            max_size: Maximum number of items to store (default from config)
        """
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._hits = 0
        self._misses = 0

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments, filtering out non-serializable objects."""
        # Filter args - skip 'self' (first arg if it's an object with __dict__)
        filtered_args = []
        for arg in args:
            if hasattr(arg, '__dict__') and not isinstance(arg, (str, int, float, bool, list, dict, tuple)):
                # Skip class instances like 'self'
                continue
            filtered_args.append(str(arg))

        # Convert kwargs to strings
        filtered_kwargs = {k: str(v) for k, v in sorted(kwargs.items())}

        key_data = f"{filtered_args}:{filtered_kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _evict_if_needed(self) -> int:
        """Evict oldest items if cache exceeds max size. Returns count of evicted items."""
        evicted = 0
        while len(self._cache) >= self.max_size:
            # Remove the oldest item (first item in OrderedDict)
            self._cache.popitem(last=False)
            evicted += 1
        return evicted

    def get(self, key: str) -> Any | None:
        """
        Get value from cache if not expired.
        Moves item to end (most recently used) on access.
        """
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                self._hits += 1
                return value
            else:
                # Expired - remove it
                del self._cache[key]

        self._misses += 1
        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with TTL."""
        # Evict if needed before adding new item
        if key not in self._cache:
            self._evict_if_needed()

        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl

        # If key exists, update and move to end
        if key in self._cache:
            del self._cache[key]

        self._cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        """Delete key from cache. Returns True if key existed."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count of removed items."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if current_time >= expiry
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

    @property
    def size(self) -> int:
        """Current number of items in cache."""
        return len(self._cache)

    @property
    def stats(self) -> dict:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "size": self.size,
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2)
        }


# Global cache instance
cache = SimpleCache()


def cached(ttl: int | None = None):
    """
    Decorator to cache function results.

    Usage:
        @cached(ttl=600)  # Cache for 10 minutes
        async def fetch_data(url: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{cache._generate_key(*args, **kwargs)}"

            # Check cache
            result = cache.get(key)
            if result is not None:
                return result

            # Call function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                cache.set(key, result, ttl)

            return result
        return wrapper
    return decorator
