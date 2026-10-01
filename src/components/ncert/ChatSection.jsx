import React, { useState, useRef, useEffect } from "react";
import { chat } from "@/api/Client";

export default function ChatSection({ book, chapters }) {
  const [language, setLanguage] = useState("en");
  const [chapterId, setChapterId] = useState(chapters?.[0]?.id || "");
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text:
        "Hello! I am your NCERT RAG assistant. Choose a chapter and language, then ask questions. Answers stay grounded in that chapter’s NCERT text.",
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
    if (!chapterId && chapters?.length) {
      setChapterId(chapters[0].id);
    }
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
        { role: "bot", text: "Please select a chapter so I can retrieve NCERT context.", source: "error" },
      ]);
      return;
    }
    setInput("");
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", text: msg }]);

    try {
      const data = await chat.send(chapterId, msg, [], language, book?.id, chapterNum);
      if (data.status === "error") {
        throw new Error(data.message || "The chat service could not answer.");
      }
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: data.answer || data.reply || "No answer returned.",
          source: "rag",
          sources: data.sources || [],
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
            <div className="ncert-chat-online"></div>
          </div>

          <div style={{ padding: "8px 16px", borderBottom: "1px solid #1e2540" }}>
            <select
              className="ncert-qg-select"
              value={chapterId}
              onChange={(e) => setChapterId(e.target.value)}
              style={{ width: "100%" }}
            >
              <option value="">— Select chapter for RAG context —</option>
              {chapters.map((ch) => (
                <option key={ch.id} value={ch.id}>
                  Chapter {ch.chapter_num ?? ch.chapter_number}: {ch.title}
                </option>
              ))}
            </select>
          </div>

          <div className="ncert-messages">
            {messages.map((m, i) => (
              <div key={i} className={`ncert-message ${m.role}`}>
                <div className="ncert-msg-avatar">{m.role === "bot" ? "📚" : "👤"}</div>
                <div className="ncert-msg-bubble">
                  {m.text}
                  {m.role === "bot" && m.source === "rag" && (
                    <div>
                      <span className="ncert-source-badge ncert-badge-qa">FAISS RAG · NCERT only</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="ncert-message bot">
                <div className="ncert-msg-avatar">📚</div>
                <div className="ncert-msg-bubble">
                  <div className="ncert-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="ncert-chat-input-row">
            <input
              className="ncert-chat-input"
              type="text"
              placeholder="Ask from this chapter in your chosen language…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button className="ncert-chat-send" onClick={sendMessage} disabled={loading}>
              ➤
            </button>
          </div>
        </div>

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
              Retrieval uses FAISS / similarity search on the selected chapter. The model must not invent facts outside NCERT.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
