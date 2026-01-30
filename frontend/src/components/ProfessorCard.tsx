"use client";

import { useState, useEffect } from "react";
import {
  ChevronDown,
  ChevronUp,
  ExternalLink,
  BookOpen,
  Users,
  Link as LinkIcon,
  Database,
  Mail,
  Lightbulb,
  Bookmark,
  BookmarkCheck,
} from "lucide-react";
import { ProfessorResult } from "@/lib/types";
import { addProfessorBookmark, removeProfessorBookmark, isProfessorBookmarked } from "@/lib/bookmarks";

interface ProfessorCardProps {
  result: ProfessorResult;
}

export default function ProfessorCard({ result }: ProfessorCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const { professor, relevance, publications, lab, data_sources } = result;

  useEffect(() => {
    setIsBookmarked(isProfessorBookmarked(professor.name, professor.university));
  }, [professor.name, professor.university]);

  const toggleBookmark = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isBookmarked) {
      removeProfessorBookmark(professor.name, professor.university);
    } else {
      addProfessorBookmark(result);
    }
    setIsBookmarked(!isBookmarked);
  };

  const relevanceColor =
    relevance.score >= 0.7
      ? "bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300"
      : relevance.score >= 0.4
      ? "bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-300"
      : "bg-gray-100 dark:bg-slate-700 text-gray-800 dark:text-gray-300";

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow border border-gray-200 dark:border-dark-border overflow-hidden">
      {/* Header - Always visible */}
      <div
        className="p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {professor.name}
              </h3>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${relevanceColor}`}>
                {Math.round(relevance.score * 100)}% match
              </span>
              <button
                onClick={toggleBookmark}
                className={`p-1.5 rounded-lg transition-colors ${
                  isBookmarked
                    ? "text-yellow-500 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/30"
                    : "text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700"
                }`}
                title={isBookmarked ? "Remove bookmark" : "Bookmark professor"}
              >
                {isBookmarked ? (
                  <BookmarkCheck className="w-4 h-4" />
                ) : (
                  <Bookmark className="w-4 h-4" />
                )}
              </button>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {professor.title && `${professor.title} • `}
              {professor.department && `${professor.department} • `}
              {professor.university}
            </p>

            {/* Email - shown prominently if available */}
            {professor.email && (
              <a
                href={`mailto:${professor.email}`}
                className="inline-flex items-center gap-1 text-sm text-blue-600 dark:text-blue-400 hover:underline mt-1"
                onClick={(e) => e.stopPropagation()}
              >
                <Mail className="w-4 h-4" />
                {professor.email}
              </a>
            )}

            {/* Matching Topics */}
            <div className="flex flex-wrap gap-1 mt-2">
              {relevance.matching_topics.map((topic) => (
                <span
                  key={topic}
                  className="px-2 py-0.5 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded"
                >
                  {topic}
                </span>
              ))}
            </div>

            {/* Research Interests if available */}
            {professor.research_interests && professor.research_interests.length > 0 && (
              <div className="mt-2">
                <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-1">
                  <Lightbulb className="w-3 h-3" />
                  Research Interests:
                </div>
                <div className="flex flex-wrap gap-1">
                  {professor.research_interests.slice(0, 5).map((interest, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded"
                    >
                      {interest}
                    </span>
                  ))}
                  {professor.research_interests.length > 5 && (
                    <span className="text-xs text-gray-400 dark:text-gray-500">
                      +{professor.research_interests.length - 5} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
          <button className="p-1 hover:bg-gray-200 dark:hover:bg-slate-700 rounded">
            {isExpanded ? (
              <ChevronUp className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            )}
          </button>
        </div>

        {/* Quick Stats */}
        <div className="flex gap-4 mt-3 text-sm text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-1">
            <BookOpen className="w-4 h-4" />
            {publications.length} papers
          </span>
          {lab && lab.students.length > 0 && (
            <span className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              {lab.students.length} students
            </span>
          )}
          <span className="flex items-center gap-1">
            <Database className="w-4 h-4" />
            {data_sources.join(", ")}
          </span>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 dark:border-dark-border p-4 space-y-4 bg-gray-50 dark:bg-slate-800/50">
          {/* Contact Information */}
          {professor.email && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1">
                <Mail className="w-4 h-4" />
                Contact Information
              </h4>
              <div className="bg-white dark:bg-slate-800 p-3 rounded border dark:border-slate-700">
                <a
                  href={`mailto:${professor.email}`}
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  {professor.email}
                </a>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {professor.university} • {professor.department || "Faculty"}
                </p>
              </div>
            </div>
          )}

          {/* Links */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1">
              <LinkIcon className="w-4 h-4" />
              Profile Links
            </h4>
            <div className="flex flex-wrap gap-2">
              {professor.semantic_scholar_url && (
                <a
                  href={professor.semantic_scholar_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 px-3 py-1 bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-full text-sm hover:bg-gray-100 dark:hover:bg-slate-700 text-gray-700 dark:text-gray-300"
                >
                  Semantic Scholar
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              {professor.google_scholar_url && (
                <a
                  href={professor.google_scholar_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 px-3 py-1 bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-full text-sm hover:bg-gray-100 dark:hover:bg-slate-700 text-gray-700 dark:text-gray-300"
                >
                  Google Scholar
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              {professor.dblp_url && (
                <a
                  href={professor.dblp_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 px-3 py-1 bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-full text-sm hover:bg-gray-100 dark:hover:bg-slate-700 text-gray-700 dark:text-gray-300"
                >
                  DBLP
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              {professor.homepage && (
                <a
                  href={professor.homepage}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 px-3 py-1 bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-full text-sm hover:bg-gray-100 dark:hover:bg-slate-700 text-gray-700 dark:text-gray-300"
                >
                  Homepage
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              {professor.profile_url && (
                <a
                  href={professor.profile_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 px-3 py-1 bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-full text-sm hover:bg-gray-100 dark:hover:bg-slate-700 text-gray-700 dark:text-gray-300"
                >
                  Faculty Profile
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>

          {/* Publications - scrollable */}
          {publications.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1">
                <BookOpen className="w-4 h-4" />
                Relevant Publications ({publications.length})
              </h4>
              <div
                className="space-y-2 max-h-64 overflow-y-auto pr-2"
                style={{ scrollbarWidth: "thin" }}
              >
                {publications.slice(0, 10).map((pub, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-white dark:bg-slate-800 rounded border dark:border-slate-700 text-sm"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        {pub.url ? (
                          <a
                            href={pub.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-medium text-blue-600 dark:text-blue-400 hover:underline"
                          >
                            {pub.title}
                          </a>
                        ) : (
                          <span className="font-medium text-gray-900 dark:text-white">{pub.title}</span>
                        )}
                        <div className="text-gray-500 dark:text-gray-400 mt-1">
                          {pub.venue && <span>{pub.venue}</span>}
                          {pub.year && <span> ({pub.year})</span>}
                          {pub.citation_count !== undefined && (
                            <span className="ml-2">• {pub.citation_count} citations</span>
                          )}
                        </div>
                        {/* Co-authors from search results */}
                        {pub.authors && pub.authors.length > 0 && (
                          <div className="mt-1.5 text-xs">
                            <span className="text-gray-400 dark:text-gray-500">Co-authored with: </span>
                            {pub.authors.slice(0, 5).map((coAuthor, coIdx) => (
                              <span key={coIdx}>
                                {coAuthor.url ? (
                                  <a
                                    href={coAuthor.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-purple-600 dark:text-purple-400 hover:underline"
                                  >
                                    {coAuthor.name}
                                  </a>
                                ) : (
                                  <span className="text-purple-600 dark:text-purple-400">{coAuthor.name}</span>
                                )}
                                {coIdx < Math.min(pub.authors!.length, 5) - 1 && ", "}
                              </span>
                            ))}
                            {pub.authors.length > 5 && (
                              <span className="text-gray-400 dark:text-gray-500"> +{pub.authors.length - 5} more</span>
                            )}
                          </div>
                        )}
                      </div>
                      <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 rounded whitespace-nowrap">
                        {pub.source}
                      </span>
                    </div>
                  </div>
                ))}
                {publications.length > 10 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-2">
                    + {publications.length - 10} more publications
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Students - scrollable if many */}
          {lab && lab.students.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-1">
                <Users className="w-4 h-4" />
                Lab Members ({lab.students.length})
                {lab.url && (
                  <a
                    href={lab.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-blue-600 dark:text-blue-400 hover:underline text-xs"
                  >
                    Visit Lab Page
                  </a>
                )}
              </h4>
              <div
                className={`flex flex-wrap gap-2 ${lab.students.length > 10 ? "max-h-32 overflow-y-auto pr-2" : ""}`}
                style={{ scrollbarWidth: "thin" }}
              >
                {lab.students.map((student, idx) => (
                  <div
                    key={idx}
                    className="px-3 py-1.5 bg-white dark:bg-slate-800 rounded border dark:border-slate-700 text-sm"
                  >
                    {student.url ? (
                      <a
                        href={student.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        {student.name}
                      </a>
                    ) : (
                      <span className="text-gray-700 dark:text-gray-300">{student.name}</span>
                    )}
                    {student.role && (
                      <span className="text-gray-500 dark:text-gray-400 ml-1">
                        ({student.role})
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Data Source Info */}
          <div className="pt-2 border-t dark:border-slate-700 text-xs text-gray-400 dark:text-gray-500">
            Data sources: {data_sources.join(", ")} • Last verified:{" "}
            {new Date(result.last_verified).toLocaleDateString()}
          </div>
        </div>
      )}
    </div>
  );
}
