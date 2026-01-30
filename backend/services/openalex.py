"""
OpenAlex API Integration
Docs: https://docs.openalex.org/

STRATEGY (Concept-Based Approach):
1. Use OpenAlex's built-in concept/topic classification to find relevant works
2. Filter by NLP/AI concepts and exclude biology/chemistry
3. Use venue filtering to prioritize CS/AI conferences
4. Extract authors from those papers
"""

import httpx
from typing import Optional
import asyncio

from config import (
    OPENALEX_BASE_URL,
    RATE_LIMIT_OPENALEX,
    MAX_WORKS_OPENALEX,
    MIN_PUBLICATION_YEAR,
    CACHE_TTL_INSTITUTION,
)
from utils.cache import cached
from utils.university_mapping import normalize_university
from utils.relevance import (
    is_biology_paper,
    calculate_topic_relevance,
    is_nlp_venue,
    get_expanded_terms,
    TOPIC_EXPANSIONS,
)
from utils.exceptions import APIError, RateLimitError, TimeoutError


# OpenAlex concept IDs for NLP/AI topics
NLP_CONCEPT_IDS = {
    "natural language processing": "C204321447",
    "nlp": "C204321447",
    "language model": "C204321447",
    "large language model": "C204321447",
    "llm": "C204321447",
    "machine learning": "C119857082",
    "deep learning": "C108583219",
    "artificial intelligence": "C154945302",
    "neural network": "C50644808",
    "transformer": "C204321447",
    "computer vision": "C31972630",
    "reinforcement learning": "C83608088",
}


def extract_openalex_id(full_id: str) -> str:
    """Extract short ID from OpenAlex URL."""
    if full_id and '/' in full_id:
        return full_id.split('/')[-1]
    return full_id


def reconstruct_abstract(abstract_index: dict) -> str:
    """Reconstruct abstract from OpenAlex inverted index format."""
    if not abstract_index:
        return ""
    try:
        max_pos = max(max(positions) for positions in abstract_index.values())
        words = [""] * (max_pos + 1)
        for word, positions in abstract_index.items():
            for pos in positions:
                if pos < len(words):
                    words[pos] = word
        return " ".join(words)
    except Exception:
        return ""


class OpenAlexAPI:
    def __init__(self, email: Optional[str] = None):
        self.email = email
        self._last_request_time = 0

    def _get_params(self, params: dict) -> dict:
        if self.email:
            params["mailto"] = self.email
        return params

    async def _rate_limit(self):
        import time
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < RATE_LIMIT_OPENALEX:
            await asyncio.sleep(RATE_LIMIT_OPENALEX - elapsed)
        self._last_request_time = time.time()

    @cached(ttl=CACHE_TTL_INSTITUTION)
    async def get_institution_id(self, university_name: str) -> Optional[str]:
        """Get OpenAlex institution ID for a university."""
        await self._rate_limit()

        uni_info = normalize_university(university_name)
        search_name = uni_info["official_name"] if uni_info else university_name

        url = f"{OPENALEX_BASE_URL}/institutions"
        params = self._get_params({
            "search": search_name,
            "per_page": 3
        })

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                if response.status_code == 429:
                    raise RateLimitError("openalex")
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                if results:
                    return results[0].get("id")
            except httpx.TimeoutException:
                raise TimeoutError("openalex", 30.0)
            except RateLimitError:
                raise
            except Exception as e:
                print(f"OpenAlex institution search failed: {e}")
        return None

    async def search_works_by_topic_at_institution(
        self,
        topics: list[str],
        institution_id: str,
        max_works: int = MAX_WORKS_OPENALEX
    ) -> tuple[list[dict], dict]:
        """
        Search for works on given topics at an institution.
        Uses OpenAlex concept filtering for better relevance.
        """
        all_works = []
        cursor = "*"
        total_from_api = None
        fetched_count = 0

        inst_short_id = extract_openalex_id(institution_id)

        # Check if any topic is LLM-related
        is_llm_search = any(
            t.lower() in ["llm", "llm memory", "context engineering", "large language model", "gpt", "chatgpt"]
            for t in topics
        )

        # Build concept filter
        concept_ids = set()
        expanded_topics = []

        for topic in topics:
            topic_lower = topic.lower().strip()

            # Add to concept filter
            if topic_lower in NLP_CONCEPT_IDS:
                concept_ids.add(NLP_CONCEPT_IDS[topic_lower])

            # Expand topic for search
            expanded_topics.extend(get_expanded_terms(topic))

        # For LLM-related searches, ALWAYS include core terms
        if is_llm_search:
            core_llm_terms = ["large language model", "language model", "LLM"]
            for term in core_llm_terms:
                if term not in expanded_topics:
                    expanded_topics.append(term)

        # Default to NLP concept for LLM-related queries
        if not concept_ids:
            has_llm_terms = any(
                t.lower() in ["llm", "language model", "gpt", "chatgpt", "transformer", "bert"]
                for t in topics
            )
            if has_llm_terms:
                concept_ids.add("C204321447")  # NLP

        # Build search query - limit to avoid API errors
        search_terms = list(set(expanded_topics))[:6]  # Max 6 terms
        search_query = " OR ".join(search_terms)
        print(f"Search query: {search_query}")

        url = f"{OPENALEX_BASE_URL}/works"

        async with httpx.AsyncClient(timeout=60.0) as client:
            while fetched_count < max_works and cursor:
                await self._rate_limit()

                # Build filter with concept restriction if we have concept IDs
                filter_parts = [
                    f"authorships.institutions.id:{inst_short_id}",
                    f"publication_year:>{MIN_PUBLICATION_YEAR}"
                ]

                # Add concept filter to restrict to NLP/AI papers
                if concept_ids:
                    concept_filter = "|".join(concept_ids)
                    filter_parts.append(f"concepts.id:{concept_filter}")

                params = self._get_params({
                    "filter": ",".join(filter_parts),
                    "search": search_query,
                    "per_page": 100,
                    "cursor": cursor,
                    "sort": "cited_by_count:desc",
                    "select": "id,title,publication_year,primary_location,cited_by_count,authorships,doi,abstract_inverted_index,concepts"
                })

                try:
                    response = await client.get(url, params=params)
                    if response.status_code == 429:
                        raise RateLimitError("openalex")
                    response.raise_for_status()
                    data = response.json()

                    works = data.get("results", [])
                    if not works:
                        break

                    if total_from_api is None:
                        meta = data.get("meta", {})
                        total_from_api = meta.get("count", 0)
                        print(f"OpenAlex: Found {total_from_api} total works for topics at institution")

                    all_works.extend(works)
                    fetched_count += len(works)

                    meta = data.get("meta", {})
                    cursor = meta.get("next_cursor")

                    if not cursor or len(works) < 100:
                        break

                except httpx.TimeoutException:
                    raise TimeoutError("openalex", 60.0)
                except RateLimitError:
                    raise
                except httpx.HTTPStatusError as e:
                    raise APIError(
                        f"Works search failed: {e}",
                        source="openalex",
                        status_code=e.response.status_code
                    )
                except Exception as e:
                    print(f"OpenAlex works search failed: {e}")
                    break

        validation_info = {
            "total_from_api": total_from_api,
            "fetched_count": fetched_count,
            "source": "openalex"
        }

        return all_works, validation_info

    async def find_professors_by_topic_and_university(
        self,
        topics: list[str],
        universities: list[str],
        max_works_per_institution: int = MAX_WORKS_OPENALEX
    ) -> tuple[dict[str, dict], dict]:
        """
        WORKS-FIRST APPROACH:
        1. Search for papers on the topics at each institution
        2. Extract unique authors from those papers
        3. Build professor profiles with their relevant papers

        This finds actual researchers rather than keyword matching.
        """
        professors: dict[str, dict] = {}
        validation_info = {
            "total_queries": 0,
            "total_works_found": 0,
            "total_authors_found": 0,
            "institutions_found": [],
            "source": "openalex"
        }

        for university in universities:
            institution_id = await self.get_institution_id(university)
            if not institution_id:
                print(f"Could not find OpenAlex institution ID for: {university}")
                continue

            inst_short_id = extract_openalex_id(institution_id)
            validation_info["institutions_found"].append({
                "name": university,
                "id": institution_id
            })
            validation_info["total_queries"] += 1

            # Get works on topics at this institution
            works, work_validation = await self.search_works_by_topic_at_institution(
                topics=topics,
                institution_id=institution_id,
                max_works=max_works_per_institution
            )

            validation_info["total_works_found"] += work_validation.get("fetched_count", 0)

            print(f"Processing {len(works)} works from {university}...")

            # Extract authors and their papers
            skipped_biology = 0
            included = 0

            for work in works:
                title = work.get("title", "") or ""
                if not title:
                    continue

                abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
                concepts = work.get("concepts", [])

                # Calculate relevance using concepts, keywords, and filtering
                relevance, is_relevant = calculate_topic_relevance(
                    title, abstract, topics, concepts
                )

                # Skip if not relevant or is a biology paper
                if not is_relevant:
                    if is_biology_paper(title, abstract):
                        skipped_biology += 1
                    continue

                included += 1

                # Process each author from this institution
                for authorship in work.get("authorships", []):
                    author = authorship.get("author", {})
                    author_id = author.get("id")
                    author_name = author.get("display_name")

                    if not author_id or not author_name:
                        continue

                    # Check if author is from this institution
                    institutions = authorship.get("institutions", [])
                    is_from_institution = any(
                        inst_short_id in str(inst.get("id", ""))
                        for inst in institutions
                    )

                    if not is_from_institution:
                        continue

                    # Initialize or update professor
                    if author_id not in professors:
                        short_author_id = extract_openalex_id(author_id)
                        author_url = f"https://openalex.org/authors/{short_author_id}"

                        # Extract research interests from paper concepts
                        research_interests = set()
                        for concept in concepts[:10]:  # Top 10 concepts
                            concept_name = concept.get("display_name", "")
                            if concept_name and concept.get("level", 0) <= 2:  # High-level concepts
                                research_interests.add(concept_name)

                        professors[author_id] = {
                            "author_id": author_id,
                            "name": author_name,
                            "openalex_id": author_id,
                            "url": author_url,
                            "university": university,
                            "matching_topics": set(),
                            "research_interests": research_interests,
                            "papers": [],
                            "source": "openalex",
                            "total_relevance": 0.0,
                            "citation_count": 0
                        }
                        validation_info["total_authors_found"] += 1
                    else:
                        # Add more research interests from this paper
                        for concept in concepts[:5]:
                            concept_name = concept.get("display_name", "")
                            if concept_name and concept.get("level", 0) <= 2:
                                professors[author_id]["research_interests"].add(concept_name)

                    # Add matching topics
                    for topic in topics:
                        if topic.lower() in f"{title} {abstract}".lower():
                            professors[author_id]["matching_topics"].add(topic)

                    professors[author_id]["total_relevance"] += relevance

                    # Build paper info
                    primary_location = work.get("primary_location", {}) or {}
                    source = primary_location.get("source", {}) or {}
                    venue = source.get("display_name")

                    paper_url = None
                    doi = work.get("doi")
                    if doi:
                        paper_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
                    elif primary_location.get("landing_page_url"):
                        paper_url = primary_location["landing_page_url"]

                    if not paper_url and work.get("id"):
                        work_id = extract_openalex_id(work["id"])
                        paper_url = f"https://openalex.org/works/{work_id}"

                    paper_info = {
                        "title": title,
                        "year": work.get("publication_year"),
                        "venue": venue,
                        "url": paper_url,
                        "citation_count": work.get("cited_by_count", 0),
                        "relevance_score": relevance,
                        "source": "openalex"
                    }

                    # Add to citations
                    professors[author_id]["citation_count"] += work.get("cited_by_count", 0) or 0

                    # Avoid duplicate papers
                    existing_titles = {p["title"].lower() for p in professors[author_id]["papers"] if p.get("title")}
                    if title.lower() not in existing_titles:
                        professors[author_id]["papers"].append(paper_info)

            print(f"  -> Included: {included} papers, Skipped (biology): {skipped_biology}")

        # Finalize professor data
        for prof in professors.values():
            prof["matching_topics"] = list(prof["matching_topics"]) if prof["matching_topics"] else topics[:1]
            # Convert research interests set to sorted list (limit to 10)
            if "research_interests" in prof:
                prof["research_interests"] = sorted(list(prof["research_interests"]))[:10]
            prof["papers"].sort(
                key=lambda x: (x.get("citation_count", 0) or 0, x.get("relevance_score", 0)),
                reverse=True
            )

        # Sort professors by number of relevant papers and citations
        validation_info["professors_found"] = len(professors)

        return professors, validation_info


# Singleton instance
openalex = OpenAlexAPI()
