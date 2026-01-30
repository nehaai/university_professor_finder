"use client";

import { useState, useEffect } from "react";
import { X, Bookmark, BookOpen, Trash2, Download, Users } from "lucide-react";
import {
  getProfessorBookmarks,
  getPaperBookmarks,
  removeProfessorBookmark,
  removePaperBookmark,
  exportBookmarks,
  BookmarkedProfessor,
  BookmarkedPaper,
} from "@/lib/bookmarks";

interface BookmarksPanelProps {
  onClose: () => void;
}

type TabType = "professors" | "papers";

export default function BookmarksPanel({ onClose }: BookmarksPanelProps) {
  const [activeTab, setActiveTab] = useState<TabType>("professors");
  const [professors, setProfessors] = useState<BookmarkedProfessor[]>([]);
  const [papers, setPapers] = useState<BookmarkedPaper[]>([]);

  useEffect(() => {
    setProfessors(getProfessorBookmarks());
    setPapers(getPaperBookmarks());
  }, []);

  const handleRemoveProfessor = (name: string, university: string) => {
    removeProfessorBookmark(name, university);
    setProfessors(getProfessorBookmarks());
  };

  const handleRemovePaper = (title: string) => {
    removePaperBookmark(title);
    setPapers(getPaperBookmarks());
  };

  const handleExport = () => {
    const data = exportBookmarks();
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `research-bookmarks-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const totalBookmarks = professors.length + papers.length;

  return (
    <div className="bg-white dark:bg-dark-card rounded-xl shadow-lg border border-gray-200 dark:border-dark-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-dark-border">
        <div className="flex items-center gap-2">
          <Bookmark className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="font-semibold text-gray-900 dark:text-white">
            Saved Items ({totalBookmarks})
          </h2>
        </div>
        <div className="flex items-center gap-2">
          {totalBookmarks > 0 && (
            <button
              onClick={handleExport}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 text-gray-600 dark:text-gray-300"
              title="Export bookmarks"
            >
              <Download className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700 text-gray-600 dark:text-gray-300"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-dark-border">
        <button
          onClick={() => setActiveTab("professors")}
          className={`flex-1 py-3 px-4 text-sm font-medium flex items-center justify-center gap-2 ${
            activeTab === "professors"
              ? "text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400"
              : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          <Users className="w-4 h-4" />
          Professors ({professors.length})
        </button>
        <button
          onClick={() => setActiveTab("papers")}
          className={`flex-1 py-3 px-4 text-sm font-medium flex items-center justify-center gap-2 ${
            activeTab === "papers"
              ? "text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400"
              : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          <BookOpen className="w-4 h-4" />
          Papers ({papers.length})
        </button>
      </div>

      {/* Content */}
      <div className="max-h-64 overflow-y-auto p-4">
        {activeTab === "professors" && (
          <>
            {professors.length === 0 ? (
              <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                No professors bookmarked yet
              </p>
            ) : (
              <div className="space-y-2">
                {professors.map((result) => (
                  <div
                    key={`${result.professor.name}-${result.professor.university}`}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-slate-800 rounded-lg"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 dark:text-white truncate">
                        {result.professor.name}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                        {result.professor.university}
                        {result.professor.department && ` • ${result.professor.department}`}
                      </p>
                    </div>
                    <button
                      onClick={() =>
                        handleRemoveProfessor(
                          result.professor.name,
                          result.professor.university
                        )
                      }
                      className="p-2 text-gray-400 hover:text-red-500 dark:hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {activeTab === "papers" && (
          <>
            {papers.length === 0 ? (
              <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                No papers bookmarked yet
              </p>
            ) : (
              <div className="space-y-2">
                {papers.map((result) => (
                  <div
                    key={result.publication.title}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-slate-800 rounded-lg"
                  >
                    <div className="flex-1 min-w-0">
                      {result.publication.url ? (
                        <a
                          href={result.publication.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-blue-600 dark:text-blue-400 hover:underline truncate block"
                        >
                          {result.publication.title}
                        </a>
                      ) : (
                        <p className="font-medium text-gray-900 dark:text-white truncate">
                          {result.publication.title}
                        </p>
                      )}
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {result.publication.year && `${result.publication.year} • `}
                        {result.publication.citation_count !== undefined &&
                          `${result.publication.citation_count} citations`}
                      </p>
                    </div>
                    <button
                      onClick={() => handleRemovePaper(result.publication.title)}
                      className="p-2 text-gray-400 hover:text-red-500 dark:hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
