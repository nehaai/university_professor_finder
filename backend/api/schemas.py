from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SearchRequest(BaseModel):
    universities: list[str] = Field(..., description="List of university names (e.g., ['CMU', 'MIT'])")
    topics: list[str] = Field(..., description="List of research topics (e.g., ['LLM Memory', 'Context Engineering'])")
    include_students: bool = Field(default=False, description="Whether to attempt finding students from lab pages")


class Author(BaseModel):
    name: str
    university: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None


class Publication(BaseModel):
    title: str
    year: Optional[int] = None
    venue: Optional[str] = None
    url: Optional[str] = None
    citation_count: Optional[int] = None
    authors: list[Author] = Field(default_factory=list, description="All professors from the search who authored this paper")
    source: str = Field(..., description="Data source (semantic_scholar, openalex, dblp)")


class Student(BaseModel):
    name: str
    role: Optional[str] = None  # PhD Student, Postdoc, etc.
    url: Optional[str] = None
    source: str = Field(default="lab_website_scrape")


class Lab(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    students: list[Student] = []


class Professor(BaseModel):
    name: str
    title: Optional[str] = None
    department: Optional[str] = None
    university: str
    email: Optional[str] = None
    profile_url: Optional[str] = None
    google_scholar_url: Optional[str] = None
    semantic_scholar_id: Optional[str] = None
    semantic_scholar_url: Optional[str] = None
    dblp_url: Optional[str] = None
    homepage: Optional[str] = None
    research_interests: list[str] = Field(default_factory=list, description="Research interests/topics from OpenAlex concepts")


class RelevanceInfo(BaseModel):
    score: float = Field(..., ge=0, le=1)
    matching_topics: list[str] = []
    relevant_papers_count: int = 0


class ProfessorResult(BaseModel):
    professor: Professor
    relevance: RelevanceInfo
    publications: list[Publication] = []
    lab: Optional[Lab] = None
    data_sources: list[str] = []
    last_verified: datetime = Field(default_factory=datetime.utcnow)


class PaperResult(BaseModel):
    """A paper with all its authors from the search results."""
    publication: Publication
    matching_topics: list[str] = []
    relevance_score: float = Field(default=0.0, ge=0, le=1)


class SearchQuery(BaseModel):
    universities: list[str]
    topics: list[str]


# Validation models
class SourceValidation(BaseModel):
    source: str
    total_available: Optional[int] = None
    fetched_count: int
    filtered_count: int
    is_complete: bool
    completeness_percentage: Optional[float] = None


class ValidationInfo(BaseModel):
    """Information about the completeness of the search results."""
    is_complete: bool = Field(description="Whether all available papers were fetched")
    sources: list[SourceValidation] = []
    total_available_estimate: Optional[int] = None
    total_fetched: int = 0
    total_after_filtering: int = 0
    warnings: list[str] = []


class SearchMetadata(BaseModel):
    total_results: int
    total_papers: int = 0
    search_time_ms: int
    sources_queried: list[str]
    validation: Optional[ValidationInfo] = None


class SearchResponse(BaseModel):
    query: SearchQuery
    results: list[ProfessorResult]
    papers: list[PaperResult] = Field(default_factory=list, description="Unique papers with all authors listed")
    metadata: SearchMetadata


# Validation request/response for checking specific authors
class ValidateAuthorRequest(BaseModel):
    author_name: str
    semantic_scholar_id: Optional[str] = None
    openalex_id: Optional[str] = None


class AuthorValidation(BaseModel):
    author_name: str
    semantic_scholar: Optional[dict] = None  # paper_count, fetched_count, is_complete
    openalex: Optional[dict] = None  # works_count, fetched_count, is_complete
    combined_estimate: Optional[int] = None
    papers_in_results: int = 0
    is_complete: bool = False
    completeness_percentage: float = 0.0


class ValidateAuthorResponse(BaseModel):
    validation: AuthorValidation
    external_links: dict = {}  # Links to verify on external sites
