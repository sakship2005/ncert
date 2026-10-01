import asyncio

from database.database import AsyncSessionLocal, init_db
from nlp_engine.document.processor import process_pdf
from nlp_engine.document.database_saver import save_processed_book


# CHANGE THIS PATH IF YOUR PDF IS IN A DIFFERENT LOCATION
PDF_PATH = r"C:\Users\shrut\Downloads\ncert-test\chp-1 class 12.pdf"


async def main():

    print("=" * 60)
    print("NCERT DATABASE SAVE TEST")
    print("=" * 60)

    # -----------------------------------------
    # 0. Initialize database
    # -----------------------------------------

    print("\n[0] Initializing database...")

    await init_db()

    print("[database] Tables ready.")

    # -----------------------------------------
    # 1. Process PDF
    # -----------------------------------------

    print("\n[1] Processing PDF...")

    processed_data = process_pdf(PDF_PATH)

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

    # -----------------------------------------
    # 2. Show detected chapters
    # -----------------------------------------

    print("\n[2] Detected chapters:")
    print("-" * 60)

    for chapter in processed_data["chapters"]:

        print(
            f"Chapter {chapter['chapter_number']}: "
            f"{chapter['title']}"
        )

        print(
            f"Pages: "
            f"{chapter['start_page']} - "
            f"{chapter['end_page']}"
        )

        print()

    # -----------------------------------------
    # 3. Open database session
    # -----------------------------------------

    async with AsyncSessionLocal() as db:

        print("[3] Saving to database...")

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

        # -----------------------------------------
        # 4. Display saved book
        # -----------------------------------------

        print("\n[4] BOOK SAVED SUCCESSFULLY")

        print("-" * 60)

        print(f"Book ID: {book.id}")
        print(f"Title: {book.title}")
        print(f"Class: {book.class_level}")
        print(f"Subject: {book.subject}")
        print(f"Language: {book.language}")
        print(f"Upload mode: {book.upload_mode}")
        print(f"Status: {book.processing_status}")

    print("\n" + "=" * 60)
    print("DATABASE TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())