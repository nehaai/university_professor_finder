"""
Tests for cache utilities.
"""

import time
import pytest
from utils.cache import SimpleCache


class TestSimpleCache:
    """Test suite for SimpleCache."""

    def test_get_set_basic(self):
        """Basic get/set should work."""
        cache = SimpleCache(max_size=100, default_ttl=3600)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_returns_none_for_missing_key(self):
        """Missing key should return None."""
        cache = SimpleCache(max_size=100, default_ttl=3600)
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        """Cache should expire after TTL."""
        cache = SimpleCache(max_size=100, default_ttl=3600)
        cache.set("key1", "value1", ttl=1)  # 1 second TTL

        # Should exist immediately
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("key1") is None

    def test_lru_eviction(self):
        """Oldest items should be evicted when max size reached."""
        cache = SimpleCache(max_size=3, default_ttl=3600)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # All should exist
        assert cache.get("key1") is not None
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None

        # Add one more, should evict oldest (key1)
        cache.set("key4", "value4")

        # key1 should be evicted
        assert cache.get("key1") is None
        assert cache.get("key2") is not None
        assert cache.get("key4") is not None

    def test_access_updates_lru_order(self):
        """Accessing an item should update its LRU position."""
        cache = SimpleCache(max_size=3, default_ttl=3600)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it most recently used
        cache.get("key1")

        # Add new key, should evict key2 (oldest now)
        cache.set("key4", "value4")

        assert cache.get("key1") is not None  # Recently accessed
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") is not None
        assert cache.get("key4") is not None

    def test_clear(self):
        """Clear should remove all items."""
        cache = SimpleCache(max_size=100, default_ttl=3600)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_stats(self):
        """Stats should track hits and misses."""
        cache = SimpleCache(max_size=100, default_ttl=3600)

        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.stats
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["size"] == 1

    def test_stores_complex_values(self):
        """Cache should store complex values like dicts and lists."""
        cache = SimpleCache(max_size=100, default_ttl=3600)

        value = {"key": "value", "list": [1, 2, 3]}
        cache.set("complex", value)

        retrieved = cache.get("complex")
        assert retrieved == value

    def test_delete(self):
        """Delete should remove specific key."""
        cache = SimpleCache(max_size=100, default_ttl=3600)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        result = cache.delete("key1")
        assert result is True
        assert cache.get("key1") is None
        assert cache.get("key2") is not None

        # Deleting non-existent key returns False
        result = cache.delete("nonexistent")
        assert result is False

    def test_cleanup_expired(self):
        """cleanup_expired should remove expired entries."""
        cache = SimpleCache(max_size=100, default_ttl=3600)
        cache.set("key1", "value1", ttl=1)  # Will expire
        cache.set("key2", "value2", ttl=3600)  # Won't expire

        time.sleep(1.1)

        removed = cache.cleanup_expired()
        assert removed == 1
        assert cache.get("key1") is None
        assert cache.get("key2") is not None

    def test_size_property(self):
        """Size property should return current item count."""
        cache = SimpleCache(max_size=100, default_ttl=3600)
        assert cache.size == 0

        cache.set("key1", "value1")
        assert cache.size == 1

        cache.set("key2", "value2")
        assert cache.size == 2

        cache.delete("key1")
        assert cache.size == 1
