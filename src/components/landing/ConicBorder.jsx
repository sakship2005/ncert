import React from "react";
import { motion } from "framer-motion";

// Rotating gradient light that shows through a 1px gap as an animated border
export default function ConicBorder({ accent = "#4f6ef7", active = true, duration = 6 }) {
  return (
    <motion.span
      animate={{ rotate: 360 }}
      transition={{ duration, repeat: Infinity, ease: "linear" }}
      style={{
        position: "absolute",
        top: "50%", left: "50%",
        width: "250%", aspectRatio: "1",
        marginLeft: "-125%", marginTop: "-125%",
        background: `conic-gradient(from 0deg, transparent 0deg, ${accent} 70deg, transparent 140deg, transparent 180deg, #7c3aed 250deg, transparent 320deg)`,
        opacity: active ? 1 : 0.3,
        transition: "opacity 0.4s",
        pointerEvents: "none",
      }}
    />
  );
}