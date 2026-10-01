import React, { useState, useEffect } from "react";
import { nlp } from "@/api/Client";

export default function DifficultWordsSection({ book, chapters }) {
  const [selectedChapter, setSelectedChapter] = useState(
    chapters && chapters.length > 0 ? (chapters[0].chapter_num ?? chapters[0].chapter_number ?? "") : ""
  );
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedWord, setSelectedWord] = useState(null);

  const fetchDifficultWords = async (chNum) => {
    if (!chNum) return;
    setLoading(true);
    setError("");
    setWords([]);
    setSelectedWord(null);
    try {
      const num = parseInt(chNum, 10);
      const chObj = chapters.find(
        (c) => (c.chapter_num ?? c.chapter_number) === num
      );
      const data = await nlp.getDifficultWords(book?.id, num, chObj?.id);
      if (data.status === "error") {
        setError(data.message || "Failed to load difficult words.");
      } else {
        setWords(data.difficult_words || []);
        if (data.difficult_words?.length > 0) {
          setSelectedWord(data.difficult_words[0]);
        }
      }
    } catch (e) {
      setError(e.message || "Error detecting difficult vocabulary.");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (selectedChapter) {
      fetchDifficultWords(selectedChapter);
    }
  }, [selectedChapter]);

  const filteredWords = words.filter((w) =>
    (w.word || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
    (w.definition || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
    (w.hindi_meaning || "").toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="fade-in">
      <div className="ncert-page-header">
        <div>
          <h2 className="ncert-page-title">📚 Automatic Difficult Word Detection</h2>
          <p className="ncert-page-subtitle">
            Uncommon, complex, and domain-specific words detected automatically from each chapter with simple definitions, synonyms, Hindi/Marathi meanings, and contextual examples.
          </p>
        </div>
      </div>

      {/* Chapter Selection & Search Bar */}
      <div className="ncert-card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "center" }}>
          <div style={{ flex: 1, minWidth: 240 }}>
            <label style={{ display: "block", fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
              Select Chapter
            </label>
            <select
              className="ncert-qg-select"
              style={{ width: "100%" }}
              value={selectedChapter}
              onChange={(e) => setSelectedChapter(e.target.value)}
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

          <div style={{ flex: 2, minWidth: 260 }}>
            <label style={{ display: "block", fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
              Search in Chapter Vocabulary ({filteredWords.length} words found)
            </label>
            <input
              type="text"
              className="ncert-qg-select"
              style={{ width: "100%", padding: "10px 14px" }}
              placeholder="🔍 Search by word or meaning..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div style={{ alignSelf: "flex-end" }}>
            <button
              className="ncert-qg-btn"
              style={{ padding: "10px 20px" }}
              onClick={() => fetchDifficultWords(selectedChapter)}
              disabled={loading}
            >
              {loading ? "Detecting…" : "🔄 Refresh"}
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
          <p style={{ color: "#6b7db3", fontSize: 14 }}>Analyzing chapter vocabulary & extracting definitions…</p>
        </div>
      ) : filteredWords.length === 0 ? (
        <div className="ncert-card" style={{ textAlign: "center", padding: "40px 20px" }}>
          <p style={{ color: "#94a3b8", fontSize: 15 }}>
            {searchQuery ? "No matching words found for your search." : "Select a chapter to detect difficult vocabulary."}
          </p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.3fr", gap: 20 }}>
          {/* Word List Deck */}
          <div className="ncert-card" style={{ maxHeight: 580, overflowY: "auto", padding: 12 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#94a3b8", marginBottom: 12, padding: "0 8px" }}>
              Detected Vocabulary Words ({filteredWords.length})
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {filteredWords.map((item, idx) => {
                const isSelected = selectedWord?.word === item.word;
                return (
                  <div
                    key={idx}
                    onClick={() => setSelectedWord(item)}
                    style={{
                      padding: "12px 16px",
                      borderRadius: 8,
                      cursor: "pointer",
                      border: "1px solid",
                      borderColor: isSelected ? "#4f6ef7" : "#1e2540",
                      background: isSelected ? "#1a2245" : "#0d1120",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      transition: "all 0.15s ease",
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, color: "#ffffff", fontSize: 15 }}>
                        {item.word}
                      </div>
                      <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 2 }}>
                        {item.hindi_meaning ? `हिं: ${item.hindi_meaning}` : item.pos || "Vocabulary"}
                      </div>
                    </div>
                    <span
                      style={{
                        fontSize: 11,
                        background: "#1e293b",
                        color: "#94a3b8",
                        padding: "2px 8px",
                        borderRadius: 12,
                      }}
                    >
                      {item.pos || "term"}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Detailed Word Inspector Card */}
          {selectedWord && (
            <div className="ncert-card" style={{ borderLeft: "4px solid #34d399", height: "fit-content" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                <div>
                  <h3 style={{ fontSize: 24, fontWeight: 700, color: "#ffffff", margin: 0 }}>
                    {selectedWord.word}
                  </h3>
                  <span style={{ fontSize: 12, color: "#34d399", fontWeight: 600, textTransform: "uppercase" }}>
                    {selectedWord.pos || "Part of speech"}
                  </span>
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  {selectedWord.frequency && (
                    <span style={{ fontSize: 12, background: "#1e2540", color: "#cbd5e1", padding: "4px 10px", borderRadius: 6 }}>
                      Occurrences: {selectedWord.frequency}
                    </span>
                  )}
                  <button
                    type="button"
                    className="ncert-qg-btn"
                    style={{ padding: "6px 12px", width: "auto" }}
                    onClick={() => {
                      const utter = new SpeechSynthesisUtterance(selectedWord.word);
                      utter.lang = /[\u0900-\u097F]/.test(selectedWord.word) ? "hi-IN" : "en-IN";
                      window.speechSynthesis?.cancel();
                      window.speechSynthesis?.speak(utter);
                    }}
                  >
                    🔊 Pronounce
                  </button>
                </div>
              </div>

              {/* Meanings */}
              <div style={{ marginBottom: 16 }}>
                <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 4, fontWeight: 600 }}>
                  SIMPLE DEFINITION
                </div>
                <div style={{ background: "#0c1020", border: "1px solid #1e2540", padding: "12px 16px", borderRadius: 6, color: "#e2e8f0", fontSize: 14, lineHeight: 1.6 }}>
                  {selectedWord.simple_meaning || selectedWord.definition}
                </div>
              </div>

              {/* Multilingual Meanings */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
                <div style={{ background: "#0c1020", border: "1px solid #1e2540", padding: "10px 14px", borderRadius: 6 }}>
                  <div style={{ fontSize: 11, color: "#f59e0b", fontWeight: 600 }}>हिंदी अर्थ (HINDI)</div>
                  <div style={{ fontSize: 14, color: "#ffffff", marginTop: 4 }}>
                    {selectedWord.hindi_meaning || "संदर्भ अनुसार समझें"}
                  </div>
                </div>
                <div style={{ background: "#0c1020", border: "1px solid #1e2540", padding: "10px 14px", borderRadius: 6 }}>
                  <div style={{ fontSize: 11, color: "#06b6d4", fontWeight: 600 }}>मराठी अर्थ (MARATHI)</div>
                  <div style={{ fontSize: 14, color: "#ffffff", marginTop: 4 }}>
                    {selectedWord.marathi_meaning || "संदर्भाप्रमाणे समजून घ्या"}
                  </div>
                </div>
              </div>

              {/* Synonyms */}
              {selectedWord.synonyms && selectedWord.synonyms.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 6, fontWeight: 600 }}>
                    SYNONYMS
                  </div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {selectedWord.synonyms.map((s, idx) => (
                      <span
                        key={idx}
                        style={{
                          background: "#1e293b",
                          border: "1px solid #334155",
                          padding: "3px 10px",
                          borderRadius: 12,
                          fontSize: 12,
                          color: "#cbd5e1",
                        }}
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Context Example */}
              <div>
                <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 4, fontWeight: 600 }}>
                  EXAMPLE USAGE IN CONTEXT
                </div>
                <div style={{ background: "#0a0e1c", borderLeft: "3px solid #6366f1", padding: "10px 14px", borderRadius: "0 6px 6px 0", color: "#93c5fd", fontStyle: "italic", fontSize: 13, lineHeight: 1.5 }}>
                  "{selectedWord.example || `The chapter employs '${selectedWord.word}' to emphasize core conceptual depth.`}"
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
