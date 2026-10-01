from nlp_engine.analysis.keywords import extract_keywords
from nlp_engine.analysis.concepts import extract_concepts
from nlp_engine.analysis.entities import extract_entities
from nlp_engine.analysis.topics import extract_topics
from nlp_engine.analysis.vocabulary import extract_vocabulary

from nlp_engine.preprocessing.cleaner import clean_text
from nlp_engine.preprocessing.tokenizer import (
    split_sentences,
    tokenize_words,
)
from nlp_engine.preprocessing.language import detect_language


def analyze_chapter(
    text: str,
    keyword_count: int = 15,
    concept_count: int = 15,
    vocabulary_count: int = 15,
    topic_count: int = 3,
) -> dict:
    """
    Perform a complete NLP analysis of an NCERT chapter.

    This function is generic and does not depend
    on any particular chapter or subject.
    """

    if not text or not text.strip():
        return {
            "status": "error",
            "message": "Chapter text is empty.",
        }

    # --------------------------------------------------
    # Preprocessing
    # --------------------------------------------------

    cleaned_text = clean_text(text)

    sentences = split_sentences(
        cleaned_text
    )

    words = tokenize_words(
        cleaned_text
    )

    language = detect_language(
        cleaned_text
    )

    # --------------------------------------------------
    # NLP Analysis
    # --------------------------------------------------

    keywords = extract_keywords(
        cleaned_text,
        top_n=keyword_count,
    )

    concepts = extract_concepts(
        cleaned_text,
        top_n=concept_count,
    )

    entities = extract_entities(
        cleaned_text,
    )

    topics = extract_topics(
        cleaned_text,
        num_topics=topic_count,
    )

    vocabulary = extract_vocabulary(
        cleaned_text,
        top_n=vocabulary_count,
    )

    # --------------------------------------------------
    # Final NLP representation
    # --------------------------------------------------

    return {
        "status": "success",

        "statistics": {
            "characters": len(cleaned_text),
            "words": len(words),
            "sentences": len(sentences),
        },

        "language": language,

        "keywords": keywords,

        "concepts": concepts,

        "entities": entities,

        "topics": topics,

        "vocabulary": vocabulary,
    }