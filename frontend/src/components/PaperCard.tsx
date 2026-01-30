"use client";

import { ExternalLink, BookOpen, Users, Mail, GraduationCap } from "lucide-react";
import { PaperResult } from "@/lib/types";

interface PaperCardProps {
  paper: PaperResult;
}

export default function PaperCard({ paper }: PaperCardProps) {
  const { publication, matching_topics, relevance_score } = paper;

  const relevanceColor =
    relevance_score >= 0.7
      ? "bg-green-100 text-green-800"
      : relevance_score >= 0.4
      ? "bg-yellow-100 text-yellow-800"
      : "bg-gray-100 text-gray-800";

  const authorCount = publication.authors?.length || 0;
  const shouldScroll = authorCount > 10;

  // Count professors (authors with university affiliation)
  const professorCount = publication.authors?.filter(a => a.university).length || 0;

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          {/* Title */}
          <div className="flex items-start gap-2">
            <BookOpen className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            {publication.url ? (
              <a
                href={publication.url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-blue-600 hover:underline text-base"
              >
                {publication.title}
                <ExternalLink className="w-3 h-3 inline ml-1" />
              </a>
            ) : (
              <span className="font-medium text-gray-900 text-base">{publication.title}</span>
            )}
          </div>

          {/* Metadata */}
          <div className="text-sm text-gray-500 mt-2 ml-7">
            {publication.venue && <span className="font-medium">{publication.venue}</span>}
            {publication.year && <span> ({publication.year})</span>}
            {publication.citation_count !== undefined && publication.citation_count > 0 && (
              <span className="ml-2 text-gray-600">• {publication.citation_count} citations</span>
            )}
          </div>

          {/* Authors - with professor tags */}
          {publication.authors && publication.authors.length > 0 && (
            <div className="mt-3 ml-7 p-3 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center gap-2 mb-2">
                <Users className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">
                  Authors ({authorCount})
                </span>
                {professorCount > 0 && (
                  <span className="text-xs text-purple-600 flex items-center gap-1">
                    <GraduationCap className="w-3 h-3" />
                    {professorCount} professor{professorCount > 1 ? 's' : ''} from selected universities
                  </span>
                )}
                {shouldScroll && (
                  <span className="text-xs text-gray-400 italic">(scroll to see all)</span>
                )}
              </div>
              <div
                className={`flex flex-wrap gap-2 ${
                  shouldScroll ? "max-h-32 overflow-y-auto pr-2" : ""
                }`}
                style={shouldScroll ? { scrollbarWidth: "thin" } : {}}
              >
                {publication.authors.map((author, idx) => {
                  const isProfessor = !!author.university;

                  return (
                    <div
                      key={idx}
                      className={`inline-flex items-center gap-1 px-2 py-1 rounded border ${
                        isProfessor
                          ? "bg-purple-50 border-purple-200"
                          : "bg-white border-gray-200"
                      }`}
                    >
                      {author.url ? (
                        <a
                          href={author.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`text-sm hover:underline font-medium ${
                            isProfessor ? "text-purple-700" : "text-gray-700"
                          }`}
                        >
                          {author.name}
                        </a>
                      ) : (
                        <span className={`text-sm font-medium ${
                          isProfessor ? "text-purple-700" : "text-gray-700"
                        }`}>
                          {author.name}
                        </span>
                      )}
                      {author.university && (
                        <span className="text-xs bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded font-medium">
                          Prof @ {author.university}
                        </span>
                      )}
                      {author.email && (
                        <a
                          href={`mailto:${author.email}`}
                          className="text-purple-500 hover:text-purple-700"
                          title={author.email}
                        >
                          <Mail className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Topics */}
          {matching_topics.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-3 ml-7">
              {matching_topics.map((topic) => (
                <span
                  key={topic}
                  className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded"
                >
                  {topic}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Badges */}
        <div className="flex flex-col gap-1 items-end">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${relevanceColor}`}>
            {Math.round(relevance_score * 100)}% match
          </span>
          <span className="text-xs px-2 py-1 bg-gray-100 rounded whitespace-nowrap">
            {publication.source}
          </span>
        </div>
      </div>
    </div>
  );
}
