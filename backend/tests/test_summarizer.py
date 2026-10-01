import asyncio

from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Chapter

from nlp_engine.analysis.summarizer import (
    generate_extractive_summary,
)


async def main():

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Chapter)
            .where(
                Chapter.chapter_number == 1,
                Chapter.title == "The Last Lesson",
            )
            .order_by(
                Chapter.word_count.desc()
            )
        )

        chapter = result.scalars().first()

        if chapter is None:
            print("Chapter not found.")
            return

        print("\nCHAPTER")
        print("=" * 70)
        print("Title:", chapter.title)
        print("Words:", chapter.word_count)

        result = generate_extractive_summary(
            chapter.cleaned_text,
            num_sentences=5,
        )

        print("\nSUMMARY")
        print("=" * 70)

        print(result["summary"])

        print("\nSELECTED SENTENCES")
        print("=" * 70)

        for number, sentence in enumerate(
            result["sentences"],
            start=1,
        ):
            print(f"\n{number}.")
            print(sentence["sentence"])
            print(
                "Score:",
                sentence["score"],
            )

        print("\nSTATISTICS")
        print("=" * 70)
        print(
            "Total valid sentences:",
            result["total_sentences"],
        )
        print(
            "Content characters:",
            result["content_characters"],
        )


if __name__ == "__main__":
    asyncio.run(main())