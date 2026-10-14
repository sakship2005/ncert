"""
Gemini 3.5 Flash client for the NCERT RAG pipeline.
Uses the new google-genai SDK (replaces deprecated google-generativeai).

Install:  pip install google-genai
Set env:  GEMINI_API_KEY=your_key_here
"""

import os
import textwrap

from dotenv import load_dotenv
load_dotenv()  # load .env before reading the key

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Client — initialised once at import time
# ---------------------------------------------------------------------------
_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not _API_KEY:
    raise RuntimeError(
        "[gemini_client] GEMINI_API_KEY is missing. "
        "Add it to your backend/.env file:\n  GEMINI_API_KEY=your_key_here"
    )
_client = genai.Client(api_key=_API_KEY)

_MODEL_NAME = "gemini-2.5-flash"   # swap to "gemini-2.5-flash" / "gemini-3.5-flash" when on your key

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------
_TIER1_SYSTEM = textwrap.dedent("""
    You are an expert NCERT tutor. Answer the student's question using ONLY
    the provided NCERT chapter passages below. Do not add information from
    outside those passages. If the answer is not present, say
    "This topic is not covered in the selected chapter."

    Keep the answer clear, concise, and student-friendly.
    Use bullet points or numbered lists where helpful.
""").strip()

_TIER2_SYSTEM = textwrap.dedent("""
    You are an expert educational researcher and NCERT tutor.
    The student wants a deep, comprehensive answer.

    You have been given:
    1. Relevant NCERT chapter passages (primary source — always prioritise these).
    2. Additional web research summaries (secondary source — use to enrich and extend).

    Synthesise both sources into a thorough, well-structured explanation.
    Cite "NCERT" or "Web" in brackets where appropriate.
    Use headings, bullet points, and examples to aid understanding.
""").strip()


def _lang_note(language: str) -> str:
    return {
        "hi": "\nRespond in Hindi.",
        "mr": "\nRespond in Marathi.",
    }.get(language, "")


def _build_tier1_prompt(query: str, passages: list[str], language: str) -> str:
    ctx = "\n\n---\n\n".join(f"[Passage {i+1}]\n{p}" for i, p in enumerate(passages))
    return (
        f"{_TIER1_SYSTEM}{_lang_note(language)}\n\n"
        f"=== NCERT PASSAGES ===\n{ctx}\n\n"
        f"=== STUDENT QUESTION ===\n{query}"
    )


def _build_tier2_prompt(
    query: str,
    passages: list[str],
    web_summaries: list[str],
    language: str,
) -> str:
    ncert_ctx = "\n\n---\n\n".join(f"[NCERT Passage {i+1}]\n{p}" for i, p in enumerate(passages))
    web_ctx   = "\n\n---\n\n".join(f"[Web Source {i+1}]\n{s}"    for i, s in enumerate(web_summaries))
    return (
        f"{_TIER2_SYSTEM}{_lang_note(language)}\n\n"
        f"=== NCERT PASSAGES ===\n{ncert_ctx}\n\n"
        f"=== WEB RESEARCH ===\n{web_ctx}\n\n"
        f"=== STUDENT QUESTION ===\n{query}"
    )


def _generate(prompt: str, temperature: float, max_tokens: int) -> str:
    if _client is None:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file and restart the server."
        )
    response = _client.models.generate_content(
        model=_MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_ONLY_HIGH",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
            ],
        ),
    )
    return response.text.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ask_tier1(
    query: str,
    passages: list[str],
    language: str = "en",
    temperature: float = 0.3,
) -> str:
    """Tier-1: NCERT-only context → Gemini answer."""
    prompt = _build_tier1_prompt(query, passages, language)
    return _generate(prompt, temperature, max_tokens=1024)


def ask_tier2(
    query: str,
    passages: list[str],
    web_summaries: list[str],
    language: str = "en",
    temperature: float = 0.5,
) -> str:
    """Tier-2: NCERT + web research context → Gemini answer."""
    prompt = _build_tier2_prompt(query, passages, web_summaries, language)
    return _generate(prompt, temperature, max_tokens=2048)