export interface Author {
  name: string;
  university?: string;
  url?: string;
  email?: string;
}

export interface Publication {
  title: string;
  year?: number;
  venue?: string;
  url?: string;
  citation_count?: number;
  authors?: Author[];
  source: string;
}

export interface PaperResult {
  publication: Publication;
  matching_topics: string[];
  relevance_score: number;
}

export interface Student {
  name: string;
  role?: string;
  url?: string;
  source: string;
}

export interface Lab {
  name?: string;
  url?: string;
  students: Student[];
}

export interface Professor {
  name: string;
  title?: string;
  department?: string;
  university: string;
  email?: string;
  profile_url?: string;
  google_scholar_url?: string;
  semantic_scholar_id?: string;
  semantic_scholar_url?: string;
  dblp_url?: string;
  homepage?: string;
  research_interests?: string[];
}

export interface RelevanceInfo {
  score: number;
  matching_topics: string[];
  relevant_papers_count: number;
}

export interface ProfessorResult {
  professor: Professor;
  relevance: RelevanceInfo;
  publications: Publication[];
  lab?: Lab;
  data_sources: string[];
  last_verified: string;
}

export interface SearchQuery {
  universities: string[];
  topics: string[];
}

// Validation types
export interface SourceValidation {
  source: string;
  total_available?: number;
  fetched_count: number;
  filtered_count: number;
  is_complete: boolean;
  completeness_percentage?: number;
}

export interface ValidationInfo {
  is_complete: boolean;
  sources: SourceValidation[];
  total_available_estimate?: number;
  total_fetched: number;
  total_after_filtering: number;
  warnings: string[];
}

export interface SearchMetadata {
  total_results: number;
  total_papers: number;
  search_time_ms: number;
  sources_queried: string[];
  validation?: ValidationInfo;
}

export interface SearchResponse {
  query: SearchQuery;
  results: ProfessorResult[];
  papers: PaperResult[];
  metadata: SearchMetadata;
}

export interface SearchRequest {
  universities: string[];
  topics: string[];
  include_students: boolean;
}
