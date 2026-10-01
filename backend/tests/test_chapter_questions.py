import asyncio

from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Chapter

from nlp_engine.retrieval.chapter_retriever import (
    build_chapter_store,
)

from nlp_engine.generation.question_generator import (
    generate_questions,
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

        # Get all chapter chunks
        context = "\n\n".join(
            chunk["text"]
            for chunk in store.chunks
        )

        print("\nCONTEXT")
        print("=" * 60)
        print("Characters:", len(context))

        # Generate questions
        questions = generate_questions(
            context=context,
            number_of_questions=10,
        )

        print("\nGENERATED QUESTION BANK")
        print("=" * 60)

        for number, question in enumerate(
            questions,
            start=1,
        ):
            print(f"\nQuestion {number}")
            print("-" * 40)
            print("Type:", question["type"])
            print("Difficulty:", question["difficulty"])
            print("Question:", question["question"])
            print("Answer:", question["answer"])


if __name__ == "__main__":
    asyncio.run(main())