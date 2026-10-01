import React, { useState, useEffect } from "react";
import { nlp } from "@/api/Client";

export default function RecommendationsSection({ book, chapters }) {
  const [selectedChapter, setSelectedChapter] = useState(
    chapters && chapters.length > 0 ? (chapters[0].chapter_num ?? chapters[0].chapter_number ?? "") : ""
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  const fetchRecommendations = async (chNum) => {
    if (!chNum) return;
    setLoading(true);
    setError("");
    setData(null);
    try {
      const num = parseInt(chNum, 10);
      const chObj = chapters.find(
        (c) => (c.chapter_num ?? c.chapter_number) === num
      );
      const res = await nlp.getRecommendations(book?.id, num, chObj?.id);
      if (res.status === "error") {
        setError(res.message || "Could not retrieve recommendations.");
      } else {
        setData(res);
      }
    } catch (e) {
      setError(e.message || "Failed to load educational resources.");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (selectedChapter) {
      fetchRecommendations(selectedChapter);
    }
  }, [selectedChapter]);

  const selectedChObj = chapters.find(
    (c) => String(c.chapter_num ?? c.chapter_number) === String(selectedChapter)
  );

  return (
    <div className="fade-in">
      <div className="ncert-page-header">
        <div>
          <h2 className="ncert-page-title">📺 Educational Video & Reference Recommendations</h2>
          <p className="ncert-page-subtitle">
            Advanced conceptual matching recommends high-impact explanatory videos, animated walkthroughs, and official NCERT reference materials tailored to difficult concepts in each chapter.
          </p>
        </div>
      </div>

      {/* Chapter Selector */}
      <div className="ncert-card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap", justifyContent: "space-between" }}>
          <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", flex: 1 }}>
            <span style={{ fontSize: 13, color: "#94a3b8", fontWeight: 600 }}>Active Chapter:</span>
            <select
              className="ncert-qg-select"
              style={{ minWidth: 260 }}
              value={selectedChapter}
              onChange={(e) => setSelectedChapter(e.target.value)}
            >
              <option value="">— Select Chapter —</option>
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
          <div>
            <button
              className="ncert-qg-btn"
              style={{ padding: "8px 20px" }}
              onClick={() => fetchRecommendations(selectedChapter)}
              disabled={loading}
            >
              {loading ? "Discovering…" : "🔍 Discover Resources"}
            </button>
          </div>
        </div>

        {error && (
          <div style={{ marginTop: 12, padding: "10px 14px", background: "#3b1717", border: "1px solid #7f1d1d", borderRadius: 6, color: "#fca5a5", fontSize: 13 }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      {loading ? (
        <div className="ncert-loading" style={{ height: 260 }}>
          <div className="ncert-spinner"></div>
          <p style={{ color: "#6b7db3", fontSize: 14 }}>Matching chapter concepts with educational videos & reference repositories…</p>
        </div>
      ) : !data ? (
        <div className="ncert-card" style={{ textAlign: "center", padding: "40px 20px", color: "#64748b" }}>
          Select a chapter to explore curated video lectures and official reference material.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          {/* Concepts Identified for Recommendation */}
          {data.concepts_covered && data.concepts_covered.length > 0 && (
            <div className="ncert-card" style={{ background: "#0c1020", border: "1px solid #1e2540", padding: "16px 20px" }}>
              <div style={{ fontSize: 12, color: "#94a3b8", fontWeight: 700, textTransform: "uppercase", marginBottom: 8 }}>
                Identified Concepts Targeted For Visual Learning
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {data.concepts_covered.map((concept, idx) => (
                  <span
                    key={idx}
                    style={{
                      background: "#1e293b",
                      border: "1px solid #334155",
                      padding: "4px 12px",
                      borderRadius: 16,
                      fontSize: 12,
                      color: "#38bdf8",
                      fontWeight: 500,
                    }}
                  >
                    ⚡ {concept}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Section 1: Video Recommendations */}
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: "#ffffff", marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
              <span>🎬</span> Curated Explanatory & Animation Videos
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 16 }}>
              {(data.video_recommendations || []).map((v, idx) => {
                // Prefer the real direct link the backend already resolved
                // (either a verified YouTube video URL, or an honest search
                // URL for the "Suggested Search" fallback) instead of
                // re-deriving one from a possibly-invented title/channel.
                const linkUrl =
                  v.url ||
                  `https://www.youtube.com/results?search_query=${encodeURIComponent(
                    v.search_query || `${v.title} ${v.channel}`
                  )}`;
                const isVerified = v.verified === true;

                return (
                  <div
                    key={idx}
                    className="ncert-card"
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "space-between",
                      borderTop: `3px solid ${isVerified ? "#ef4444" : "#64748b"}`,
                    }}
                  >
                    <div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                        <span
                          style={{
                            fontSize: 11,
                            background: isVerified ? "#2e1212" : "#1e293b",
                            color: isVerified ? "#f87171" : "#94a3b8",
                            padding: "2px 8px",
                            borderRadius: 4,
                            fontWeight: 600,
                          }}
                        >
                          {isVerified ? (v.type || "YouTube Video") : "Suggested Search (not a specific video)"}
                        </span>
                        {v.duration && (
                          <span style={{ fontSize: 11, color: "#94a3b8" }}>⏱️ {v.duration}</span>
                        )}
                      </div>

                      <h4 style={{ fontSize: 15, fontWeight: 600, color: "#ffffff", margin: "0 0 8px 0", lineHeight: 1.4 }}>
                        {v.title}
                      </h4>

                      {v.channel && (
                        <div style={{ fontSize: 12, color: "#38bdf8", fontWeight: 600, marginBottom: 8 }}>
                          📺 Channel: {v.channel}
                        </div>
                      )}

                      <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.5, margin: "0 0 16px 0" }}>
                        {v.description}
                      </p>
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: 12, borderTop: "1px solid #1e2540" }}>
                      <span style={{ fontSize: 11, color: "#a78bfa" }}>
                        Concept: <strong>{v.concept_tag || "General"}</strong>
                      </span>
                      <a
                        href={linkUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          background: isVerified ? "#ef4444" : "#334155",
                          color: "#ffffff",
                          padding: "6px 14px",
                          borderRadius: 6,
                          fontSize: 12,
                          fontWeight: 600,
                          textDecoration: "none",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 6,
                        }}
                      >
                        {isVerified ? "Watch Video ↗" : "Search YouTube ↗"}
                      </a>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section 2: Official Reference & Study Modules */}
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: "#ffffff", marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
              <span>📖</span> Official Reference Modules & Interactive Simulations
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
              {(data.reference_resources || []).map((ref, idx) => (
                <div
                  key={idx}
                  className="ncert-card"
                  style={{
                    background: "#0c1020",
                    border: "1px solid #1e2540",
                    borderLeft: "3px solid #34d399",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                    <span style={{ fontSize: 11, background: "#0b2b20", color: "#34d399", padding: "2px 8px", borderRadius: 4, fontWeight: 600 }}>
                      {ref.type || "Reference"}
                    </span>
                    <span style={{ fontSize: 11, color: "#64748b" }}>{ref.source}</span>
                  </div>
                  <h4 style={{ fontSize: 15, fontWeight: 600, color: "#ffffff", margin: "0 0 6px 0" }}>
                    {ref.title}
                  </h4>
                  <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.5, margin: "0 0 12px 0" }}>
                    {ref.description}
                  </p>
                  {ref.url && (
                    <a
                      href={ref.url.startsWith("http") ? ref.url : `https://${ref.url}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ fontSize: 12, color: "#34d399", fontWeight: 600, textDecoration: "none" }}
                    >
                      Open resource ↗
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}