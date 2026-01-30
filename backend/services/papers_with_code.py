"""
Papers with Code API Integration
Docs: https://paperswithcode.com/api/v1/docs/

This is excellent for ML/AI/NLP research as it:
1. Focuses specifically on CS/ML papers
2. Links papers to code repositories
3. Has task/method categorization
4. No authentication required
"""

import httpx
from typing import Optional
import asyncio

from utils.cache import cached


BASE_URL = "https://paperswithcode.com/api/v1"
RATE_LIMIT_DELAY = 0.2  # Be polite


class PapersWithCodeAPI:
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
        page: int = 1,
        items_per_page: int = 50
    ) -> tuple[list[dict], dict]:
        """
        Search for papers by query.
        Returns papers with their associated code repositories.
        """
        await self._rate_limit()

        url = f"{BASE_URL}/papers/"
        params = {
            "q": query,
            "page": page,
            "items_per_page": min(items_per_page, 50)  # API max is 50
        }

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                papers = []
                for item in data.get("results", []):
                    paper = {
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "abstract": item.get("abstract"),
                        "url_abs": item.get("url_abs"),  # Paper URL
                        "url_pdf": item.get("url_pdf"),  # PDF URL
                        "arxiv_id": item.get("arxiv_id"),
                        "proceeding": item.get("proceeding"),  # Venue
                        "published": item.get("published"),  # Date
                        "authors": item.get("authors", []),
                        "tasks": item.get("tasks", []),  # ML tasks
                        "methods": item.get("methods", []),  # ML methods
                        "repository_count": len(item.get("repositories", [])),
                        "repositories": item.get("repositories", [])[:3],  # Top 3 repos
                        "source": "papers_with_code"
                    }
                    papers.append(paper)

                validation = {
                    "total_count": data.get("count", 0),
                    "fetched_count": len(papers),
                    "has_next": data.get("next") is not None,
                    "source": "papers_with_code"
                }

                return papers, validation

            except Exception as e:
                print(f"Papers with Code search failed: {e}")
                return [], {"error": str(e), "source": "papers_with_code"}

    @cached(ttl=3600)
    async def get_paper_details(self, paper_id: str) -> Optional[dict]:
        """Get detailed information about a specific paper."""
        await self._rate_limit()

        url = f"{BASE_URL}/papers/{paper_id}/"

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Papers with Code paper fetch failed: {e}")
                return None

    @cached(ttl=3600)
    async def search_by_task(
        self,
        task: str,
        page: int = 1,
        items_per_page: int = 50
    ) -> tuple[list[dict], dict]:
        """
        Search papers by ML task (e.g., 'question-answering', 'text-generation').
        This is very useful for finding LLM papers.
        """
        await self._rate_limit()

        # First get the task ID
        task_url = f"{BASE_URL}/tasks/"
        params = {"q": task, "items_per_page": 5}

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(task_url, params=params)
                response.raise_for_status()
                task_data = response.json()

                if not task_data.get("results"):
                    return [], {"error": f"Task '{task}' not found"}

                task_info = task_data["results"][0]
                task_id = task_info.get("id")

                # Now get papers for this task
                papers_url = f"{BASE_URL}/tasks/{task_id}/papers/"
                papers_params = {
                    "page": page,
                    "items_per_page": min(items_per_page, 50)
                }

                response = await client.get(papers_url, params=papers_params)
                response.raise_for_status()
                papers_data = response.json()

                papers = []
                for item in papers_data.get("results", []):
                    paper = {
                        "id": item.get("paper", {}).get("id") if isinstance(item.get("paper"), dict) else item.get("paper"),
                        "title": item.get("paper", {}).get("title") if isinstance(item.get("paper"), dict) else None,
                        "url": item.get("paper", {}).get("url_abs") if isinstance(item.get("paper"), dict) else None,
                        "task": task_info.get("name"),
                        "source": "papers_with_code"
                    }
                    if paper["title"]:
                        papers.append(paper)

                return papers, {
                    "task_name": task_info.get("name"),
                    "task_description": task_info.get("description"),
                    "total_papers": task_info.get("paper_count", 0),
                    "fetched_count": len(papers),
                    "source": "papers_with_code"
                }

            except Exception as e:
                print(f"Papers with Code task search failed: {e}")
                return [], {"error": str(e)}

    async def find_papers_for_topics(
        self,
        topics: list[str],
        max_papers: int = 100
    ) -> tuple[list[dict], dict]:
        """
        Find ML/AI papers for given topics.
        Uses both keyword search and task-based search.
        """
        all_papers = []
        seen_titles = set()
        total_found = 0

        # Map common topics to Papers with Code tasks
        topic_to_tasks = {
            "llm": ["language-modelling", "text-generation", "question-answering"],
            "large language model": ["language-modelling", "text-generation"],
            "nlp": ["natural-language-processing", "text-classification", "named-entity-recognition"],
            "context engineering": ["in-context-learning", "prompt-engineering"],
            "llm memory": ["retrieval-augmented-generation", "question-answering"],
            "transformer": ["language-modelling", "machine-translation"],
            "rag": ["retrieval-augmented-generation", "question-answering"],
            "machine learning": ["machine-learning"],
            "deep learning": ["deep-learning"],
            "computer vision": ["image-classification", "object-detection"],
        }

        # First, do keyword search
        for topic in topics:
            papers, validation = await self.search_papers(
                query=topic,
                items_per_page=min(max_papers // len(topics), 50)
            )
            total_found += validation.get("total_count", 0)

            for paper in papers:
                title = paper.get("title", "").lower()
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    all_papers.append(paper)

        # Then, search by relevant tasks
        tasks_searched = set()
        for topic in topics:
            topic_lower = topic.lower().strip()
            if topic_lower in topic_to_tasks:
                for task in topic_to_tasks[topic_lower]:
                    if task not in tasks_searched:
                        tasks_searched.add(task)
                        try:
                            papers, _ = await self.search_by_task(
                                task=task,
                                items_per_page=20
                            )
                            for paper in papers:
                                title = (paper.get("title") or "").lower()
                                if title and title not in seen_titles:
                                    seen_titles.add(title)
                                    all_papers.append(paper)
                        except Exception as e:
                            print(f"Task search failed for {task}: {e}")

        validation_info = {
            "total_from_api": total_found,
            "fetched_count": len(all_papers),
            "topics_searched": topics,
            "tasks_searched": list(tasks_searched),
            "source": "papers_with_code"
        }

        return all_papers, validation_info


# Singleton instance
papers_with_code = PapersWithCodeAPI()
