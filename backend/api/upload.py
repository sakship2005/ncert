import os
import shutil
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database.models import Book

from nlp_engine.document.processor import (
    process_pdf,
)
from nlp_engine.preprocessing.language import detect_language

from nlp_engine.document.database_saver import (
    save_processed_book,
    save_chapter_to_book,
)


router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


UPLOAD_DIR = "storage/books"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True,
)


def save_uploaded_file(
    file: UploadFile,
) -> str:
    """
    Save an uploaded PDF.
    """

    file_id = str(uuid4())

    filename = f"{file_id}.pdf"

    file_path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    with open(
        file_path,
        "wb",
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )

    return file_path


# ==================================================
# CHAPTER-WISE UPLOAD
# ==================================================

@router.post("/upload/chapter")
async def upload_chapter(
    file: UploadFile = File(...),

    book_id: str = Form(...),

    chapter_number: int = Form(...),

    title: str = Form(...),

    db: AsyncSession = Depends(get_db),
):
    """
    Upload one chapter into an existing book.
    """

    # --------------------------------------------------
    # Validate PDF
    # --------------------------------------------------

    if not file.filename:

        return {
            "status": "error",
            "message": "No file selected.",
        }

    if not file.filename.lower().endswith(".pdf"):

        return {
            "status": "error",
            "message": "Only PDF files are supported.",
        }

    book_result = await db.execute(select(Book).where(Book.id == book_id))
    book = book_result.scalar_one_or_none()
    if book is None:
        return {
            "status": "error",
            "message": "Book not found.",
        }

    # --------------------------------------------------
    # Save PDF
    # --------------------------------------------------

    file_path = save_uploaded_file(
        file
    )

    # --------------------------------------------------
    # Process PDF
    # --------------------------------------------------

    try:

        processed_data = process_pdf(file_path, language=book.language or "auto")

    except Exception as error:

        return {
            "status": "error",
            "message": "PDF processing failed.",
            "error": str(error),
        }

    # --------------------------------------------------
    # Check chapter detection
    # --------------------------------------------------

    if not processed_data["chapters"]:

        return {
            "status": "error",
            "message": (
                "No chapter could be detected "
                "from the uploaded PDF."
            ),
        }

    # --------------------------------------------------
    # Save chapter to existing book
    # --------------------------------------------------

    try:

        chapter = await save_chapter_to_book(
            db=db,
            book_id=book_id,
            chapter_number=chapter_number,
            title=title,
            source_file=file_path,
            processed_data=processed_data,
        )

    except ValueError as error:

        return {
            "status": "error",
            "message": str(error),
        }

    except Exception as error:

        return {
            "status": "error",
            "message": "Database save failed.",
            "error": str(error),
        }

    # --------------------------------------------------
    # Return result
    # --------------------------------------------------

    return {
        "status": "success",
        "message": "Chapter added to book successfully.",
        "book_id": book_id,
        "chapter_id": chapter.id,
        "chapter_number": chapter.chapter_number,
        "title": chapter.title,
        "page_start": chapter.page_start,
        "page_end": chapter.page_end,
        "word_count": chapter.word_count,
    }


# ==================================================
# FULL BOOK UPLOAD
# ==================================================

@router.post("/upload/full")
async def upload_full_book(
    file: UploadFile = File(...),

    title: str = Form(...),

    chapter_number: int | None = Form(None),

    class_level: str = Form(...),

    subject: str = Form(...),

    language: str = Form("en"),

    db: AsyncSession = Depends(get_db),
):
    """
    Upload a complete textbook PDF.
    """

    if not file.filename:

        return {
            "status": "error",
            "message": "No file selected.",
        }

    if not file.filename.lower().endswith(".pdf"):

        return {
            "status": "error",
            "message": "Only PDF files are supported.",
        }

    file_path = save_uploaded_file(
        file
    )

    try:

        processed_data = process_pdf(file_path, language=language)

    except Exception as error:

        return {
            "status": "error",
            "message": "Textbook processing failed.",
            "error": str(error),
        }

    chapters = processed_data["chapters"]

    if not chapters:
        # A chapter PDF often has no textbook-style heading. Store the
        # complete PDF as one chapter using the metadata supplied by the user.
        pages = processed_data["cleaned_pages"]
        if not pages:
            return {
                "status": "error",
                "message": "No readable text could be extracted from the PDF.",
            }
        chapters = [{
            "chapter_number": chapter_number or 1,
            "title": title,
            "start_page": pages[0]["page_number"],
            "end_page": pages[-1]["page_number"],
        }]
        processed_data["chapters"] = chapters

    try:

        book = await save_processed_book(
            db=db,
            title=title,
            class_level=class_level,
            subject=subject,
            language=(
                detect_language(processed_data["cleaned_text"])
                if language == "auto"
                else language
            ),
            upload_mode="full_book",
            source_file=file_path,
            processed_data=processed_data,
        )

    except Exception as error:

        return {
            "status": "error",
            "message": "Database save failed.",
            "error": str(error),
        }

    return {
        "status": "success",
        "message": (
            "Full textbook uploaded successfully."
        ),
        "book_id": book.id,
        "title": book.title,
        "class_level": book.class_level,
        "subject": book.subject,
        "language": book.language,
        "upload_mode": book.upload_mode,
        "pages_processed": processed_data[
            "page_count"
        ],
        "chapters_detected": len(
            chapters
        ),
        "chapters": chapters,
    }