import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

HINDI_STOPS = {
    "और", "था", "थी", "थे", "है", "हैं", "का", "के", "की", "में", "से", "पर",
    "ने", "को", "भी", "यह", "वह", "तो", "ही", "एक", "इस", "उस", "नहीं",
    "गया", "गई", "गए", "लिए", "बाद", "कहा", "किया", "हो", "था।", "है।",
}


def _pack_topic(topic_number: int, topic_words: list[str]) -> dict:
    name = (topic_words[0] if topic_words else f"Theme {topic_number}").strip()
    if name:
        name = name[:1].upper() + name[1:]
    return {
        "topic": topic_number,
        "name": name,
        "words": topic_words,
        "keywords": topic_words,
    }


def extract_topics(
    text: str,
    num_topics: int = 3,
    words_per_topic: int = 8,
) -> list[dict]:
    """
    Extract major topics from NCERT text using LDA (English)
    or frequency clusters (Hindi / Devanagari).
    """

    if not text or not text.strip():
        return []

    is_hindi = len(re.findall(r"[\u0900-\u097F]", text)) > (len(text) * 0.15)
    if is_hindi:
        tokens = [w for w in re.findall(r"[\u0900-\u097F]{3,}", text) if w not in HINDI_STOPS]
        if not tokens:
            return []
        counts = Counter(tokens).most_common(num_topics * words_per_topic)
        topics = []
        chunk_size = max(words_per_topic, 1)
        for i in range(num_topics):
            slice_words = [w for w, _ in counts[i * 3:(i * 3) + chunk_size]]
            if not slice_words:
                break
            topics.append(_pack_topic(i + 1, slice_words))
        return topics

    vectorizer = CountVectorizer(
        stop_words="english",
        lowercase=True,
        max_features=3000,
        ngram_range=(1, 2),
    )

    try:
        document_term_matrix = vectorizer.fit_transform([text])
    except ValueError:
        return []

    if document_term_matrix.shape[1] == 0:
        return []

    lda = LatentDirichletAllocation(
        n_components=min(
            num_topics,
            document_term_matrix.shape[1],
        ),
        random_state=42,
    )

    lda.fit(document_term_matrix)

    feature_names = vectorizer.get_feature_names_out()

    topics = []

    for topic_number, topic in enumerate(
        lda.components_,
        start=1,
    ):
        top_indices = topic.argsort()[
            -words_per_topic:
        ][::-1]

        topic_words = [
            feature_names[index]
            for index in top_indices
        ]

        topics.append(_pack_topic(topic_number, topic_words))

    return topics