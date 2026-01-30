"""
Simple in-memory rate limiter for API endpoints.
No external dependencies (free alternative to Redis).
"""

import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Optional
import threading


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int = 10
    requests_per_hour: int = 100
    burst_limit: int = 5  # Max requests in quick succession


class RateLimiter:
    """
    Thread-safe in-memory rate limiter using sliding window algorithm.
    Tracks requests per IP address.
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self._minute_windows: Dict[str, list] = defaultdict(list)
        self._hour_windows: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
        self._cleanup_counter = 0

    def _cleanup_old_entries(self, ip: str, now: float):
        """Remove timestamps older than tracking windows."""
        minute_ago = now - 60
        hour_ago = now - 3600

        self._minute_windows[ip] = [
            ts for ts in self._minute_windows[ip] if ts > minute_ago
        ]
        self._hour_windows[ip] = [
            ts for ts in self._hour_windows[ip] if ts > hour_ago
        ]

    def _periodic_cleanup(self, now: float):
        """Occasionally clean up all entries to prevent memory growth."""
        self._cleanup_counter += 1
        if self._cleanup_counter >= 100:  # Every 100 requests
            self._cleanup_counter = 0
            minute_ago = now - 60
            hour_ago = now - 3600

            # Clean all IPs
            for ip in list(self._minute_windows.keys()):
                self._minute_windows[ip] = [
                    ts for ts in self._minute_windows[ip] if ts > minute_ago
                ]
                if not self._minute_windows[ip]:
                    del self._minute_windows[ip]

            for ip in list(self._hour_windows.keys()):
                self._hour_windows[ip] = [
                    ts for ts in self._hour_windows[ip] if ts > hour_ago
                ]
                if not self._hour_windows[ip]:
                    del self._hour_windows[ip]

    def is_allowed(self, ip: str) -> tuple[bool, Optional[str]]:
        """
        Check if a request from the given IP is allowed.

        Returns:
            (is_allowed, error_message)
        """
        now = time.time()

        with self._lock:
            self._cleanup_old_entries(ip, now)
            self._periodic_cleanup(now)

            minute_count = len(self._minute_windows[ip])
            hour_count = len(self._hour_windows[ip])

            # Check burst limit (requests in last 5 seconds)
            recent = [ts for ts in self._minute_windows[ip] if ts > now - 5]
            if len(recent) >= self.config.burst_limit:
                return False, f"Burst limit exceeded. Please wait a few seconds."

            # Check per-minute limit
            if minute_count >= self.config.requests_per_minute:
                oldest = min(self._minute_windows[ip])
                wait_seconds = int(60 - (now - oldest)) + 1
                return False, f"Rate limit exceeded. Try again in {wait_seconds} seconds."

            # Check per-hour limit
            if hour_count >= self.config.requests_per_hour:
                oldest = min(self._hour_windows[ip])
                wait_minutes = int((3600 - (now - oldest)) / 60) + 1
                return False, f"Hourly limit exceeded. Try again in {wait_minutes} minutes."

            # Allow the request and record it
            self._minute_windows[ip].append(now)
            self._hour_windows[ip].append(now)

            return True, None

    def get_remaining(self, ip: str) -> dict:
        """Get remaining requests for an IP."""
        now = time.time()

        with self._lock:
            self._cleanup_old_entries(ip, now)

            minute_count = len(self._minute_windows[ip])
            hour_count = len(self._hour_windows[ip])

            return {
                "minute": {
                    "remaining": max(0, self.config.requests_per_minute - minute_count),
                    "limit": self.config.requests_per_minute,
                    "reset_in_seconds": 60
                },
                "hour": {
                    "remaining": max(0, self.config.requests_per_hour - hour_count),
                    "limit": self.config.requests_per_hour,
                    "reset_in_seconds": 3600
                }
            }


# Global rate limiter instance
rate_limiter = RateLimiter(RateLimitConfig(
    requests_per_minute=10,  # 10 searches per minute
    requests_per_hour=100,   # 100 searches per hour
    burst_limit=3            # Max 3 rapid requests
))
