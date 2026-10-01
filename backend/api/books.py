from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database.models import Book, Chapter


router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


# ==================================================
# CREATE BOOK
# ==================================================

@router.post("/create")
async def create_book(
    title: str = Form(...),
    class_level: str = Form(...),
    subject: str = Form(...),
    language: str = Form("en"),
    db: AsyncSession = Depends(get_db),
):
    book = Book(
        title=title,
        class_level=class_level,
        subject=subject,
        language=language,
        upload_mode="chapter",
        processing_status="completed",
    )

    db.add(book)
    await db.commit()
    await db.refresh(book)

    return {
        "status": "success",
        "message": "Book created successfully.",
        "id": book.id,
        "book_id": book.id,
        "title": book.title,
        "class_level": book.class_level,
        "subject": book.subject,
        "language": book.language,
    }


# ==================================================
# LIST BOOKS
# ==================================================

@router.get("")
@router.get("/")
async def list_books(
    db: AsyncSession = Depends(get_db),
):
    """
    Return all books and their chapters.
    Normalized with both 'id' and 'book_id' for frontend compatibility.
    """
    result = await db.execute(select(Book))
    books = result.scalars().all()

    response = []
    for book in books:
        chapter_result = await db.execute(
            select(Chapter)
            .where(Chapter.book_id == book.id)
            .order_by(Chapter.chapter_number)
        )
        chs = chapter_result.scalars().all()

        response.append({
            "id": book.id,
            "book_id": book.id,
            "title": book.title,
            "class_level": book.class_level,
            "subject": book.subject,
            "language": book.language,
            "processing_status": book.processing_status,
            "overall_summary": f"NCERT {book.subject} for Class {book.class_level}. Contains {len(chs)} chapters.",
            "chapters": [
                {
                    "id": ch.id,
                    "chapter_id": ch.id,
                    "chapter_num": ch.chapter_number,
                    "chapter_number": ch.chapter_number,
                    "title": ch.title,
                    "page_start": ch.page_start,
                    "page_end": ch.page_end,
                    "word_count": ch.word_count,
                    "processing_status": ch.processing_status,
                }
                for ch in chs
            ],
        })

    # Return list directly so both array-expecting and object-expecting clients work
    return response


# ==================================================
# GET SINGLE BOOK
# ==================================================

@router.get("/{book_id}")
async def get_book(
    book_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    chapter_result = await db.execute(
        select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.chapter_number)
    )
    chs = chapter_result.scalars().all()

    return {
        "id": book.id,
        "book_id": book.id,
        "title": book.title,
        "class_level": book.class_level,
        "subject": book.subject,
        "language": book.language,
        "processing_status": book.processing_status,
        "overall_summary": f"NCERT {book.subject} for Class {book.class_level}. Contains {len(chs)} chapters.",
        "chapters": [
            {
                "id": ch.id,
                "chapter_id": ch.id,
                "chapter_num": ch.chapter_number,
                "chapter_number": ch.chapter_number,
                "title": ch.title,
                "page_start": ch.page_start,
                "page_end": ch.page_end,
                "word_count": ch.word_count,
            }
            for ch in chs
        ],
    }


# ==================================================
# GET CHAPTERS FOR A BOOK
# ==================================================

@router.get("/{book_id}/chapters")
async def get_book_chapters(
    book_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Chapter)
        .where(Chapter.book_id == book_id)
        .order_by(Chapter.chapter_number)
    )
    chs = result.scalars().all()

    return [
        {
            "id": ch.id,
            "chapter_id": ch.id,
            "chapter_num": ch.chapter_number,
            "chapter_number": ch.chapter_number,
            "title": ch.title,
            "page_start": ch.page_start,
            "page_end": ch.page_end,
            "word_count": ch.word_count,
            "processing_status": ch.processing_status,
        }
        for ch in chs
    ]


# ==================================================
# GET SINGLE CHAPTER
# ==================================================

@router.get("/chapters/{chapter_id}")
async def get_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()

    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found.")

    return {
        "id": chapter.id,
        "chapter_id": chapter.id,
        "book_id": chapter.book_id,
        "chapter_num": chapter.chapter_number,
        "chapter_number": chapter.chapter_number,
        "title": chapter.title,
        "page_start": chapter.page_start,
        "page_end": chapter.page_end,
        "word_count": chapter.word_count,
        "cleaned_text": chapter.cleaned_text,
        "processing_status": chapter.processing_status,
    }