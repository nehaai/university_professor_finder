"""
arXiv API Integration
Docs: https://info.arxiv.org/help/api/index.html

arXiv is essential for ML/AI research as most papers appear here first.
Categories relevant to LLM research:
- cs.CL (Computation and Language) - NLP papers
- cs.LG (Machine Learning)
- cs.AI (Artificial Intelligence)
- cs.CV (Computer Vision)
"""

import httpx
from typing import Optional
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
import re

from utils.cache import cached


BASE_URL = "https://export.arxiv.org/api/query"
RATE_LIMIT_DELAY = 3.0  # arXiv asks for 3 second delay between requests


# arXiv categories for different research areas
ARXIV_CATEGORIES = {
    "llm": ["cs.CL", "cs.LG", "cs.AI"],
    "nlp": ["cs.CL"],
    "machine learning": ["cs.LG", "stat.ML"],
    "deep learning": ["cs.LG", "cs.NE"],
    "computer vision": ["cs.CV"],
    "artificial intelligence": ["cs.AI"],
    "reinforcement learning": ["cs.LG", "cs.AI"],
    "robotics": ["cs.RO"],
}


def parse_arxiv_entry(entry, namespaces) -> dict:
    """Parse a single arXiv entry from XML."""

    def get_text(element, tag):
        el = element.find(tag, namespaces)
        return el.text.strip() if el is not None and el.text else None

    def get_all_text(element, tag):
        els = element.findall(tag, namespaces)
        return [el.text.strip() for el in els if el is not None and el.text]

    # Get authors
    authors = []
    for author_el in entry.findall("atom:author", namespaces):
        name = get_text(author_el, "atom:name")
        affiliation_els = author_el.findall("arxiv:affiliation", namespaces)
        affiliations = [aff.text.strip() for aff in affiliation_els if aff.text]
        if name:
            authors.append({
                "name": name,
                "affiliations": affiliations
            })

    # Get categories
    categories = []
    for cat_el in entry.findall("atom:category", namespaces):
        term = cat_el.get("term")
        if term:
            categories.append(term)

    # Get links
    pdf_url = None
    abs_url = None
    for link_el in entry.findall("atom:link", namespaces):
        link_type = link_el.get("type", "")
        link_href = link_el.get("href", "")
        if "pdf" in link_type or link_href.endswith(".pdf"):
            pdf_url = link_href
        elif link_el.get("rel") == "alternate":
            abs_url = link_href

    # Parse ID to get arxiv ID
    full_id = get_text(entry, "atom:id") or ""
    arxiv_id = full_id.split("/abs/")[-1] if "/abs/" in full_id else full_id.split("/")[-1]

    # Parse published date
    published = get_text(entry, "atom:published")
    year = None
    if published:
        try:
            year = int(published[:4])
        except:
            pass

    return {
        "arxiv_id": arxiv_id,
        "title": get_text(entry, "atom:title"),
        "abstract": get_text(entry, "atom:summary"),
        "authors": authors,
        "categories": categories,
        "primary_category": categories[0] if categories else None,
        "published": published,
        "year": year,
        "updated": get_text(entry, "atom:updated"),
        "url": abs_url or f"https://arxiv.org/abs/{arxiv_id}",
        "pdf_url": pdf_url or f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        "comment": get_text(entry, "arxiv:comment"),
        "source": "arxiv"
    }


class ArxivAPI:
    def __init__(self):
        self._last_request_time = 0

    async def _rate_limit(self):
        import time
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()

    @cached(ttl=3600)
    async def search_papers(
        self,
        query: str,
        categories: list[str] = None,
        max_results: int = 100,
        sort_by: str = "relevance",  # or "lastUpdatedDate", "submittedDate"
        sort_order: str = "descending"
    ) -> tuple[list[dict], dict]:
        """
        Search arXiv for papers.

        Args:
            query: Search query (supports AND, OR, ANDNOT)
            categories: List of arXiv categories to filter (e.g., ["cs.CL", "cs.LG"])
            max_results: Maximum papers to return
            sort_by: Sort field
            sort_order: "ascending" or "descending"
        """
        await self._rate_limit()

        # Build search query
        search_query = f'all:"{query}"'

        # Add category filter
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            search_query = f"({search_query}) AND ({cat_query})"

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": min(max_results, 100),  # arXiv max is 100 per request
            "sortBy": sort_by,
            "sortOrder": sort_order
        }

        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            try:
                response = await client.get(BASE_URL, params=params)
                response.raise_for_status()

                # Parse XML response
                root = ET.fromstring(response.text)

                # Define namespaces
                namespaces = {
                    "atom": "http://www.w3.org/2005/Atom",
                    "arxiv": "http://arxiv.org/schemas/atom",
                    "opensearch": "http://a9.com/-/spec/opensearch/1.1/"
                }

                # Get total results
                total_el = root.find("opensearch:totalResults", namespaces)
                total_results = int(total_el.text) if total_el is not None else 0

                # Parse entries
                papers = []
                for entry in root.findall("atom:entry", namespaces):
                    paper = parse_arxiv_entry(entry, namespaces)
                    if paper.get("title"):
                        papers.append(paper)

                validation = {
                    "total_from_api": total_results,
                    "fetched_count": len(papers),
                    "query": query,
                    "categories": categories,
                    "source": "arxiv"
                }

                return papers, validation

            except Exception as e:
                print(f"arXiv search failed: {e}")
                return [], {"error": str(e), "source": "arxiv"}

    async def search_by_author(
        self,
        author_name: str,
        categories: list[str] = None,
        max_results: int = 50
    ) -> tuple[list[dict], dict]:
        """Search for papers by a specific author."""
        await self._rate_limit()

        search_query = f'au:"{author_name}"'

        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            search_query = f"({search_query}) AND ({cat_query})"

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": min(max_results, 100),
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }

        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            try:
                response = await client.get(BASE_URL, params=params)
                response.raise_for_status()

                root = ET.fromstring(response.text)
                namespaces = {
                    "atom": "http://www.w3.org/2005/Atom",
                    "arxiv": "http://arxiv.org/schemas/atom",
                    "opensearch": "http://a9.com/-/spec/opensearch/1.1/"
                }

                papers = []
                for entry in root.findall("atom:entry", namespaces):
                    paper = parse_arxiv_entry(entry, namespaces)
                    if paper.get("title"):
                        papers.append(paper)

                return papers, {
                    "author": author_name,
                    "fetched_count": len(papers),
                    "source": "arxiv"
                }

            except Exception as e:
                print(f"arXiv author search failed: {e}")
                return [], {"error": str(e)}

    async def find_papers_for_topics(
        self,
        topics: list[str],
        max_papers: int = 100
    ) -> tuple[list[dict], dict]:
        """
        Find papers for given topics, using appropriate arXiv categories.
        """
        all_papers = []
        seen_ids = set()
        total_found = 0

        # Determine relevant categories based on topics
        categories = set()
        for topic in topics:
            topic_lower = topic.lower().strip()
            for key, cats in ARXIV_CATEGORIES.items():
                if key in topic_lower or topic_lower in key:
                    categories.update(cats)

        # Default to NLP/ML categories for LLM-related searches
        if not categories:
            if any(t.lower() in ["llm", "language model", "gpt", "chatgpt", "transformer", "bert"]
                   for t in topics):
                categories = {"cs.CL", "cs.LG", "cs.AI"}

        categories = list(categories) if categories else None

        # Search for each topic
        papers_per_topic = max_papers // len(topics)

        for topic in topics:
            papers, validation = await self.search_papers(
                query=topic,
                categories=categories,
                max_results=papers_per_topic,
                sort_by="relevance"
            )

            total_found += validation.get("total_from_api", 0)

            for paper in papers:
                arxiv_id = paper.get("arxiv_id")
                if arxiv_id and arxiv_id not in seen_ids:
                    seen_ids.add(arxiv_id)
                    all_papers.append(paper)

        return all_papers, {
            "total_from_api": total_found,
            "fetched_count": len(all_papers),
            "categories_searched": categories,
            "source": "arxiv"
        }


# Singleton instance
arxiv_api = ArxivAPI()
