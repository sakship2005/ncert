"""
Two-tier RAG pipeline for the NCERT AI Chat.

Tier 1  — TF-IDF keyword retrieval → Gemini (NCERT passages only)
Tier 2  — TF-IDF retrieval + web search → Gemini (NCERT + web)
"""

from __future__ import annotations

import asyncio
import logging
import re

from nlp_engine.retrieval.tfidf_retriever import TFIDFIndex
from nlp_engine.retrieval import gemini_client as gemini
from nlp_engine.retrieval.web_search import fetch_web_summaries

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tier-detection heuristics
# ---------------------------------------------------------------------------
_DEEP_PATTERNS = re.compile(
    r"\b("
    r"deep(er|ly)?|detail(ed|s)?|explain (more|in depth|thoroughly)|"
    r"elaborate|comprehensive|in[\s-]depth|more about|tell me more|"
    r"research|full explanation|advanced|expand"
    r")\b",
    re.IGNORECASE,
)

_COVERAGE_THRESHOLD = 0.4
_MIN_TOP_SCORE = 0.05


def _should_upgrade(
    query: str,
    index: TFIDFIndex,
    top_results: list[dict],
    deep: bool,
) -> bool:
    if deep:
        return True
    if _DEEP_PATTERNS.search(query):
        return True
    if not top_results:
        return True
    if top_results[0].get("tfidf_score", 0) < _MIN_TOP_SCORE:
        return True
    if index.coverage(query) < _COVERAGE_THRESHOLD:
        return True
    return False


# ---------------------------------------------------------------------------
# Main entry-point
# ---------------------------------------------------------------------------

async def answer(
    chapter_chunks: list[dict],
    query: str,
    language: str = "en",
    deep: bool = False,
    top_k: int = 4,
) -> dict:
    if not chapter_chunks:
        return {
            "answer": "No chapter content available to search.",
            "tier": 0,
            "sources": [],
            "coverage": 0.0,
            "web_used": False,
        }

    # ── TF-IDF retrieval ─────────────────────────────────────────────────
    index = TFIDFIndex(chapter_chunks)
    top_results = index.search(query, top_k=top_k)
    coverage = index.coverage(query)
    passages = [r["text"] for r in top_results]

    # ── Decide tier ───────────────────────────────────────────────────────
    tier = 2 if _should_upgrade(query, index, top_results, deep) else 1

    logger.info(
        "RAG | query=%r | tier=%d | coverage=%.2f | top_score=%.4f",
        query,
        tier,
        coverage,
        top_results[0].get("tfidf_score", 0) if top_results else 0,
    )

    # ── Call Gemini (sync → thread so we don't block the event loop) ─────
    try:
        if tier == 1:
            web_summaries: list[str] = []
            answer_text = await asyncio.to_thread(
                gemini.ask_tier1, query, passages, language
            )
        else:
            chapter_hint = passages[0] if passages else ""
            web_summaries = await asyncio.to_thread(
                fetch_web_summaries, query, chapter_hint
            )
            answer_text = await asyncio.to_thread(
                gemini.ask_tier2, query, passages, web_summaries, language
            )
    except Exception as exc:
        # Re-raise with the real error so nlp.py can log it clearly
        logger.error("Gemini call failed: %s", exc, exc_info=True)
        raise

    # ── Source snippets for the UI ────────────────────────────────────────
    sources = []
    for r in top_results:
        snippet = r["text"][:200].rstrip() + ("…" if len(r["text"]) > 200 else "")
        sources.append(
            {
                "chunk_id": r.get("chunk_id"),
                "snippet": snippet,
                "score": r.get("tfidf_score", 0),
                "sentence_start": r.get("sentence_start"),
                "sentence_end": r.get("sentence_end"),
            }
        )

    return {
        "answer": answer_text,
        "tier": tier,
        "sources": sources,
        "coverage": round(coverage, 3),
        "web_used": len(web_summaries) > 0,
    }