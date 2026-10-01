from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp_engine.retrieval.embeddings import (
    generate_embeddings,
)


def calculate_tfidf_similarity(
    sentence_a: str,
    sentence_b: str,
) -> float:
    """
    Calculate similarity between two sentences
    using TF-IDF and cosine similarity.
    """

    if not sentence_a.strip() or not sentence_b.strip():
        return 0.0

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform([
        sentence_a,
        sentence_b,
    ])

    similarity = cosine_similarity(
        vectors[0:1],
        vectors[1:2],
    )[0][0]

    return round(float(similarity), 4)


def calculate_semantic_similarity(
    sentence_a: str,
    sentence_b: str,
) -> float:
    """
    Calculate semantic similarity between two
    sentences using sentence embeddings.
    """

    if not sentence_a.strip() or not sentence_b.strip():
        return 0.0

    embeddings = generate_embeddings([
        sentence_a,
        sentence_b,
    ])

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]],
    )[0][0]

    return round(float(similarity), 4)


def compare_sentences(
    sentence_a: str,
    sentence_b: str,
) -> dict:
    """
    Compare two sentences using both
    traditional NLP and semantic embeddings.
    """

    tfidf_score = calculate_tfidf_similarity(
        sentence_a,
        sentence_b,
    )

    semantic_score = calculate_semantic_similarity(
        sentence_a,
        sentence_b,
    )

    return {
        "sentence_a": sentence_a,
        "sentence_b": sentence_b,
        "tfidf_similarity": tfidf_score,
        "semantic_similarity": semantic_score,
    }