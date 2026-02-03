"""
University Professor Research Finder - Backend API
FastAPI application that aggregates data from multiple academic sources.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.routes import router


app = FastAPI(
    title="University Professor Finder",
    description="""
    Find professors and their students working on specific research topics at universities.

    ## Features
    - Search across multiple academic databases (Semantic Scholar, OpenAlex, DBLP)
    - Get verified links to profiles and publications
    - Optionally scrape lab pages for student information

    ## Data Sources
    - **Semantic Scholar**: Publication and author data with affiliation filtering
    - **OpenAlex**: Open catalog of scholarly works and authors
    - **DBLP**: Computer science publications database
    - **Lab Websites**: Scraped for student information (when available)

    ## Usage
    POST to `/api/search` with:
    ```json
    {
        "universities": ["CMU", "MIT"],
        "topics": ["LLM Memory", "Context Engineering"],
        "include_students": true
    }
    ```
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend - configurable via environment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://frontend-liard-three-27.vercel.app").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "University Professor Finder API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
