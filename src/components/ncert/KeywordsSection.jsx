import React, { useState, useMemo, useEffect } from "react";
import { nlp } from "@/api/Client";

const VIBRANT_COLORS = [
  "#4f6ef7", "#7c3aed", "#06b6d4", "#f472b6", "#34d399",
  "#f59e0b", "#818cf8", "#38bdf8", "#a78bfa", "#fb7185",
  "#2dd4bf", "#e879f9", "#60a5fa", "#4ade80", "#fbbf24"
];

export default function KeywordsSection({ book, chapters = [] }) {
  const [selectedChapterNum, setSelectedChapterNum] = useState("all");
  const [selectedWord, setSelectedWord] = useState(null);
  const [filterType, setFilterType] = useState("all"); // 'all' | 'concepts' | 'terms'
  const [liveKeywords, setLiveKeywords] = useState([]);
  const [chapterAnalysisLoaded, setChapterAnalysisLoaded] = useState(false);
  const [loadingCloud, setLoadingCloud] = useState(false);

  useEffect(() => {
    async function loadChapterCloud() {
      if (selectedChapterNum === "all") {
        setLiveKeywords([]);
        setChapterAnalysisLoaded(false);
        return;
      }
      const ch = chapters.find(
        (c) => String(c.chapter_num ?? c.chapter_number) === String(selectedChapterNum)
      );
      if (!ch || !book?.id) return;
      setLoadingCloud(true);
      setChapterAnalysisLoaded(false);
      try {
        const data = await nlp.getChapterAnalysis(book.id, parseInt(selectedChapterNum, 10), ch.id);
        const items = [];
        (data.concepts || []).forEach((c) => {
          items.push({ word: c.concept || c.name, count: (c.count || 1) * 3, isConcept: true });
        });
        (data.topics || []).forEach((t) => {
          const topicWords = t.words || t.keywords || [];
          topicWords.forEach((w, i) => items.push({ word: w, count: 6 - i, isConcept: i === 0 }));
        });
        ["persons", "locations", "organizations"].forEach((cat) => {
          (data.entities?.[cat] || []).forEach((e) => {
            items.push({ word: e.name, count: (e.count || 1) + 4, isConcept: true });
          });
        });
        setLiveKeywords(items);
      } catch {
        setLiveKeywords([]);
      } finally {
        setChapterAnalysisLoaded(true);
      }
      setLoadingCloud(false);
    }
    loadChapterCloud();
  }, [selectedChapterNum, book, chapters]);

  // Extract keywords / concepts based on selection
  const rawKeywords = useMemo(() => {
    if (selectedChapterNum !== "all" && chapterAnalysisLoaded) return liveKeywords;
    if (selectedChapterNum === "all") {
      const topKw = book?.book_analysis?.top_keywords || [];
      const topConcepts = (book?.book_analysis?.major_concepts || []).map(c => ({
        word: c.concept || c.name,
        count: (c.count || 1) * 2,
        isConcept: true,
      }));
      const combined = [...topKw, ...topConcepts];
      if (combined.length > 0) return combined;
    } else {
      const ch = chapters.find(
        (c) => String(c.chapter_num ?? c.chapter_number) === String(selectedChapterNum)
      );
      if (ch) {
        const concepts = (ch.extracted?.concepts || []).map(w => ({ word: w, count: 5, isConcept: true }));
        const terms = (ch.extracted?.key_terms || []).map(w => ({ word: w, count: 4, isTerm: true }));
        const topics = (ch.extracted?.topics || []).map(w => ({ word: w, count: 6, isConcept: true }));
        const combined = [...concepts, ...terms, ...topics];
        if (combined.length > 0) return combined;
      }
    }

    // Default fallback vocabulary words from the textbook
    return (book?.book_analysis?.top_keywords || []).slice(0, 60);
  }, [selectedChapterNum, book, chapters, liveKeywords, chapterAnalysisLoaded]);

  // Aggregate frequencies
  const processedWords = useMemo(() => {
    const map = new Map();
    rawKeywords.forEach(item => {
      const w = (typeof item === "string" ? item : item.word || item.name || "").trim();
      if (!w || w.length < 3) return;
      const count = (typeof item === "object" && item.count) ? item.count : 2;
      const isConcept = typeof item === "object" && item.isConcept;
      const current = map.get(w.toLowerCase()) || { word: w, count: 0, isConcept: false };
      map.set(w.toLowerCase(), {
        word: w,
        count: current.count + count,
        isConcept: current.isConcept || isConcept,
      });
    });

    let list = Array.from(map.values());
    if (filterType === "concepts") {
      list = list.filter(w => w.isConcept);
    }
    return list.sort((a, b) => b.count - a.count).slice(0, 65);
  }, [rawKeywords, filterType]);

  const maxCount = processedWords.length > 0 ? processedWords[0].count : 1;
  const minCount = processedWords.length > 0 ? processedWords[processedWords.length - 1].count : 1;

  // Pseudo-random deterministic placement to avoid layout jump on re-render
  const displayWords = useMemo(() => {
    return [...processedWords].sort((a, b) => {
      const hashA = a.word.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
      const hashB = b.word.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
      return (hashA % 17) - (hashB % 17);
    });
  }, [processedWords]);

  return (
    <div className="fade-in">
      <div className="ncert-page-header">
        <div>
          <h2 className="ncert-page-title">☁️ Dense WordCloud Visualization</h2>
          <p className="ncert-page-subtitle">
            A dense, concept-weighted visual map of major themes and high-frequency concepts for each chapter. Note: Useless word frequency graphs have been eliminated in favor of contextual concept density.
          </p>
        </div>
      </div>

      {/* Control Bar */}
      <div className="ncert-card" style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap", justifyContent: "space-between" }}>
          <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", flex: 1 }}>
            <span style={{ fontSize: 13, color: "#94a3b8", fontWeight: 600 }}>Filter by Scope:</span>
            <select
              className="ncert-qg-select"
              style={{ minWidth: 220 }}
              value={selectedChapterNum}
              onChange={(e) => {
                setSelectedChapterNum(e.target.value);
                setSelectedWord(null);
              }}
            >
              <option value="all">Entire Textbook (All Chapters)</option>
              {chapters.map((ch) => {
                const num = ch.chapter_num ?? ch.chapter_number ?? 1;
                return (
                  <option key={ch.id || num} value={num}>
                    Chapter {num}: {ch.title}
                  </option>
                );
              })}
            </select>

            <div style={{ display: "flex", gap: 6 }}>
              {[
                { id: "all", label: "All Keywords & Concepts" },
                { id: "concepts", label: "Core Concepts Only" },
              ].map((f) => (
                <button
                  key={f.id}
                  onClick={() => setFilterType(f.id)}
                  style={{
                    padding: "6px 12px",
                    borderRadius: 6,
                    fontSize: 12,
                    fontWeight: 500,
                    cursor: "pointer",
                    border: "1px solid",
                    background: filterType === f.id ? "#4f6ef7" : "#131728",
                    borderColor: filterType === f.id ? "#6366f1" : "#1e2540",
                    color: filterType === f.id ? "#ffffff" : "#94a3b8",
                  }}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div style={{ fontSize: 12, color: "#64748b" }}>
            Showing <strong>{displayWords.length}</strong> prominent concepts & terms
          </div>
        </div>
      </div>

      {/* Dense WordCloud Container */}
      <div className="ncert-card" style={{ padding: "32px 28px", minHeight: 440, background: "#0a0e1c", border: "1px solid #1e2540" }}>
        {loadingCloud ? (
          <div style={{ textAlign: "center", padding: "60px 0", color: "#64748b" }}>
            Building concept-weighted word cloud…
          </div>
        ) : displayWords.length === 0 ? (
          <div style={{ textAlign: "center", padding: "60px 0", color: "#64748b" }}>
            No prominent concepts found for this selection. Try selecting another chapter.
          </div>
        ) : (
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              alignItems: "center",
              justifyContent: "center",
              gap: "12px 18px",
              lineHeight: 1.4,
            }}
          >
            {displayWords.map((item, idx) => {
              const ratio = (item.count - minCount) / Math.max(maxCount - minCount, 1);
              const fontSize = 13 + Math.round(ratio * 28); // 13px to 41px
              const color = VIBRANT_COLORS[idx % VIBRANT_COLORS.length];
              const opacity = 0.65 + ratio * 0.35;
              const isSelected = selectedWord?.word === item.word;

              return (
                <span
                  key={idx}
                  onClick={() => setSelectedWord(item)}
                  style={{
                    fontSize: `${fontSize}px`,
                    fontWeight: item.isConcept || ratio > 0.5 ? 700 : 500,
                    color: color,
                    opacity: opacity,
                    cursor: "pointer",
                    padding: "4px 8px",
                    borderRadius: 6,
                    background: isSelected ? "rgba(99, 102, 241, 0.25)" : "transparent",
                    border: isSelected ? `1px solid ${color}` : "1px solid transparent",
                    transform: isSelected ? "scale(1.15)" : "scale(1)",
                    transition: "all 0.15s ease",
                    letterSpacing: item.isConcept ? "0.02em" : "normal",
                  }}
                  title={`${item.word}: ${item.count} prominence score`}
                >
                  {item.word}
                  {item.isConcept && (
                    <span style={{ fontSize: "10px", verticalAlign: "super", marginLeft: 2, color: "#38bdf8" }}>
                      ✦
                    </span>
                  )}
                </span>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected Concept Detail Card */}
      {selectedWord && (
        <div className="ncert-card" style={{ marginTop: 20, borderLeft: "4px solid #06b6d4" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ fontSize: 11, color: "#06b6d4", fontWeight: 700, textTransform: "uppercase" }}>
                Selected Concept Focus
              </span>
              <h3 style={{ fontSize: 20, color: "#ffffff", margin: "4px 0" }}>
                {selectedWord.word}
              </h3>
            </div>
            <div style={{ textAlign: "right" }}>
              <span style={{ fontSize: 12, background: "#1e2540", color: "#38bdf8", padding: "4px 10px", borderRadius: 12 }}>
                Prominence Score: {selectedWord.count}
              </span>
            </div>
          </div>
          <p style={{ color: "#94a3b8", fontSize: 13, marginTop: 8, margin: 0 }}>
            This term is identified as a critical recurring concept in the chapter. High prominence signifies that questions, summaries, and exam themes revolve directly around this concept.
          </p>
        </div>
      )}
    </div>
  );
}