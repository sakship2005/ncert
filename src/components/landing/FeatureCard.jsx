import React from "react";
import { motion } from "framer-motion";
import TiltCard from "@/components/landing/TiltCard";

const cardIn = {
  hidden: { opacity: 0, y: 60, rotateX: -20, filter: "blur(10px)" },
  show: { opacity: 1, y: 0, rotateX: 0, filter: "blur(0px)" },
};

export default function FeatureCard({ f, i }) {
  return (
    <TiltCard
      accent={f.c}
      variants={cardIn}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.8, delay: (i % 3) * 0.12, ease: [0.22, 1, 0.36, 1] }}
    >
      <span
        style={{
          position: "absolute", top: -8, right: 0,
          fontFamily: "'Playfair Display', serif", fontSize: 44, fontWeight: 900,
          color: f.c, opacity: 0.14,
        }}
      >
        0{i + 1}
      </span>
      <motion.div
        animate={{ y: [0, -6, 0], rotate: [0, 4, 0] }}
        transition={{ duration: 3.5 + i * 0.3, repeat: Infinity, ease: "easeInOut" }}
        style={{
          width: 52, height: 52, borderRadius: 14,
          background: `${f.c}1a`, border: `1px solid ${f.c}40`, boxShadow: `0 0 24px ${f.c}30`,
          display: "flex", alignItems: "center", justifyContent: "center",
          color: f.c, marginBottom: 18,
        }}
      >
        {f.icon}
      </motion.div>
      <h3 style={{ fontSize: 19, fontWeight: 700, marginBottom: 8 }}>{f.t}</h3>
      <p style={{ fontSize: 14, color: "var(--nmuted)", lineHeight: 1.7 }}>{f.d}</p>
    </TiltCard>
  );
}