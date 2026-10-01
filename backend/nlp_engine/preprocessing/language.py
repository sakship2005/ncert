import re


def detect_language(text: str) -> str:
    """
    Detect whether the text is mainly English or Hindi.

    Returns:
        "en"      -> English
        "hi"      -> Hindi
        "unknown" -> Cannot determine
    """

    if not text or not text.strip():
        return "unknown"

    # Count Hindi/Devanagari characters
    hindi_chars = len(
        re.findall(r"[\u0900-\u097F]", text)
    )

    # Count English alphabet characters
    english_chars = len(
        re.findall(r"[A-Za-z]", text)
    )

    if hindi_chars == 0 and english_chars == 0:
        return "unknown"

    if hindi_chars > english_chars:
        return "hi"

    return "en"