import fitz


def extract_page_text(page) -> str:
    """
    Extract text using PDF word positions.

    Using word-level extraction helps preserve spaces
    between words that may be incorrectly joined by
    normal PDF text extraction.
    """

    words = page.get_text("words")

    if not words:
        return ""

    # Sort by block, line, and horizontal position
    words = sorted(
        words,
        key=lambda word: (
            word[5],  # block number
            word[6],  # line number
            word[7],  # word number
        ),
    )

    lines = []
    current_line = []
    current_line_number = None
    current_block_number = None

    for word in words:

        x0, y0, x1, y1, text, block_no, line_no, word_no = word

        # New block or new line
        if (
            current_line
            and (
                block_no != current_block_number
                or line_no != current_line_number
            )
        ):
            lines.append(
                " ".join(current_line)
            )

            current_line = []

        current_line.append(text)

        current_block_number = block_no
        current_line_number = line_no

    # Add final line
    if current_line:
        lines.append(
            " ".join(current_line)
        )

    return "\n".join(lines)


def extract_pdf_text(pdf_path: str) -> dict:
    """
    Extract text from an NCERT PDF while preserving
    word spacing and page information.
    """

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(
        document,
        start=1,
    ):

        text = extract_page_text(page)

        pages.append({
            "page_number": page_number,
            "text": text.strip(),
        })

    document.close()

    full_text = "\n\n".join(
        page["text"]
        for page in pages
        if page["text"]
    )

    return {
        "page_count": len(pages),
        "pages": pages,
        "text": full_text,
        "text_length": len(full_text),
    }