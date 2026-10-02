import React from "react";
import { motion } from "framer-motion";

// Button with a periodic light sweep and springy hover
export default function ShineButton({ children, style, onClick }) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.97 }}
      style={{ position: "relative", overflow: "hidden", display: "inline-flex", alignItems: "center", ...style }}
    >
      <motion.span
        animate={{ x: ["-150%", "350%"] }}
        transition={{ duration: 2.2, repeat: Infinity, repeatDelay: 2, ease: "easeInOut" }}
        style={{
          position: "absolute", top: 0, bottom: 0, left: 0, width: "35%",
          background: "linear-gradient(100deg, transparent, rgba(255,255,255,0.4), transparent)",
          pointerEvents: "none",
        }}
      />
      <span style={{ position: "relative", display: "inline-flex", alignItems: "center", gap: 10 }}>{children}</span>
    </motion.button>
  );
}