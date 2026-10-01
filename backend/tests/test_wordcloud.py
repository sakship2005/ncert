import asyncio
import os

from sqlalchemy import select

from database.database import AsyncSessionLocal
from database.models import Chapter

from nlp_engine.analysis.wordcloud_generator import (
    generate_wordcloud,
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

        output_path = (
            "storage/wordcloud.png"
        )

        result = generate_wordcloud(
            text=chapter.cleaned_text,
            output_path=output_path,
        )

        print("\nWORD CLOUD")
        print("=" * 70)

        print(
            "Status:",
            result["status"],
        )

        print(
            "Total meaningful words:",
            result.get("total_words"),
        )

        print(
            "Unique words:",
            result.get("unique_words"),
        )

        print("\nTOP WORDS")
        print("=" * 70)

        for item in result.get(
            "top_words",
            [],
        ):
            print(
                item["word"],
                "→",
                item["frequency"],
            )

        print("\nIMAGE")
        print("=" * 70)

        if os.path.exists(
            output_path
        ):
            print(
                "Word cloud created successfully:"
            )
            print(
                os.path.abspath(
                    output_path
                )
            )
        else:
            print(
                "Word cloud image was not created."
            )


if __name__ == "__main__":
    asyncio.run(main())