import React, { useEffect, useRef } from "react";

const COLORS = ["79,110,247", "124,58,237", "6,182,212", "244,114,182"];

// Interactive "knowledge network" — nodes drift, connect, and react to the cursor
export default function ConstellationCanvas() {
  const ref = useRef(null);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas.getContext("2d");
    const mouse = { x: -9999, y: -9999 };
    let w = 0, h = 0, nodes = [], raf;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      w = window.innerWidth; h = window.innerHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      nodes = Array.from({ length: Math.min(80, Math.floor((w * h) / 18000)) }, () => ({
        x: Math.random() * w, y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3,
        r: 1 + Math.random() * 1.6, p: Math.random() * 6.28,
        c: COLORS[Math.floor(Math.random() * COLORS.length)],
      }));
    };

    const draw = () => {
      ctx.clearRect(0, 0, w, h);
      nodes.forEach((n) => {
        n.x += n.vx; n.y += n.vy; n.p += 0.03;
        if (n.x < 0 || n.x > w) n.vx *= -1;
        if (n.y < 0 || n.y > h) n.vy *= -1;
        const dx = n.x - mouse.x, dy = n.y - mouse.y, d = Math.hypot(dx, dy) || 1;
        if (d < 120) { n.x += (dx / d) * 1.2; n.y += (dy / d) * 1.2; }
        n.x = Math.max(0, Math.min(w, n.x)); n.y = Math.max(0, Math.min(h, n.y));
      });
      ctx.lineWidth = 0.7;
      for (let i = 0; i < nodes.length; i++) {
        const a = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const b = nodes[j];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < 130) {
            ctx.strokeStyle = `rgba(${a.c},${(1 - d / 130) * 0.35})`;
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
          }
        }
        const md = Math.hypot(a.x - mouse.x, a.y - mouse.y);
        if (md < 200) {
          ctx.strokeStyle = `rgba(167,139,250,${(1 - md / 200) * 0.5})`;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
        }
        ctx.fillStyle = `rgba(${a.c},${0.55 + Math.sin(a.p) * 0.35})`;
        ctx.beginPath(); ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2); ctx.fill();
      }
      raf = requestAnimationFrame(draw);
    };

    const onMove = (e) => { mouse.x = e.clientX; mouse.y = e.clientY; };
    resize(); draw();
    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", onMove);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", onMove);
    };
  }, []);

  return <canvas ref={ref} style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />;
}