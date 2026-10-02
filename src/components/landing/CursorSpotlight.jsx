import React, { useEffect } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";

// Soft glow that smoothly trails the cursor
export default function CursorSpotlight() {
  const x = useMotionValue(-1000);
  const y = useMotionValue(-1000);
  const sx = useSpring(x, { stiffness: 70, damping: 20 });
  const sy = useSpring(y, { stiffness: 70, damping: 20 });

  useEffect(() => {
    const onMove = (e) => { x.set(e.clientX - 300); y.set(e.clientY - 300); };
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, [x, y]);

  return (
    <motion.div
      style={{
        position: "absolute",
        left: 0, top: 0,
        x: sx, y: sy,
        width: 600, height: 600,
        borderRadius: "50%",
        background: "radial-gradient(circle, rgba(124,58,237,0.2), rgba(79,110,247,0.08) 40%, transparent 70%)",
        mixBlendMode: "screen",
      }}
    />
  );
}