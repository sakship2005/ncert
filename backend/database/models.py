from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)


from database.database import Base


class Book(Base):
    """
    Represents an NCERT textbook.

    A book can contain multiple chapters.
    """

    __tablename__ = "books"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    title = Column(
        String,
        nullable=False,
    )

    class_level = Column(
        String,
        nullable=False,
    )

    subject = Column(
        String,
        nullable=False,
    )

    language = Column(
        String,
        default="en",
    )

    upload_mode = Column(
        String,
        nullable=False,
    )
    # "full_book" or "chapter"

    source_file = Column(
        String,
        nullable=True,
    )

    processing_status = Column(
        String,
        default="pending",
    )
    # pending
    # processing
    # completed
    # failed

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


class Chapter(Base):
    """
    Represents one chapter inside a book.

    A chapter can come from either:
    - full textbook upload
    - chapter-wise upload
    """

    __tablename__ = "chapters"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    book_id = Column(
        String,
        nullable=False,
    )

    chapter_number = Column(
        Integer,
        nullable=False,
    )

    title = Column(
        String,
        nullable=False,
    )

    source_file = Column(
        String,
        nullable=True,
    )

    page_start = Column(
        Integer,
        nullable=True,
    )

    page_end = Column(
        Integer,
        nullable=True,
    )

    original_text = Column(
        Text,
        default="",
    )

    cleaned_text = Column(
        Text,
        default="",
    )

    word_count = Column(
        Integer,
        default=0,
    )

    processing_status = Column(
        String,
        default="pending",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint(
            "book_id",
            "chapter_number",
            name="unique_book_chapter",
        ),
    )