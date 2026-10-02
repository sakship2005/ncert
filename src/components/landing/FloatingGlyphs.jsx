import React from "react";
import { motion } from "framer-motion";

const GLYPHS = ["अ", "A", "π", "ज्ञान", "∑", "क", "Ω", "√", "θ", "ह", "∞", "Δ", "λ", "स", "α", "ब"];
const COLORS = ["#4f6ef7", "#7c3aed", "#06b6d4", "#f472b6"];

// Multilingual letters & symbols rising slowly with parallax depth
export default function FloatingGlyphs() {
  return (
    <>
      {GLYPHS.map((g, i) => {
        const depth = (i % 3) + 1; // 1 = far, 3 = near
        const peak = 0.12 + depth * 0.1;
        return (
          <motion.span
            key={i}
            initial={{ y: "110vh", opacity: 0 }}
            animate={{ y: "-15vh", opacity: [0, peak, peak, 0], rotate: [0, i % 2 ? 30 : -30] }}
            transition={{ duration: 30 - depth * 5, repeat: Infinity, delay: i * 0.9, ease: "linear" }}
            style={{
              position: "absolute",
              top: 0,
              left: `${(i * 61 + 7) % 94}%`,
              fontFamily: "'Playfair Display', serif",
              fontSize: 18 + depth * 14,
              fontWeight: 700,
              color: COLORS[i % 4],
              filter: `blur(${(3 - depth) * 1.5}px)`,
              textShadow: "0 0 24px currentColor",
            }}
          >
            {g}
          </motion.span>
        );
      })}
    </>
  );
}