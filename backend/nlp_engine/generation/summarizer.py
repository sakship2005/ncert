"""
NCERT Summarizer Module
Delegates directly to the fine-tuned Hybrid Hindi Summarizer (MBart-50 + Groq).
"""

from nlp_engine.generation.hindi_summarizer import (
    load_model,
    summarize_chapter,
    is_good_summary,
    chunk_text,
    local_summarize,
    groq_merge,
)

__all__ = [
    "load_model",
    "summarize_chapter",
    "is_good_summary",
    "chunk_text",
    "local_summarize",
    "groq_merge",
]
