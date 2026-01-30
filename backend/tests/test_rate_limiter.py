"""
Tests for the rate limiter utility.
"""

import time
import pytest
from utils.rate_limiter import RateLimiter, RateLimitConfig


class TestRateLimiter:
    """Test suite for RateLimiter."""

    def test_allows_initial_request(self):
        """First request should always be allowed."""
        limiter = RateLimiter(RateLimitConfig(
            requests_per_minute=5,
            requests_per_hour=100,
            burst_limit=3
        ))
        allowed, error = limiter.is_allowed("192.168.1.1")
        assert allowed is True
        assert error is None

    def test_allows_requests_within_limit(self):
        """Requests within the limit should be allowed."""
        limiter = RateLimiter(RateLimitConfig(
            requests_per_minute=5,
            requests_per_hour=100,
            burst_limit=10  # High burst to not trigger it
        ))
        ip = "192.168.1.2"

        for i in range(5):
            allowed, _ = limiter.is_allowed(ip)
            assert allowed is True

    def test_blocks_after_minute_limit(self):
        """Requests should be blocked after hitting per-minute limit."""
        limiter = RateLimiter(RateLimitConfig(
            requests_per_minute=3,
            requests_per_hour=100,
            burst_limit=10
        ))
        ip = "192.168.1.3"

        # Use up the limit
        for i in range(3):
            limiter.is_allowed(ip)

        # Next request should be blocked
        allowed, error = limiter.is_allowed(ip)
        assert allowed is False
        assert "Rate limit exceeded" in error

    def test_blocks_burst_requests(self):
        """Rapid requests should be blocked by burst limit."""
        limiter = RateLimiter(RateLimitConfig(
            requests_per_minute=100,  # High to not trigger
            requests_per_hour=1000,
            burst_limit=2
        ))
        ip = "192.168.1.4"

        # Quick requests
        limiter.is_allowed(ip)
        limiter.is_allowed(ip)
        allowed, error = limiter.is_allowed(ip)

        assert allowed is False
        assert "Burst limit exceeded" in error

    def test_different_ips_tracked_separately(self):
        """Different IPs should have separate limits."""
        limiter = RateLimiter(RateLimitConfig(
            requests_per_minute=2,
            requests_per_hour=100,
            burst_limit=10
        ))

        ip1 = "192.168.1.5"
        ip2 = "192.168.1.6"

        # Use up ip1's limit
        limiter.is_allowed(ip1)
        limiter.is_allowed(ip1)

        # ip1 should be blocked
        allowed, _ = limiter.is_allowed(ip1)
        assert allowed is False

        # ip2 should still be allowed
        allowed, _ = limiter.is_allowed(ip2)
        assert allowed is True

    def test_get_remaining_shows_correct_counts(self):
        """get_remaining should show accurate remaining counts."""
        limiter = RateLimiter(RateLimitConfig(
            requests_per_minute=5,
            requests_per_hour=10,
            burst_limit=10
        ))
        ip = "192.168.1.7"

        # Initial state
        remaining = limiter.get_remaining(ip)
        assert remaining["minute"]["remaining"] == 5
        assert remaining["hour"]["remaining"] == 10

        # After 2 requests
        limiter.is_allowed(ip)
        limiter.is_allowed(ip)

        remaining = limiter.get_remaining(ip)
        assert remaining["minute"]["remaining"] == 3
        assert remaining["hour"]["remaining"] == 8


class TestRateLimitConfig:
    """Test suite for RateLimitConfig."""

    def test_default_values(self):
        """Default config should have sensible values."""
        config = RateLimitConfig()
        assert config.requests_per_minute == 10
        assert config.requests_per_hour == 100
        assert config.burst_limit == 5

    def test_custom_values(self):
        """Custom config values should be set correctly."""
        config = RateLimitConfig(
            requests_per_minute=20,
            requests_per_hour=200,
            burst_limit=10
        )
        assert config.requests_per_minute == 20
        assert config.requests_per_hour == 200
        assert config.burst_limit == 10
