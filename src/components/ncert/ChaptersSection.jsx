import React, { useEffect, useState } from "react";
import { nlp } from "@/api/Client";

export default function ChaptersSection({ chapters }) {
  const [openIdx, setOpenIdx] = useState(null);
  const [chapterAnalysis, setChapterAnalysis] = useState({});

  useEffect(() => {
    let active = true;

    async function loadAnalysis() {
      const results = await Promise.all(
        chapters.map(async (chapter) => {
          try {
            const chapterNum = chapter.chapter_num ?? chapter.chapter_number;
            const data = await nlp.getChapterAnalysis(null, chapterNum, chapter.id);
            return [chapter.id, data.status === "success" ? data : null];
          } catch {
            return [chapter.id, null];
          }
        })
      );

      if (active) {
        setChapterAnalysis(Object.fromEntries(results.filter(([, data]) => data)));
      }
    }

    if (chapters.length > 0) loadAnalysis();
    return () => {
      active = false;
    };
  }, [chapters]);

  const toggle = (idx) => setOpenIdx(openIdx === idx ? null : idx);

  return (
    <div className="fade-in">
      <div className="ncert-section-title"><span>📖</span> Chapter Explorer</div>
      <div className="ncert-chapter-list">
        {chapters.map((ch, idx) => {
          const ext = chapterAnalysis[ch.id] || ch.extracted || {};
          const conceptNames = (ext.concepts || [])
            .map((concept) => typeof concept === "string" ? concept : concept.concept || concept.name)
            .filter(Boolean);
          const topicNames = (ext.topics || []).flatMap((topic) => topic.words || topic.keywords || []);
          const entityNames = ["persons", "locations", "organizations"]
            .flatMap((category) => (ext.entities?.[category] || []).map((entity) => entity.name || entity));
          const tags = [
            ...conceptNames.slice(0, 2).map((t) => ({ text: t, cls: "ncert-tag-concept" })),
            ...topicNames.slice(0, 2).map((t) => ({ text: t, cls: "ncert-tag-topic" })),
            ...entityNames.slice(0, 2).map((t) => ({ text: t, cls: "ncert-tag-term" })),
          ];
          const kwChips = [...conceptNames, ...topicNames, ...entityNames].slice(0, 8);
          const keyPoints = ext.key_points?.length
            ? ext.key_points
            : [...entityNames, ...topicNames].slice(0, 8);

          return (
            <div
              key={idx}
              className={`ncert-chapter-item ${openIdx === idx ? "open" : ""}`}
              onClick={() => toggle(idx)}
            >
              <div className="ncert-ch-num">{ch.chapter_num}</div>
              <div className="ncert-ch-meta">
                <div className="ncert-ch-title">{ch.title || "Untitled"}</div>
                <div className="ncert-ch-tags">
                  {tags.map((t, i) => (
                    <span key={i} className={`ncert-tag ${t.cls}`}>{t.text}</span>
                  ))}
                </div>
                <div className="ncert-ch-detail">
                  <p className="ncert-summary-text">{(ch.summary || "").substring(0, 300)}…</p>
                  <div className="ncert-detail-grid">
                    <div className="ncert-detail-box">
                      <div className="ncert-detail-box-title">🔑 Keywords</div>
                      {kwChips.map((k, i) => (
                        <span key={i} className="ncert-kw-chip">{k}</span>
                      ))}
                    </div>
                    <div className="ncert-detail-box">
                      <div className="ncert-detail-box-title">📌 Key Points</div>
                      {keyPoints.length > 0 ? (
                        keyPoints.map((e, i) => (
                          <div key={i} style={{ fontSize: 13, padding: "4px 0", borderBottom: "1px solid #1e2540", color: "#6b7db3" }}>
                            • {e}
                          </div>
                        ))
                      ) : (
                        <span style={{ color: "#6b7db3", fontSize: 13 }}>—</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              <div className="ncert-ch-arrow">›</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}