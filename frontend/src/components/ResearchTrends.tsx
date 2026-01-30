"use client";

import { useMemo } from "react";
import { TrendingUp, BarChart3 } from "lucide-react";
import { PaperResult } from "@/lib/types";

interface ResearchTrendsProps {
  papers: PaperResult[];
}

export default function ResearchTrends({ papers }: ResearchTrendsProps) {
  const trends = useMemo(() => {
    if (!papers || papers.length === 0) return null;

    // Get papers by year
    const yearData: Record<number, { count: number; citations: number }> = {};
    const currentYear = new Date().getFullYear();

    papers.forEach((p) => {
      const year = p.publication.year;
      if (year && year >= 2018 && year <= currentYear) {
        if (!yearData[year]) {
          yearData[year] = { count: 0, citations: 0 };
        }
        yearData[year].count++;
        yearData[year].citations += p.publication.citation_count || 0;
      }
    });

    // Create array with all years in range
    const years = [];
    for (let y = 2018; y <= currentYear; y++) {
      years.push({
        year: y,
        count: yearData[y]?.count || 0,
        citations: yearData[y]?.citations || 0,
      });
    }

    // Find max for scaling
    const maxCount = Math.max(...years.map((y) => y.count), 1);
    const maxCitations = Math.max(...years.map((y) => y.citations), 1);

    return {
      years,
      maxCount,
      maxCitations,
    };
  }, [papers]);

  if (!trends || trends.years.length === 0) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow border border-gray-200 dark:border-dark-border p-4 mb-4">
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4 flex items-center gap-2">
        <BarChart3 className="w-4 h-4" />
        Publication Trends by Year
      </h3>

      {/* Bar Chart */}
      <div className="relative">
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 bottom-6 w-8 flex flex-col justify-between text-xs text-gray-400 dark:text-gray-500">
          <span>{trends.maxCount}</span>
          <span>{Math.round(trends.maxCount / 2)}</span>
          <span>0</span>
        </div>

        {/* Chart area */}
        <div className="ml-10 flex items-end justify-between gap-1 h-32">
          {trends.years.map((yearData) => {
            const height = (yearData.count / trends.maxCount) * 100;
            return (
              <div
                key={yearData.year}
                className="flex-1 flex flex-col items-center group relative"
              >
                {/* Bar */}
                <div
                  className="w-full bg-blue-500 dark:bg-blue-400 rounded-t transition-all hover:bg-blue-600 dark:hover:bg-blue-300 cursor-pointer"
                  style={{ height: `${height}%`, minHeight: yearData.count > 0 ? "4px" : "0" }}
                >
                  {/* Tooltip */}
                  <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                    <div className="bg-gray-900 dark:bg-gray-700 text-white text-xs rounded px-2 py-1 whitespace-nowrap">
                      {yearData.count} papers
                      <br />
                      {yearData.citations.toLocaleString()} citations
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* X-axis labels */}
        <div className="ml-10 flex justify-between mt-2">
          {trends.years.map((yearData) => (
            <div
              key={yearData.year}
              className="flex-1 text-center text-xs text-gray-500 dark:text-gray-400"
            >
              {yearData.year.toString().slice(-2)}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-4 text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-blue-500 dark:bg-blue-400 rounded" />
          <span>Paper Count</span>
        </div>
        <span className="text-gray-300 dark:text-gray-600">|</span>
        <span>Hover for details</span>
      </div>

      {/* Trend Summary */}
      <div className="mt-4 pt-3 border-t border-gray-200 dark:border-slate-700">
        <div className="flex items-center gap-2 text-sm">
          <TrendingUp className="w-4 h-4 text-green-500" />
          <span className="text-gray-600 dark:text-gray-400">
            {trends.years[trends.years.length - 1]?.count || 0} papers in{" "}
            {trends.years[trends.years.length - 1]?.year}
            {trends.years.length >= 2 && (
              <>
                {" "}
                (
                {trends.years[trends.years.length - 1]?.count >
                trends.years[trends.years.length - 2]?.count ? (
                  <span className="text-green-600 dark:text-green-400">
                    +
                    {trends.years[trends.years.length - 1]?.count -
                      trends.years[trends.years.length - 2]?.count}{" "}
                    from last year
                  </span>
                ) : trends.years[trends.years.length - 1]?.count <
                  trends.years[trends.years.length - 2]?.count ? (
                  <span className="text-red-600 dark:text-red-400">
                    -
                    {trends.years[trends.years.length - 2]?.count -
                      trends.years[trends.years.length - 1]?.count}{" "}
                    from last year
                  </span>
                ) : (
                  <span className="text-gray-500">same as last year</span>
                )}
                )
              </>
            )}
          </span>
        </div>
      </div>
    </div>
  );
}
