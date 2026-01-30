"""
Shared relevance scoring and filtering logic.
Used by semantic_scholar.py and openalex.py to avoid code duplication.
"""

import re

# Keywords that indicate biology/chemistry/neuroscience papers (to exclude from CS/AI searches)
EXCLUDE_KEYWORDS = [
    # Biology/Medical
    "protein", "amino acid", "dna", "rna", "gene", "genome", "genomic",
    "cell", "cellular", "molecular", "molecule", "enzyme", "peptide",
    "biology", "biological", "biomedical", "clinical", "patient",
    "drug", "pharmaceutical", "therapeutic", "disease", "cancer",
    "histopathology", "pathology", "tumor", "tissue", "biopsy",
    "organism", "species", "evolution", "phylogenetic",
    # Chemistry/Materials
    "chemistry", "chemical", "compound", "synthesis",
    "materials science", "phase-property", "alloy", "catalyst",
    # Neuroscience (brain imaging, not AI)
    "fmri", "brain imaging", "neuroimaging", "eeg", "meg",
    "cortex", "cortical", "hippocampus", "prefrontal",
    "brain region", "brain activity", "neural activity",
    "cognitive neuroscience", "brain network",
    # Speech/Audio (not text NLP)
    "speech recognition", "speech synthesis", "acoustic",
    "phoneme", "phonetic", "prosody", "audio signal",
    # Other non-relevant
    "climate", "weather", "ocean", "atmosphere",
    "physics", "quantum", "particle",
]

# Topic expansions for better search coverage
TOPIC_EXPANSIONS = {
    "llm": ["llm", "llms", "large language model", "large language models", "chatgpt", "gpt-4", "gpt-3", "claude", "gemini"],
    "large language model": ["large language model", "large language models", "llm", "llms", "chatgpt", "gpt"],
    "nlp": ["nlp", "natural language processing", "text processing"],
    "natural language processing": ["natural language processing", "nlp", "text processing"],
    "context engineering": ["context engineering", "in-context learning", "context window", "prompt engineering", "few-shot learning", "zero-shot"],
    "llm memory": ["llm memory", "memory augmented", "retrieval augmented", "rag", "long context", "context length", "memory-augmented language model"],
    "machine learning": ["machine learning", "ml", "deep learning"],
    "transformer": ["transformer", "attention mechanism", "self-attention"],
    "gpt": ["gpt", "gpt-2", "gpt-3", "gpt-4", "chatgpt", "openai"],
    "bert": ["bert", "roberta", "albert", "distilbert"],
}

# REQUIRED keywords - at least one must be present for LLM-related searches
LLM_REQUIRED_KEYWORDS = [
    "language model", "llm", "gpt", "bert", "transformer",
    "chatgpt", "prompt", "in-context", "few-shot", "zero-shot",
    "text generation", "nlp", "natural language processing",
    "question answering", "text classification", "summarization",
    "machine translation", "sentiment analysis", "named entity",
    "retrieval augmented", "rag", "fine-tuning", "pre-training",
    "tokenization", "embedding", "attention mechanism",
]

# NLP/AI venue keywords for filtering
NLP_AI_VENUES = [
    "acl", "emnlp", "naacl", "coling", "eacl",  # NLP conferences
    "neurips", "nips", "icml", "iclr",  # ML conferences
    "aaai", "ijcai",  # AI conferences
    "cvpr", "iccv", "eccv",  # Vision conferences
    "arxiv",  # Preprints
    "transactions on",  # IEEE/ACM transactions
    "journal of machine learning",
    "artificial intelligence",
]


def should_exclude_paper(title: str, abstract: str = "") -> bool:
    """
    Check if a paper should be excluded based on keywords.
    Returns True if paper should be EXCLUDED (not relevant to CS/AI LLM research).
    """
    text = f"{title} {abstract}".lower()

    # Count exclude keywords
    exclude_count = sum(1 for kw in EXCLUDE_KEYWORDS if kw in text)

    # If multiple exclude keywords, reject
    if exclude_count >= 2:
        return True

    # Special cases for common false positives
    # "language network" in brain = neuroscience, not NLP
    if "language network" in text and ("brain" in text or "fmri" in text or "neural" in text):
        return True

    # "speech" without "text" or "nlp" = audio processing
    if "speech" in text and "text" not in text and "nlp" not in text and "language model" not in text:
        return True

    return False


def has_required_keywords(title: str, abstract: str, topics: list[str]) -> bool:
    """
    Check if paper has at least one required keyword for LLM-related searches.
    This ensures we only return papers actually about LLMs/NLP, not tangentially related.
    """
    text = f"{title} {abstract}".lower()

    # Check if any required keyword is present
    for kw in LLM_REQUIRED_KEYWORDS:
        if kw in text:
            return True

    # Also check expanded topic terms
    for topic in topics:
        expanded = get_expanded_terms(topic)
        for term in expanded:
            if term.lower() in text:
                return True

    return False


def is_nlp_venue(venue: str) -> bool:
    """Check if the venue is a known NLP/AI venue."""
    if not venue:
        return False
    venue_lower = venue.lower()
    return any(v in venue_lower for v in NLP_AI_VENUES)


def get_expanded_terms(topic: str) -> list[str]:
    """Get expanded search terms for a topic."""
    topic_lower = topic.lower().strip()
    return TOPIC_EXPANSIONS.get(topic_lower, [topic_lower])


def calculate_topic_relevance(
    title: str,
    abstract: str,
    topics: list[str],
    concepts: list[dict] = None
) -> tuple[float, bool]:
    """
    Calculate relevance score for a paper against given topics.

    STRICT FILTERING:
    1. Must NOT contain exclude keywords (biology, neuroscience, etc.)
    2. Must contain at least one required keyword (language model, nlp, etc.)
    3. Keyword matching against expanded topic terms

    Returns (score, is_relevant) where:
    - score: 0.0-1.0 relevance score
    - is_relevant: True if paper should be included
    """
    if not title:
        return 0.0, False

    title_lower = title.lower()
    abstract_lower = (abstract or '').lower()
    text = f"{title_lower} {abstract_lower}"

    # STEP 1: Check exclusions - reject if contains exclude keywords
    if should_exclude_paper(title, abstract):
        return 0.0, False

    # STEP 2: Check required keywords - must have at least one LLM/NLP keyword
    if not has_required_keywords(title, abstract, topics):
        return 0.0, False

    # STEP 3: Score based on topic matching
    keyword_score = 0.0
    matched_in_title = False

    for topic in topics:
        expanded_terms = get_expanded_terms(topic)

        for term in expanded_terms:
            term_lower = term.lower()
            if term_lower in title_lower:
                keyword_score = max(keyword_score, 1.0)
                matched_in_title = True
                break
            elif term_lower in text:
                keyword_score = max(keyword_score, 0.7)

    # Bonus for matching in title
    if matched_in_title:
        keyword_score = 1.0

    # Check OpenAlex concepts if available (bonus scoring)
    if concepts:
        for concept in concepts:
            concept_name = concept.get("display_name", "").lower()
            concept_score_val = concept.get("score", 0)

            # Check if concept matches NLP/AI
            nlp_terms = [
                "natural language processing", "language model", "machine learning",
                "deep learning", "artificial intelligence", "transformer",
            ]
            if any(nlp_term in concept_name for nlp_term in nlp_terms):
                keyword_score = max(keyword_score, 0.8)

    # Final relevance decision
    is_relevant = keyword_score >= 0.5

    return keyword_score, is_relevant


def is_valid_paper_url(url: str) -> bool:
    """Check if a URL is a valid paper link (not a search page or placeholder)."""
    if not url:
        return False

    invalid_patterns = [r'search\?', r'google\.com/search', r'^#', r'javascript:']
    for pattern in invalid_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False
    return True


# Keep old function name for backward compatibility
def is_biology_paper(title: str, abstract: str = "") -> bool:
    """Deprecated: Use should_exclude_paper instead."""
    return should_exclude_paper(title, abstract)
