import re


def normalize_text(text: str) -> str:
    """
    Normalize whitespace for classification.
    """

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def is_question_or_exercise(text: str) -> bool:
    """
    Detect NCERT questions, exercises and activities.
    """

    text = normalize_text(text)
    lower = text.lower()

    # Explicit question mark
    if "?" in text:
        return True

    patterns = [
        r"^what did\b",
        r"^what do\b",
        r"^what is\b",
        r"^what are\b",
        r"^why did\b",
        r"^why do\b",
        r"^why was\b",
        r"^why were\b",
        r"^how did\b",
        r"^how does\b",
        r"^how was\b",
        r"^how were\b",
        r"^who\b",
        r"^where\b",
        r"^when\b",
        r"^which\b",

        r"^answer\b",
        r"^discuss\b",
        r"^explain\b",
        r"^describe\b",
        r"^narrate\b",
        r"^write\b",
        r"^find\b",
        r"^find out\b",
        r"^pick out\b",
        r"^identify\b",
        r"^compare\b",
        r"^complete\b",
        r"^choose\b",
        r"^select\b",
        r"^say why\b",
        r"^give reasons\b",
        r"^give reason\b",
        r"^make a list\b",
        r"^list\b",
    ]

    return any(
        re.search(pattern, lower)
        for pattern in patterns
    )


def is_answer_option(text: str) -> bool:
    """
    Detect MCQ or exercise answer options.
    """

    text = normalize_text(text)

    patterns = [
        r"^\([a-z]\)",
        r"^\([ivxlcdm]+\)",
        r"^[a-z]\.",
        r"^[ivxlcdm]+\.",
        r"^\d+\.",
    ]

    return any(
        re.match(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
        for pattern in patterns
    )


def is_teacher_material(text: str) -> bool:
    """
    Detect teacher-support/reference material.
    """

    text = normalize_text(text)
    lower = text.lower()

    patterns = [
        r"^this shall help pupils\b",
        r"^this will help pupils\b",
        r"^this activity\b",
        r"^there could be\b",
        r"^there can be\b",
        r"^students need\b",
        r"^students may\b",
        r"^students should\b",
        r"^teacher\b",
        r"^teaching\b",
        r"^discussion\b",
        r"^follow[- ]?up\b",
        r"^noticing form\b",
        r"^learning outcome\b",
        r"^learning outcomes\b",
        r"^classroom\b",
        r"^activity\b",
        r"^suggested activity\b",
    ]

    return any(
        re.search(pattern, lower)
        for pattern in patterns
    )


def is_reference_noise(text: str) -> bool:
    """
    Detect common textbook/reference artifacts.
    """

    text = normalize_text(text)
    lower = text.lower()

    patterns = [
        r"^reprint\b",
        r"^contents\b",
        r"^glossary\b",
        r"^notes?\b",
        r"^noticing form\b",
        r"^language work\b",
        r"^reading comprehension\b",
        r"^writing\b",
        r"^grammar\b",
        r"^vocabulary\b",
        r"^project work\b",
        r"^activities\b",
        r"^exercise\b",
        r"^questions?\b",
    ]

    return any(
        re.search(pattern, lower)
        for pattern in patterns
    )


def is_fragment(text: str) -> bool:
    """
    Detect obvious incomplete text fragments.
    """

    text = normalize_text(text)

    if not text:
        return True

    words = text.split()

    if len(words) < 7:
        return True

    # Lowercase beginning usually indicates a PDF fragment.
    if text[0].islower():
        return True

    return False


def is_valid_chapter_sentence(text: str) -> bool:
    """
    Final classifier for sentences that belong to
    actual NCERT chapter content.
    """

    text = normalize_text(text)

    if not text:
        return False

    if is_fragment(text):
        return False

    if is_question_or_exercise(text):
        return False

    if is_answer_option(text):
        return False

    if is_teacher_material(text):
        return False

    if is_reference_noise(text):
        return False

    return True


def clean_content_sentences(
    sentences: list[str],
) -> list[str]:
    """
    Keep only sentences that appear to belong to
    the actual chapter narrative/content.
    """

    cleaned = []

    for sentence in sentences:

        sentence = normalize_text(
            sentence
        )

        if is_valid_chapter_sentence(
            sentence
        ):
            cleaned.append(sentence)

    return cleaned