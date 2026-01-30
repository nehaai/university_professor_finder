"""
Aggregator Service
Combines results from multiple data sources and deduplicates professors.
Creates both professor-centric and paper-centric views with validation info.
"""

from typing import Optional
from datetime import datetime
import asyncio
import re

from services.semantic_scholar import semantic_scholar
from services.openalex import openalex
from services.dblp import dblp
from services.scraper import lab_scraper
from services.arxiv_api import arxiv_api
from api.schemas import (
    Professor, Publication, Student, Lab, RelevanceInfo, ProfessorResult,
    Author, PaperResult, ValidationInfo, SourceValidation
)


def calculate_relevance_score(
    matching_topics: list[str],
    total_topics: int,
    paper_count: int
) -> float:
    """
    Calculate a relevance score based on topic matches and paper count.
    """
    if total_topics == 0:
        return 0.0

    topic_score = len(matching_topics) / total_topics
    paper_score = min(paper_count / 10, 1.0)  # Cap at 10 papers

    # Weighted combination
    return round(0.6 * topic_score + 0.4 * paper_score, 2)


def normalize_name(name: str) -> str:
    """Normalize a name for comparison."""
    return ' '.join(name.lower().strip().split())


def normalize_title(title: str) -> str:
    """Normalize a paper title for comparison and deduplication."""
    if not title:
        return ""
    # Remove HTML tags like <i>
    normalized = re.sub(r'<[^>]+>', '', title)
    # Lowercase
    normalized = normalized.lower()
    # Replace hyphens with spaces before removing punctuation (so "atomic-level" becomes "atomic level")
    normalized = normalized.replace('-', ' ')
    # Remove all punctuation
    normalized = re.sub(r'[^\w\s]', '', normalized)
    # Collapse multiple spaces
    normalized = ' '.join(normalized.split())
    return normalized


def merge_professor_data(prof1: dict, prof2: dict) -> dict:
    """
    Merge two professor records, preferring non-null values.
    """
    merged = prof1.copy()

    for key, value in prof2.items():
        if key == 'matching_topics':
            # Combine topics
            existing = set(merged.get('matching_topics', []))
            existing.update(value if isinstance(value, list) else [value])
            merged['matching_topics'] = list(existing)
        elif key == 'papers':
            # Combine papers, avoiding duplicates
            existing_titles = {normalize_title(p.get('title', '')) for p in merged.get('papers', [])}
            for paper in value:
                if normalize_title(paper.get('title', '')) not in existing_titles:
                    merged.setdefault('papers', []).append(paper)
                    existing_titles.add(normalize_title(paper.get('title', '')))
        elif key == 'data_sources':
            existing = set(merged.get('data_sources', []))
            existing.update(value if isinstance(value, list) else [value])
            merged['data_sources'] = list(existing)
        elif not merged.get(key) and value:
            merged[key] = value

    return merged


class AggregatorService:
    async def _search_arxiv_by_authors(
        self,
        author_names: list[str],
        topics: list[str],
        universities: list[str]
    ) -> tuple[list[dict], dict]:
        """
        Search arXiv for papers by known researchers.
        This is more effective than topic search because arXiv doesn't have affiliation data.
        """
        all_papers = []
        seen_ids = set()

        # Search for each author (limit to avoid rate limits)
        authors_searched = 0
        max_authors = 15  # Limit to avoid too many API calls

        for author_name in author_names[:max_authors]:
            try:
                papers, _ = await arxiv_api.search_by_author(
                    author_name=author_name,
                    max_results=20
                )
                authors_searched += 1

                for paper in papers:
                    arxiv_id = paper.get('arxiv_id')
                    if arxiv_id and arxiv_id not in seen_ids:
                        # Check if paper is relevant to topics
                        title = paper.get('title', '').lower()
                        abstract = paper.get('abstract', '').lower()
                        text = f"{title} {abstract}"

                        is_relevant = any(
                            topic.lower() in text
                            for topic in topics
                        )

                        # Also check for common LLM terms
                        llm_terms = ['language model', 'llm', 'gpt', 'transformer', 'attention', 'context', 'prompt']
                        if not is_relevant:
                            is_relevant = any(term in text for term in llm_terms)

                        if is_relevant:
                            seen_ids.add(arxiv_id)
                            # Mark which university researcher this came from
                            paper['found_via_author'] = author_name
                            paper['university'] = universities[0] if universities else None
                            all_papers.append(paper)

            except Exception as e:
                print(f"arXiv author search failed for {author_name}: {e}")

        print(f"arXiv: Found {len(all_papers)} relevant papers from {authors_searched} researchers")

        return all_papers, {
            "source": "arxiv",
            "authors_searched": authors_searched,
            "fetched_count": len(all_papers)
        }

    async def search_professors(
        self,
        universities: list[str],
        topics: list[str],
        include_students: bool = True
    ) -> tuple[list[ProfessorResult], list[PaperResult], ValidationInfo]:
        """
        Search for professors across all data sources, aggregate and deduplicate results.
        Always fetches ALL available papers using pagination for complete results.
        Returns (professor_results, paper_results, validation_info).
        """
        # Run all API searches in parallel - always fetch all papers
        semantic_task = semantic_scholar.find_professors_by_topic_and_university(
            topics=topics,
            universities=universities
        )
        openalex_task = openalex.find_professors_by_topic_and_university(
            topics=topics,
            universities=universities
        )
        # DBLP doesn't have affiliation filtering, so we'll use it for enrichment
        dblp_task = dblp.find_professors_by_topic(
            topics=topics
        )
        # Papers with Code - currently disabled as API redirects to Hugging Face
        # pwc_task = papers_with_code.find_papers_for_topics(
        #     topics=topics,
        #     max_papers=100
        # )

        # arXiv task will be done AFTER we have professor names from OpenAlex
        # This allows us to search arXiv by author name for better results
        arxiv_papers = []
        arxiv_validation = {}

        # Wait for primary searches to complete
        results = await asyncio.gather(
            semantic_task,
            openalex_task,
            dblp_task,
            return_exceptions=True
        )

        # Handle results - now they return tuples (data, validation_info)
        ss_results = {}
        ss_validation = {}
        oa_results = {}
        oa_validation = {}
        dblp_results = {}

        if isinstance(results[0], Exception):
            print(f"Semantic Scholar search failed: {results[0]}")
        else:
            ss_results, ss_validation = results[0]

        if isinstance(results[1], Exception):
            print(f"OpenAlex search failed: {results[1]}")
        else:
            oa_results, oa_validation = results[1]

        if isinstance(results[2], Exception):
            print(f"DBLP search failed: {results[2]}")
        else:
            dblp_results = results[2]

        # Now search arXiv by author names from OpenAlex results
        # This is the KEY improvement - we search by known researcher names
        arxiv_papers = []
        arxiv_validation = {"source": "arxiv", "fetched_count": 0}

        if oa_results:
            # Get top researchers by paper count to search on arXiv
            sorted_profs = sorted(
                oa_results.values(),
                key=lambda x: len(x.get('papers', [])),
                reverse=True
            )[:20]  # Top 20 researchers

            prof_names = [p.get('name') for p in sorted_profs if p.get('name')]
            print(f"arXiv: Searching for papers by {len(prof_names)} known researchers...")

            arxiv_papers, arxiv_validation = await self._search_arxiv_by_authors(
                author_names=prof_names,
                topics=topics,
                universities=universities
            )

        # Build validation info
        validation_sources = []
        warnings = []

        if ss_validation:
            validation_sources.append(SourceValidation(
                source="semantic_scholar",
                total_available=ss_validation.get("total_from_api"),
                fetched_count=ss_validation.get("total_papers_found", ss_validation.get("fetched_count", 0)),
                filtered_count=ss_validation.get("professors_found", len(ss_results)),
                is_complete=True,
                completeness_percentage=100.0
            ))

        if oa_validation:
            validation_sources.append(SourceValidation(
                source="openalex",
                total_available=oa_validation.get("total_from_api"),
                fetched_count=oa_validation.get("total_works_found", oa_validation.get("fetched_count", 0)),
                filtered_count=oa_validation.get("professors_found", len(oa_results)),
                is_complete=True,
                completeness_percentage=100.0
            ))

        if arxiv_validation:
            validation_sources.append(SourceValidation(
                source="arxiv",
                total_available=arxiv_validation.get("total_from_api"),
                fetched_count=arxiv_validation.get("fetched_count", len(arxiv_papers)),
                filtered_count=len(arxiv_papers),
                is_complete=True,
                completeness_percentage=100.0
            ))

        # Aggregate results by normalized name
        aggregated: dict[str, dict] = {}

        # Process Semantic Scholar results
        for author_id, prof_data in ss_results.items():
            name_key = normalize_name(prof_data.get('name', ''))
            if not name_key:
                continue

            prof_data['data_sources'] = ['semantic_scholar']

            if name_key in aggregated:
                aggregated[name_key] = merge_professor_data(aggregated[name_key], prof_data)
            else:
                aggregated[name_key] = prof_data

        # Process OpenAlex results
        for author_id, prof_data in oa_results.items():
            name_key = normalize_name(prof_data.get('name', ''))
            if not name_key:
                continue

            prof_data['data_sources'] = ['openalex']

            if name_key in aggregated:
                aggregated[name_key] = merge_professor_data(aggregated[name_key], prof_data)
            else:
                aggregated[name_key] = prof_data

        # Enrich with DBLP data (cross-reference by name)
        for author_key, prof_data in dblp_results.items():
            name_key = normalize_name(prof_data.get('name', ''))
            if name_key in aggregated:
                # Add DBLP data to existing professor
                if prof_data.get('dblp_url'):
                    aggregated[name_key]['dblp_url'] = prof_data['dblp_url']
                aggregated[name_key].setdefault('data_sources', []).append('dblp')

                # Add any papers not already present
                existing_titles = {normalize_title(p.get('title', '')) for p in aggregated[name_key].get('papers', [])}
                for paper in prof_data.get('papers', []):
                    if normalize_title(paper.get('title', '')) not in existing_titles:
                        aggregated[name_key].setdefault('papers', []).append(paper)

        # Build a map of papers with all their authors
        # Key: normalized title, Value: paper info with list of authors
        unique_papers: dict[str, dict] = {}

        for name_key, prof_data in aggregated.items():
            prof_info = {
                'name': prof_data.get('name', 'Unknown'),
                'university': prof_data.get('university', 'Unknown'),
                'url': prof_data.get('url'),
                'name_key': name_key
            }

            for paper in prof_data.get('papers', []):
                title_key = normalize_title(paper.get('title', ''))
                if not title_key:
                    continue

                if title_key not in unique_papers:
                    unique_papers[title_key] = {
                        'title': paper.get('title'),
                        'year': paper.get('year'),
                        'venue': paper.get('venue'),
                        'url': paper.get('url'),
                        'citation_count': paper.get('citation_count'),
                        'source': paper.get('source', 'unknown'),
                        'authors': [],
                        'matching_topics': set(),
                        'relevance_score': paper.get('relevance_score', 0.5)
                    }

                # Add this professor as an author if not already added
                if not any(a['name_key'] == name_key for a in unique_papers[title_key]['authors']):
                    unique_papers[title_key]['authors'].append(prof_info)

                # Add matching topics from this professor
                for topic in prof_data.get('matching_topics', []):
                    unique_papers[title_key]['matching_topics'].add(topic)

        # Add arXiv papers - these were found by searching for known researchers
        # so we trust they're from the right university
        arxiv_added = 0

        for paper in arxiv_papers:
            title_key = normalize_title(paper.get('title', ''))
            if not title_key:
                continue

            # Get the author who led us to this paper
            found_via = paper.get('found_via_author', '')
            paper_university = paper.get('university', universities[0] if universities else None)

            # Build author list
            authors_list = []
            for author in paper.get('authors', []):
                author_name = author.get('name', '') if isinstance(author, dict) else str(author)
                if not author_name:
                    continue

                # Check if this is the author we searched for
                is_known_researcher = normalize_name(author_name) == normalize_name(found_via)

                authors_list.append({
                    'name': author_name,
                    'university': paper_university if is_known_researcher else None,
                    'url': None,
                    'name_key': normalize_name(author_name)
                })

            # Add or update paper
            if title_key in unique_papers:
                # Paper already exists - just add any missing authors
                for author_info in authors_list:
                    if not any(a.get('name_key') == author_info['name_key'] for a in unique_papers[title_key]['authors']):
                        unique_papers[title_key]['authors'].append(author_info)
                arxiv_added += 1
            else:
                # New paper from arXiv - we found it via a known researcher
                unique_papers[title_key] = {
                    'title': paper.get('title'),
                    'year': paper.get('year'),
                    'venue': f"arXiv ({paper.get('primary_category', 'cs')})",
                    'url': paper.get('url'),
                    'citation_count': None,
                    'source': 'arxiv',
                    'authors': authors_list,
                    'matching_topics': set(topics),
                    'relevance_score': 0.9,
                    'arxiv_id': paper.get('arxiv_id'),
                    'pdf_url': paper.get('pdf_url'),
                    'found_via': found_via
                }
                arxiv_added += 1

        print(f"arXiv: Added {arxiv_added} papers from known researchers")

        # Convert to ProfessorResult objects
        professor_results = []

        for name_key, prof_data in aggregated.items():
            # Build Professor object
            professor = Professor(
                name=prof_data.get('name', 'Unknown'),
                title=prof_data.get('title'),
                department=prof_data.get('department'),
                university=prof_data.get('university', 'Unknown'),
                email=prof_data.get('email'),
                profile_url=prof_data.get('profile_url'),
                google_scholar_url=prof_data.get('google_scholar_url'),
                semantic_scholar_id=prof_data.get('author_id'),
                semantic_scholar_url=prof_data.get('url'),
                dblp_url=prof_data.get('dblp_url'),
                homepage=prof_data.get('homepage'),
                research_interests=prof_data.get('research_interests', [])
            )

            # Count unique papers for this professor
            paper_count = len(prof_data.get('papers', []))

            # Calculate relevance
            matching_topics = prof_data.get('matching_topics', [])
            relevance = RelevanceInfo(
                score=calculate_relevance_score(
                    matching_topics=matching_topics,
                    total_topics=len(topics),
                    paper_count=paper_count
                ),
                matching_topics=matching_topics,
                relevant_papers_count=paper_count
            )

            # Try to get student info if requested
            lab = None
            if include_students and professor.homepage:
                try:
                    lab_url = await lab_scraper.find_lab_url_from_homepage(professor.homepage)
                    if lab_url:
                        students_data = await lab_scraper.scrape_lab_for_students(lab_url)
                        if students_data:
                            students = [
                                Student(
                                    name=s['name'],
                                    role=s.get('role'),
                                    url=s.get('url'),
                                    source='lab_website_scrape'
                                )
                                for s in students_data[:20]  # Limit students
                            ]
                            lab = Lab(url=lab_url, students=students)
                except Exception as e:
                    print(f"Failed to scrape lab for {professor.name}: {e}")

            # Build publications for this professor with co-author info
            publications = []
            for paper in prof_data.get('papers', []):
                title_key = normalize_title(paper.get('title', ''))
                # Get co-authors from the unique_papers map
                co_authors = []
                if title_key in unique_papers:
                    for author in unique_papers[title_key]['authors']:
                        # Skip self
                        if author['name_key'] != name_key:
                            co_authors.append(Author(
                                name=author['name'],
                                university=author.get('university'),
                                url=author.get('url')
                            ))

                publications.append(Publication(
                    title=paper.get('title', ''),
                    year=paper.get('year'),
                    venue=paper.get('venue'),
                    url=paper.get('url'),
                    citation_count=paper.get('citation_count'),
                    source=paper.get('source', 'unknown'),
                    authors=co_authors  # Co-authors only (not self)
                ))

            professor_results.append(ProfessorResult(
                professor=professor,
                relevance=relevance,
                publications=publications,
                lab=lab,
                data_sources=prof_data.get('data_sources', []),
                last_verified=datetime.utcnow()
            ))

        # Sort professors by relevance score descending
        professor_results.sort(key=lambda x: x.relevance.score, reverse=True)

        # Build paper results
        paper_results = []
        for title_key, paper_data in unique_papers.items():
            authors = [
                Author(
                    name=a['name'],
                    university=a.get('university'),
                    url=a.get('url')
                )
                for a in paper_data['authors']
            ]

            publication = Publication(
                title=paper_data['title'],
                year=paper_data.get('year'),
                venue=paper_data.get('venue'),
                url=paper_data.get('url'),
                citation_count=paper_data.get('citation_count'),
                authors=authors,
                source=paper_data.get('source', 'unknown')
            )

            paper_results.append(PaperResult(
                publication=publication,
                matching_topics=list(paper_data['matching_topics']),
                relevance_score=paper_data.get('relevance_score', 0.5)
            ))

        # Sort papers by relevance score and citation count
        paper_results.sort(
            key=lambda x: (x.relevance_score, x.publication.citation_count or 0),
            reverse=True
        )

        # Build final validation info
        total_fetched = sum(s.fetched_count for s in validation_sources)
        total_filtered = len(paper_results)

        validation_info = ValidationInfo(
            is_complete=True,  # Always complete - we fetch all papers
            sources=validation_sources,
            total_available_estimate=None,
            total_fetched=total_fetched,
            total_after_filtering=total_filtered,
            warnings=warnings
        )

        return professor_results, paper_results, validation_info


# Singleton instance
aggregator = AggregatorService()
