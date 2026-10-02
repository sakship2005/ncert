import React from "react";
import { motion } from "framer-motion";
import ConstellationCanvas from "@/components/landing/ConstellationCanvas";
import FloatingGlyphs from "@/components/landing/FloatingGlyphs";
import CursorSpotlight from "@/components/landing/CursorSpotlight";

// Modern 2026 animated background — aurora orbs, particles, light streaks,
// rotating conic ring, floating shapes, animated grid and aurora wave
export default function AnimatedBackground() {
  const orbs = [
    { c: "rgba(79, 110, 247, 0.38)", size: 560, x: "-10%", y: "-14%", dur: 16, dx: 70, dy: 50 },
    { c: "rgba(124, 58, 237, 0.34)", size: 480, x: "72%", y: "6%", dur: 20, dx: -80, dy: 60 },
    { c: "rgba(6, 182, 212, 0.24)", size: 400, x: "55%", y: "60%", dur: 24, dx: -60, dy: -70 },
    { c: "rgba(244, 114, 182, 0.20)", size: 340, x: "10%", y: "68%", dur: 22, dx: 90, dy: -40 },
    { c: "rgba(52, 211, 153, 0.16)", size: 300, x: "38%", y: "32%", dur: 28, dx: -50, dy: 40 },
  ];

  const streaks = Array.from({ length: 6 }, (_, i) => ({
    id: i,
    top: `${10 + i * 15}%`,
    delay: i * 1.8,
    dur: 6 + (i % 3),
    rotate: -25 + (i % 2) * 5,
  }));

  const shapes = [
    { c: "#4f6ef7", size: 14, x: "18%", y: "22%", dur: 9, type: "ring" },
    { c: "#7c3aed", size: 10, x: "82%", y: "30%", dur: 11, type: "dot" },
    { c: "#06b6d4", size: 18, x: "64%", y: "78%", dur: 13, type: "ring" },
    { c: "#f472b6", size: 8, x: "30%", y: "82%", dur: 8, type: "dot" },
    { c: "#34d399", size: 12, x: "48%", y: "14%", dur: 12, type: "ring" },
  ];

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 0,
        overflow: "hidden",
        pointerEvents: "none",
      }}
    >
      {/* Aurora orbs */}
      {orbs.map((o, i) => (
        <motion.div
          key={`orb-${i}`}
          animate={{ x: [0, o.dx, 0], y: [0, o.dy, 0], scale: [1, 1.2, 1] }}
          transition={{ duration: o.dur, repeat: Infinity, ease: "easeInOut" }}
          style={{
            position: "absolute",
            left: o.x, top: o.y,
            width: o.size, height: o.size,
            borderRadius: "50%",
            background: o.c,
            filter: "blur(100px)",
          }}
        />
      ))}

      {/* Rotating conic gradient ring */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        style={{
          position: "absolute",
          top: "8%", left: "50%",
          marginLeft: "-350px",
          width: 700, height: 700,
          borderRadius: "50%",
          background:
            "conic-gradient(from 0deg, transparent, rgba(79,110,247,0.12), transparent, rgba(124,58,237,0.12), transparent)",
          filter: "blur(40px)",
          opacity: 0.6,
        }}
      />

      {/* Shooting light streaks */}
      {streaks.map((s) => (
        <motion.div
          key={`streak-${s.id}`}
          initial={{ x: "-20vw", opacity: 0 }}
          animate={{ x: "120vw", opacity: [0, 1, 0] }}
          transition={{ duration: s.dur, repeat: Infinity, delay: s.delay, ease: "easeIn" }}
          style={{
            position: "absolute",
            top: s.top,
            width: 160, height: 2,
            rotate: `${s.rotate}deg`,
            background: "linear-gradient(90deg, transparent, rgba(124,58,237,0.9), rgba(79,110,247,0.4), transparent)",
            filter: "blur(1px)",
            boxShadow: "0 0 12px rgba(124,58,237,0.8)",
          }}
        />
      ))}

      {/* Floating geometric shapes */}
      {shapes.map((s, i) => (
        <motion.div
          key={`shape-${i}`}
          animate={{ y: [0, -24, 0], rotate: [0, 180, 360], opacity: [0.4, 0.9, 0.4] }}
          transition={{ duration: s.dur, repeat: Infinity, ease: "easeInOut", delay: i * 0.5 }}
          style={{
            position: "absolute",
            left: s.x, top: s.y,
            width: s.size, height: s.size,
            borderRadius: s.type === "ring" ? "50%" : "30%",
            border: s.type === "ring" ? `2px solid ${s.c}` : "none",
            background: s.type === "ring" ? "transparent" : s.c,
            boxShadow: s.type === "dot" ? `0 0 10px ${s.c}` : "none",
          }}
        />
      ))}

      {/* Interactive knowledge network */}
      <ConstellationCanvas />

      {/* Rising multilingual glyphs */}
      <FloatingGlyphs />

      {/* Animated grid */}
      <motion.div
        animate={{ opacity: [0.12, 0.28, 0.12], scale: [1, 1.05, 1] }}
        transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(79,110,247,0.09) 1px, transparent 1px), linear-gradient(90deg, rgba(79,110,247,0.09) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
          maskImage: "radial-gradient(ellipse at center, black 25%, transparent 78%)",
          WebkitMaskImage: "radial-gradient(ellipse at center, black 25%, transparent 78%)",
        }}
      />

      {/* Sheen sweep */}
      <motion.div
        animate={{ x: ["-100%", "130%"] }}
        transition={{ duration: 11, repeat: Infinity, ease: "linear" }}
        style={{
          position: "absolute",
          top: 0, left: 0,
          width: "45%", height: "100%",
          background: "linear-gradient(90deg, transparent, rgba(124,58,237,0.06), transparent)",
          filter: "blur(40px)",
        }}
      />

      {/* Aurora wave at bottom */}
      <motion.svg
        animate={{ y: [0, -12, 0] }}
        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
        style={{ position: "absolute", bottom: -20, left: 0, width: "100%", height: 180 }}
        viewBox="0 0 1440 180"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient id="waveg" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="rgba(79,110,247,0.25)" />
            <stop offset="50%" stopColor="rgba(124,58,237,0.25)" />
            <stop offset="100%" stopColor="rgba(6,182,212,0.25)" />
          </linearGradient>
        </defs>
        <motion.path
          animate={{
            d: [
              "M0,100 C320,160 480,40 720,90 C960,140 1120,30 1440,80 L1440,180 L0,180 Z",
              "M0,120 C320,60 520,150 720,110 C940,70 1140,150 1440,100 L1440,180 L0,180 Z",
              "M0,100 C320,160 480,40 720,90 C960,140 1120,30 1440,80 L1440,180 L0,180 Z",
            ],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          fill="url(#waveg)"
          filter="blur(2px)"
        />
      </motion.svg>

      {/* Cursor-following glow */}
      <CursorSpotlight />
    </div>
  );
}