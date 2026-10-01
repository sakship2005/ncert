import React, { useState, useEffect } from "react";
import { nlp } from "@/api/Client";

export default function QuizSection({ book, chapters }) {
  const [selectedChapter, setSelectedChapter] = useState(
    chapters && chapters.length > 0 ? (chapters[0].chapter_num ?? chapters[0].chapter_number ?? "") : ""
  );
  const [totalQuestions, setTotalQuestions] = useState(8);
  const [language, setLanguage] = useState("en");
  const [selectedTypes, setSelectedTypes] = useState(["mcq", "true_false", "fill_blank", "short_answer"]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Quiz State
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [userAnswers, setUserAnswers] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [score, setScore] = useState(null);
  const [history, setHistory] = useState([]);

  // Load chapter performance history from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem(`ncert_quiz_history_${book?.id}`);
      if (saved) setHistory(JSON.parse(saved));
    } catch {}
  }, [book?.id]);

  const handleGenerateQuiz = async () => {
    if (!selectedChapter) {
      setError("Please select a chapter for the quiz.");
      return;
    }
    setLoading(true);
    setError("");
    setIsSubmitted(false);
    setUserAnswers({});
    setScore(null);
    setQuizQuestions([]);

    try {
      const num = parseInt(selectedChapter, 10);
      const chObj = chapters.find(
        (c) => (c.chapter_num ?? c.chapter_number) === num
      );
      const data = await nlp.generateQuiz(
        book?.id,
        num,
        chObj?.id,
        totalQuestions,
        ["mcq", "true_false", "fill_blank", "short_answer"].filter((t) => selectedTypes.includes(t)).length
          ? selectedTypes
          : ["mcq", "true_false", "fill_blank", "short_answer"],
        language
      );
      if (data.status === "error") {
        setError(data.message || "Failed to generate quiz questions.");
      } else {
        setQuizQuestions(data.questions || []);
      }
    } catch (e) {
      setError(e.message || "An error occurred while generating the quiz.");
    }
    setLoading(false);
  };

  const handleSelectOption = (qId, val) => {
    if (isSubmitted) return;
    setUserAnswers((prev) => ({ ...prev, [qId]: val }));
  };

  const handleSubmitQuiz = () => {
    let earned = 0;
    let totalGraded = 0;

    quizQuestions.forEach((q) => {
      const ans = userAnswers[q.id];
      if (q.type === "mcq") {
        totalGraded++;
        if (ans !== undefined && parseInt(ans, 10) === q.correct_index) {
          earned++;
        }
      } else if (q.type === "true_false") {
        totalGraded++;
        if (ans === q.correct_bool) {
          earned++;
        }
      } else if (q.type === "fill_blank") {
        totalGraded++;
        if (
          ans &&
          ans.trim().toLowerCase() === (q.correct_answer || "").trim().toLowerCase()
        ) {
          earned++;
        }
      } else {
        // short answer is self-assessed / marked complete if student typed something
        totalGraded++;
        if (ans && ans.trim().length > 5) {
          earned++;
        }
      }
    });

    const percent = Math.round((earned / Math.max(totalGraded, 1)) * 100);
    const scoreResult = {
      earned,
      total: totalGraded,
      percent,
      chapter: selectedChapter,
      date: new Date().toLocaleDateString(),
    };
    setScore(scoreResult);
    setIsSubmitted(true);

    // Persist history
    const updatedHistory = [scoreResult, ...history].slice(0, 10);
    setHistory(updatedHistory);
    try {
      localStorage.setItem(`ncert_quiz_history_${book?.id}`, JSON.stringify(updatedHistory));
    } catch {}
  };

  const selectedChObj = chapters.find(
    (c) => String(c.chapter_num ?? c.chapter_number) === String(selectedChapter)
  );

  return (
    <div className="fade-in">
      <div className="ncert-page-header">
        <div>
          <h2 className="ncert-page-title">🎯 Automatic Question & Quiz Generator</h2>
          <p className="ncert-page-subtitle">
            Generate customized NCERT practice quizzes with <strong>MCQs, True/False, Fill in the Blanks, and Short Answer</strong> questions. Take the interactive quiz to get instant scoring, detailed explanations, and performance tracking.
          </p>
        </div>
      </div>

      {/* Control Panel */}
      <div className="ncert-card" style={{ marginBottom: 24 }}>
        <div className="ncert-card-title">
          <span className="ncert-card-title-dot"></span> Quiz Configuration
        </div>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "center" }}>
          {/* Chapter */}
          <div style={{ flex: 2, minWidth: 240 }}>
            <label style={{ display: "block", fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
              Select Chapter
            </label>
            <select
              className="ncert-qg-select"
              style={{ width: "100%" }}
              value={selectedChapter}
              onChange={(e) => {
                setSelectedChapter(e.target.value);
                setQuizQuestions([]);
                setIsSubmitted(false);
              }}
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

          {/* Question Count */}
          <div style={{ flex: 1, minWidth: 140 }}>
            <label style={{ display: "block", fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
              Questions
            </label>
            <select
              className="ncert-qg-select"
              style={{ width: "100%" }}
              value={totalQuestions}
              onChange={(e) => setTotalQuestions(parseInt(e.target.value, 10))}
            >
              <option value={5}>5 Questions</option>
              <option value={8}>8 Questions</option>
              <option value={10}>10 Questions</option>
            </select>
          </div>

          {/* Language */}
          <div style={{ flex: 1, minWidth: 160 }}>
            <label style={{ display: "block", fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
              Language
            </label>
            <select
              className="ncert-qg-select"
              style={{ width: "100%" }}
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="mr">मराठी (Marathi)</option>
            </select>
          </div>

          {/* Formats */}
          <div style={{ flex: 2, minWidth: 280 }}>
            <label style={{ display: "block", fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
              Question formats
            </label>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {[
                { id: "mcq", label: "MCQ" },
                { id: "true_false", label: "True/False" },
                { id: "fill_blank", label: "Fill blanks" },
                { id: "short_answer", label: "Short answer" },
              ].map((t) => {
                const on = selectedTypes.includes(t.id);
                return (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() =>
                      setSelectedTypes((prev) =>
                        prev.includes(t.id) ? prev.filter((x) => x !== t.id) : [...prev, t.id]
                      )
                    }
                    style={{
                      padding: "6px 10px",
                      borderRadius: 6,
                      fontSize: 12,
                      cursor: "pointer",
                      border: "1px solid",
                      background: on ? "#4f6ef7" : "#131728",
                      borderColor: on ? "#6366f1" : "#1e2540",
                      color: on ? "#fff" : "#94a3b8",
                    }}
                  >
                    {t.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Action */}
          <div style={{ alignSelf: "flex-end" }}>
            <button
              className="ncert-qg-btn"
              style={{ padding: "10px 24px" }}
              onClick={handleGenerateQuiz}
              disabled={loading}
            >
              {loading ? "Generating Quiz…" : "🚀 Start Quiz"}
            </button>
          </div>
        </div>

        {error && (
          <div style={{ marginTop: 12, padding: "10px 14px", background: "#3b1717", border: "1px solid #7f1d1d", borderRadius: 6, color: "#fca5a5", fontSize: 13 }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Score Banner when Submitted */}
      {isSubmitted && score && (
        <div
          className="ncert-card"
          style={{
            marginBottom: 24,
            background: score.percent >= 60 ? "linear-gradient(135deg, #0b2e21, #0d1120)" : "linear-gradient(135deg, #3b1717, #0d1120)",
            border: `1px solid ${score.percent >= 60 ? "#10b981" : "#ef4444"}`,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
            <div>
              <span style={{ fontSize: 12, textTransform: "uppercase", fontWeight: 700, color: score.percent >= 60 ? "#34d399" : "#f87171" }}>
                {score.percent >= 75 ? "🎉 Excellent Work!" : score.percent >= 50 ? "👍 Good Effort!" : "📚 Needs Review"}
              </span>
              <h2 style={{ fontSize: 28, margin: "4px 0", color: "#ffffff" }}>
                Your Score: {score.earned} / {score.total} ({score.percent}%)
              </h2>
              <p style={{ color: "#94a3b8", fontSize: 13, margin: 0 }}>
                Review each question below to inspect correct answers and detailed NCERT textual explanations.
              </p>
            </div>
            <button
              className="ncert-qg-btn"
              style={{ width: "auto", padding: "10px 20px" }}
              onClick={handleGenerateQuiz}
            >
              🔄 Retake Another Quiz
            </button>
          </div>
        </div>
      )}

      {/* Quiz Questions List */}
      {loading ? (
        <div className="ncert-loading" style={{ height: 260 }}>
          <div className="ncert-spinner"></div>
          <p style={{ color: "#6b7db3", fontSize: 14 }}>Formulating NCERT grounded questions, options & explanations…</p>
        </div>
      ) : quizQuestions.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {quizQuestions.map((q, idx) => {
            const userAns = userAnswers[q.id];

            return (
              <div
                key={q.id || idx}
                className="ncert-card"
                style={{
                  borderLeft: `4px solid ${
                    isSubmitted
                      ? q.type === "mcq"
                        ? parseInt(userAns, 10) === q.correct_index
                          ? "#10b981"
                          : "#ef4444"
                        : q.type === "true_false"
                        ? userAns === q.correct_bool
                          ? "#10b981"
                          : "#ef4444"
                        : "#6366f1"
                      : "#4f6ef7"
                  }`,
                }}
              >
                {/* Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 14, fontWeight: 700, color: "#ffffff" }}>
                      Q{idx + 1}.
                    </span>
                    <span
                      style={{
                        fontSize: 11,
                        background: "#1e2540",
                        color: "#94a3b8",
                        padding: "2px 8px",
                        borderRadius: 12,
                        textTransform: "uppercase",
                      }}
                    >
                      {q.type.replace("_", " ")}
                    </span>
                  </div>
                </div>

                {/* Question Text */}
                <p style={{ fontSize: 16, fontWeight: 600, color: "#e2e8f0", marginBottom: 16, lineHeight: 1.5 }}>
                  {q.question}
                </p>

                {/* Question Type 1: MCQ */}
                {q.type === "mcq" && (
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                    {(q.options || []).map((opt, oIdx) => {
                      const isChosen = userAns === oIdx;
                      let bg = isChosen ? "#1e293b" : "#0c1020";
                      let border = isChosen ? "#6366f1" : "#1e2540";
                      if (isSubmitted) {
                        if (oIdx === q.correct_index) {
                          bg = "#0b2e21";
                          border = "#10b981";
                        } else if (isChosen && oIdx !== q.correct_index) {
                          bg = "#3b1717";
                          border = "#ef4444";
                        }
                      }

                      return (
                        <div
                          key={oIdx}
                          onClick={() => handleSelectOption(q.id, oIdx)}
                          style={{
                            padding: "12px 16px",
                            borderRadius: 8,
                            cursor: isSubmitted ? "default" : "pointer",
                            background: bg,
                            border: `1px solid ${border}`,
                            color: "#ffffff",
                            fontSize: 14,
                            display: "flex",
                            alignItems: "center",
                            gap: 10,
                            transition: "all 0.15s ease",
                          }}
                        >
                          <span
                            style={{
                              width: 24,
                              height: 24,
                              borderRadius: "50%",
                              background: isChosen ? "#4f6ef7" : "#1e2540",
                              display: "inline-flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontSize: 12,
                              fontWeight: 700,
                            }}
                          >
                            {String.fromCharCode(65 + oIdx)}
                          </span>
                          <span>{opt}</span>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Question Type 2: True/False */}
                {q.type === "true_false" && (
                  <div style={{ display: "flex", gap: 12 }}>
                    {[true, false].map((val) => {
                      const isChosen = userAns === val;
                      let bg = isChosen ? "#1e293b" : "#0c1020";
                      let border = isChosen ? "#6366f1" : "#1e2540";
                      if (isSubmitted) {
                        if (val === q.correct_bool) {
                          bg = "#0b2e21";
                          border = "#10b981";
                        } else if (isChosen && val !== q.correct_bool) {
                          bg = "#3b1717";
                          border = "#ef4444";
                        }
                      }

                      return (
                        <button
                          key={String(val)}
                          type="button"
                          onClick={() => handleSelectOption(q.id, val)}
                          disabled={isSubmitted}
                          style={{
                            padding: "10px 28px",
                            borderRadius: 8,
                            cursor: isSubmitted ? "default" : "pointer",
                            background: bg,
                            border: `1px solid ${border}`,
                            color: "#ffffff",
                            fontWeight: 600,
                            fontSize: 14,
                          }}
                        >
                          {val ? "✅ True" : "❌ False"}
                        </button>
                      );
                    })}
                  </div>
                )}

                {/* Question Type 3: Fill in Blanks */}
                {q.type === "fill_blank" && (
                  <div>
                    <input
                      type="text"
                      className="ncert-qg-select"
                      placeholder="Type your answer here..."
                      style={{ maxWidth: 360 }}
                      value={userAns || ""}
                      onChange={(e) => handleSelectOption(q.id, e.target.value)}
                      disabled={isSubmitted}
                    />
                    {isSubmitted && (
                      <div style={{ marginTop: 8, fontSize: 13, color: "#34d399" }}>
                        Correct Answer: <strong>{q.correct_answer}</strong>
                      </div>
                    )}
                  </div>
                )}

                {/* Question Type 4: Short Answer */}
                {q.type === "short_answer" && (
                  <div>
                    <textarea
                      className="ncert-qg-select"
                      rows={3}
                      placeholder="Write your brief answer based on NCERT content..."
                      style={{ width: "100%", resize: "vertical" }}
                      value={userAns || ""}
                      onChange={(e) => handleSelectOption(q.id, e.target.value)}
                      disabled={isSubmitted}
                    />
                    {isSubmitted && (
                      <div style={{ marginTop: 10, background: "#0c1020", padding: "12px 16px", borderRadius: 6, border: "1px solid #1e2540" }}>
                        <div style={{ fontSize: 12, color: "#38bdf8", fontWeight: 700 }}>MODEL ANSWER:</div>
                        <div style={{ fontSize: 14, color: "#e2e8f0", marginTop: 4 }}>{q.answer}</div>
                      </div>
                    )}
                  </div>
                )}

                {/* Explanation Box (shown after submit) */}
                {isSubmitted && q.explanation && (
                  <div
                    style={{
                      marginTop: 14,
                      padding: "12px 16px",
                      background: "#0c1020",
                      border: "1px solid #1e2540",
                      borderRadius: 8,
                      fontSize: 13,
                      color: "#94a3b8",
                      lineHeight: 1.6,
                    }}
                  >
                    💡 <strong>NCERT Explanation:</strong> {q.explanation}
                  </div>
                )}
              </div>
            );
          })}

          {/* Submit Quiz Button */}
          {!isSubmitted && (
            <div style={{ textAlign: "center", padding: "20px 0" }}>
              <button
                className="ncert-qg-btn"
                style={{ padding: "14px 48px", fontSize: 16 }}
                onClick={handleSubmitQuiz}
              >
                🏁 Submit Quiz & See Answers
              </button>
            </div>
          )}
        </div>
      ) : (
        /* Empty / Chapter Performance Tracking Deck */
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
          <div className="ncert-card">
            <div className="ncert-card-title">
              <span className="ncert-card-title-dot" style={{ background: "#4f6ef7" }}></span>
              About Quiz Mode
            </div>
            <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.6 }}>
              Select a chapter and launch a self-assessment quiz. The system analyzes the chapter content to dynamically generate mixed questions covering essential learning outcomes.
            </p>
            <ul style={{ color: "#cbd5e1", fontSize: 13, paddingLeft: 20, lineHeight: 1.8 }}>
              <li><strong>Multiple Choice (MCQ):</strong> Conceptual test of critical facts</li>
              <li><strong>True/False:</strong> Analytical statement evaluation</li>
              <li><strong>Fill in the Blanks:</strong> Key vocabulary and terminology recall</li>
              <li><strong>Short Answer:</strong> Comprehension synthesis</li>
            </ul>
          </div>

          <div className="ncert-card">
            <div className="ncert-card-title">
              <span className="ncert-card-title-dot" style={{ background: "#34d399" }}></span>
              Chapter Performance Tracking
            </div>
            {history.length === 0 ? (
              <p style={{ color: "#64748b", fontSize: 13 }}>
                No completed quizzes yet. Take a quiz to start tracking your performance across chapters!
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {history.map((h, i) => (
                  <div
                    key={i}
                    style={{
                      background: "#0c1020",
                      border: "1px solid #1e2540",
                      padding: "8px 12px",
                      borderRadius: 6,
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      fontSize: 13,
                    }}
                  >
                    <div>
                      <span style={{ color: "#ffffff", fontWeight: 600 }}>Chapter {h.chapter}</span>
                      <span style={{ color: "#64748b", fontSize: 11, marginLeft: 8 }}>{h.date}</span>
                    </div>
                    <span
                      style={{
                        color: h.percent >= 60 ? "#34d399" : "#f87171",
                        fontWeight: 700,
                      }}
                    >
                      {h.earned}/{h.total} ({h.percent}%)
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
