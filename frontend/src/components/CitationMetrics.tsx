"use client";

import { useMemo } from "react";
import { TrendingUp, Award, Calendar, BookOpen } from "lucide-react";
import { PaperResult } from "@/lib/types";

interface CitationMetricsProps {
  papers: PaperResult[];
}

export default function CitationMetrics({ papers }: CitationMetricsProps) {
  const metrics = useMemo(() => {
    if (!papers || papers.length === 0) {
      return null;
    }

    // Total citations
    const totalCitations = papers.reduce(
      (sum, p) => sum + (p.publication.citation_count || 0),
      0
    );

    // Average citations
    const avgCitations = totalCitations / papers.length;

    // Top cited paper
    const topCited = papers.reduce((top, p) => {
      const citations = p.publication.citation_count || 0;
      const topCitations = top?.publication.citation_count || 0;
      return citations > topCitations ? p : top;
    }, papers[0]);

    // Year distribution
    const yearCounts: Record<number, number> = {};
    papers.forEach((p) => {
      if (p.publication.year) {
        yearCounts[p.publication.year] = (yearCounts[p.publication.year] || 0) + 1;
      }
    });

    // Most active year
    const mostActiveYear = Object.entries(yearCounts).reduce(
      (max, [year, count]) => (count > max.count ? { year: parseInt(year), count } : max),
      { year: 0, count: 0 }
    );

    // Venue distribution (top 3)
    const venueCounts: Record<string, number> = {};
    papers.forEach((p) => {
      if (p.publication.venue) {
        venueCounts[p.publication.venue] = (venueCounts[p.publication.venue] || 0) + 1;
      }
    });
    const topVenues = Object.entries(venueCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3);

    // Highly cited papers (>50 citations)
    const highlyCited = papers.filter(
      (p) => (p.publication.citation_count || 0) > 50
    ).length;

    return {
      totalCitations,
      avgCitations,
      topCited,
      mostActiveYear,
      topVenues,
      highlyCited,
      paperCount: papers.length,
    };
  }, [papers]);

  if (!metrics) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow border border-gray-200 dark:border-dark-border p-4 mb-4">
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
        <TrendingUp className="w-4 h-4" />
        Citation Metrics
      </h3>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Total Citations */}
        <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {metrics.totalCitations.toLocaleString()}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Total Citations</div>
        </div>

        {/* Average Citations */}
        <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {metrics.avgCitations.toFixed(1)}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Avg per Paper</div>
        </div>

        {/* Highly Cited */}
        <div className="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
          <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
            {metrics.highlyCited}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">50+ Citations</div>
        </div>

        {/* Most Active Year */}
        <div className="text-center p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {metrics.mostActiveYear.year || "N/A"}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">
            Most Active ({metrics.mostActiveYear.count} papers)
          </div>
        </div>
      </div>

      {/* Top Cited Paper */}
      {metrics.topCited && metrics.topCited.publication.citation_count > 0 && (
        <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
          <div className="flex items-start gap-2">
            <Award className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium text-yellow-800 dark:text-yellow-300 mb-1">
                Top Cited Paper ({metrics.topCited.publication.citation_count} citations)
              </div>
              {metrics.topCited.publication.url ? (
                <a
                  href={metrics.topCited.publication.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline line-clamp-2"
                >
                  {metrics.topCited.publication.title}
                </a>
              ) : (
                <span className="text-sm text-gray-800 dark:text-gray-200 line-clamp-2">
                  {metrics.topCited.publication.title}
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Top Venues */}
      {metrics.topVenues.length > 0 && (
        <div className="mt-3">
          <div className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2 flex items-center gap-1">
            <BookOpen className="w-3 h-3" />
            Top Venues
          </div>
          <div className="flex flex-wrap gap-2">
            {metrics.topVenues.map(([venue, count]) => (
              <span
                key={venue}
                className="px-2 py-1 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 text-xs rounded"
              >
                {venue.length > 40 ? venue.substring(0, 40) + "..." : venue} ({count})
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
