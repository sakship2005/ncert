import React, { useState } from "react";
import { nlp } from "@/api/Client";

export default function SemanticSearchSection({ book }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Enter a search query");
      return;
    }
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const data = await nlp.semanticSearch(book?.id, query.trim());
      setResults(data.results || []);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  return (
    <div className="fade-in">
      <div className="ncert-section-title"><span>🔍</span> Semantic Search</div>
      <p style={{ color: "#6b7db3", fontSize: 14, marginBottom: 24 }}>
        TF-IDF retrieval finds the most relevant chapters; the QA model extracts the matching
        passage from each.
      </p>

      <div className="ncert-card" style={{ marginBottom: 24 }}>
        <div className="ncert-card-title">
          <span className="ncert-card-title-dot"></span> Search NCERT Content
        </div>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <input
            className="ncert-chat-input"
            style={{ flex: 1, minWidth: 200 }}
            placeholder="e.g. How does photosynthesis work?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button
            className="ncert-qg-btn"
            style={{ width: "auto", padding: "8px 24px" }}
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? "⏳ Searching…" : "🔍 Search"}
          </button>
        </div>
        {error && <p style={{ color: "#f472b6", fontSize: 12, marginTop: 8 }}>{error}</p>}
      </div>

      {results && (
        <div>
          <div className="ncert-card-title" style={{ marginBottom: 16 }}>
            <span className="ncert-card-title-dot" style={{ background: "#06b6d4" }}></span>
            {results.length} Relevant Results
          </div>
          {results.length === 0 ? (
            <div className="ncert-card">
              <p style={{ color: "#6b7db3" }}>No matching content found.</p>
            </div>
          ) : (
            results.map((r, i) => (
              <div className="ncert-search-result" key={i}>
                <div className="ncert-search-meta">
                  Chapter {r.chapter_num}: {r.title} · Relevance: {Math.round(r.score * 100)}%
                </div>
                <div className="ncert-search-snippet">{r.snippet}</div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}