import asyncio

from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Chapter

from nlp_engine.retrieval.chapter_retriever import (
    build_chapter_store,
)


async def main():

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Chapter)
            .where(
                Chapter.chapter_number == 1,
                Chapter.title == "The Last Lesson",
            )
            .order_by(Chapter.word_count.desc())
        )

        chapter = result.scalars().first()

        if chapter is None:
            print("Chapter 1 not found.")
            return

        if not chapter.cleaned_text:
            print("Chapter 1 has no text.")
            return

        print("\nCHAPTER")
        print("=" * 60)

        print("Chapter:", chapter.chapter_number)
        print("Title:", chapter.title)
        print("Words:", chapter.word_count)
        print("Chapter ID:", chapter.id)
        print("Text length:", len(chapter.cleaned_text))

        store = await build_chapter_store(
            db,
            chapter.id,
        )

        print("\nFAISS")
        print("=" * 60)

        print("Chunks indexed:", store.size())

        query = "Why was the French language important?"

        results = store.search(
            query,
            top_k=3,
        )

        print("\nQuestion:")
        print(query)

        print("\nRetrieved NCERT content:")

        for result in results:

            print("\n--------------------")

            print("Chunk:", result["chunk_id"])

            print(
                "Similarity:",
                result["similarity"],
            )

            print("Text:")
            print(result["text"])


if __name__ == "__main__":
    asyncio.run(main())