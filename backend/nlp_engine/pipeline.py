from nlp_engine.preprocessing.cleaner import clean_text
from nlp_engine.preprocessing.tokenizer import (
    split_sentences,
    tokenize_words,
)
from nlp_engine.preprocessing.language import detect_language


def analyze_text(text: str) -> dict:
    """
    First stage of the NCERT NLP Engine.

    Takes raw text and performs:
    - text cleaning
    - language detection
    - sentence segmentation
    - word tokenization
    """

    # Clean the text
    cleaned_text = clean_text(text)

    # Detect language
    language = detect_language(cleaned_text)

    # Split into sentences
    sentences = split_sentences(cleaned_text)

    # Tokenize into words
    words = tokenize_words(cleaned_text)

    return {
        "language": language,
        "characters": len(cleaned_text),
        "words": len(words),
        "sentences": len(sentences),
        "sentences_preview": sentences[:10],
    }