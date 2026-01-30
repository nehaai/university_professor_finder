import { ProfessorResult, PaperResult } from "./types";

const PROFESSOR_BOOKMARKS_KEY = "professor_bookmarks";
const PAPER_BOOKMARKS_KEY = "paper_bookmarks";

export interface BookmarkedProfessor extends ProfessorResult {
  bookmarkedAt: string;
}

export interface BookmarkedPaper extends PaperResult {
  bookmarkedAt: string;
}

// Professor bookmarks
export function getProfessorBookmarks(): BookmarkedProfessor[] {
  if (typeof window === "undefined") return [];
  const stored = localStorage.getItem(PROFESSOR_BOOKMARKS_KEY);
  if (!stored) return [];
  try {
    return JSON.parse(stored);
  } catch {
    return [];
  }
}

export function addProfessorBookmark(professor: ProfessorResult): void {
  const bookmarks = getProfessorBookmarks();
  const exists = bookmarks.some(
    (b) => b.professor.name === professor.professor.name &&
           b.professor.university === professor.professor.university
  );
  if (!exists) {
    bookmarks.push({
      ...professor,
      bookmarkedAt: new Date().toISOString(),
    });
    localStorage.setItem(PROFESSOR_BOOKMARKS_KEY, JSON.stringify(bookmarks));
  }
}

export function removeProfessorBookmark(name: string, university: string): void {
  const bookmarks = getProfessorBookmarks();
  const filtered = bookmarks.filter(
    (b) => !(b.professor.name === name && b.professor.university === university)
  );
  localStorage.setItem(PROFESSOR_BOOKMARKS_KEY, JSON.stringify(filtered));
}

export function isProfessorBookmarked(name: string, university: string): boolean {
  return getProfessorBookmarks().some(
    (b) => b.professor.name === name && b.professor.university === university
  );
}

// Paper bookmarks
export function getPaperBookmarks(): BookmarkedPaper[] {
  if (typeof window === "undefined") return [];
  const stored = localStorage.getItem(PAPER_BOOKMARKS_KEY);
  if (!stored) return [];
  try {
    return JSON.parse(stored);
  } catch {
    return [];
  }
}

export function addPaperBookmark(paper: PaperResult): void {
  const bookmarks = getPaperBookmarks();
  const exists = bookmarks.some(
    (b) => b.publication.title === paper.publication.title
  );
  if (!exists) {
    bookmarks.push({
      ...paper,
      bookmarkedAt: new Date().toISOString(),
    });
    localStorage.setItem(PAPER_BOOKMARKS_KEY, JSON.stringify(bookmarks));
  }
}

export function removePaperBookmark(title: string): void {
  const bookmarks = getPaperBookmarks();
  const filtered = bookmarks.filter((b) => b.publication.title !== title);
  localStorage.setItem(PAPER_BOOKMARKS_KEY, JSON.stringify(filtered));
}

export function isPaperBookmarked(title: string): boolean {
  return getPaperBookmarks().some((b) => b.publication.title === title);
}

// Export all bookmarks
export function exportBookmarks(): string {
  const professors = getProfessorBookmarks();
  const papers = getPaperBookmarks();
  return JSON.stringify({ professors, papers }, null, 2);
}

// Clear all bookmarks
export function clearAllBookmarks(): void {
  localStorage.removeItem(PROFESSOR_BOOKMARKS_KEY);
  localStorage.removeItem(PAPER_BOOKMARKS_KEY);
}
