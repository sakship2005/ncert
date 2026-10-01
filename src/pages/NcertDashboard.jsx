import React, { useState, useEffect } from "react";
import { books as booksApi, chapters as chaptersApi } from "@/api/Client";
import Sidebar from "@/components/ncert/Sidebar";
import OverviewSection from "@/components/ncert/OverviewSection";
import KeywordsSection from "@/components/ncert/KeywordsSection";
import ChaptersSection from "@/components/ncert/ChaptersSection";
import SummarySection from "@/components/ncert/SummarySection";
import SemanticSearchSection from "@/components/ncert/SemanticSearchSection";
import ChatSection from "@/components/ncert/ChatSection";
import UploadSection from "@/components/ncert/UploadSection";
import EmptyState from "@/components/ncert/EmptyState";
import DifficultWordsSection from "@/components/ncert/DifficultWordsSection";
import ChapterAnalysisSection from "@/components/ncert/ChapterAnalysisSection";
import QuizSection from "@/components/ncert/QuizSection";
import RecommendationsSection from "@/components/ncert/RecommendationsSection";

export default function NcertDashboard() {
  const [activeSection, setActiveSection] = useState("upload");
  const [booksList, setBooksList] = useState([]);
  const [selectedBookId, setSelectedBookId] = useState(null);
  const [book, setBook] = useState(null);
  const [chaptersList, setChaptersList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [backendWarning, setBackendWarning] = useState("");

  async function loadChaptersFor(bookId) {
    if (!bookId) { setChaptersList([]); return; }
    const chs = await chaptersApi.listByBook(bookId);
    chs.sort((a, b) => (a.chapter_num || a.chapter_number || 0) - (b.chapter_num || b.chapter_number || 0));
    setChaptersList(chs);
  }

  useEffect(() => {
    async function loadData() {
      try {
        const allBooks = await booksApi.list();
        setBooksList(allBooks);
        if (allBooks.length === 0) {
          setActiveSection("upload");
          setLoading(false);
          return;
        }
        const b = allBooks[0];
        setSelectedBookId(b.id || b.book_id);
        setBook(b);
        await loadChaptersFor(b.id || b.book_id);
      } catch (e) {
        console.warn("Backend unreachable on startup:", e.message);
        setActiveSection("upload");
        setBackendWarning(e.message);
      }
      setLoading(false);
    }
    loadData();
  }, []);

  async function handleSelectBook(bookId) {
    const b = booksList.find((x) => (x.id || x.book_id) === bookId);
    if (!b) return;
    setSelectedBookId(bookId);
    setBook(b);
    await loadChaptersFor(bookId);
    if (activeSection === "upload") setActiveSection("overview");
  }

  async function handleBookAdded(bookId) {
    const allBooks = await booksApi.list();
    setBooksList(allBooks);
    const b = allBooks.find((x) => (x.id || x.book_id) === bookId);
    if (b) {
      setSelectedBookId(b.id || b.book_id);
      setBook(b);
      await loadChaptersFor(b.id || b.book_id);
      setActiveSection("overview");
    }
  }

  if (loading) {
    return (
      <div className="ncert-app">
        <div className="ncert-loading">
          <div className="ncert-spinner"></div>
          <p style={{ fontSize: 14, color: "#6b7db3" }}>Loading textbook…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ncert-app">
      {(error || backendWarning) && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, zIndex: 999,
          background: "#2d1a1a", borderBottom: "1px solid #7f1d1d",
          padding: "10px 24px", display: "flex", alignItems: "center", gap: 12,
          fontSize: 13, color: "#fca5a5",
        }}>
          <span>⚠️</span>
          <span>
            Backend not reachable ({error || backendWarning}). Start your FastAPI server on{" "}
            <code style={{ background: "#1a0a0a", padding: "1px 6px", borderRadius: 4 }}>
              localhost:8000
            </code>{" "}
            — the UI is still browsable.
          </span>
        </div>
      )}
      <div className="ncert-content" style={(error || backendWarning) ? { paddingTop: 44 } : {}}>
        <Sidebar
          activeSection={activeSection}
          setActiveSection={setActiveSection}
          books={booksList}
          selectedBookId={selectedBookId}
          onSelectBook={handleSelectBook}
        />
        <main className="ncert-main">
          {activeSection === "upload" && <UploadSection onBookAdded={handleBookAdded} />}
          {activeSection !== "upload" && !book && <EmptyState onUpload={() => setActiveSection("upload")} />}
          {activeSection === "overview" && book && (
            <OverviewSection book={book} chapters={chaptersList} setActiveSection={setActiveSection} />
          )}
          {activeSection === "difficult-words" && book && (
            <DifficultWordsSection book={book} chapters={chaptersList} />
          )}
          {activeSection === "keywords" && book && (
            <KeywordsSection book={book} chapters={chaptersList} />
          )}
          {activeSection === "chapter-analysis" && book && (
            <ChapterAnalysisSection book={book} chapters={chaptersList} />
          )}
          {activeSection === "quiz" && book && (
            <QuizSection book={book} chapters={chaptersList} />
          )}
          {activeSection === "recommendations" && book && (
            <RecommendationsSection book={book} chapters={chaptersList} />
          )}
          {activeSection === "chapters" && book && <ChaptersSection chapters={chaptersList} />}
          {activeSection === "summary" && book && <SummarySection chapters={chaptersList} book={book} />}
          {activeSection === "search" && book && <SemanticSearchSection book={book} />}
          {activeSection === "chat" && book && <ChatSection book={book} chapters={chaptersList} />}
        </main>
      </div>
    </div>
  );
}
