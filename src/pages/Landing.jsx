import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  BookOpen,
  Sparkles,
  MessageCircle,
  Upload,
  Search,
  BarChart3,
  ArrowRight,
  GraduationCap,
  Languages,
  Lightbulb,
} from "lucide-react";
import AnimatedBackground from "@/components/ncert/AnimatedBackground";
import FeatureCard from "@/components/landing/FeatureCard";
import StepCard from "@/components/landing/StepCard";
import ShineButton from "@/components/landing/ShineButton";
import ConicBorder from "@/components/landing/ConicBorder";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0 },
};

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="ncert-app">
      <AnimatedBackground />
      <div className="ncert-content" style={{ position: "relative", zIndex: 2 }}>
        {/* Nav */}
        <motion.nav
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          style={{
            position: "fixed",
            top: 0, left: 0, right: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "20px 48px",
            zIndex: 200,
            background: "rgba(7, 8, 15, 0.7)",
            backdropFilter: "blur(12px)",
            borderBottom: "1px solid var(--nborder)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 38, height: 38, borderRadius: 10,
                background: "linear-gradient(135deg, var(--naccent1), var(--naccent2))",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}
            >
              <GraduationCap size={20} color="#fff" />
            </div>
            <span style={{ fontFamily: "'Playfair Display', serif", fontWeight: 900, fontSize: 20 }}>
              Learnly
            </span>
          </div>
          <button
            onClick={() => navigate("/dashboard")}
            style={{
              padding: "10px 22px", borderRadius: 10, border: "none", cursor: "pointer",
              background: "linear-gradient(135deg, var(--naccent1), var(--naccent2))",
              color: "#fff", fontSize: 14, fontWeight: 600,
              fontFamily: "'DM Sans', sans-serif",
              display: "flex", alignItems: "center", gap: 8,
            }}
          >
            Get Started <ArrowRight size={16} />
          </button>
        </motion.nav>

        {/* Hero */}
        <section style={{ padding: "160px 48px 80px", maxWidth: 1100, margin: "0 auto", textAlign: "center" }}>
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="show"
            transition={{ duration: 0.7, delay: 0.1 }}
            style={{
              display: "inline-flex", alignItems: "center", gap: 8,
              padding: "8px 16px", borderRadius: 30,
              background: "rgba(79, 110, 247, 0.12)",
              border: "1px solid rgba(79, 110, 247, 0.3)",
              fontSize: 13, color: "#a5b4fc", marginBottom: 28,
            }}
          >
            <Sparkles size={15} /> Your books, now smart
          </motion.div>

          <motion.h1
            variants={fadeUp}
            initial="hidden"
            animate="show"
            transition={{ duration: 0.7, delay: 0.2 }}
            style={{
              fontFamily: "'Playfair Display', serif",
              fontSize: "clamp(40px, 6vw, 76px)",
              fontWeight: 900, lineHeight: 1.1, marginBottom: 24,
            }}
          >
            {"Turn any book into".split(" ").map((w, i) => (
              <motion.span
                key={i}
                initial={{ opacity: 0, y: 30, filter: "blur(10px)" }}
                animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                transition={{ duration: 0.7, delay: 0.25 + i * 0.12, ease: [0.22, 1, 0.36, 1] }}
                style={{
                  display: "inline-block", marginRight: "0.25em",
                  background: "linear-gradient(180deg, var(--ntext), #a5b4fc)",
                  WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
                }}
              >
                {w}
              </motion.span>
            ))}
            <br />
            <motion.span
              animate={{ backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }}
              transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
              style={{
                background: "linear-gradient(90deg, var(--naccent1), var(--naccent2), var(--naccent3), var(--naccent1))",
                backgroundSize: "300% 100%",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              your smart study buddy
            </motion.span>
          </motion.h1>

          <motion.p
            variants={fadeUp}
            initial="hidden"
            animate="show"
            transition={{ duration: 0.7, delay: 0.3 }}
            style={{ fontSize: 19, color: "var(--nmuted)", maxWidth: 620, margin: "0 auto 40px", lineHeight: 1.7 }}
          >
            Just upload your book. We read it, understand it, and help you study it —
            with summaries, key ideas, and answers to your questions, in your words.
          </motion.p>

          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="show"
            transition={{ duration: 0.7, delay: 0.4 }}
            style={{ display: "flex", gap: 16, justifyContent: "center", flexWrap: "wrap" }}
          >
            <ShineButton
              onClick={() => navigate("/dashboard")}
              style={{
                padding: "16px 32px", borderRadius: 12, border: "none", cursor: "pointer",
                background: "linear-gradient(135deg, var(--naccent1), var(--naccent2))",
                color: "#fff", fontSize: 16, fontWeight: 600,
                fontFamily: "'DM Sans', sans-serif",
                boxShadow: "0 0 30px rgba(79, 110, 247, 0.4)",
              }}
            >
              <Upload size={18} /> Upload your book
            </ShineButton>
            <button
              onClick={() => navigate("/dashboard")}
              style={{
                padding: "16px 32px", borderRadius: 12, cursor: "pointer",
                background: "transparent", border: "1px solid var(--nborder)",
                color: "var(--ntext)", fontSize: 16, fontWeight: 500,
                fontFamily: "'DM Sans', sans-serif",
                display: "flex", alignItems: "center", gap: 10,
              }}
            >
              See how it works <ArrowRight size={18} />
            </button>
          </motion.div>

          {/* Floating book cards */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            style={{ marginTop: 64, display: "flex", gap: 18, justifyContent: "center", flexWrap: "wrap" }}
          >
            {[
              { icon: <BookOpen size={22} />, label: "Any subject", c: "var(--naccent1)" },
              { icon: <Languages size={22} />, label: "English & हिंदी", c: "var(--naccent2)" },
              { icon: <GraduationCap size={22} />, label: "Any class", c: "var(--naccent3)" },
            ].map((b, i) => (
              <motion.div
                key={i}
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 3, repeat: Infinity, delay: i * 0.4, ease: "easeInOut" }}
                whileHover={{ scale: 1.08, transition: { duration: 0.25 } }}
                style={{
                  display: "flex", alignItems: "center", gap: 12,
                  padding: "16px 24px", borderRadius: 14,
                  background: "rgba(19, 23, 40, 0.55)", border: "1px solid rgba(124, 58, 237, 0.25)",
                  backdropFilter: "blur(12px)",
                  boxShadow: "0 10px 40px -12px rgba(79, 110, 247, 0.45), inset 0 1px 0 rgba(255,255,255,0.06)",
                  fontSize: 15, fontWeight: 500, cursor: "default",
                }}
              >
                <span style={{ color: b.c }}>{b.icon}</span> {b.label}
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* Features */}
        <section style={{ padding: "60px 48px", maxWidth: 1100, margin: "0 auto" }}>
          <motion.h2
            variants={fadeUp}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            style={{ fontFamily: "'Playfair Display', serif", fontSize: 40, fontWeight: 900, textAlign: "center", marginBottom: 14 }}
          >
            Everything you need to <span style={{ background: "linear-gradient(135deg, var(--naccent1), var(--naccent2))", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>understand your book</span>
          </motion.h2>
          <motion.p
            variants={fadeUp}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            style={{ textAlign: "center", color: "var(--nmuted)", fontSize: 16, marginBottom: 56 }}
          >
            From the first page to exam day, your book works for you.
          </motion.p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 22 }}>
            {[
              { icon: <Upload size={24} />, c: "#4f6ef7", t: "Add your book", d: "Drop in any book PDF. We read every page and learn what's inside." },
              { icon: <Lightbulb size={24} />, c: "#7c3aed", t: "See the key ideas", d: "Get short summaries and the most important points in seconds." },
              { icon: <Search size={24} />, c: "#06b6d4", t: "Find anything fast", d: "Search your whole book and jump straight to what matters." },
              { icon: <MessageCircle size={24} />, c: "#f472b6", t: "Ask questions", d: "Chat with your book and get clear answers in your own words." },
              { icon: <BarChart3 size={24} />, c: "#34d399", t: "Know what's important", d: "See which topics and words come up the most." },
              { icon: <Sparkles size={24} />, c: "#4f6ef7", t: "Practice anytime", d: "Turn your book into questions and test yourself when you want." },
            ].map((f, i) => (
              <FeatureCard key={i} f={f} i={i} />
            ))}
          </div>
        </section>

        {/* How it works */}
        <section style={{ padding: "80px 48px", maxWidth: 1100, margin: "0 auto" }}>
          <motion.h2
            variants={fadeUp}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            style={{ fontFamily: "'Playfair Display', serif", fontSize: 40, fontWeight: 900, textAlign: "center", marginBottom: 56 }}
          >
            Three easy steps
          </motion.h2>
          <div style={{ position: "relative", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 28 }}>
            <motion.div
              className="landing-steps-line"
              initial={{ scaleX: 0 }}
              whileInView={{ scaleX: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1.4, delay: 0.3, ease: "easeInOut" }}
              style={{
                position: "absolute", top: 36, left: "17%", right: "17%", height: 2,
                transformOrigin: "left", opacity: 0.7,
                background: "linear-gradient(90deg, var(--naccent1), var(--naccent2), var(--naccent3))",
              }}
            >
              <motion.span
                animate={{ left: ["0%", "100%"] }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                style={{
                  position: "absolute", top: -4, width: 10, height: 10, marginLeft: -5, borderRadius: "50%",
                  background: "#fff", boxShadow: "0 0 12px #7c3aed, 0 0 24px #4f6ef7",
                }}
              />
            </motion.div>
            {[
              { n: "1", icon: <Upload size={22} />, t: "Upload", d: "Add your book PDF. Tell us the subject and class — that's it." },
              { n: "2", icon: <BookOpen size={22} />, t: "Explore", d: "We read your book and show you summaries, key ideas, and topics." },
              { n: "3", icon: <MessageCircle size={22} />, t: "Ask & learn", d: "Ask questions, search, and practice — your book answers back." },
            ].map((s, i) => (
              <StepCard key={i} s={s} i={i} />
            ))}
          </div>
        </section>

        {/* CTA */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          style={{ padding: "40px 48px 100px", maxWidth: 1000, margin: "0 auto" }}
        >
          <div style={{ position: "relative", borderRadius: 24, padding: 1.5, overflow: "hidden", boxShadow: "0 0 60px rgba(79,110,247,0.25)" }}>
            <ConicBorder duration={8} />
            <div style={{
              position: "relative", overflow: "hidden", borderRadius: 23, padding: "64px 40px", textAlign: "center",
              background: "linear-gradient(135deg, rgba(79,110,247,0.18), rgba(124,58,237,0.18)), var(--nsurface)",
            }}>
              {[
                { x: "8%", y: "18%", s: 22, c: "#4f6ef7" },
                { x: "88%", y: "22%", s: 18, c: "#a78bfa" },
                { x: "14%", y: "76%", s: 16, c: "#06b6d4" },
                { x: "84%", y: "74%", s: 24, c: "#f472b6" },
              ].map((sp, i) => (
                <motion.div
                  key={i}
                  animate={{ y: [0, -14, 0], rotate: [0, 180, 360], scale: [1, 1.25, 1], opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 5 + i, repeat: Infinity, ease: "easeInOut" }}
                  style={{ position: "absolute", left: sp.x, top: sp.y, color: sp.c }}
                >
                  <Sparkles size={sp.s} />
                </motion.div>
              ))}
              <h2 style={{ position: "relative", fontFamily: "'Playfair Display', serif", fontSize: 42, fontWeight: 900, marginBottom: 16 }}>
                Ready to make your book <span style={{ background: "linear-gradient(135deg, var(--naccent1), var(--naccent2))", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>come alive?</span>
              </h2>
              <p style={{ position: "relative", fontSize: 17, color: "var(--nmuted)", maxWidth: 520, margin: "0 auto 36px", lineHeight: 1.7 }}>
                Upload your book and start learning in minutes. No setup, no fuss.
              </p>
              <ShineButton
                onClick={() => navigate("/dashboard")}
                style={{
                  padding: "18px 40px", borderRadius: 14, border: "none", cursor: "pointer",
                  background: "linear-gradient(135deg, var(--naccent1), var(--naccent2))",
                  color: "#fff", fontSize: 17, fontWeight: 700,
                  fontFamily: "'DM Sans', sans-serif",
                  boxShadow: "0 0 40px rgba(79,110,247,0.5)",
                }}
              >
                Start learning free <ArrowRight size={20} />
              </ShineButton>
            </div>
          </div>
        </motion.section>

        {/* Footer */}
        <footer style={{ padding: "32px 48px", borderTop: "1px solid var(--nborder)", textAlign: "center", color: "var(--nmuted)", fontSize: 13 }}>
          Made with <span style={{ color: "var(--naccent4)" }}>♥</span> for curious learners
        </footer>
      </div>
    </div>
  );
}