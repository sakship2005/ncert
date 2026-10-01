from fastapi import APIRouter
from pydantic import BaseModel

from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Chapter

from nlp_engine.retrieval.chapter_retriever import (
    build_chapter_store,
)


router = APIRouter(
    prefix="/search",
    tags=["Semantic Search"],
)


class SearchRequest(BaseModel):
    chapter_id: str
    query: str
    top_k: int = 5


@router.post("")
async def semantic_search(
    request: SearchRequest,
):

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Chapter).where(
                Chapter.id == request.chapter_id
            )
        )

        chapter = result.scalar_one_or_none()

        if chapter is None:
            return {
                "status": "error",
                "message": "Chapter not found.",
            }

        if not chapter.cleaned_text:
            return {
                "status": "error",
                "message": "Chapter has no text.",
            }

        store = await build_chapter_store(
            db,
            chapter.id,
        )

        results = store.search(
            request.query,
            top_k=request.top_k,
        )

        return {
            "status": "success",
            "chapter": chapter.title,
            "query": request.query,
            "results": results,
        }