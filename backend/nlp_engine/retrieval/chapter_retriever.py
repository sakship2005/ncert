from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Chapter

from nlp_engine.retrieval.chunking import create_chunks
from nlp_engine.retrieval.vector_store import VectorStore


async def build_chapter_store(
    db: AsyncSession,
    chapter_id: str,
) -> VectorStore:
    """
    Load a chapter from the database,
    split it into chunks, and create
    a FAISS vector store.
    """

    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id
        )
    )

    chapter = result.scalar_one_or_none()

    if chapter is None:
        raise ValueError("Chapter not found.")

    if not chapter.cleaned_text:
        raise ValueError(
            "Chapter does not contain text."
        )

    chunks = create_chunks(
        chapter.cleaned_text,
        sentences_per_chunk=5,
        overlap=1,
    )

    store = VectorStore()

    store.add_chunks(chunks)

    return store