"""
Configuration constants for the University Professor Finder.
Centralizes magic numbers and settings.
"""

# =============================================================================
# API Rate Limits (seconds between requests)
# =============================================================================
RATE_LIMIT_SEMANTIC_SCHOLAR = 0.5  # 100 requests per 5 minutes
RATE_LIMIT_OPENALEX = 0.12  # ~8 requests per second allowed
RATE_LIMIT_DBLP = 1.0  # Be polite, 1 request per second
RATE_LIMIT_ARXIV = 0.5  # ~3 requests per second allowed

# =============================================================================
# Search Limits (max items to fetch per query)
# =============================================================================
MAX_PAPERS_SEMANTIC_SCHOLAR = 300
MAX_WORKS_OPENALEX = 500
MAX_PUBS_PER_TOPIC_DBLP = 50
MAX_ARXIV_RESULTS_PER_AUTHOR = 20
MAX_AUTHORS_FOR_ARXIV_SEARCH = 15

# =============================================================================
# Cache Settings
# =============================================================================
CACHE_TTL_DEFAULT = 3600  # 1 hour
CACHE_TTL_INSTITUTION = 3600  # 1 hour for institution lookups
CACHE_MAX_SIZE = 1000  # Maximum number of cached items

# =============================================================================
# Filtering Settings
# =============================================================================
MIN_PUBLICATION_YEAR = 2018  # Only fetch papers from this year onwards
MIN_RELEVANCE_SCORE = 0.5  # Minimum score to include a paper
MAX_STUDENTS_PER_LAB = 20  # Limit students shown per lab

# =============================================================================
# API Base URLs
# =============================================================================
SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1"
OPENALEX_BASE_URL = "https://api.openalex.org"
DBLP_BASE_URL = "https://dblp.org"
ARXIV_BASE_URL = "http://export.arxiv.org/api/query"
