import React, { useState } from "react";
import { upload } from "@/api/Client";

const STAGE = { IDLE: "idle", UPLOADING: "uploading", ANALYZING: "analyzing", DONE: "done", ERROR: "error" };

export default function UploadSection({ onBookAdded }) {
  const [file, setFile] = useState(null);
  const [meta, setMeta] = useState({ title: "", chapter_number: "", subject: "", class_level: "", language: "auto" });
  const [stage, setStage] = useState(STAGE.IDLE);
  const [progress, setProgress] = useState("");
  const [error, setError] = useState("");

  const update = (k) => (e) => setMeta({ ...meta, [k]: e.target.value });

  const canSubmit =
    file && meta.title.trim() && (stage === STAGE.IDLE || stage === STAGE.ERROR || stage === STAGE.DONE);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file || !meta.title.trim()) return;
    setError("");
    setStage(STAGE.UPLOADING);

    try {
      const data = await upload.analyzeBook(file, meta, (msg) => {
        // First progress message = still uploading, second = analysing
        if (msg.startsWith("Uploading")) {
          setStage(STAGE.UPLOADING);
        } else {
          setStage(STAGE.ANALYZING);
        }
        setProgress(msg);
      });

      setStage(STAGE.DONE);
      const chapterCount = data.chapters_detected || data.chapters?.length || 0;
      setProgress(`Analysed ${chapterCount} chapters. Your textbook is ready to explore.`);
      setFile(null);
      setMeta({ title: "", chapter_number: "", subject: "", class_level: "", language: "auto" });
      if (onBookAdded) onBookAdded(data.book_id);
    } catch (err) {
      setError(err.message || "Something went wrong.");
      setStage(STAGE.ERROR);
    }
  }

  const busy = stage === STAGE.UPLOADING || stage === STAGE.ANALYZING;

  return (
    <div className="fade-in">
      <div className="ncert-page-header">
        <div>
          <h2 className="ncert-page-title">Upload NCERT Textbook</h2>
          <p className="ncert-page-subtitle">
            Upload any NCERT PDF — any class, any subject. We extract chapters and run NLP + Gemini
            analysis automatically.
          </p>
        </div>
      </div>

      <form className="ncert-card" style={{ maxWidth: 640 }} onSubmit={handleSubmit}>
        <div className="ncert-upload-dropzone">
          <label className="ncert-upload-label">
            <input
              type="file"
              accept="application/pdf"
              disabled={busy}
              onChange={(e) => setFile(e.target.files[0] || null)}
              style={{ display: "none" }}
            />
            <span className="ncert-upload-icon">📄</span>
            <span className="ncert-upload-text">{file ? file.name : "Choose a PDF file"}</span>
            <span className="ncert-upload-hint">NCERT textbook (English or Hindi)</span>
          </label>
        </div>

        <div className="ncert-upload-fields">
          <div className="ncert-field">
            <label className="ncert-field-label">Title *</label>
            <input
              className="ncert-field-input"
              value={meta.title}
              onChange={update("title")}
              disabled={busy}
              placeholder="e.g. Science Class 10"
            />
          </div>
          <div className="ncert-field">
            <label className="ncert-field-label">Chapter number</label>
            <input
              className="ncert-field-input"
              type="number"
              min="1"
              value={meta.chapter_number}
              onChange={update("chapter_number")}
              disabled={busy}
              placeholder="e.g. 2"
            />
          </div>
          <div className="ncert-field">
            <label className="ncert-field-label">Subject</label>
            <input
              className="ncert-field-input"
              value={meta.subject}
              onChange={update("subject")}
              disabled={busy}
              placeholder="e.g. Science"
            />
          </div>
          <div className="ncert-field">
            <label className="ncert-field-label">Class</label>
            <input
              className="ncert-field-input"
              value={meta.class_level}
              onChange={update("class_level")}
              disabled={busy}
              placeholder="e.g. 10"
            />
          </div>
          <div className="ncert-field">
            <label className="ncert-field-label">Language</label>
            <select
              className="ncert-field-input"
              value={meta.language}
              onChange={update("language")}
              disabled={busy}
            >
              <option value="auto">Auto-detect</option>
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="both">Both</option>
            </select>
          </div>
        </div>

        <button type="submit" className="ncert-upload-btn" disabled={!canSubmit || busy}>
          {busy ? "Processing…" : "Analyse Textbook"}
        </button>

        {busy && (
          <div className="ncert-upload-progress">
            <div className="ncert-spinner" style={{ width: 28, height: 28 }}></div>
            <span>{progress}</span>
          </div>
        )}
        {stage === STAGE.DONE && !busy && (
          <div className="ncert-upload-success">✅ {progress}</div>
        )}
        {error && <div className="ncert-upload-error">❌ {error}</div>}
      </form>
    </div>
  );
}