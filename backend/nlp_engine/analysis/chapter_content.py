import re


def clean_text(text: str) -> str:
    """
    Basic cleanup while preserving the original
    paragraph structure.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\xa0", " ")

    # Remove reprint markers
    text = re.sub(
        r"Reprint\s+\d{4}-\d{2}",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove obvious page numbers
    text = re.sub(
        r"(?m)^\s*\d+\s*$",
        "",
        text,
    )

    # Remove page references such as:
    # The Last Lesson/3
    # 4/Flamingo
    text = re.sub(
        r"(?m)^\s*The Last Lesson/\d+\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"(?m)^\s*\d+/Flamingo\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove obvious extraction fragments
    text = re.sub(
        r"(?m)^\s*(rec|F|ae\)|ba-)\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text


def find_story_start(lines: list[str]) -> int:
    """
    Find the beginning of the actual story.

    For the NCERT 'The Last Lesson' structure,
    the story begins with:

    'I started for school very late...'
    """

    for index, line in enumerate(lines):

        normalized = re.sub(
            r"\s+",
            " ",
            line,
        ).strip().lower()

        if normalized.startswith(
            "i started for school"
        ):
            return index

    return 0


def is_end_section(line: str) -> bool:
    """
    Detect the beginning of exercises/reference
    material after the story.
    """

    text = re.sub(
        r"\s+",
        " ",
        line,
    ).strip().lower()

    end_sections = [
        "thinking about the text",
        "thinking about language",
        "noticing form",
        "working with words",
        "working with language",
        "understanding the text",
        "things to do",
        "activities",
        "activity",
        "questions",
        "exercise",
        "exercises",
        "writing",
        "grammar",
        "vocabulary",
        "discussion",
        "speaking",
    ]

    for heading in end_sections:

        if text == heading:
            return True

        if text.startswith(
            heading + ":"
        ):
            return True

    return False


def clean_story_line(line: str) -> str:
    """
    Clean individual story lines without trying
    to interpret their meaning.
    """

    line = re.sub(
        r"\s+",
        " ",
        line,
    ).strip()

    # Common PDF word joins
    replacements = {
        "schoolvery": "school very",
        "thelast": "the last",
        "shallgive": "shall give",
        "onhis": "on his",
        "inhis": "in his",
        "inthe": "in the",
        "onthe": "on the",
        "tothe": "to the",
        "ofthe": "of the",
        "forthe": "for the",
        "withthe": "with the",
        "atthe": "at the",
        "bythe": "by the",
        "fromthe": "from the",
        "fromhis": "from his",
        "tohim": "to him",
        "toher": "to her",
        "withme": "with me",
        "ourheads": "our heads",
        "beinglate": "being late",
        "toldme": "told me",
        "couldn't": "couldn't",
    }

    for wrong, correct in replacements.items():

        line = re.sub(
            rf"\b{wrong}\b",
            correct,
            line,
            flags=re.IGNORECASE,
        )

    # Remove isolated extraction number
    line = re.sub(
        r"\s+\d+\s*$",
        "",
        line,
    )

    return line.strip()


def extract_chapter_content(
    text: str,
) -> str:
    """
    Extract the actual NCERT chapter/story.

    Strategy:

    1. Clean PDF artifacts.
    2. Find where the story starts.
    3. Keep story content.
    4. Stop when an exercise/reference section
       begins.
    """

    if not text:
        return ""

    text = clean_text(text)

    lines = text.splitlines()

    # --------------------------------------------------------
    # Find story beginning
    # --------------------------------------------------------

    start_index = find_story_start(
        lines
    )

    story_lines = []

    # --------------------------------------------------------
    # Extract story
    # --------------------------------------------------------

    for line in lines[start_index:]:

        line = line.strip()

        if not line:
            continue

        # Stop at exercise/reference section
        if is_end_section(line):
            break

        # Ignore obvious page artifacts
        lower = line.lower()

        if lower.startswith(
            "reprint "
        ):
            continue

        if lower.startswith(
            "the last lesson/"
        ):
            continue

        if lower.startswith(
            "flamingo"
        ):
            continue

        cleaned = clean_story_line(
            line
        )

        if cleaned:
            story_lines.append(
                cleaned
            )

    # --------------------------------------------------------
    # Join lines
    # --------------------------------------------------------

    return "\n".join(
        story_lines
    ).strip()