from nlp_engine.document.pdf_extractor import extract_pdf_text
from nlp_engine.document.ocr import ocr_pdf
from nlp_engine.document.chapter_detector import detect_chapters
from nlp_engine.preprocessing.cleaner import clean_text


MIN_EXTRACTED_TEXT = 200


def process_pdf(pdf_path: str, language: str = "auto") -> dict:
    """
    Process an NCERT PDF.

    Pipeline:

    PDF
      ↓
    Normal text extraction
      ↓
    OCR fallback if necessary
      ↓
    Text cleaning
      ↓
    Chapter detection
    """

    # -----------------------------------------
    # 1. Try normal PDF extraction
    # -----------------------------------------

    extracted = extract_pdf_text(pdf_path)

    # -----------------------------------------
    # 2. OCR fallback
    # -----------------------------------------

    if language in {"hi", "both"} or extracted["text_length"] < MIN_EXTRACTED_TEXT:

        print("[document] Normal extraction insufficient.")
        print("[document] Running OCR...")

        extracted = ocr_pdf(pdf_path, language=language)

    else:

        print("[document] Normal PDF extraction successful.")

    # -----------------------------------------
    # 3. Clean page text
    # -----------------------------------------

    cleaned_pages = []

    for page in extracted["pages"]:

        cleaned = clean_text(page["text"])

        cleaned_pages.append({
            "page_number": page["page_number"],
            "text": cleaned,
        })

    # -----------------------------------------
    # 4. Rebuild cleaned full text
    # -----------------------------------------

    cleaned_text = "\n\n".join(
        page["text"]
        for page in cleaned_pages
        if page["text"]
    )

    # -----------------------------------------
    # 5. Detect chapters
    # -----------------------------------------

    chapters = detect_chapters(cleaned_pages)

    return {
    "page_count": extracted["page_count"],
    "original_text": extracted["text"],
    "cleaned_text": cleaned_text,
    "cleaned_pages": cleaned_pages,
    "text_length": len(cleaned_text),
    "chapters": chapters,
}