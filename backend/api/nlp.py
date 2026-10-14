import asyncio
import os
import re
from collections import Counter
from typing import Optional, List
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Chapter, Book
from nlp_engine.retrieval.chapter_retriever import build_chapter_store
from nlp_engine.generation.answer_generator import answer_question
from nlp_engine.retrieval.rag_pipeline import answer as rag_answer
from nlp_engine.generation.question_generator import generate_questions
from nlp_engine.analysis.summarizer import generate_extractive_summary, summarize_offline
from nlp_engine.generation.quiz_generator import generate_interactive_quiz
from nlp_engine.analysis.vocabulary import extract_difficult_words
from nlp_engine.analysis.entities import extract_chapter_entities
from nlp_engine.analysis.concepts import extract_concepts
from nlp_engine.analysis.topics import extract_topics
from nlp_engine.analysis.recommendations import recommend_educational_resources

router = APIRouter(
    prefix="/nlp",
    tags=["NLP"],
)


# Helper to fetch chapter from db
async def get_chapter_by_request(db, chapter_id: Optional[str] = None, book_id: Optional[str] = None, chapter_num: Optional[int] = None):
    if chapter_id:
        result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
        return result.scalar_one_or_none()
    elif book_id and chapter_num is not None:
        result = await db.execute(
            select(Chapter).where(
                Chapter.book_id == book_id,
                Chapter.chapter_number == chapter_num,
            )
        )
        return result.scalar_one_or_none()
    elif book_id:
        result = await db.execute(
            select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.chapter_number)
        )
        return result.scalars().first()
    return None


# ==================================================
# 1. HYBRID HINDI / MULTILINGUAL SUMMARIZER
# ==================================================

class SummarizeRequest(BaseModel):
    book_id: Optional[str] = None
    chapter_num: Optional[int] = None
    chapter_id: Optional[str] = None
    language: Optional[str] = "hi"


@router.post("/summarize")
async def summarize_chapter_endpoint(request: SummarizeRequest):
    """
    Generate a summary using the book's source language pipeline and translate
    it to the requested output language when English/Hindi conversion is needed.
    """
    async with AsyncSessionLocal() as db:
        chapter = await get_chapter_by_request(db, request.chapter_id, request.book_id, request.chapter_num)
        if not chapter:
            return {"status": "error", "message": "Chapter not found."}

        text = chapter.cleaned_text or chapter.original_text or ""
        if not text.strip():
            return {"status": "error", "message": "Chapter has no text."}

        book_result = await db.execute(select(Book).where(Book.id == chapter.book_id))
        book = book_result.scalar_one_or_none()
        source_lang = (book.language if book else "en") or "en"
        source_lang = source_lang.lower()
        if source_lang not in {"en", "hi", "mr"}:
            devanagari_ratio = len(re.findall(r"[\u0900-\u097F]", text)) / max(len(text), 1)
            source_lang = "hi" if devanagari_ratio >= 0.15 else "en"

        target_lang = (request.language or source_lang).lower()
        if target_lang not in {"en", "hi", "mr"}:
            target_lang = source_lang

        res = await asyncio.to_thread(
            summarize_offline, text, source_lang, target_lang, 6
        )
        summary      = res["summary"]
        mode         = res["mode"]
        chunks_total = res["chunks_total"]
        chunks_used  = res["chunks_used"]

        return {
            "status": "success",
            "chapter_id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "chapter_title": chapter.title,
            "summary": summary,
            "abstractive": summary,
            "extractive": summary,
            "mode": mode,
            "method": res.get("method", ""),
            "chunks_total": chunks_total,
            "chunks_used": chunks_used,
            "source_language": source_lang,
            "translated": False,
            "translation_model": None,
            "language": target_lang,
        }


# ==================================================
# 2. AUTOMATIC DIFFICULT WORD DETECTION
# ==================================================

class DifficultWordsRequest(BaseModel):
    chapter_id: Optional[str] = None
    book_id: Optional[str] = None
    chapter_num: Optional[int] = None
    top_n: Optional[int] = 20


@router.post("/difficult-words")
async def difficult_words_endpoint(request: DifficultWordsRequest):
    """
    Automatically detects difficult/uncommon words from the chapter text
    and provides definitions, simple meanings, synonyms, examples, and translations.
    """
    async with AsyncSessionLocal() as db:
        chapter = await get_chapter_by_request(db, request.chapter_id, request.book_id, request.chapter_num)
        if not chapter:
            return {"status": "error", "message": "Chapter not found.", "difficult_words": []}

        text = chapter.cleaned_text or chapter.original_text or ""
        if not text.strip():
            return {"status": "error", "message": "Chapter has no text.", "difficult_words": []}

        book_result = await db.execute(select(Book).where(Book.id == chapter.book_id))
        book = book_result.scalar_one_or_none()
        book_language = book.language if book else "auto"
        words = extract_difficult_words(
            text,
            top_n=request.top_n or 20,
            language=book_language,
        )
        return {
            "status": "success",
            "chapter_id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "chapter_title": chapter.title,
            "total_words": len(words),
            "difficult_words": words,
        }


# ==================================================
# 3. CHAPTER-WISE DETAILED NLP ANALYSIS
# ==================================================

class ChapterAnalysisRequest(BaseModel):
    chapter_id: Optional[str] = None
    book_id: Optional[str] = None
    chapter_num: Optional[int] = None


@router.post("/chapter-analysis")
async def chapter_analysis_endpoint(request: ChapterAnalysisRequest):
    """
    Detailed NLP analysis showing:
    - Named Entities with actual names (Persons, Locations, Organizations, Dates)
    - Main Topics with actual names and descriptive keywords
    - Core Concepts with actual names and occurrences
    """
    async with AsyncSessionLocal() as db:
        chapter = await get_chapter_by_request(db, request.chapter_id, request.book_id, request.chapter_num)
        if not chapter:
            return {"status": "error", "message": "Chapter not found."}

        text = chapter.cleaned_text or chapter.original_text or ""
        if not text.strip():
            return {"status": "error", "message": "Chapter has no text."}

        book_result = await db.execute(select(Book).where(Book.id == chapter.book_id))
        book = book_result.scalar_one_or_none()
        book_language = book.language if book else "auto"
        devanagari_words = re.findall(r"[\u0900-\u097F]{3,}", text)
        devanagari_counts = Counter(devanagari_words)
        entities = extract_chapter_entities(text)
        if book_language in {"hi", "mr", "both"} or len(devanagari_words) >= 20:
            concepts = [
                {"concept": word, "name": word, "count": count}
                for word, count in devanagari_counts.most_common(30)
            ]
            topics = [{"topic": "मुख्य शब्द", "words": [item["concept"] for item in concepts[:12]]}]
        else:
            concepts = extract_concepts(text, top_n=15)
            topics = extract_topics(text, num_topics=4)

        return {
            "status": "success",
            "chapter_id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "chapter_title": chapter.title,
            "entities": entities,
            "concepts": concepts,
            "topics": topics,
            "word_count": chapter.word_count,
            "language": book_language,
        }


# ==================================================
# 4. INTERACTIVE QUIZ GENERATOR
# ==================================================

class QuizRequest(BaseModel):
    chapter_id: Optional[str] = None
    book_id: Optional[str] = None
    chapter_num: Optional[int] = None
    total_questions: Optional[int] = 35
    types: Optional[List[str]] = ["mcq", "true_false", "fill_blank", "multi"]
    language: Optional[str] = "en"


@router.post("/generate-quiz")
async def generate_quiz_endpoint(request: QuizRequest):
    """
    Generates multi-format quiz questions:
    MCQs with 4 options and correct answer, True/False, Fill in blanks, and Short Answer.
    """
    async with AsyncSessionLocal() as db:
        chapter = await get_chapter_by_request(db, request.chapter_id, request.book_id, request.chapter_num)
        if not chapter:
            return {"status": "error", "message": "Chapter not found.", "questions": []}

        text = chapter.cleaned_text or chapter.original_text or ""
        if not text.strip():
            return {"status": "error", "message": "Chapter has no text.", "questions": []}

        res = await asyncio.to_thread(
            generate_interactive_quiz,
            text,
            request.total_questions or 8,
            request.types,
            request.language or "en",
        )
        if res.get("status") == "error" or not res.get("questions"):
            return {
                "status": "error",
                "message": res.get("message", "Quiz generation returned no questions."),
                "questions": [],
            }
        return {
            "status": "success",
            "chapter_id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "chapter_title": chapter.title,
            "total": res.get("total", len(res.get("questions", []))),
            "questions": res.get("questions", []),
        }


# ==================================================
# 5. EDUCATIONAL VIDEO & REFERENCE RECOMMENDATION
# ==================================================

class RecommendationRequest(BaseModel):
    chapter_id: Optional[str] = None
    book_id: Optional[str] = None
    chapter_num: Optional[int] = None


@router.post("/recommendations")
async def recommendations_endpoint(request: RecommendationRequest):
    """
    Recommends curated educational videos (NCERT official, Khan Academy, animations)
    and reference resources matching chapter concepts.
    """
    async with AsyncSessionLocal() as db:
        chapter = await get_chapter_by_request(db, request.chapter_id, request.book_id, request.chapter_num)
        if not chapter:
            return {"status": "error", "message": "Chapter not found."}

        # Also get book subject/class
        book_result = await db.execute(select(Book).where(Book.id == chapter.book_id))
        book = book_result.scalar_one_or_none()
        subject = book.subject if book else "English"
        class_level = book.class_level if book else "12"

        text = chapter.cleaned_text or chapter.original_text or ""
        res = recommend_educational_resources(
            chapter_title=chapter.title,
            chapter_text=text,
            subject=subject,
            class_level=class_level,
        )
        return {
            "status": "success",
            "chapter_id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "chapter_title": chapter.title,
            "concepts_covered": res.get("concepts_covered", []),
            "video_recommendations": res.get("video_recommendations", []),
            "reference_resources": res.get("reference_resources", []),
        }


# ==================================================
# 6. MULTILINGUAL RAG Q&A (Existing Pipeline + Language)
# ==================================================

class QuestionRequest(BaseModel):
    chapter_id: Optional[str] = None
    book_id: Optional[str] = None
    chapter_num: Optional[int] = None
    question: str
    language: Optional[str] = "en"
    deep: Optional[bool] = False   # True → Tier 2 (NCERT + web research)


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Two-tier RAG Q&A powered by TF-IDF retrieval + Gemini 3.5 Flash.

    Tier 1  — TF-IDF keyword match on chapter chunks → Gemini (NCERT only)
               Fast, token-efficient, strictly grounded in the chapter text.

    Tier 2  — Same retrieval + live DuckDuckGo web search → Gemini
               Activated when `deep=True`, query coverage is low, or the
               user's phrasing signals a request for deeper explanation.
    """
    async with AsyncSessionLocal() as db:
        chapter = await get_chapter_by_request(
            db, request.chapter_id, request.book_id, request.chapter_num
        )

        if chapter is None:
            return {"status": "error", "message": "Chapter not found."}

        if not chapter.cleaned_text:
            return {"status": "error", "message": "Chapter has no text."}

        # ── Build chunks from the chapter's cleaned text ─────────────────
        from nlp_engine.retrieval.chunking import create_chunks

        chunks = create_chunks(
            chapter.cleaned_text,
            sentences_per_chunk=5,
            overlap=1,
        )

        if not chunks:
            return {"status": "error", "message": "Chapter text could not be chunked."}

        # ── Run the two-tier RAG pipeline ─────────────────────────────────
        try:
            result = await rag_answer(
                chapter_chunks=chunks,
                query=request.question,
                language=request.language or "en",
                deep=request.deep or False,
            )
        except Exception as error:
            import traceback
            print(f"[NLP/RAG] Pipeline failed: {error}")
            traceback.print_exc()
            # Graceful fallback: return the top matching raw chunk text
            from nlp_engine.retrieval.tfidf_retriever import TFIDFIndex

            index = TFIDFIndex(chunks)
            top = index.search(request.question, top_k=3)
            fallback_text = "\n\n".join(r["text"] for r in top) if top else chapter.cleaned_text[:1200]
            return {
                "status": "success",
                "chapter": chapter.title,
                "question": request.question,
                "answer": (
                    f"⚠️ Gemini error: {error}\n\n"
                    "Most relevant chapter section:\n\n"
                    + fallback_text
                ),
                "tier": 0,
                "sources": [],
                "coverage": 0.0,
                "web_used": False,
                "language": request.language or "en",
            }

        return {
            "status": "success",
            "chapter": chapter.title,
            "question": request.question,
            "answer": result["answer"],
            "tier": result["tier"],          # 1 = NCERT-only, 2 = NCERT+web
            "sources": result["sources"],    # chunk snippets shown in UI
            "coverage": result["coverage"],  # 0–1 TF-IDF query coverage
            "web_used": result.get("web_used", False),
            "language": request.language or "en",
        }


# ==================================================
# 7. PRACTICE QUESTION GENERATOR (Original Untouched)
# ==================================================

class GenerateQuestionsRequest(BaseModel):
    chapter_id: str
    number_of_questions: int = 10


@router.post("/generate-questions")
async def generate_chapter_questions(request: GenerateQuestionsRequest):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Chapter).where(Chapter.id == request.chapter_id))
        chapter = result.scalar_one_or_none()

        if chapter is None:
            return {"status": "error", "message": "Chapter not found."}

        if not chapter.cleaned_text:
            return {"status": "error", "message": "Chapter has no text."}

        store = await build_chapter_store(db, chapter.id)
        if store.size() == 0:
            return {"status": "error", "message": "No content available for this chapter."}

        context = "\n\n".join(chunk["text"] for chunk in store.chunks)
        questions = generate_questions(
            context=context,
            number_of_questions=request.number_of_questions,
        )

        return {
            "status": "success",
            "chapter_id": chapter.id,
            "chapter": chapter.title,
            "questions": questions,
        }