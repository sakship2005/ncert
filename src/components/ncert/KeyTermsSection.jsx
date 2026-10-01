import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip,
} from "recharts";

const COLORS = ["#4f6ef7", "#7c3aed", "#06b6d4", "#f472b6", "#34d399", "#f59e0b", "#ef4444", "#8b5cf6", "#10b981", "#3b82f6"];

export default function KeyTermsSection({ book }) {
  const terms = (book?.book_analysis?.key_terms || []).slice(0, 12);

  if (terms.length === 0) {
    return (
      <div className="fade-in">
        <div className="ncert-section-title"><span>🔬</span> Key Terms</div>
        <div className="ncert-card"><p style={{ color: "#6b7db3" }}>No key terms available.</p></div>
      </div>
    );
  }

  const max = terms[0].count || 1;

  return (
    <div className="fade-in">
      <div className="ncert-section-title"><span>🔬</span> Key Term Mentions</div>
      <div className="ncert-grid-2">
        <div className="ncert-card">
          <div className="ncert-card-title">
            <span className="ncert-card-title-dot"></span> Mention Count
          </div>
          <div className="ncert-term-list">
            {terms.map((t, i) => (
              <div className="ncert-term-row" key={i}>
                <div
                  className="ncert-term-avatar"
                  style={{ background: `linear-gradient(135deg, ${COLORS[i % 10]}, ${COLORS[(i + 2) % 10]})` }}
                >
                  {t.name.charAt(0).toUpperCase()}
                </div>
                <div className="ncert-term-info">
                  <div className="ncert-term-name">{t.name}</div>
                  <div className="ncert-term-bar-wrap">
                    <div
                      className="ncert-term-bar"
                      style={{ width: `${Math.round((t.count / max) * 100)}%`, background: COLORS[i % 10] }}
                    ></div>
                  </div>
                </div>
                <div className="ncert-term-count">{t.count}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="ncert-card">
          <div className="ncert-card-title">
            <span className="ncert-card-title-dot" style={{ background: "#7c3aed" }}></span> Key Terms Chart
          </div>
          <div className="ncert-chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={terms} layout="vertical" margin={{ left: 20, right: 20 }}>
                <XAxis type="number" tick={{ fill: "#6b7db3", fontSize: 11 }} axisLine={{ stroke: "#1e2540" }} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fill: "#e8eaf6", fontSize: 12 }} axisLine={{ stroke: "#1e2540" }} tickLine={false} width={100} />
                <Tooltip contentStyle={{ background: "#131728", border: "1px solid #1e2540", borderRadius: 8 }} />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {terms.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}