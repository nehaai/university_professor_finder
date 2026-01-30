"use client";

import { useState } from "react";
import { GraduationCap, AlertCircle, Bookmark } from "lucide-react";
import SearchForm from "@/components/SearchForm";
import ResultsTable from "@/components/ResultsTable";
import ThemeToggle from "@/components/ThemeToggle";
import BookmarksPanel from "@/components/BookmarksPanel";
import { searchProfessors } from "@/lib/api";
import { SearchResponse, ProfessorResult } from "@/lib/types";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [showBookmarks, setShowBookmarks] = useState(false);

  const handleSearch = async (
    universities: string[],
    topics: string[],
    includeStudents: boolean,
    filters?: { yearFrom?: number; yearTo?: number; minCitations?: number }
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await searchProfessors({
        universities,
        topics,
        include_students: includeStudents,
        ...filters,
      });
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
      setResults(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen py-8 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="flex items-center gap-3 flex-1 justify-center">
              <GraduationCap className="w-10 h-10 text-blue-600 dark:text-blue-400" />
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                University Professor Finder
              </h1>
            </div>
            <div className="absolute right-4 top-4 sm:right-8 sm:top-8 flex items-center gap-2">
              <button
                onClick={() => setShowBookmarks(!showBookmarks)}
                className="p-2 rounded-lg bg-gray-100 dark:bg-dark-card hover:bg-gray-200 dark:hover:bg-slate-600 transition-colors relative"
                aria-label="View bookmarks"
              >
                <Bookmark className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
              <ThemeToggle />
            </div>
          </div>
          <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Find professors and their research papers on specific topics
            at universities. All data is sourced from verified academic databases
            with direct links to profiles and publications.
          </p>
        </div>

        {/* Bookmarks Panel */}
        {showBookmarks && (
          <div className="mb-8">
            <BookmarksPanel onClose={() => setShowBookmarks(false)} />
          </div>
        )}

        {/* Search Form */}
        <div className="mb-8">
          <SearchForm onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-800 dark:text-red-300 font-medium">Search Error</p>
              <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
              <p className="text-red-500 dark:text-red-500 text-xs mt-1">
                Please try again. If the problem persists, the server may be starting up.
              </p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="bg-white dark:bg-dark-card rounded-lg shadow p-8 text-center">
            <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-gray-600 dark:text-gray-300">
              Searching all papers from academic databases...
            </p>
            <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">
              This may take 1-3 minutes to fetch complete results
            </p>
          </div>
        )}

        {/* Results */}
        {!isLoading && results && <ResultsTable response={results} />}

        {/* Empty State */}
        {!isLoading && !results && !error && (
          <div className="bg-white dark:bg-dark-card rounded-lg shadow p-12 text-center">
            <GraduationCap className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600 dark:text-gray-300 mb-2">
              Ready to Search
            </h3>
            <p className="text-gray-400 dark:text-gray-500 max-w-md mx-auto">
              Enter university names and research topics above to find all relevant
              papers and their authors. Results include links to verified profiles
              and publications.
            </p>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-gray-400 dark:text-gray-500">
          <p>
            Data sourced from{" "}
            <a
              href="https://www.semanticscholar.org"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:underline"
            >
              Semantic Scholar
            </a>
            ,{" "}
            <a
              href="https://openalex.org"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:underline"
            >
              OpenAlex
            </a>
            , and{" "}
            <a
              href="https://dblp.org"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:underline"
            >
              DBLP
            </a>
          </p>
          <p className="mt-1">
            All links point directly to verified source pages. No hallucinated data.
          </p>
        </footer>
      </div>
    </main>
  );
}
