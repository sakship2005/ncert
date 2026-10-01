import nltk

nltk.download("punkt")
nltk.download("punkt_tab")


def split_sentences(text: str) -> list[str]:
    """
    Split NCERT text into sentences.
    """

    if not text:
        return []

    return [
        sentence.strip()
        for sentence in nltk.sent_tokenize(text)
        if sentence.strip()
    ]


def tokenize_words(text: str) -> list[str]:
    """
    Tokenize text into individual words.
    """

    if not text:
        return []

    return nltk.word_tokenize(text)