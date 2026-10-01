import React from "react";

const NAV_ITEMS = [
  { id: "upload", icon: "📤", label: "Upload Textbook" },
  { id: "overview", icon: "📊", label: "Overview" },
  { id: "summary", icon: "📝", label: "Hybrid Summarizer" },
  { id: "difficult-words", icon: "📚", label: "Difficult Words" },
  { id: "keywords", icon: "☁️", label: "Word Cloud" },
  { id: "chapter-analysis", icon: "🔬", label: "Chapter NLP" },
  { id: "quiz", icon: "🎯", label: "Quiz Mode" },
  { id: "recommendations", icon: "📺", label: "Recommendations" },
  { id: "chat", icon: "💬", label: "AI Chat" },
  { id: "chapters", icon: "📖", label: "Chapters" },
  { id: "search", icon: "🔍", label: "Semantic Search" },
];

export default function Sidebar({ activeSection, setActiveSection, books, selectedBookId, onSelectBook }) {
  return (
    <aside className="ncert-sidebar">
      <div className="ncert-sidebar-logo">
        <h1>NCERT Learning Platform</h1>
        <p>Hybrid Hindi NLP Dashboard</p>
      </div>

      {books && books.length > 1 && (
        <div className="ncert-book-selector">
          <label className="ncert-book-selector-label">Active Textbook</label>
          <select
            className="ncert-book-selector-select"
            value={selectedBookId || ""}
            onChange={(e) => onSelectBook && onSelectBook(e.target.value)}
          >
            {books.map((b) => (
              <option key={b.id || b.book_id} value={b.id || b.book_id}>
                {b.title}{b.class_level ? ` · Cl ${b.class_level}` : ""}
              </option>
            ))}
          </select>
        </div>
      )}

      <nav className="ncert-nav">
        {NAV_ITEMS.map((item) => (
          <div
            key={item.id}
            className={`ncert-nav-item ${activeSection === item.id ? "active" : ""}`}
            onClick={() => setActiveSection(item.id)}
          >
            <span className="ncert-nav-icon">{item.icon}</span>
            {item.label}
          </div>
        ))}
      </nav>
      <div className="ncert-model-bar">
        <div className="st">Model Status</div>
        <div className="ncert-sdot">
          <span className="ncert-dot on"></span>
          <span>Hybrid Hindi MBart-50</span>
        </div>
        <div className="ncert-sdot">
          <span className="ncert-dot on"></span>
          <span>Groq Merge + RAG</span>
        </div>
        <div className="ncert-sdot">
          <span className="ncert-dot on"></span>
          <span>FAISS Chapter Retrieval</span>
        </div>
      </div>
    </aside>
  );
}
