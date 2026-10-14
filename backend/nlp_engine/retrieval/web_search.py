"""
Tier-2 web search helper.

Uses DuckDuckGo (zero-cost, no API key) via the `duckduckgo-search` package.
Falls back to a stub if the package isn't installed so Tier-1 always works.

Install:  pip install duckduckgo-search --break-system-packages
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def _ddg_search(query: str, max_results: int) -> list[dict]:
    from duckduckgo_search import DDGS  # type: ignore

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(
                {
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "href": r.get("href", ""),
                }
            )
    return results


def fetch_web_summaries(
    query: str,
    chapter_context: str = "",
    max_results: int = 4,
) -> list[str]:
    """
    Run a web search for *query* (optionally enriched with chapter context)
    and return a list of plain-text summaries ready to be injected into the
    Tier-2 prompt.

    Returns an empty list if the package is unavailable or all requests fail.
    """
    enriched_query = query
    if chapter_context:
        # Add a few keywords from the chapter to ground web results
        keywords = " ".join(chapter_context.split()[:8])
        enriched_query = f"{query} {keywords} NCERT"

    try:
        hits = _ddg_search(enriched_query, max_results)
    except ImportError:
        logger.warning(
            "duckduckgo-search not installed — Tier-2 web search disabled. "
            "Run: pip install duckduckgo-search"
        )
        return []
    except Exception as exc:
        logger.error("Web search failed: %s", exc)
        return []

    summaries = []
    for hit in hits:
        title = hit.get("title", "").strip()
        body = hit.get("body", "").strip()
        href = hit.get("href", "").strip()
        if body:
            summaries.append(f"**{title}**\n{body}\nSource: {href}")

    return summaries