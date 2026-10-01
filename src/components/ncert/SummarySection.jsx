import React, { useEffect, useState } from "react";
import { nlp } from "@/api/Client";

export default function SummarySection({ chapters, book }) {
  const [selectedChapter, setSelectedChapter] = useState(
    chapters && chapters.length > 0 ? (chapters[0].chapter_num ?? chapters[0].chapter_number ?? "") : ""
  );
  const [language, setLanguage] = useState("hi");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const bookLanguage = book?.language?.toLowerCase();
    if (["en", "hi", "mr"].includes(bookLanguage)) {
      setLanguage(bookLanguage);
    }
  }, [book?.language]);

  const handleSummarize = async () => {
    if (!selectedChapter) {
      setError("Please select a chapter to summarize.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const chNum = parseInt(selectedChapter, 10);
      const chObj = chapters.find(
        (c) => (c.chapter_num ?? c.chapter_number) === chNum
      );
      const data = await nlp.summarize(book?.id, chNum, language, chObj?.id);
      if (data.status === "error") {
        setError(data.message || "Failed to generate summary.");
      } else {
        setResult(data);
      }
    } catch (e) {
      setError(e.message || "An error occurred while generating the summary.");
    }
    setLoading(false);
  };

  const selectedChObj = chapters.find(
    (c) => String(c.chapter_num ?? c.chapter_number) === String(selectedChapter)
  );

  return (
    <div className="fade-in">
      <div className="ncert-page-header">
        <div>
          <h2 className="ncert-page-title">📝 Chapter-wise Summarizer</h2>
          <p className="ncert-page-subtitle">
            English chapters use semantic extractive summarization. Hindi chapters use the fine-tuned Hindi model, with English/Hindi translation when you choose another output language.
          </p>
        </div>
      </div>

      {/* Control Card */}
      <div className="ncert-card" style={{ marginBottom: 24 }}>
        <div className="ncert-card-title">
          <span className="ncert-card-title-dot"></span> Select Chapter & Target Language
        </div>

        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "center" }}>
          {/* Chapter Selector */}
          <div style={{ flex: 2, minWidth: 260 }}>
            <label style={{ display: "block", fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
              Chapter (1 at a time)
            </label>
            <select
              className="ncert-qg-select"
              style={{ width: "100%" }}
              value={selectedChapter}
              onChange={(e) => {
                setSelectedChapter(e.target.value);
                setResult(null);
                setError("");
              }}
            >
              <option value="">— Select a Chapter —</option>
              {chapters.map((ch) => {
                const num = ch.chapter_num ?? ch.chapter_number ?? 1;
                return (
                  <option key={ch.id || num} value={num}>
                    Chapter {num}: {ch.title}
                  </option>
                );
              })}
            </select>
          </div>

          {/* Language Selector */}
          <div style={{ flex: 1, minWidth: 180 }}>
            <label style={{ display: "block", fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
              Output Language
            </label>
            <div style={{ display: "flex", gap: 6 }}>
              {[
                { code: "hi", label: "हिंदी (Hindi)" },
                { code: "mr", label: "मराठी (Marathi)" },
                { code: "en", label: "English" },
              ].map((l) => (
                <button
                  key={l.code}
                  type="button"
                  onClick={() => setLanguage(l.code)}
                  style={{
                    flex: 1,
                    padding: "8px 10px",
                    borderRadius: 6,
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                    border: "1px solid",
                    background: language === l.code ? "#4f6ef7" : "#1a2035",
                    borderColor: language === l.code ? "#6366f1" : "#2d3748",
                    color: language === l.code ? "#ffffff" : "#94a3b8",
                    transition: "all 0.2s ease",
                  }}
                >
                  {l.label}
                </button>
              ))}
            </div>
          </div>

          {/* Action Button */}
          <div style={{ flex: "0 0 auto", alignSelf: "flex-end" }}>
            <button
              className="ncert-qg-btn"
              style={{ padding: "10px 28px", minWidth: 190 }}
              onClick={handleSummarize}
              disabled={loading}
            >
              {loading ? "⏳ Generating Summary…" : "✨ Generate Chapter Summary"}
            </button>
          </div>
        </div>

        {error && (
          <div style={{ marginTop: 14, padding: "10px 14px", background: "#3b1717", border: "1px solid #7f1d1d", borderRadius: 6, color: "#fca5a5", fontSize: 13 }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Model Info Badges */}
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 24 }}>
        <div style={{ background: "#131728", border: "1px solid #1e2540", padding: "8px 14px", borderRadius: 8, fontSize: 12, color: "#94a3b8" }}>
          🚀 <strong>Engine:</strong> Language-aware summary pipeline
        </div>
        <div style={{ background: "#131728", border: "1px solid #1e2540", padding: "8px 14px", borderRadius: 8, fontSize: 12, color: "#94a3b8" }}>
          ⚡ <strong>English:</strong> Semantic extractive summary
        </div>
        <div style={{ background: "#131728", border: "1px solid #1e2540", padding: "8px 14px", borderRadius: 8, fontSize: 12, color: "#34d399" }}>
          ✅ <strong>Hindi:</strong> Fine-tuned MBart summarizer
        </div>
        <div style={{ background: "#131728", border: "1px solid #1e2540", padding: "8px 14px", borderRadius: 8, fontSize: 12, color: "#60a5fa" }}>
          📖 <strong>Processing:</strong> 1 Chapter At A Time
        </div>
      </div>

      {/* Summary Output */}
      {result && (
        <div className="ncert-card" style={{ borderLeft: "4px solid #4f6ef7" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, flexWrap: "wrap", gap: 8 }}>
            <div className="ncert-card-title" style={{ margin: 0 }}>
              <span className="ncert-card-title-dot" style={{ background: "#4f6ef7" }}></span>
              {result.chapter_title || selectedChObj?.title || `Chapter ${selectedChapter}`} — Summary
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <span className="ncert-source-badge ncert-badge-model">
                Chunks: {result.chunks_used} / {result.chunks_total}
              </span>
              <span className="ncert-source-badge ncert-badge-llm">
                {result.language === "hi" ? "हिंदी" : result.language === "mr" ? "मराठी" : "English"}
              </span>
            </div>
          </div>

          <div
            style={{
              lineHeight: 1.8,
              fontSize: 15,
              color: "#e2e8f0",
              whiteSpace: "pre-line",
              background: "#0c1020",
              padding: "20px 24px",
              borderRadius: 8,
              border: "1px solid #1e2540",
            }}
          >
            {result.summary}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16, fontSize: 12, color: "#64748b" }}>
            <span>Pipeline: Source-language summary → Optional English/Hindi translation</span>
            <span>Mode: {result.mode}</span>
          </div>
        </div>
      )}
    </div>
  );
}