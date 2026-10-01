import React from "react";

export default function PageNotFound() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        color: "#6b7db3",
        fontFamily: "sans-serif",
      }}
    >
      <div style={{ fontSize: 48, marginBottom: 16 }}>404</div>
      <p style={{ fontSize: 16 }}>Page not found.</p>
      <a href="/" style={{ marginTop: 12, color: "#4f6ef7", textDecoration: "none" }}>
        ← Back to dashboard
      </a>
    </div>
  );
}