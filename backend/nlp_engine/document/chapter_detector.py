import re


CHAPTER_PATTERNS = [
    re.compile(
        r"^\s*chapter\s+(\d+)\s*[:.\-]?\s*(.*?)\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*अध्याय\s+(\d+)\s*[:.\-]?\s*(.*?)\s*$",
    ),
]


def _looks_like_table_of_contents(text: str) -> bool:
    """
    Check whether a page looks like a table of contents.

    NCERT books often have multiple chapter titles and
    author names on the first page. Those titles should
    NOT be treated as actual chapter headings.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(lines) < 3:
        return False

    possible_entries = 0

    for line in lines:

        # Lines ending with a page number
        if re.search(r"\d+\s*$", line):
            possible_entries += 1

        # Short lines are often chapter titles or author names
        elif len(line.split()) <= 8:
            possible_entries += 1

    return possible_entries >= 5


def _find_real_chapter_heading(
    pages: list[dict],
) -> list[dict]:
    """
    Detect chapters that explicitly use headings such as:

        Chapter 1: Introduction
        Chapter 2: Motion

    Table-of-contents pages are ignored.
    """

    detected = []

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        # Ignore likely table-of-contents pages
        if page_number <= 2 and _looks_like_table_of_contents(text):
            continue

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for line in lines:

            for pattern in CHAPTER_PATTERNS:

                match = pattern.match(line)

                if match:

                    chapter_number = int(
                        match.group(1)
                    )

                    title = match.group(2).strip()

                    detected.append(
                        {
                            "chapter_number": chapter_number,
                            "title": title,
                            "start_page": page_number,
                        }
                    )

                    break

    return detected


def _clean_ocr_title(title: str) -> str:
    """
    Clean small OCR errors from a detected chapter title.

    Example:

        The Last Lesson iO]

    becomes:

        The Last Lesson
    """

    title = re.sub(
        r"\s+",
        " ",
        title,
    ).strip()

    # Remove common OCR noise appearing after
    # the actual chapter title.
    title = re.sub(
        r"\s*i[o0]\]?\s*$",
        "",
        title,
        flags=re.IGNORECASE,
    )

    return title.strip()


def _detect_single_chapter(
    pages: list[dict],
) -> list[dict]:
    """
    Detect a single chapter when the PDF does not
    contain an explicit 'Chapter 1' heading.

    Example:

        The Last Lesson iO]
        About the author

    The heading immediately before 'About the author'
    is treated as the chapter title.
    """

    # Skip the first page because NCERT books commonly
    # contain the table of contents there.
    candidate_pages = pages[1:]

    for page in candidate_pages:

        page_number = page["page_number"]

        lines = [
            line.strip()
            for line in page["text"].splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        for index, line in enumerate(lines):

            if index + 1 >= len(lines):
                continue

            next_line = lines[index + 1].lower()

            if next_line == "about the author":

                title = _clean_ocr_title(line)

                return [
                    {
                        "chapter_number": 1,
                        "title": title,
                        "start_page": page_number,
                    }
                ]

    return []


def detect_chapters(
    pages: list[dict],
) -> list[dict]:
    """
    Detect actual chapters from page-level NCERT text.

    Supports:

    1. Full textbooks with explicit headings:

       Chapter 1: Introduction
       Chapter 2: Motion

    2. Single-chapter PDFs where the chapter does
       not use an explicit chapter number:

       The Last Lesson
       About the author

    Table-of-contents pages are ignored.
    """

    # --------------------------------------------------
    # STEP 1
    # Try explicit chapter-number headings.
    # --------------------------------------------------

    chapters = _find_real_chapter_heading(
        pages
    )

    # --------------------------------------------------
    # STEP 2
    # If there are no explicit chapter headings,
    # treat the PDF as a single chapter.
    # --------------------------------------------------

    if not chapters:

        chapters = _detect_single_chapter(
            pages
        )

    # --------------------------------------------------
    # STEP 3
    # Remove duplicate chapter numbers.
    # --------------------------------------------------

    unique = {}

    for chapter in chapters:

        number = chapter["chapter_number"]

        if number not in unique:

            unique[number] = chapter

    chapters = list(
        unique.values()
    )

    # --------------------------------------------------
    # STEP 4
    # Sort chapters by chapter number.
    # --------------------------------------------------

    chapters.sort(
        key=lambda item: item["chapter_number"]
    )

    # --------------------------------------------------
    # STEP 5
    # Calculate chapter end pages.
    # --------------------------------------------------

    for index, chapter in enumerate(
        chapters
    ):

        if index + 1 < len(chapters):

            next_chapter = chapters[
                index + 1
            ]

            chapter["end_page"] = (
                next_chapter["start_page"] - 1
            )

        else:

            chapter["end_page"] = pages[
                -1
            ]["page_number"]

    return chapters