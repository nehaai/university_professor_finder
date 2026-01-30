# University Professor Research Finder - Implementation Plan

## Project Overview
Build a web application that finds professors (and optionally students) working on specific research topics at given universities, with verified links and no hallucinated data.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   Backend API    │────▶│  Data Sources   │
│   (React/Next)  │◀────│   (Python/Fast)  │◀────│  (APIs + Scrape)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Data Sources (Hybrid Approach)

### Primary APIs (Reliable, Structured)
1. **Semantic Scholar API** (Free, no auth required for basic use)
   - Search papers by topic + affiliation
   - Get author profiles with institution
   - Rate limit: 100 requests/5 minutes

2. **DBLP API** (Free, no auth)
   - Computer science publications
   - Author search with affiliation filtering
   - Good for CS-related topics

3. **OpenAlex API** (Free, no auth)
   - Open catalog of scholarly works
   - Affiliation data included
   - Good coverage across fields

### Secondary (Scraping for enrichment)
4. **University Faculty Pages**
   - Verify professor affiliations
   - Get lab websites
   - Find student listings on lab pages

## Tech Stack Recommendation

### Backend: Python + FastAPI
- `httpx` / `aiohttp` - Async API calls
- `beautifulsoup4` - HTML parsing for scraping
- `fastapi` - REST API framework
- `pydantic` - Data validation

### Frontend: Next.js + React
- Clean dashboard UI
- Search interface
- Results with filtering/sorting

### Database: SQLite (simple) or PostgreSQL
- Cache API results
- Store scraped data
- Reduce redundant API calls

## Core Features

### 1. Search Interface
- Input: University name(s), Research topic(s)
- Output: List of professors with:
  - Name
  - Department
  - University
  - Research interests
  - Recent relevant publications (with links)
  - Lab website (if found)
  - Students (if available from lab page)

### 2. Data Verification Strategy
To ensure 100% legitimate data (no hallucination):
- **Only use data from verified API responses**
- **Include source URLs for every data point**
- **Cross-reference across multiple sources**
- **Mark confidence levels** (API-verified vs scraped)

### 3. Results Dashboard
- Sortable/filterable table
- Expandable professor cards
- Direct links to:
  - Google Scholar profile
  - Semantic Scholar profile
  - University faculty page
  - Lab website
  - Recent publications

## File Structure

```
uni_prof/
├── backend/
│   ├── main.py              # FastAPI app entry
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── semantic_scholar.py
│   │   ├── dblp.py
│   │   ├── openalex.py
│   │   └── scraper.py       # University page scraper
│   ├── utils/
│   │   └── cache.py         # Caching logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx     # Main search page
│   │   │   └── layout.tsx
│   │   └── components/
│   │       ├── SearchForm.tsx
│   │       ├── ResultsTable.tsx
│   │       └── ProfessorCard.tsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## API Response Format

```json
{
  "query": {
    "universities": ["CMU", "MIT"],
    "topics": ["LLM Memory", "Context Engineering"]
  },
  "results": [
    {
      "professor": {
        "name": "John Doe",
        "title": "Associate Professor",
        "department": "Computer Science",
        "university": "Carnegie Mellon University",
        "email": "jdoe@cmu.edu",
        "profile_url": "https://www.cs.cmu.edu/~jdoe",
        "google_scholar": "https://scholar.google.com/...",
        "semantic_scholar_id": "12345"
      },
      "relevance": {
        "score": 0.92,
        "matching_topics": ["LLM Memory"],
        "relevant_papers_count": 5
      },
      "publications": [
        {
          "title": "Memory-Augmented LLMs...",
          "year": 2024,
          "venue": "NeurIPS",
          "url": "https://...",
          "source": "semantic_scholar"
        }
      ],
      "lab": {
        "name": "AI Research Lab",
        "url": "https://ailab.cmu.edu",
        "students": [
          {
            "name": "Jane Smith",
            "role": "PhD Student",
            "url": "https://...",
            "source": "lab_website_scrape"
          }
        ]
      },
      "data_sources": ["semantic_scholar", "openalex", "university_website"],
      "last_verified": "2024-01-27T10:00:00Z"
    }
  ],
  "metadata": {
    "total_results": 25,
    "search_time_ms": 3200,
    "sources_queried": ["semantic_scholar", "openalex", "dblp"]
  }
}
```

## Implementation Phases

### Phase 1: Core Backend (MVP)
1. Set up FastAPI project structure
2. Implement Semantic Scholar API integration
3. Implement OpenAlex API integration
4. Basic search endpoint
5. Response formatting with source links

### Phase 2: Enhanced Data
1. Add DBLP integration
2. Implement university page scraper
3. Lab website discovery
4. Student extraction from lab pages

### Phase 3: Frontend Dashboard
1. Next.js project setup
2. Search form component
3. Results table with sorting/filtering
4. Professor detail cards
5. Export functionality (CSV/JSON)

### Phase 4: Polish
1. Caching layer
2. Rate limiting handling
3. Error handling & retries
4. Loading states
5. Mobile responsiveness

## Key Design Decisions

1. **No Hallucination Guarantee**: Every piece of data must have a verifiable source URL
2. **Graceful Degradation**: If an API fails, show partial results from other sources
3. **Transparency**: Show data source for each field (API vs scraped)
4. **Caching**: Cache results to avoid hitting rate limits and improve speed
5. **Async Operations**: Use async throughout for parallel API calls

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API rate limits | Implement caching, exponential backoff |
| Scraping breaks | Graceful fallback, mark as "unverified" |
| Stale data | Show last-verified timestamp, allow refresh |
| Name disambiguation | Use Semantic Scholar IDs as primary key |
| University name variations | Maintain mapping (CMU → Carnegie Mellon) |

---

**Ready to implement?** Approve this plan to proceed.
