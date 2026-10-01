from sklearn.feature_extraction.text import TfidfVectorizer


def extract_keywords(
    text: str,
    top_n: int = 20,
) -> list[dict]:
    """
    Extract important keywords from NCERT text
    using TF-IDF.

    TF-IDF gives higher importance to terms that
    are important within the supplied document.
    """

    if not text or not text.strip():
        return []

    # --------------------------------------------------
    # Create TF-IDF vectorizer
    # --------------------------------------------------

    vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True,
        max_features=5000,
        ngram_range=(1, 2),
    )

    try:

        matrix = vectorizer.fit_transform(
            [text]
        )

    except ValueError:

        return []

    # --------------------------------------------------
    # Get feature names
    # --------------------------------------------------

    feature_names = vectorizer.get_feature_names_out()

    scores = matrix.toarray()[0]

    # --------------------------------------------------
    # Pair keyword with score
    # --------------------------------------------------

    keyword_scores = []

    for word, score in zip(
        feature_names,
        scores,
    ):

        if score <= 0:
            continue

        keyword_scores.append(
            {
                "keyword": word,
                "score": round(
                    float(score),
                    4,
                ),
            }
        )

    # --------------------------------------------------
    # Sort by importance
    # --------------------------------------------------

    keyword_scores.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return keyword_scores[:top_n]