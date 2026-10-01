import asyncio

from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Chapter

from nlp_engine.analysis.chapter_content import (
    extract_chapter_content,
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

        print("\nORIGINAL CLEANED TEXT")
        print("=" * 70)

        print(
            chapter.cleaned_text[:5000]
        )

        print("\n\nEXTRACTED CHAPTER CONTENT")
        print("=" * 70)

        extracted = extract_chapter_content(
            chapter.cleaned_text
        )

        print(
            extracted[:5000]
        )


if __name__ == "__main__":
    asyncio.run(main())