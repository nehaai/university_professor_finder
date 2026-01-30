"""
Semantic Scholar API Integration
Docs: https://api.semanticscholar.org/api-docs/

Note: Semantic Scholar has limited affiliation data, so we focus on
paper search and use it as a supplementary source to OpenAlex.
"""

import httpx
from typing import Optional
import asyncio

from config import (
    SEMANTIC_SCHOLAR_BASE_URL,
    RATE_LIMIT_SEMANTIC_SCHOLAR,
    MAX_PAPERS_SEMANTIC_SCHOLAR,
)
from utils.cache import cached
from utils.university_mapping import get_university_search_terms
from utils.relevance import (
    is_biology_paper,
    calculate_topic_relevance,
    is_valid_paper_url,
    get_expanded_terms,
)
from utils.exceptions import APIError, RateLimitError, TimeoutError


PAPER_SEARCH_URL = f"{SEMANTIC_SCHOLAR_BASE_URL}/paper/search"
AUTHOR_SEARCH_URL = f"{SEMANTIC_SCHOLAR_BASE_URL}/author/search"


def build_paper_url(paper_id: str) -> Optional[str]:
    """Build Semantic Scholar paper URL."""
    if paper_id:
        return f"https://www.semanticscholar.org/paper/{paper_id}"
    return None


class SemanticScholarAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["x-api-key"] = api_key
        self._last_request_time = 0

    async def _rate_limit(self):
        import time
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < RATE_LIMIT_SEMANTIC_SCHOLAR:
            await asyncio.sleep(RATE_LIMIT_SEMANTIC_SCHOLAR - elapsed)
        self._last_request_time = time.time()

    async def search_papers_with_pagination(
        self,
        query: str,
        max_papers: int = MAX_PAPERS_SEMANTIC_SCHOLAR
    ) -> tuple[list[dict], dict]:
        """
        Search for papers with pagination.
        """
        all_papers = []
        offset = 0
        limit = 100
        total_from_api = None

        async with httpx.AsyncClient(timeout=60.0) as client:
            while offset < max_papers:
                await self._rate_limit()

                params = {
                    "query": query,
                    "offset": offset,
                    "limit": limit,
                    "fields": "paperId,title,abstract,year,venue,url,citationCount,authors,authors.name,authors.affiliations,authors.authorId"
                }

                try:
                    response = await client.get(
                        PAPER_SEARCH_URL,
                        params=params,
                        headers=self.headers
                    )

                    if response.status_code == 429:
                        raise RateLimitError("semantic_scholar")
                    response.raise_for_status()

                    data = response.json()
                    papers = data.get("data", [])
                    if not papers:
                        break

                    if total_from_api is None:
                        total_from_api = data.get("total", 0)
                        print(f"Semantic Scholar: Found {total_from_api} total papers for query")

                    all_papers.extend(papers)
                    offset += len(papers)

                    if len(papers) < limit:
                        break

                except httpx.TimeoutException:
                    raise TimeoutError("semantic_scholar", 60.0)
                except RateLimitError:
                    raise
                except httpx.HTTPStatusError as e:
                    raise APIError(
                        f"Paper search failed: {e}",
                        source="semantic_scholar",
                        status_code=e.response.status_code
                    )
                except Exception as e:
                    print(f"Semantic Scholar paper search failed: {e}")
                    break

        validation_info = {
            "total_from_api": total_from_api,
            "fetched_count": offset,
            "source": "semantic_scholar"
        }

        return all_papers, validation_info

    def _matches_university(self, affiliations: list, universities: list[str]) -> Optional[str]:
        """Check if any affiliation matches any of the universities."""
        if not affiliations:
            return None

        for university in universities:
            uni_terms = get_university_search_terms(university)
            for affiliation in affiliations:
                if affiliation:
                    aff_lower = affiliation.lower()
                    if any(term.lower() in aff_lower for term in uni_terms):
                        return university
        return None

    async def find_professors_by_topic_and_university(
        self,
        topics: list[str],
        universities: list[str],
        max_papers: int = MAX_PAPERS_SEMANTIC_SCHOLAR
    ) -> tuple[dict[str, dict], dict]:
        """
        Search for papers on topics and extract authors from target universities.

        Note: Semantic Scholar has limited affiliation data compared to OpenAlex,
        so results may be fewer. Use in combination with OpenAlex for best results.
        """
        professors: dict[str, dict] = {}
        validation_info = {
            "total_queries": 0,
            "total_papers_found": 0,
            "total_authors_found": 0,
            "source": "semantic_scholar"
        }

        # Build search query
        search_query = " ".join(topics)
        validation_info["total_queries"] += 1

        papers, paper_validation = await self.search_papers_with_pagination(
            query=search_query,
            max_papers=max_papers
        )

        validation_info["total_papers_found"] = paper_validation.get("fetched_count", 0)

        print(f"Processing {len(papers)} papers from Semantic Scholar...")

        for paper in papers:
            title = paper.get("title", "") or ""
            if not title:
                continue

            abstract = paper.get("abstract", "") or ""
            relevance, is_strongly_relevant = calculate_topic_relevance(title, abstract, topics)

            # STRICT FILTERING: Only include papers where topic is in TITLE
            # Abstract-only matches are too unreliable
            if not is_strongly_relevant or relevance < 1.0:
                continue

            # Check each author
            for author in paper.get("authors", []):
                author_id = author.get("authorId")
                author_name = author.get("name")
                affiliations = author.get("affiliations", []) or []

                if not author_id or not author_name:
                    continue

                # Check if author is from target university
                matched_university = self._matches_university(affiliations, universities)
                if not matched_university:
                    continue

                # Initialize or update professor
                if author_id not in professors:
                    author_url = f"https://www.semanticscholar.org/author/{author_id}"

                    professors[author_id] = {
                        "author_id": author_id,
                        "name": author_name,
                        "affiliations": affiliations,
                        "url": author_url,
                        "university": matched_university,
                        "matching_topics": set(),
                        "papers": [],
                        "source": "semantic_scholar",
                        "total_relevance": 0.0,
                        "citation_count": 0
                    }
                    validation_info["total_authors_found"] += 1

                # Add matching topics
                for topic in topics:
                    if topic.lower() in f"{title} {abstract}".lower():
                        professors[author_id]["matching_topics"].add(topic)

                professors[author_id]["total_relevance"] += relevance

                # Build paper info
                paper_url = paper.get("url")
                paper_id = paper.get("paperId")
                if not is_valid_paper_url(paper_url):
                    paper_url = build_paper_url(paper_id)

                paper_info = {
                    "title": title,
                    "year": paper.get("year"),
                    "venue": paper.get("venue"),
                    "url": paper_url,
                    "citation_count": paper.get("citationCount", 0),
                    "relevance_score": relevance,
                    "source": "semantic_scholar"
                }

                professors[author_id]["citation_count"] += paper.get("citationCount", 0) or 0

                # Avoid duplicates
                existing_titles = {p["title"].lower() for p in professors[author_id]["papers"] if p.get("title")}
                if title.lower() not in existing_titles:
                    professors[author_id]["papers"].append(paper_info)

        # Finalize
        for prof in professors.values():
            prof["matching_topics"] = list(prof["matching_topics"]) if prof["matching_topics"] else topics[:1]
            prof["papers"].sort(
                key=lambda x: (x.get("citation_count", 0) or 0, x.get("relevance_score", 0)),
                reverse=True
            )

        validation_info["professors_found"] = len(professors)

        return professors, validation_info


# Singleton instance
semantic_scholar = SemanticScholarAPI()
