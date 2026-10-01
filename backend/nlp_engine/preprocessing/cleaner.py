import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean extracted NCERT text while preserving
    meaningful paragraph structure.
    """

    if not text:
        return ""

    # Normalize Unicode characters
    text = unicodedata.normalize("NFC", text)

    # Replace non-breaking spaces
    text = text.replace("\xa0", " ")

    # Normalize dash characters
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Remove control characters
    text = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f]",
        " ",
        text,
    )

    # Remove spaces at the beginning/end of lines
    text = re.sub(
        r"[ \t]*\n[ \t]*",
        "\n",
        text,
    )

    # Preserve paragraph breaks temporarily
    text = re.sub(
        r"\n{2,}",
        "\n\n",
        text,
    )

    # PDF extraction often puts every visual line
    # on a separate line. Convert single line breaks
    # into spaces.
    text = re.sub(
        r"(?<!\n)\n(?!\n)",
        " ",
        text,
    )

    # Remove repeated spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Remove spaces immediately before punctuation
    text = re.sub(
        r"\s+([,.!?;:])",
        r"\1",
        text,
    )

    # Clean spaces around quotation marks
    text = re.sub(
        r'"\s+',
        '"',
        text,
    )

    # Final cleanup
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()