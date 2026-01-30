"use client";

import { useState } from "react";
import { Search, X, Plus, ChevronDown, ChevronUp, SlidersHorizontal } from "lucide-react";

interface SearchFormProps {
  onSearch: (
    universities: string[],
    topics: string[],
    includeStudents: boolean,
    filters?: { yearFrom?: number; yearTo?: number; minCitations?: number }
  ) => void;
  isLoading: boolean;
}

const SUGGESTED_UNIVERSITIES = [
  "CMU", "MIT", "Stanford", "Berkeley", "Harvard",
  "Princeton", "Cornell", "UW", "Georgia Tech", "UIUC"
];

const SUGGESTED_TOPICS = [
  "LLM", "Machine Learning", "NLP", "Computer Vision",
  "Reinforcement Learning", "Robotics", "AI Safety"
];

const currentYear = new Date().getFullYear();

export default function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [universities, setUniversities] = useState<string[]>([]);
  const [topics, setTopics] = useState<string[]>([]);
  const [universityInput, setUniversityInput] = useState("");
  const [topicInput, setTopicInput] = useState("");
  const [includeStudents, setIncludeStudents] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Advanced filters
  const [yearFrom, setYearFrom] = useState<string>("");
  const [yearTo, setYearTo] = useState<string>("");
  const [minCitations, setMinCitations] = useState<string>("");

  const addUniversity = (uni: string) => {
    const trimmed = uni.trim();
    if (trimmed && !universities.includes(trimmed)) {
      setUniversities([...universities, trimmed]);
    }
    setUniversityInput("");
  };

  const removeUniversity = (uni: string) => {
    setUniversities(universities.filter((u) => u !== uni));
  };

  const addTopic = (topic: string) => {
    const trimmed = topic.trim();
    if (trimmed && !topics.includes(trimmed)) {
      setTopics([...topics, trimmed]);
    }
    setTopicInput("");
  };

  const removeTopic = (topic: string) => {
    setTopics(topics.filter((t) => t !== topic));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (universities.length > 0 && topics.length > 0) {
      const filters: { yearFrom?: number; yearTo?: number; minCitations?: number } = {};
      if (yearFrom) filters.yearFrom = parseInt(yearFrom);
      if (yearTo) filters.yearTo = parseInt(yearTo);
      if (minCitations) filters.minCitations = parseInt(minCitations);

      onSearch(universities, topics, includeStudents, Object.keys(filters).length > 0 ? filters : undefined);
    }
  };

  const handleKeyDown = (
    e: React.KeyboardEvent<HTMLInputElement>,
    type: "university" | "topic"
  ) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (type === "university" && universityInput) {
        addUniversity(universityInput);
      } else if (type === "topic" && topicInput) {
        addTopic(topicInput);
      }
    }
  };

  const hasActiveFilters = yearFrom || yearTo || minCitations;

  return (
    <form onSubmit={handleSubmit} className="bg-white dark:bg-dark-card rounded-xl shadow-lg p-6 space-y-6 border border-gray-200 dark:border-dark-border">
      {/* Universities Section */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Universities
        </label>
        <div className="flex flex-wrap gap-2 mb-2">
          {universities.map((uni) => (
            <span
              key={uni}
              className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 rounded-full text-sm"
            >
              {uni}
              <button
                type="button"
                onClick={() => removeUniversity(uni)}
                className="hover:bg-blue-200 dark:hover:bg-blue-800 rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={universityInput}
            onChange={(e) => setUniversityInput(e.target.value)}
            onKeyDown={(e) => handleKeyDown(e, "university")}
            placeholder="Add university (e.g., CMU, MIT)"
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="button"
            onClick={() => addUniversity(universityInput)}
            disabled={!universityInput}
            className="px-4 py-2 bg-gray-100 dark:bg-slate-700 hover:bg-gray-200 dark:hover:bg-slate-600 rounded-lg disabled:opacity-50"
          >
            <Plus className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-1">
          {SUGGESTED_UNIVERSITIES.filter((u) => !universities.includes(u)).slice(0, 5).map((uni) => (
            <button
              key={uni}
              type="button"
              onClick={() => addUniversity(uni)}
              className="text-xs px-2 py-1 bg-gray-50 dark:bg-slate-700 hover:bg-gray-100 dark:hover:bg-slate-600 text-gray-600 dark:text-gray-300 rounded border border-gray-200 dark:border-slate-600"
            >
              + {uni}
            </button>
          ))}
        </div>
      </div>

      {/* Topics Section */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Research Topics
        </label>
        <div className="flex flex-wrap gap-2 mb-2">
          {topics.map((topic) => (
            <span
              key={topic}
              className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300 rounded-full text-sm"
            >
              {topic}
              <button
                type="button"
                onClick={() => removeTopic(topic)}
                className="hover:bg-green-200 dark:hover:bg-green-800 rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={topicInput}
            onChange={(e) => setTopicInput(e.target.value)}
            onKeyDown={(e) => handleKeyDown(e, "topic")}
            placeholder="Add topic (e.g., LLM Memory, Context Engineering)"
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
          <button
            type="button"
            onClick={() => addTopic(topicInput)}
            disabled={!topicInput}
            className="px-4 py-2 bg-gray-100 dark:bg-slate-700 hover:bg-gray-200 dark:hover:bg-slate-600 rounded-lg disabled:opacity-50"
          >
            <Plus className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-1">
          {SUGGESTED_TOPICS.filter((t) => !topics.includes(t)).slice(0, 5).map((topic) => (
            <button
              key={topic}
              type="button"
              onClick={() => addTopic(topic)}
              className="text-xs px-2 py-1 bg-gray-50 dark:bg-slate-700 hover:bg-gray-100 dark:hover:bg-slate-600 text-gray-600 dark:text-gray-300 rounded border border-gray-200 dark:border-slate-600"
            >
              + {topic}
            </button>
          ))}
        </div>
      </div>

      {/* Advanced Filters Toggle */}
      <div>
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
        >
          <SlidersHorizontal className="w-4 h-4" />
          Advanced Filters
          {hasActiveFilters && (
            <span className="px-1.5 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 rounded">
              Active
            </span>
          )}
          {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showFilters && (
          <div className="mt-4 p-4 bg-gray-50 dark:bg-slate-800 rounded-lg space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Year Range */}
              <div>
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Year From
                </label>
                <input
                  type="number"
                  value={yearFrom}
                  onChange={(e) => setYearFrom(e.target.value)}
                  placeholder="2018"
                  min="1990"
                  max={currentYear}
                  className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-dark-border rounded-lg bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Year To
                </label>
                <input
                  type="number"
                  value={yearTo}
                  onChange={(e) => setYearTo(e.target.value)}
                  placeholder={currentYear.toString()}
                  min="1990"
                  max={currentYear}
                  className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-dark-border rounded-lg bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                />
              </div>
              {/* Min Citations */}
              <div>
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                  Min Citations
                </label>
                <input
                  type="number"
                  value={minCitations}
                  onChange={(e) => setMinCitations(e.target.value)}
                  placeholder="0"
                  min="0"
                  className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-dark-border rounded-lg bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
            {hasActiveFilters && (
              <button
                type="button"
                onClick={() => {
                  setYearFrom("");
                  setYearTo("");
                  setMinCitations("");
                }}
                className="text-xs text-red-600 dark:text-red-400 hover:underline"
              >
                Clear all filters
              </button>
            )}
          </div>
        )}
      </div>

      {/* Options */}
      <div className="flex items-start gap-2">
        <input
          type="checkbox"
          id="includeStudents"
          checked={includeStudents}
          onChange={(e) => setIncludeStudents(e.target.checked)}
          className="w-4 h-4 mt-0.5 text-blue-600 rounded focus:ring-blue-500 dark:bg-slate-700 dark:border-slate-600"
        />
        <div>
          <label htmlFor="includeStudents" className="text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
            Include students (scrapes lab pages - slower)
          </label>
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || universities.length === 0 || topics.length === 0}
        className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Searching All Papers...
          </>
        ) : (
          <>
            <Search className="w-5 h-5" />
            Search Papers
          </>
        )}
      </button>

      <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
        Searches all available papers from Semantic Scholar and OpenAlex with full pagination.
      </p>
    </form>
  );
}
