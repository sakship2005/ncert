import re


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences.
    """

    if not text or not text.strip():
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def create_chunks(
    text: str,
    sentences_per_chunk: int = 5,
    overlap: int = 1,
) -> list[dict]:
    """
    Divide text into overlapping semantic chunks.

    Each chunk contains a group of consecutive sentences.
    """

    if not text or not text.strip():
        return []

    sentences = split_into_sentences(text)

    if not sentences:
        return []

    chunks = []

    start = 0
    chunk_number = 1

    while start < len(sentences):

        end = min(
            start + sentences_per_chunk,
            len(sentences),
        )

        chunk_sentences = sentences[start:end]

        chunk_text = " ".join(chunk_sentences)

        chunks.append({
            "chunk_id": chunk_number,
            "text": chunk_text,
            "sentence_start": start + 1,
            "sentence_end": end,
        })

        if end >= len(sentences):
            break

        start = end - overlap
        chunk_number += 1

    return chunks