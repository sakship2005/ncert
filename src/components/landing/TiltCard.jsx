import React, { useRef, useState } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import ConicBorder from "@/components/landing/ConicBorder";

// 3D tilt card with cursor glare and glowing animated border
export default function TiltCard({ children, accent = "#4f6ef7", ...motionProps }) {
  const ref = useRef(null);
  const [hovered, setHovered] = useState(false);
  const mx = useMotionValue(0.5);
  const my = useMotionValue(0.5);
  const rotateX = useSpring(useTransform(my, [0, 1], [9, -9]), { stiffness: 160, damping: 18 });
  const rotateY = useSpring(useTransform(mx, [0, 1], [-9, 9]), { stiffness: 160, damping: 18 });
  const glare = useTransform([mx, my], ([x, y]) =>
    `radial-gradient(circle at ${x * 100}% ${y * 100}%, ${accent}40, transparent 55%)`
  );

  const onMove = (e) => {
    const r = ref.current.getBoundingClientRect();
    mx.set((e.clientX - r.left) / r.width);
    my.set((e.clientY - r.top) / r.height);
  };
  const onLeave = () => { setHovered(false); mx.set(0.5); my.set(0.5); };

  return (
    <motion.div {...motionProps} style={{ transformPerspective: 1000, height: "100%" }}>
      <motion.div
        ref={ref}
        onMouseMove={onMove}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={onLeave}
        style={{
          rotateX, rotateY, transformPerspective: 1000,
          position: "relative", borderRadius: 18, padding: 1, overflow: "hidden", height: "100%",
          background: "var(--nborder)",
          boxShadow: hovered ? `0 24px 60px -20px ${accent}90` : "0 0 0 transparent",
          transition: "box-shadow 0.35s",
        }}
      >
        <ConicBorder accent={accent} active={hovered} />
        <div style={{ position: "relative", borderRadius: 17, background: "var(--ncard)", padding: 28, height: "100%" }}>
          <motion.div
            style={{
              position: "absolute", inset: 0, borderRadius: 17, background: glare,
              opacity: hovered ? 1 : 0, transition: "opacity 0.3s", pointerEvents: "none",
            }}
          />
          <div style={{ position: "relative" }}>{children}</div>
        </div>
      </motion.div>
    </motion.div>
  );
}