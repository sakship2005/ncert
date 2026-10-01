import asyncio

from sqlalchemy import delete, select

from database.database import (
    AsyncSessionLocal,
    init_db,
)

from database.models import (
    Book,
    Chapter,
)

from nlp_engine.document.processor import (
    process_pdf,
)

from nlp_engine.document.database_saver import (
    save_processed_book,
)


PDF_PATH = r"C:\Users\shrut\Downloads\ncert-test\chp-1 class 12.pdf"


async def clear_test_database():
    """
    Remove previous test data.

    This is only for development/testing.
    """

    async with AsyncSessionLocal() as db:

        print("\n[database] Removing old test data...")

        await db.execute(
            delete(Chapter)
        )

        await db.execute(
            delete(Book)
        )

        await db.commit()

        print("[database] Old test data removed.")


async def verify_database():

    async with AsyncSessionLocal() as db:

        print("\n[5] Verifying database...")
        print("-" * 60)

        # Get books
        book_result = await db.execute(
            select(Book)
        )

        books = book_result.scalars().all()

        print(
            f"Books in database: {len(books)}"
        )

        # Get chapters
        chapter_result = await db.execute(
            select(Chapter)
        )

        chapters = chapter_result.scalars().all()

        print(
            f"Chapters in database: {len(chapters)}"
        )

        print()

        for book in books:

            print(
                f"Book: {book.title}"
            )

            print(
                f"Class: {book.class_level}"
            )

            print(
                f"Subject: {book.subject}"
            )

            print(
                f"Upload mode: {book.upload_mode}"
            )

            print(
                f"Status: {book.processing_status}"
            )

            print()

        for chapter in chapters:

            print(
                f"Chapter {chapter.chapter_number}: "
                f"{chapter.title}"
            )

            print(
                f"Pages: "
                f"{chapter.page_start} - "
                f"{chapter.page_end}"
            )

            print(
                f"Words: "
                f"{chapter.word_count}"
            )

            print(
                f"Status: "
                f"{chapter.processing_status}"
            )

            print()


async def main():

    print("=" * 60)
    print("NCERT DATABASE SAVE TEST")
    print("=" * 60)

    # --------------------------------------------------
    # 1. Initialize database
    # --------------------------------------------------

    print("\n[1] Initializing database...")

    await init_db()

    print(
        "[database] Tables ready."
    )

    # --------------------------------------------------
    # 2. Clear previous test data
    # --------------------------------------------------

    await clear_test_database()

    # --------------------------------------------------
    # 3. Process PDF
    # --------------------------------------------------

    print("\n[2] Processing PDF...")

    processed_data = process_pdf(
        PDF_PATH
    )

    print(
        f"Pages processed: "
        f"{processed_data['page_count']}"
    )

    print(
        f"Text length: "
        f"{processed_data['text_length']}"
    )

    print(
        f"Chapters detected: "
        f"{len(processed_data['chapters'])}"
    )

    # --------------------------------------------------
    # 4. Show detected chapters
    # --------------------------------------------------

    print("\n[3] Detected chapters:")
    print("-" * 60)

    for chapter in processed_data["chapters"]:

        print(
            f"Chapter "
            f"{chapter['chapter_number']}: "
            f"{chapter['title']}"
        )

        print(
            f"Pages: "
            f"{chapter['start_page']} - "
            f"{chapter['end_page']}"
        )

        print()

    # --------------------------------------------------
    # 5. Save to database
    # --------------------------------------------------

    print("[4] Saving to database...")

    async with AsyncSessionLocal() as db:

        book = await save_processed_book(
            db=db,
            title="The Last Lesson",
            class_level="12",
            subject="English",
            language="en",
            upload_mode="chapter",
            source_file=PDF_PATH,
            processed_data=processed_data,
        )

        print(
            "\n[database] Book saved successfully."
        )

        print(
            f"Book ID: {book.id}"
        )

        print(
            f"Title: {book.title}"
        )

        print(
            f"Class: {book.class_level}"
        )

        print(
            f"Subject: {book.subject}"
        )

        print(
            f"Upload mode: {book.upload_mode}"
        )

        print(
            f"Status: {book.processing_status}"
        )

    # --------------------------------------------------
    # 6. Verify database
    # --------------------------------------------------

    await verify_database()

    print("=" * 60)
    print("DATABASE TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())