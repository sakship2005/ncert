import React, { useState, useRef, useEffect } from "react";
import { chat } from "@/api/Client";

/** Minimal markdown → HTML for bot replies (bold, headings, bullets) */
function renderMarkdown(text) {
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  const html = escaped
    // headings
    .replace(/^#### (.+)$/gm, "<h4 style='margin:10px 0 4px;font-size:13px;color:#e8eaf6'>$1</h4>")
    .replace(/^### (.+)$/gm,  "<h3 style='margin:12px 0 6px;font-size:14px;color:#e8eaf6'>$1</h3>")
    .replace(/^## (.+)$/gm,   "<h2 style='margin:14px 0 6px;font-size:15px;color:#e8eaf6'>$1</h2>")
    // bold
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    // italic
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    // bullet lines (- or *)
    .replace(/^[-*] (.+)$/gm, "<li style='margin:3px 0;padding-left:4px'>$1</li>")
    // numbered list
    .replace(/^\d+\. (.+)$/gm, "<li style='margin:3px 0;padding-left:4px'>$1</li>")
    // wrap consecutive <li> in <ul>
    .replace(/(<li[^>]*>.*<\/li>\n?)+/g, (m) => `<ul style='margin:6px 0;padding-left:18px'>${m}</ul>`)
    // horizontal rule
    .replace(/^---$/gm, "<hr style='border-color:#1e2540;margin:10px 0'>")
    // line breaks
    .replace(/\n/g, "<br>");

  return html;
}

export default function ChatSection({ book, chapters }) {
  const [language, setLanguage] = useState("en");
  const [chapterId, setChapterId] = useState(chapters?.[0]?.id || "");
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Hello! I am your NCERT AI assistant. Choose a chapter and language, then ask me anything. I'll search the chapter and answer using AI.",
      source: "rag",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (!chapterId && chapters?.length) setChapterId(chapters[0].id);
  }, [chapters, chapterId]);

  const selectedChapter = chapters.find((c) => c.id === chapterId);
  const chapterNum = selectedChapter?.chapter_num ?? selectedChapter?.chapter_number ?? null;

  const suggestions = [
    "What is the main idea of this chapter?",
    "Name the important characters or people.",
    "Explain the key concepts in simple words.",
    "What should I remember for the exam?",
  ];

  const sendMessage = async () => {
    const msg = input.trim();
    if (!msg || loading) return;
    if (!chapterId) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Please select a chapter first.", source: "error" },
      ]);
      return;
    }
    setInput("");
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", text: msg }]);

    try {
      const data = await chat.send(chapterId, msg, [], language, book?.id, chapterNum);
      if (data.status === "error") throw new Error(data.message || "The chat service could not answer.");

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: data.answer || data.reply || "No answer returned.",
          source: "rag",
          sources: data.sources || [],
          webUsed: data.web_used ?? false,
        },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: `⚠️ ${e.message}`, source: "error" },
      ]);
    }
    setLoading(false);
  };

  return (
    <div className="fade-in">
      <div className="ncert-section-title"><span>💬</span> Multilingual RAG Chat</div>
      <div className="ncert-chat-layout">
        <div className="ncert-chat-window">

          {/* Header */}
          <div className="ncert-chat-header">
            <div className="ncert-chat-avatar">🤖</div>
            <div className="ncert-chat-info">
              <h3>NCERT Assistant</h3>
              <p>{book?.title || "—"} · {selectedChapter?.title || "Select a chapter"}</p>
            </div>
            <div className="ncert-lang-toggle" style={{ marginLeft: "auto" }}>
              {[
                { code: "en", label: "EN" },
                { code: "hi", label: "हिं" },
                { code: "mr", label: "मर" },
              ].map((l) => (
                <button
                  key={l.code}
                  className={`ncert-lang-btn ${language === l.code ? "active" : ""}`}
                  onClick={() => setLanguage(l.code)}
                >
                  {l.label}
                </button>
              ))}
            </div>
            <div className="ncert-chat-online" />
          </div>

          {/* Chapter selector */}
          <div style={{ padding: "8px 16px", borderBottom: "1px solid #1e2540" }}>
            <select
              className="ncert-qg-select"
              value={chapterId}
              onChange={(e) => setChapterId(e.target.value)}
              style={{ width: "100%" }}
            >
              <option value="">— Select chapter —</option>
              {chapters.map((ch) => (
                <option key={ch.id} value={ch.id}>
                  Chapter {ch.chapter_num ?? ch.chapter_number}: {ch.title}
                </option>
              ))}
            </select>
          </div>

          {/* Messages */}
          <div className="ncert-messages">
            {messages.map((m, i) => (
              <div key={i} className={`ncert-message ${m.role}`}>
                <div className="ncert-msg-avatar">
                  {m.role === "bot" ? "📚" : "👤"}
                </div>
                <div className="ncert-msg-bubble">
                  {m.role === "bot" ? (
                    <div dangerouslySetInnerHTML={{ __html: renderMarkdown(m.text) }} />
                  ) : (
                    m.text
                  )}

                  {/* Source badge + collapsible chunks */}
                  {m.role === "bot" && m.source === "rag" && (
                    <div style={{ marginTop: 6 }}>
                      <span className="ncert-source-badge ncert-badge-qa">
                        {m.webUsed ? "🌐 NCERT + Web" : "📖 NCERT · RAG"}
                      </span>

                      {m.sources && m.sources.length > 0 && (
                        <details style={{ marginTop: 6 }}>
                          <summary
                            style={{
                              fontSize: 11,
                              color: "#6b7db3",
                              cursor: "pointer",
                              userSelect: "none",
                            }}
                          >
                            📄 {m.sources.length} source chunk{m.sources.length > 1 ? "s" : ""} used
                          </summary>
                          <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 6 }}>
                            {m.sources.map((s, si) => (
                              <div
                                key={si}
                                style={{
                                  background: "rgba(255,255,255,0.04)",
                                  border: "1px solid #1e2540",
                                  borderRadius: 8,
                                  padding: "8px 10px",
                                  fontSize: 12,
                                  color: "#6b7db3",
                                  lineHeight: 1.5,
                                }}
                              >
                                <span style={{ color: "#4f6ef7", fontWeight: 600 }}>
                                  Chunk {s.chunk_id}
                                  {s.sentence_start != null ? ` · Lines ${s.sentence_start}–${s.sentence_end}` : ""}
                                </span>
                                <br />
                                {s.snippet}
                              </div>
                            ))}
                          </div>
                        </details>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="ncert-message bot">
                <div className="ncert-msg-avatar">📚</div>
                <div className="ncert-msg-bubble">
                  <div className="ncert-typing">
                    <span /><span /><span />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input row */}
          <div className="ncert-chat-input-row">
            <input
              className="ncert-chat-input"
              type="text"
              placeholder="Ask anything from this chapter…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button className="ncert-chat-send" onClick={sendMessage} disabled={loading}>
              ➤
            </button>
          </div>
        </div>

        {/* Suggestions sidebar */}
        <div className="ncert-suggestions">
          <div className="ncert-suggestion-card">
            <div className="ncert-suggestion-title">💡 Suggested Questions</div>
            {suggestions.map((s, i) => (
              <button key={i} className="ncert-sugg-btn" onClick={() => setInput(s)}>
                {s}
              </button>
            ))}
          </div>
          <div className="ncert-suggestion-card">
            <div className="ncert-suggestion-title">📌 Grounding</div>
            <div style={{ fontSize: 13, color: "#6b7db3", lineHeight: 1.7 }}>
              Answers are retrieved from the selected NCERT chapter using TF-IDF search and answered by Gemini AI. Web research activates automatically for complex questions.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}