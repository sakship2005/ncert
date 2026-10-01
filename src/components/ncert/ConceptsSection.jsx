import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from "recharts";

const COLORS = ["#4f6ef7", "#7c3aed", "#06b6d4", "#f472b6", "#34d399", "#f59e0b", "#ef4444", "#8b5cf6"];

export default function ConceptsSection({ book, chapters }) {
  const concepts = book?.book_analysis?.major_concepts || [];
  const top7 = concepts.slice(0, 7);
  const top5 = concepts.slice(0, 5).map((c) => c.concept);

  const heatmapData = chapters.map((c) => {
    const row = { chapter: `Ch${c.chapter_num}` };
    top5.forEach((concept) => {
      row[concept] = (c.extracted?.concepts || []).includes(concept) ? 1 : 0;
    });
    return row;
  });

  return (
    <div className="fade-in">
      <div className="ncert-section-title"><span>💡</span> Concept Frequency</div>
      <div className="ncert-grid-2">
        <div className="ncert-card">
          <div className="ncert-card-title">
            <span className="ncert-card-title-dot"></span> Concept Distribution
          </div>
          <div className="ncert-chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={concepts} layout="vertical" margin={{ left: 20, right: 20 }}>
                <XAxis type="number" tick={{ fill: "#6b7db3", fontSize: 11 }} axisLine={{ stroke: "#1e2540" }} tickLine={false} />
                <YAxis type="category" dataKey="concept" tick={{ fill: "#e8eaf6", fontSize: 12 }} axisLine={{ stroke: "#1e2540" }} tickLine={false} width={100} />
                <Tooltip contentStyle={{ background: "#131728", border: "1px solid #1e2540", borderRadius: 8 }} />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {concepts.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="ncert-card">
          <div className="ncert-card-title">
            <span className="ncert-card-title-dot" style={{ background: "#7c3aed" }}></span> Concept Radar
          </div>
          <div className="ncert-chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={top7}>
                <PolarGrid stroke="#1e2540" />
                <PolarAngleAxis dataKey="concept" tick={{ fill: "#e8eaf6", fontSize: 11 }} />
                <PolarRadiusAxis tick={{ fill: "#6b7db3", fontSize: 10 }} stroke="#1e2540" />
                <Radar dataKey="count" stroke="#4f6ef7" fill="#4f6ef7" fillOpacity={0.2} strokeWidth={2} />
                <Tooltip contentStyle={{ background: "#131728", border: "1px solid #1e2540", borderRadius: 8 }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="ncert-card">
        <div className="ncert-card-title">
          <span className="ncert-card-title-dot" style={{ background: "#06b6d4" }}></span> Concept Presence per Chapter
        </div>
        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={heatmapData} margin={{ left: 10, right: 20, bottom: 40 }}>
              <XAxis dataKey="chapter" tick={{ fill: "#6b7db3", fontSize: 9 }} axisLine={{ stroke: "#1e2540" }} tickLine={false} interval={0} />
              <YAxis tick={{ fill: "#6b7db3", fontSize: 11 }} axisLine={{ stroke: "#1e2540" }} tickLine={false} />
              <Tooltip contentStyle={{ background: "#131728", border: "1px solid #1e2540", borderRadius: 8 }} />
              {top5.map((concept, i) => (
                <Bar key={concept} dataKey={concept} stackId="a" fill={COLORS[i % COLORS.length] + "cc"} radius={2} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}