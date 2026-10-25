from fastapi import APIRouter
from pydantic import BaseModel

from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Book, Chapter

from nlp_engine.retrieval.chunking import create_chunks
from nlp_engine.retrieval.vector_store import VectorStore


router = APIRouter(
    prefix="/search",
    tags=["Semantic Search"],
)


class SearchRequest(BaseModel):
    # Frontend sends book_id; legacy frontend sent chapter_id containing the
    # book's id. Accept both so either version works.
    book_id: str | None = None
    chapter_id: str | None = None        # treated as book_id when book_id absent
    query: str
    top_k: int = 5
    min_score: float = 0.15             # chunks below this score are dropped


@router.post("")
async def semantic_search(request: SearchRequest):

    # Resolve whichever id field was sent
    book_id = request.book_id or request.chapter_id

    if not book_id:
        return {"status": "error", "message": "book_id is required.", "results": []}

    if not request.query or not request.query.strip():
        return {"status": "error", "message": "Query cannot be empty.", "results": []}

    async with AsyncSessionLocal() as db:

        # Verify the book exists
        book_result = await db.execute(
            select(Book).where(Book.id == book_id)
        )
        book = book_result.scalar_one_or_none()

        if book is None:
            return {"status": "error", "message": "Book not found.", "results": []}

        # Load every chapter that belongs to this book
        chapters_result = await db.execute(
            select(Chapter)
            .where(Chapter.book_id == book_id)
            .order_by(Chapter.chapter_number)
        )
        chapters = chapters_result.scalars().all()

        if not chapters:
            return {"status": "success", "results": []}

        results = []

        for chapter in chapters:
            text = chapter.cleaned_text or chapter.original_text or ""
            if not text.strip():
                continue

            # Build an in-memory vector store for this chapter
            chunks = create_chunks(text, sentences_per_chunk=5, overlap=1)
            if not chunks:
                continue

            store = VectorStore()
            store.add_chunks(chunks)

            # search() returns [{chunk_id, text, sentence_start,
            #                    sentence_end, similarity}]
            hits = store.search(request.query, top_k=3)

            for hit in hits:
                score = hit.get("similarity", 0.0)
                if score < request.min_score:
                    continue

                results.append({
                    # Fields the frontend reads
                    "chapter_num": chapter.chapter_number,
                    "title":       chapter.title or f"Chapter {chapter.chapter_number}",
                    "snippet":     hit["text"],
                    "score":       round(score, 4),
                })

        # Sort across all chapters, return top_k overall
        results.sort(key=lambda r: r["score"], reverse=True)

        return {
            "status":  "success",
            "results": results[: request.top_k],
        }