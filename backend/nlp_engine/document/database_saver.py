from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Book, Chapter


async def save_processed_book(
    db: AsyncSession,
    title: str,
    class_level: str,
    subject: str,
    language: str,
    upload_mode: str,
    source_file: str,
    processed_data: dict,
):
    """
    Create a new book and save all detected chapters.
    """

    book = Book(
        title=title,
        class_level=class_level,
        subject=subject,
        language=language,
        upload_mode=upload_mode,
        source_file=source_file,
        processing_status="processing",
    )

    db.add(book)

    await db.flush()

    for chapter_data in processed_data["chapters"]:

        start_page = chapter_data["start_page"]
        end_page = chapter_data["end_page"]

        chapter_pages = [
            page
            for page in processed_data["cleaned_pages"]
            if start_page <= page["page_number"] <= end_page
        ]

        chapter_text = "\n\n".join(
            page["text"]
            for page in chapter_pages
            if page["text"]
        )

        chapter = Chapter(
            book_id=book.id,
            chapter_number=chapter_data["chapter_number"],
            title=chapter_data["title"],
            source_file=source_file,
            page_start=start_page,
            page_end=end_page,
            original_text=chapter_text,
            cleaned_text=chapter_text,
            word_count=len(chapter_text.split()),
            processing_status="completed",
        )

        db.add(chapter)

    book.processing_status = "completed"

    await db.commit()

    await db.refresh(book)

    return book


async def save_chapter_to_book(
    db: AsyncSession,
    book_id: str,
    chapter_number: int,
    title: str,
    source_file: str,
    processed_data: dict,
):
    """
    Save one uploaded chapter inside an existing book.
    """

    # --------------------------------------------------
    # Find book
    # --------------------------------------------------

    result = await db.execute(
        select(Book).where(
            Book.id == book_id
        )
    )

    book = result.scalar_one_or_none()

    if book is None:

        raise ValueError(
            "Book not found."
        )

    # --------------------------------------------------
    # Check duplicate chapter
    # --------------------------------------------------

    result = await db.execute(
        select(Chapter).where(
            Chapter.book_id == book_id,
            Chapter.chapter_number == chapter_number,
        )
    )

    existing_chapter = result.scalar_one_or_none()

    if existing_chapter is not None:

        raise ValueError(
            f"Chapter {chapter_number} already exists "
            f"in this book."
        )

    # --------------------------------------------------
    # Get detected chapter
    # --------------------------------------------------

    if not processed_data["chapters"]:

        raise ValueError(
            "No chapter detected."
        )

    detected_chapter = (
        processed_data["chapters"][0]
    )

    start_page = detected_chapter[
        "start_page"
    ]

    end_page = detected_chapter[
        "end_page"
    ]

    # --------------------------------------------------
    # Extract chapter text
    # --------------------------------------------------

    chapter_pages = [
        page
        for page in processed_data["cleaned_pages"]
        if start_page <= page["page_number"] <= end_page
    ]

    chapter_text = "\n\n".join(
        page["text"]
        for page in chapter_pages
        if page["text"]
    )

    # --------------------------------------------------
    # Create chapter
    # --------------------------------------------------

    chapter = Chapter(
        book_id=book_id,
        chapter_number=chapter_number,
        title=title,
        source_file=source_file,
        page_start=start_page,
        page_end=end_page,
        original_text=chapter_text,
        cleaned_text=chapter_text,
        word_count=len(
            chapter_text.split()
        ),
        processing_status="completed",
    )

    db.add(chapter)

    await db.commit()

    await db.refresh(chapter)

    return chapter