import React, { useState, useEffect } from "react";
import { nlp } from "@/api/Client";

export default function ChapterAnalysisSection({ book, chapters }) {
  const [selectedChapter, setSelectedChapter] = useState(
    chapters && chapters.length > 0 ? (chapters[0].chapter_num ?? chapters[0].chapter_number ?? "") : ""
  );
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchChapterAnalysis = async (chNum) => {
    if (!chNum) return;
    setLoading(true);
    setError("");
    setAnalysis(null);
    try {
      const num = parseInt(chNum, 10);
      const chObj = chapters.find(
        (c) => (c.chapter_num ?? c.chapter_number) === num
      );
      const data = await nlp.getChapterAnalysis(book?.id, num, chObj?.id);
      if (data.status === "error") {
        setError(data.message || "Failed to load chapter analysis.");
      } else {
        setAnalysis(data);
      }
    } catch (e) {
      setError(e.message || "Error analyzing chapter.");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (selectedChapter) {
      fetchChapterAnalysis(selectedChapter);
    }
  }, [selectedChapter]);

  const selectedChObj = chapters.find(
    (c) => String(c.chapter_num ?? c.chapter_number) === String(selectedChapter)
  );

  const entities = analysis?.entities || {};
  const persons = entities.persons || [];
  const locations = entities.locations || [];
  const organizations = entities.organizations || [];
  const dates = entities.dates || [];
  const concepts = analysis?.concepts || [];
  const topics = analysis?.topics || [];

  return (
    <div className="fade-in">
      <div className="ncert-page-header">
        <div>
          <h2 className="ncert-page-title">🔬 Chapter-wise Detailed NLP Analysis</h2>
          <p className="ncert-page-subtitle">
            Deep linguistic extraction identifying <strong>actual names</strong> for Named Entities (Persons, Locations, Organizations, Dates) and key concepts/topics rather than only displaying statistical numbers.
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
              <option value="">— Choose Chapter —</option>
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
              style={{ padding: "8px 18px" }}
              onClick={() => fetchChapterAnalysis(selectedChapter)}
              disabled={loading}
            >
              {loading ? "Analyzing…" : "🔄 Re-Analyze"}
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
          <p style={{ color: "#6b7db3", fontSize: 14 }}>Extracting named entities, topics, and conceptual relationships…</p>
        </div>
      ) : !analysis ? (
        <div className="ncert-card" style={{ textAlign: "center", padding: "40px 20px", color: "#64748b" }}>
          Please select a chapter to view its detailed NLP breakdown.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          {/* Section 1: Named Entities with Actual Names */}
          <div className="ncert-card">
            <div className="ncert-card-title">
              <span className="ncert-card-title-dot" style={{ background: "#7c3aed" }}></span>
              Named Entities (Actual Names & Mentions)
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16, marginTop: 12 }}>
              {/* Persons */}
              <div style={{ background: "#0c1020", border: "1px solid #1e2540", borderRadius: 8, padding: 14 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: "#a78bfa", marginBottom: 10, display: "flex", alignItems: "center", gap: 6 }}>
                  <span>👤</span> PERSONS & CHARACTERS ({persons.length})
                </div>
                {persons.length === 0 ? (
                  <div style={{ fontSize: 12, color: "#64748b" }}>None detected in text.</div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {persons.map((p, idx) => (
                      <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 13, background: "#131728", padding: "6px 10px", borderRadius: 6 }}>
                        <span style={{ color: "#ffffff", fontWeight: 500 }}>{p.name}</span>
                        <span style={{ fontSize: 11, color: "#a78bfa", background: "#1e1e38", padding: "2px 6px", borderRadius: 4 }}>
                          {p.count} mentions
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Locations */}
              <div style={{ background: "#0c1020", border: "1px solid #1e2540", borderRadius: 8, padding: 14 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: "#38bdf8", marginBottom: 10, display: "flex", alignItems: "center", gap: 6 }}>
                  <span>📍</span> LOCATIONS & REGIONS ({locations.length})
                </div>
                {locations.length === 0 ? (
                  <div style={{ fontSize: 12, color: "#64748b" }}>None detected in text.</div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {locations.map((loc, idx) => (
                      <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 13, background: "#131728", padding: "6px 10px", borderRadius: 6 }}>
                        <span style={{ color: "#ffffff", fontWeight: 500 }}>{loc.name}</span>
                        <span style={{ fontSize: 11, color: "#38bdf8", background: "#102a45", padding: "2px 6px", borderRadius: 4 }}>
                          {loc.count} mentions
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Organizations */}
              <div style={{ background: "#0c1020", border: "1px solid #1e2540", borderRadius: 8, padding: 14 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: "#34d399", marginBottom: 10, display: "flex", alignItems: "center", gap: 6 }}>
                  <span>🏛️</span> ORGANIZATIONS & INSTITUTIONS ({organizations.length})
                </div>
                {organizations.length === 0 ? (
                  <div style={{ fontSize: 12, color: "#64748b" }}>None detected in text.</div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {organizations.map((org, idx) => (
                      <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 13, background: "#131728", padding: "6px 10px", borderRadius: 6 }}>
                        <span style={{ color: "#ffffff", fontWeight: 500 }}>{org.name}</span>
                        <span style={{ fontSize: 11, color: "#34d399", background: "#0b2b20", padding: "2px 6px", borderRadius: 4 }}>
                          {org.count} mentions
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Dates & Time Markers */}
              <div style={{ background: "#0c1020", border: "1px solid #1e2540", borderRadius: 8, padding: 14 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: "#f59e0b", marginBottom: 10, display: "flex", alignItems: "center", gap: 6 }}>
                  <span>⏳</span> DATES & TEMPORAL MARKERS ({dates.length})
                </div>
                {dates.length === 0 ? (
                  <div style={{ fontSize: 12, color: "#64748b" }}>None detected in text.</div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {dates.map((d, idx) => (
                      <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 13, background: "#131728", padding: "6px 10px", borderRadius: 6 }}>
                        <span style={{ color: "#ffffff", fontWeight: 500 }}>{d.name}</span>
                        <span style={{ fontSize: 11, color: "#f59e0b", background: "#2e210b", padding: "2px 6px", borderRadius: 4 }}>
                          {d.count} mentions
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Section 2: Core Concepts & Main Topics with Names */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            {/* Core Concepts */}
            <div className="ncert-card">
              <div className="ncert-card-title">
                <span className="ncert-card-title-dot" style={{ background: "#06b6d4" }}></span>
                Core Concepts (Named Themes)
              </div>
              <p style={{ fontSize: 12, color: "#94a3b8", marginBottom: 12 }}>
                High-importance conceptual nouns and multi-word phrases extracted via semantic parsing.
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {concepts.map((c, idx) => {
                  const name = c.concept || c.name || c;
                  const count = c.count || 1;
                  return (
                    <div
                      key={idx}
                      style={{
                        background: "#131728",
                        border: "1px solid #1e2540",
                        padding: "8px 14px",
                        borderRadius: 8,
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                      }}
                    >
                      <span style={{ color: "#ffffff", fontWeight: 600, fontSize: 13 }}>{name}</span>
                      <span style={{ fontSize: 11, background: "#06b6d4", color: "#000", fontWeight: 700, padding: "1px 6px", borderRadius: 10 }}>
                        {count}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Main Topics */}
            <div className="ncert-card">
              <div className="ncert-card-title">
                <span className="ncert-card-title-dot" style={{ background: "#f472b6" }}></span>
                Main Topic Clusters
              </div>
              <p style={{ fontSize: 12, color: "#94a3b8", marginBottom: 12 }}>
                Thematic clusters showing key conceptual vocabulary associated with chapter sub-topics.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {topics.map((t, idx) => (
                  <div key={idx} style={{ background: "#0c1020", border: "1px solid #1e2540", borderRadius: 8, padding: 12 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "#f472b6", marginBottom: 6 }}>
                      Topic {t.topic || idx + 1}: {(t.name || t.words?.[0] || t.keywords?.[0] || "Thematic cluster").toString().toUpperCase()}
                    </div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                      {(t.words || t.keywords || []).map((w, wIdx) => (
                        <span
                          key={wIdx}
                          style={{
                            background: "#1e293b",
                            padding: "3px 8px",
                            borderRadius: 4,
                            fontSize: 11,
                            color: "#cbd5e1",
                          }}
                        >
                          {w}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
