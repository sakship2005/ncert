import React from "react";

export default function EmptyState({ onUpload }) {
  return (
    <div className="fade-in">
      <div className="ncert-page-header">
        <div>
          <h2 className="ncert-page-title">No Textbook Yet</h2>
          <p className="ncert-page-subtitle">This dashboard is built entirely from your own NCERT textbook uploads.</p>
        </div>
      </div>
      <div className="ncert-card" style={{ textAlign: "center", padding: "48px 24px" }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>📚</div>
        <p style={{ fontSize: 16, color: "#e8eaf6", marginBottom: 8, fontWeight: 500 }}>
          Upload an NCERT textbook to begin
        </p>
        <p style={{ fontSize: 14, color: "#6b7db3", maxWidth: 460, margin: "0 auto 24px", lineHeight: 1.7 }}>
          Any class, any subject, English or Hindi. We extract the chapters and run NLP + Gemini analysis to power every section here.
        </p>
        <button className="ncert-upload-btn" style={{ maxWidth: 220, margin: "0 auto" }} onClick={onUpload}>
          📤 Upload Textbook
        </button>
      </div>
    </div>
  );
}