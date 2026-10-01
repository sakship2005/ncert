import os

import fitz
import pytesseract

from PIL import Image


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def ocr_pdf(pdf_path: str, language: str = "auto") -> dict:
    """
    Run OCR on each page of a PDF.
    """

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        image = Image.frombytes(
            "RGB",
            [pixmap.width, pixmap.height],
            pixmap.samples,
        )

        # Hindi scans must be OCR'd with the Devanagari model. Keep English
        # enabled as well because NCERT books commonly contain both scripts.
        ocr_language = "hin+eng" if language in {"hi", "both", "auto"} else "eng"
        try:
            text = pytesseract.image_to_string(image, lang=ocr_language)
        except pytesseract.TesseractError:
            text = pytesseract.image_to_string(image, lang="eng")

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