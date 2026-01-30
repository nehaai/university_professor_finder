"""
DBLP API Integration
Docs: https://dblp.org/faq/How+to+use+the+dblp+search+API.html
Free, no auth required. Rate limit: Be polite, no more than 1 request/second recommended.

Note: DBLP does not support affiliation filtering. This service is used for
enrichment only - cross-referencing with professors found in other sources.
"""

import httpx
from typing import Optional
import asyncio

from config import (
    DBLP_BASE_URL,
    RATE_LIMIT_DBLP,
    MAX_PUBS_PER_TOPIC_DBLP,
)
from utils.cache import cached
from utils.exceptions import APIError, RateLimitError, TimeoutError


SEARCH_URL = f"{DBLP_BASE_URL}/search/publ/api"
AUTHOR_SEARCH_URL = f"{DBLP_BASE_URL}/search/author/api"


class DBLPAPI:
    def __init__(self):
        self._last_request_time = 0

    async def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        import time
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < RATE_LIMIT_DBLP:
            await asyncio.sleep(RATE_LIMIT_DBLP - elapsed)
        self._last_request_time = time.time()

    @cached(ttl=3600)
    async def search_publications(
        self,
        query: str,
        limit: int = MAX_PUBS_PER_TOPIC_DBLP
    ) -> list[dict]:
        """
        Search for publications by query.
        DBLP doesn't directly support affiliation filtering, so we get publications
        and then filter authors separately.
        """
        await self._rate_limit()

        params = {
            "q": query,
            "format": "json",
            "h": min(limit, 1000)  # DBLP max is 1000
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(SEARCH_URL, params=params)
                if response.status_code == 429:
                    raise RateLimitError("dblp")
                response.raise_for_status()
                data = response.json()

                result = data.get("result", {})
                hits = result.get("hits", {})
                hit_list = hits.get("hit", [])

                publications = []
                for hit in hit_list:
                    info = hit.get("info", {})
                    publications.append({
                        "title": info.get("title"),
                        "year": info.get("year"),
                        "venue": info.get("venue"),
                        "url": info.get("ee"),  # Electronic edition URL
                        "dblp_url": info.get("url"),  # DBLP page URL
                        "authors": info.get("authors", {}).get("author", []),
                        "type": info.get("type")
                    })

                return publications

            except httpx.TimeoutException:
                raise TimeoutError("dblp", 30.0)
            except RateLimitError:
                raise
            except httpx.HTTPStatusError as e:
                raise APIError(
                    f"Publication search failed: {e}",
                    source="dblp",
                    status_code=e.response.status_code
                )
            except Exception as e:
                print(f"DBLP publication search failed: {e}")
                return []

    @cached(ttl=3600)
    async def search_authors(
        self,
        query: str,
        limit: int = 50
    ) -> list[dict]:
        """
        Search for authors by name.
        """
        await self._rate_limit()

        params = {
            "q": query,
            "format": "json",
            "h": min(limit, 1000)
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(AUTHOR_SEARCH_URL, params=params)
                if response.status_code == 429:
                    raise RateLimitError("dblp")
                response.raise_for_status()
                data = response.json()

                result = data.get("result", {})
                hits = result.get("hits", {})
                hit_list = hits.get("hit", [])

                authors = []
                for hit in hit_list:
                    info = hit.get("info", {})
                    authors.append({
                        "name": info.get("author"),
                        "url": info.get("url"),  # DBLP author page
                        "notes": info.get("notes", {})  # May contain affiliation
                    })

                return authors

            except httpx.TimeoutException:
                raise TimeoutError("dblp", 30.0)
            except RateLimitError:
                raise
            except httpx.HTTPStatusError as e:
                raise APIError(
                    f"Author search failed: {e}",
                    source="dblp",
                    status_code=e.response.status_code
                )
            except Exception as e:
                print(f"DBLP author search failed: {e}")
                return []

    async def find_professors_by_topic(
        self,
        topics: list[str],
        pubs_per_topic: int = MAX_PUBS_PER_TOPIC_DBLP
    ) -> dict[str, dict]:
        """
        Find professors working on given topics.

        Note: DBLP doesn't have built-in affiliation filtering, so this returns
        ALL authors publishing on these topics. The aggregator service filters
        by cross-referencing with professors found in OpenAlex/Semantic Scholar.

        Returns a dict mapping author_name to author info with their relevant papers.
        """
        professors: dict[str, dict] = {}

        for topic in topics:
            publications = await self.search_publications(
                query=topic,
                limit=pubs_per_topic
            )

            for pub in publications:
                authors = pub.get("authors", [])

                # Handle both single author (string) and multiple authors (list)
                if isinstance(authors, str):
                    authors = [authors]
                elif isinstance(authors, dict):
                    # Sometimes it's a dict with single author
                    authors = [authors.get("text", authors)]

                for author in authors:
                    # Author can be string or dict
                    if isinstance(author, dict):
                        author_name = author.get("text", author.get("@pid", "Unknown"))
                        author_pid = author.get("@pid")
                    else:
                        author_name = str(author)
                        author_pid = None

                    if not author_name or author_name == "Unknown":
                        continue

                    # Use author name as key (DBLP doesn't always have consistent IDs)
                    author_key = author_name.lower().strip()

                    if author_key not in professors:
                        dblp_url = None
                        if author_pid:
                            dblp_url = f"https://dblp.org/pid/{author_pid}"

                        professors[author_key] = {
                            "name": author_name,
                            "dblp_pid": author_pid,
                            "dblp_url": dblp_url,
                            "matching_topics": set(),
                            "papers": [],
                            "source": "dblp"
                        }

                    professors[author_key]["matching_topics"].add(topic)

                    paper_info = {
                        "title": pub.get("title"),
                        "year": pub.get("year"),
                        "venue": pub.get("venue"),
                        "url": pub.get("url") or pub.get("dblp_url"),
                        "source": "dblp"
                    }

                    # Avoid duplicate papers
                    existing_titles = [p["title"] for p in professors[author_key]["papers"]]
                    if paper_info["title"] and paper_info["title"] not in existing_titles:
                        professors[author_key]["papers"].append(paper_info)

        # Convert sets to lists
        for prof in professors.values():
            prof["matching_topics"] = list(prof["matching_topics"])

        return professors


# Singleton instance
dblp = DBLPAPI()
