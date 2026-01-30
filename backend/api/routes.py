"""
API Routes for the University Professor Finder
"""

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import time

from api.schemas import SearchRequest, SearchResponse, SearchQuery, SearchMetadata
from services.aggregator import aggregator
from utils.rate_limiter import rate_limiter


router = APIRouter()


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    # Check for forwarded header (when behind proxy/load balancer)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # Check for real IP header (Nginx/Cloudflare)
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    # Fallback to direct client
    return request.client.host if request.client else "unknown"


@router.post("/search", response_model=SearchResponse)
async def search_professors(request: SearchRequest, req: Request):
    """
    Search for professors working on specific topics at given universities.
    Always fetches ALL available papers for complete results.

    - **universities**: List of university names (e.g., ["CMU", "MIT"])
    - **topics**: List of research topics (e.g., ["LLM Memory", "Context Engineering"])
    - **include_students**: Whether to attempt finding students from lab pages (slower)

    Rate limited: 10 requests/minute, 100 requests/hour per IP.
    """
    if not request.universities:
        raise HTTPException(status_code=400, detail="At least one university is required")

    if not request.topics:
        raise HTTPException(status_code=400, detail="At least one topic is required")

    # Rate limiting
    client_ip = get_client_ip(req)
    allowed, error_msg = rate_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(status_code=429, detail=error_msg)

    start_time = time.time()

    try:
        professor_results, paper_results, validation_info = await aggregator.search_professors(
            universities=request.universities,
            topics=request.topics,
            include_students=request.include_students
        )

        search_time_ms = int((time.time() - start_time) * 1000)

        # Determine which sources were queried
        sources_queried = set()
        for result in professor_results:
            sources_queried.update(result.data_sources)

        return SearchResponse(
            query=SearchQuery(
                universities=request.universities,
                topics=request.topics
            ),
            results=professor_results,
            papers=paper_results,
            metadata=SearchMetadata(
                total_results=len(professor_results),
                total_papers=len(paper_results),
                search_time_ms=search_time_ms,
                sources_queried=list(sources_queried) or ["semantic_scholar", "openalex"],
                validation=validation_info
            )
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/rate-limit-status")
async def rate_limit_status(req: Request):
    """Get current rate limit status for the requesting IP."""
    client_ip = get_client_ip(req)
    remaining = rate_limiter.get_remaining(client_ip)
    return {
        "ip": client_ip,
        "limits": remaining
    }
