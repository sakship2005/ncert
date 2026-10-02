import React from "react";
import { motion } from "framer-motion";

const GRAD = "linear-gradient(135deg, var(--naccent1), var(--naccent2))";

export default function StepCard({ s, i }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50, scale: 0.85 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true, amount: 0.4 }}
      transition={{ duration: 0.7, delay: 0.3 + i * 0.35, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -8, transition: { duration: 0.25 } }}
      style={{ textAlign: "center", position: "relative", zIndex: 1 }}
    >
      <div style={{ position: "relative", display: "inline-flex", marginBottom: 24 }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 14, repeat: Infinity, ease: "linear" }}
          style={{ position: "absolute", inset: -12, borderRadius: "50%", border: "1.5px dashed rgba(124,58,237,0.55)" }}
        />
        <motion.div
          animate={{ scale: [1, 1.5], opacity: [0.45, 0] }}
          transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.8, ease: "easeOut" }}
          style={{ position: "absolute", inset: 0, borderRadius: 20, background: GRAD }}
        />
        <div style={{
          position: "relative", width: 72, height: 72, borderRadius: 20, background: GRAD,
          display: "flex", alignItems: "center", justifyContent: "center", color: "#fff",
          boxShadow: "0 10px 30px -8px rgba(124,58,237,0.6)",
        }}>
          {s.icon}
        </div>
        <div style={{
          position: "absolute", top: -8, right: -8, zIndex: 2,
          width: 28, height: 28, borderRadius: "50%",
          background: "var(--ncard)", border: "1px solid var(--naccent1)",
          color: "var(--naccent1)", fontSize: 13, fontWeight: 700,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontFamily: "'Playfair Display', serif",
        }}>
          {s.n}
        </div>
      </div>
      <h3 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>{s.t}</h3>
      <p style={{ fontSize: 14, color: "var(--nmuted)", lineHeight: 1.7, maxWidth: 240, margin: "0 auto" }}>{s.d}</p>
    </motion.div>
  );
}