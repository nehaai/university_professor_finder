"""
Custom exceptions for the University Professor Finder.
Provides specific error types for better error handling.
"""


class APIError(Exception):
    """Base exception for API-related errors."""

    def __init__(self, message: str, source: str = None, status_code: int = None):
        self.message = message
        self.source = source
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        parts = [self.message]
        if self.source:
            parts.insert(0, f"[{self.source}]")
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        return " ".join(parts)


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, source: str, retry_after: int = None):
        self.retry_after = retry_after
        message = "Rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after}s"
        super().__init__(message, source=source, status_code=429)


class AuthenticationError(APIError):
    """Raised when API authentication fails."""

    def __init__(self, source: str):
        super().__init__("Authentication failed", source=source, status_code=401)


class NotFoundError(APIError):
    """Raised when requested resource is not found."""

    def __init__(self, resource: str, source: str = None):
        super().__init__(f"Resource not found: {resource}", source=source, status_code=404)


class ValidationError(APIError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class TimeoutError(APIError):
    """Raised when API request times out."""

    def __init__(self, source: str, timeout_seconds: float):
        super().__init__(
            f"Request timed out after {timeout_seconds}s",
            source=source,
            status_code=504
        )


class ScrapingError(Exception):
    """Raised when web scraping fails."""

    def __init__(self, url: str, reason: str = None):
        self.url = url
        self.reason = reason
        message = f"Failed to scrape {url}"
        if reason:
            message += f": {reason}"
        super().__init__(message)
