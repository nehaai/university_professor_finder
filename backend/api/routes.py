"""
API Routes for the University Professor Finder
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import time

from api.schemas import SearchRequest, SearchResponse, SearchQuery, SearchMetadata
from services.aggregator import aggregator


router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_professors(request: SearchRequest):
    """
    Search for professors working on specific topics at given universities.
    Always fetches ALL available papers for complete results.

    - **universities**: List of university names (e.g., ["CMU", "MIT"])
    - **topics**: List of research topics (e.g., ["LLM Memory", "Context Engineering"])
    - **include_students**: Whether to attempt finding students from lab pages (slower)
    """
    if not request.universities:
        raise HTTPException(status_code=400, detail="At least one university is required")

    if not request.topics:
        raise HTTPException(status_code=400, detail="At least one topic is required")

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
