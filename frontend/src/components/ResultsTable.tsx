"use client";

import { useState, useMemo } from "react";
import { ArrowUpDown, Download, Filter, ChevronUp, BookOpen, CheckCircle, AlertTriangle, Info } from "lucide-react";
import { SearchResponse } from "@/lib/types";
import PaperCard from "./PaperCard";

interface ResultsTableProps {
  response: SearchResponse;
}

type PaperSortField = "title" | "relevance" | "citations" | "year";
type SortOrder = "asc" | "desc";

export default function ResultsTable({ response }: ResultsTableProps) {
  const [paperSortField, setPaperSortField] = useState<PaperSortField>("relevance");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [filterUniversity, setFilterUniversity] = useState<string>("");
  const [filterTopic, setFilterTopic] = useState<string>("");

  const { papers, metadata, query } = response;

  // Get unique universities from paper authors
  const universities = useMemo(() => {
    const unis = new Set<string>();
    (papers || []).forEach((p) => {
      p.publication.authors?.forEach((a) => {
        if (a.university) unis.add(a.university);
      });
    });
    return Array.from(unis).sort();
  }, [papers]);

  // Get all topics from papers
  const allTopics = useMemo(() => {
    const topics = new Set<string>();
    (papers || []).forEach((p) => {
      p.matching_topics.forEach((t) => topics.add(t));
    });
    return Array.from(topics).sort();
  }, [papers]);

  // Filter and sort papers
  const processedPapers = useMemo(() => {
    let filtered = [...(papers || [])];

    // Apply topic filter
    if (filterTopic) {
      filtered = filtered.filter((p) =>
        p.matching_topics.includes(filterTopic)
      );
    }

    // Apply university filter (filter by author university)
    if (filterUniversity) {
      filtered = filtered.filter((p) =>
        p.publication.authors?.some((a) => a.university === filterUniversity)
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      switch (paperSortField) {
        case "title":
          comparison = a.publication.title.localeCompare(b.publication.title);
          break;
        case "relevance":
          comparison = a.relevance_score - b.relevance_score;
          break;
        case "citations":
          comparison = (a.publication.citation_count || 0) - (b.publication.citation_count || 0);
          break;
        case "year":
          comparison = (a.publication.year || 0) - (b.publication.year || 0);
          break;
      }
      return sortOrder === "asc" ? comparison : -comparison;
    });

    return filtered;
  }, [papers, paperSortField, sortOrder, filterUniversity, filterTopic]);

  const scrollToTop = () => {
    document.getElementById("results-container")?.scrollTo({ top: 0, behavior: "smooth" });
  };

  const exportToCSV = () => {
    const headers = [
      "Title",
      "Year",
      "Venue",
      "Citations",
      "Authors",
      "Universities",
      "Matching Topics",
      "Relevance Score",
      "URL",
      "Source",
    ];

    const rows = processedPapers.map((p) => [
      p.publication.title,
      p.publication.year?.toString() || "",
      p.publication.venue || "",
      p.publication.citation_count?.toString() || "",
      p.publication.authors?.map((a) => a.name).join("; ") || "",
      p.publication.authors?.map((a) => a.university).filter(Boolean).join("; ") || "",
      p.matching_topics.join("; "),
      p.relevance_score.toFixed(2),
      p.publication.url || "",
      p.publication.source,
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map((row) =>
        row.map((cell) => `"${cell.replace(/"/g, '""')}"`).join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `papers_${query.universities.join("-")}_${Date.now()}.csv`;
    link.click();
  };

  const exportToJSON = () => {
    const blob = new Blob([JSON.stringify({ papers: processedPapers, query, metadata }, null, 2)], {
      type: "application/json",
    });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `papers_${query.universities.join("-")}_${Date.now()}.json`;
    link.click();
  };

  const validation = metadata.validation;

  return (
    <div className="space-y-4">
      {/* Validation Info Banner */}
      {validation && (
        <div className={`p-4 rounded-lg border ${
          validation.is_complete
            ? "bg-green-50 border-green-200"
            : "bg-yellow-50 border-yellow-200"
        }`}>
          <div className="flex items-start gap-3">
            {validation.is_complete ? (
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <div className={`font-medium ${
                validation.is_complete ? "text-green-800" : "text-yellow-800"
              }`}>
                {validation.is_complete
                  ? "Complete Results"
                  : "Partial Results (Quick Search)"}
              </div>
              <div className="text-sm mt-1 space-y-1">
                <p className={validation.is_complete ? "text-green-700" : "text-yellow-700"}>
                  Fetched {validation.total_fetched} papers from APIs,
                  {" "}{validation.total_after_filtering} after filtering for relevance.
                </p>
                {validation.sources.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {validation.sources.map((source) => (
                      <span
                        key={source.source}
                        className={`text-xs px-2 py-1 rounded ${
                          source.is_complete
                            ? "bg-green-100 text-green-800"
                            : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {source.source}: {source.fetched_count} fetched
                        {source.is_complete && " (complete)"}
                      </span>
                    ))}
                  </div>
                )}
                {validation.warnings.length > 0 && (
                  <div className="mt-2 flex items-start gap-2 text-xs text-yellow-700">
                    <Info className="w-4 h-4 flex-shrink-0" />
                    <span>{validation.warnings[0]}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center gap-2 text-lg font-medium text-gray-900">
        <BookOpen className="w-5 h-5" />
        Research Papers
      </div>

      {/* Stats and Controls - Sticky header */}
      <div className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-4 bg-white p-4 rounded-lg shadow border border-gray-200">
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-600">
            <span className="font-semibold text-gray-900">
              {processedPapers.length}
            </span>{" "}
            papers found
            {processedPapers.length !== (papers?.length || 0) && (
              <span className="text-gray-400">
                {" "}
                (filtered from {papers?.length || 0})
              </span>
            )}
          </div>
          <div className="text-sm text-gray-400">
            Searched in {metadata.search_time_ms}ms
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Filters */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={filterUniversity}
              onChange={(e) => setFilterUniversity(e.target.value)}
              className="text-sm border rounded px-2 py-1"
            >
              <option value="">All Universities</option>
              {universities.map((uni) => (
                <option key={uni} value={uni}>
                  {uni}
                </option>
              ))}
            </select>
            <select
              value={filterTopic}
              onChange={(e) => setFilterTopic(e.target.value)}
              className="text-sm border rounded px-2 py-1"
            >
              <option value="">All Topics</option>
              {allTopics.map((topic) => (
                <option key={topic} value={topic}>
                  {topic}
                </option>
              ))}
            </select>
          </div>

          {/* Sort */}
          <div className="flex items-center gap-1 border-l pl-2">
            <ArrowUpDown className="w-4 h-4 text-gray-400" />
            <select
              value={`${paperSortField}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split("-");
                setPaperSortField(field as PaperSortField);
                setSortOrder(order as SortOrder);
              }}
              className="text-sm border rounded px-2 py-1"
            >
              <option value="relevance-desc">Relevance (High to Low)</option>
              <option value="relevance-asc">Relevance (Low to High)</option>
              <option value="citations-desc">Citations (Most)</option>
              <option value="citations-asc">Citations (Least)</option>
              <option value="year-desc">Year (Newest)</option>
              <option value="year-asc">Year (Oldest)</option>
              <option value="title-asc">Title (A-Z)</option>
            </select>
          </div>

          {/* Export */}
          <div className="flex items-center gap-1 border-l pl-2">
            <Download className="w-4 h-4 text-gray-400" />
            <button
              onClick={exportToCSV}
              className="text-sm px-2 py-1 hover:bg-gray-100 rounded"
            >
              CSV
            </button>
            <button
              onClick={exportToJSON}
              className="text-sm px-2 py-1 hover:bg-gray-100 rounded"
            >
              JSON
            </button>
          </div>
        </div>
      </div>

      {/* Papers List */}
      {processedPapers.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No papers found matching your criteria.</p>
        </div>
      ) : (
        <div className="relative">
          <div
            id="results-container"
            className="max-h-[600px] overflow-y-auto space-y-3 pr-2 scroll-smooth"
            style={{ scrollbarGutter: "stable" }}
          >
            {processedPapers.map((paper, idx) => (
              <PaperCard key={`${paper.publication.title}-${idx}`} paper={paper} />
            ))}
          </div>

          {processedPapers.length > 5 && (
            <button
              onClick={scrollToTop}
              className="absolute bottom-4 right-4 p-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors"
              title="Scroll to top"
            >
              <ChevronUp className="w-5 h-5" />
            </button>
          )}

          <div className="mt-3 text-center text-sm text-gray-400">
            Showing {processedPapers.length} of {papers?.length || 0} papers
          </div>
        </div>
      )}
    </div>
  );
}
