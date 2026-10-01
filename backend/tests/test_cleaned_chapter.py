import asyncio

from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Chapter

from nlp_engine.preprocessing.cleaner import clean_text


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
            print("Chapter not found.")
            return

        print("\nCHAPTER")
        print("=" * 60)
        print("Title:", chapter.title)
        print("Original stored length:", len(chapter.original_text))
        print("Old cleaned length:", len(chapter.cleaned_text))

        # Apply the NEW cleaner
        new_cleaned_text = clean_text(
            chapter.original_text
        )

        print(
            "New cleaned length:",
            len(new_cleaned_text),
        )

        print("\nNEW CLEANED TEXT PREVIEW")
        print("=" * 60)

        print(
            new_cleaned_text[:3000]
        )


if __name__ == "__main__":
    asyncio.run(main())