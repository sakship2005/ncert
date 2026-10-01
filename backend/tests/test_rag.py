import asyncio

from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Chapter

from nlp_engine.retrieval.chapter_retriever import (
    build_chapter_store,
)

from nlp_engine.generation.answer_generator import (
    generate_answer,
)


async def main():

    async with AsyncSessionLocal() as db:

        # Find Chapter 1 with actual text
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
            print("Chapter not found.")
            return

        print("\nCHAPTER")
        print("=" * 60)
        print("Title:", chapter.title)
        print("Words:", chapter.word_count)

        # Build FAISS store
        store = await build_chapter_store(
            db,
            chapter.id,
        )

        print("\nFAISS")
        print("=" * 60)
        print("Chunks indexed:", store.size())

        # Student question
        question = (
            "Why was the French language important?"
        )

        # Retrieve relevant NCERT chunks
        results = store.search(
            question,
            top_k=3,
        )

        print("\nRETRIEVED CHUNKS")
        print("=" * 60)

        for result in results:
            print(
                f"\nChunk {result['chunk_id']}"
            )

            print(
                "Similarity:",
                result["similarity"],
            )

            print(result["text"])

        # Combine retrieved chunks
        context = "\n\n".join(
            result["text"]
            for result in results
        )

        # Generate answer using Groq
        answer = generate_answer(
            question=question,
            context=context,
        )

        print("\nAI TUTOR ANSWER")
        print("=" * 60)
        print(answer)


if __name__ == "__main__":
    asyncio.run(main())