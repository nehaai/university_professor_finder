# University Professor Finder

Find professors and their students working on specific research topics at universities. All data is sourced from verified academic databases with direct links to profiles and publications - no hallucinated data.

## Features

- **Multi-source aggregation**: Queries Semantic Scholar, OpenAlex, and DBLP APIs
- **Verified links**: Every data point links to its source
- **Student discovery**: Optionally scrapes lab pages for student information
- **Export options**: Download results as CSV or JSON
- **No hallucination**: All data comes directly from academic databases

## Quick Start

### 1. Start the Backend

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The API will be available at http://localhost:8000

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### 2. Start the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The dashboard will be available at http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Enter university names (e.g., "CMU", "MIT", "Stanford")
3. Enter research topics (e.g., "LLM Memory", "Context Engineering", "Machine Learning")
4. Toggle "Include students" if you want to scrape lab pages (slower)
5. Click "Search Professors"

## API Usage

You can also use the API directly:

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "universities": ["CMU", "MIT"],
    "topics": ["LLM Memory", "Context Engineering"],
    "include_students": true
  }'
```

## Project Structure

```
uni_prof/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── semantic_scholar.py  # Semantic Scholar API
│   │   ├── openalex.py          # OpenAlex API
│   │   ├── dblp.py              # DBLP API
│   │   ├── scraper.py           # Lab page scraper
│   │   └── aggregator.py        # Result aggregation
│   └── utils/
│       ├── cache.py             # In-memory caching
│       └── university_mapping.py # University name normalization
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx     # Main search page
│   │   │   └── layout.tsx   # App layout
│   │   ├── components/
│   │   │   ├── SearchForm.tsx   # Search input form
│   │   │   ├── ResultsTable.tsx # Results display
│   │   │   └── ProfessorCard.tsx # Professor card component
│   │   └── lib/
│   │       ├── api.ts       # API client
│   │       └── types.ts     # TypeScript types
│   └── package.json
└── README.md
```

## Data Sources

| Source | What it provides | Rate limits |
|--------|------------------|-------------|
| **Semantic Scholar** | Publications, author profiles, affiliations | 100 req/5 min |
| **OpenAlex** | Open scholarly catalog, institution IDs | 100,000 req/day |
| **DBLP** | CS publications | ~1 req/sec |
| **Lab websites** | Student information (scraped) | 1 req/2 sec |

## Supported Universities

The system includes mappings for common university abbreviations:
- CMU → Carnegie Mellon University
- MIT → Massachusetts Institute of Technology
- Stanford → Stanford University
- Berkeley → University of California, Berkeley
- Harvard → Harvard University
- Princeton → Princeton University
- Cornell → Cornell University
- And many more...

You can also enter full university names.

## Limitations

1. **Rate limits**: API searches are rate-limited to be polite to data sources
2. **Lab scraping**: Student information depends on lab page structure (may not work for all labs)
3. **Name disambiguation**: Professors with common names might have some overlap
4. **Affiliation filtering**: DBLP doesn't support affiliation filtering, so it's used for enrichment only

## License

MIT
