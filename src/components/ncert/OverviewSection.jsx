import React from "react";

const FEATURES = [
  { id: "summary", icon: "📝", title: "Hybrid Summarizer", desc: "AlbertTokenizer + MBart-50 with Groq merge, one chapter at a time, Hindi / English / Marathi." },
  { id: "difficult-words", icon: "📚", title: "Difficult Words", desc: "Uncommon vocabulary with simple definitions, synonyms, examples, and Hindi/Marathi meanings." },
  { id: "keywords", icon: "☁️", title: "Dense Word Cloud", desc: "Concept-weighted cloud from TF-IDF, noun phrases, and entity prominence — no frequency bars." },
  { id: "chapter-analysis", icon: "🔬", title: "Chapter NLP", desc: "Actual named entities (persons, places, organizations, dates) plus named topics and concepts." },
  { id: "quiz", icon: "🎯", title: "Quiz Mode", desc: "MCQ, True/False, fill-in-the-blanks, and short answers with instant scoring and explanations." },
  { id: "recommendations", icon: "📺", title: "Study Videos", desc: "NCERT, Khan Academy, and reference links matched to the chapter’s difficult concepts." },
  { id: "chat", icon: "💬", title: "Multilingual RAG Chat", desc: "Ask questions grounded only in this NCERT chapter, in English, Hindi, or Marathi." },
];

export default function OverviewSection({ book, chapters, setActiveSection }) {
  const totalWords = chapters.reduce((s, c) => s + (c.word_count || 0), 0);

  const stats = [
    { label: "Chapters", value: chapters.length },
    { label: "Total Words", value: totalWords.toLocaleString("en-IN") },
    { label: "Class", value: book?.class_level || "—" },
    { label: "Subject", value: book?.subject || "—" },
    { label: "Language", value: book?.language === "hi" ? "Hindi" : book?.language === "mr" ? "Marathi" : "English" },
  ];

  return (
    <div className="fade-in">
      <div className="ncert-page-header">
        <div>
          <h2 className="ncert-page-title">{book?.title || "NCERT Textbook"}</h2>
          <p className="ncert-page-subtitle">
            {book?.subject} · Class {book?.class_level} · Hybrid Hindi Summarizer + Advanced NLP Learning Suite
          </p>
        </div>
      </div>

      <div className="ncert-stats-row">
        {stats.map((s, i) => (
          <div className="ncert-stat-card" key={i}>
            <div className="ncert-stat-value">{s.value}</div>
            <div className="ncert-stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="ncert-card">
        <div className="ncert-card-title">
          <span className="ncert-card-title-dot" style={{ background: "#06b6d4" }}></span> Textbook Snapshot
        </div>
        <p className="ncert-summary-box">
          {book?.overall_summary || "Upload or select a textbook to unlock chapter-wise hybrid summaries, vocabulary, quizzes, and RAG chat."}
        </p>
      </div>

      <div className="ncert-card" style={{ marginTop: 20 }}>
        <div className="ncert-card-title">
          <span className="ncert-card-title-dot"></span> Learning Suite
        </div>
        <p style={{ color: "#94a3b8", fontSize: 13, marginBottom: 16 }}>
          Word-frequency bar charts have been removed. Use these chapter-wise tools instead.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 14 }}>
          {FEATURES.map((f) => (
            <button
              key={f.id}
              type="button"
              onClick={() => setActiveSection && setActiveSection(f.id)}
              style={{
                textAlign: "left",
                background: "#0c1020",
                border: "1px solid #1e2540",
                borderRadius: 10,
                padding: "16px 16px",
                cursor: "pointer",
                color: "inherit",
              }}
            >
              <div style={{ fontSize: 18, marginBottom: 8 }}>{f.icon} {f.title}</div>
              <div style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.5 }}>{f.desc}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
