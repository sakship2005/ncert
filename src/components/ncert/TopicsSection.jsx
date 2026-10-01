import React from "react";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Legend,
} from "recharts";

const COLORS = ["#4f6ef7", "#7c3aed", "#06b6d4", "#f472b6", "#34d399", "#f59e0b", "#ef4444", "#8b5cf6"];
const TOPIC_COLORS = {
  Theory: "#fde68a", Process: "#c7d2fe", Definition: "#fecdd3",
  Experiment: "#a5f3fc", Application: "#d8b4fe", Analysis: "#86efac",
  "बिग्यान": "#6ee7b7", "प्रक्रिया": "#fcd34d",
};

export default function TopicsSection({ book, chapters }) {
  const topics = book?.book_analysis?.topic_categories || [];
  const top3 = topics.slice(0, 3).map((t) => t.topic);

  const arcData = chapters.map((c) => {
    const row = { chapter: `Ch${c.chapter_num}` };
    top3.forEach((topic) => {
      row[topic] = (c.extracted?.topics || []).includes(topic) ? 1 : 0;
    });
    return row;
  });

  return (
    <div className="fade-in">
      <div className="ncert-section-title"><span>🎭</span> Topic Analysis</div>
      <div className="ncert-topic-grid" style={{ marginBottom: 28 }}>
        {topics.map((t, i) => {
          const bg = TOPIC_COLORS[t.topic] || COLORS[i % COLORS.length];
          return (
            <div
              key={i}
              className="ncert-topic-pill"
              style={{ background: bg + "20", borderColor: bg + "40" }}
            >
              <div className="ncert-topic-name" style={{ color: bg }}>{t.topic}</div>
              <div className="ncert-topic-count" style={{ color: bg }}>{t.count} chapters</div>
            </div>
          );
        })}
      </div>

      <div className="ncert-grid-2">
        <div className="ncert-card">
          <div className="ncert-card-title">
            <span className="ncert-card-title-dot"></span> Topic Frequency
          </div>
          <div className="ncert-chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={topics} dataKey="count" nameKey="topic" cx="50%" cy="50%" outerRadius={100} paddingAngle={2}>
                  {topics.map((t, i) => (
                    <Cell key={i} fill={(TOPIC_COLORS[t.topic] || COLORS[i % COLORS.length]) + "88"} stroke={TOPIC_COLORS[t.topic] || COLORS[i % COLORS.length]} strokeWidth={1.5} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#131728", border: "1px solid #1e2540", borderRadius: 8 }} />
                <Legend wrapperStyle={{ fontSize: 11, color: "#e8eaf6" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="ncert-card">
          <div className="ncert-card-title">
            <span className="ncert-card-title-dot" style={{ background: "#7c3aed" }}></span> Topic Arc
          </div>
          <div className="ncert-chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={arcData} margin={{ left: 0, right: 20, bottom: 40 }}>
                <CartesianGrid stroke="#1e2540" />
                <XAxis dataKey="chapter" tick={{ fill: "#6b7db3", fontSize: 9 }} axisLine={{ stroke: "#1e2540" }} tickLine={false} interval={0} />
                <YAxis tick={{ fill: "#6b7db3", fontSize: 11 }} axisLine={{ stroke: "#1e2540" }} tickLine={false} />
                <Tooltip contentStyle={{ background: "#131728", border: "1px solid #1e2540", borderRadius: 8 }} />
                <Legend wrapperStyle={{ fontSize: 11, color: "#e8eaf6" }} />
                {top3.map((topic, i) => (
                  <Line key={topic} type="monotone" dataKey={topic} stroke={COLORS[i]} strokeWidth={2} dot={{ r: 2 }} fill={COLORS[i] + "22"} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}