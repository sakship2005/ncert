import React from "react";
import { useNavigate } from "react-router-dom";

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
  const navigate = useNavigate();
  return (
    <aside className="ncert-sidebar" style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
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

      <style>{`
        .ncert-nav::-webkit-scrollbar { width: 3px; }
        .ncert-nav::-webkit-scrollbar-track { background: transparent; }
        .ncert-nav::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }
        .ncert-nav::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }
      `}</style>
      <nav className="ncert-nav" style={{ flex: 1, overflowY: "auto", overflowX: "hidden", scrollbarWidth: "thin", scrollbarColor: "rgba(255,255,255,0.08) transparent" }}>
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

      <button
        onClick={() => navigate("/")}
        style={{
          margin: "12px 16px 20px",
          width: "calc(100% - 32px)",
          padding: "10px 0",
          borderRadius: 8,
          border: "1px solid rgba(239,68,68,0.35)",
          background: "rgba(239,68,68,0.08)",
          color: "#f87171",
          fontSize: 13,
          fontWeight: 600,
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
          transition: "background 0.2s",
        }}
        onMouseEnter={e => e.currentTarget.style.background = "rgba(239,68,68,0.18)"}
        onMouseLeave={e => e.currentTarget.style.background = "rgba(239,68,68,0.08)"}
      >
        ← Back to Home
      </button>
    </aside>
  );
}