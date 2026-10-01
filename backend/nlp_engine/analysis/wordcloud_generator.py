from collections import Counter

import matplotlib.pyplot as plt
from wordcloud import WordCloud

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


nltk.download("stopwords")
nltk.download("punkt")
nltk.download("punkt_tab")


def generate_wordcloud(
    text: str,
    output_path: str = "storage/wordcloud.png",
) -> dict:
    """
    Generate a word cloud from NCERT chapter text.

    The function:
    1. Tokenizes the text.
    2. Removes stopwords.
    3. Removes punctuation and numbers.
    4. Calculates word frequencies.
    5. Generates a word cloud image.
    """

    if not text or not text.strip():
        return {
            "status": "error",
            "message": "Text is empty.",
        }

    # --------------------------------------------------
    # Tokenization
    # --------------------------------------------------

    words = word_tokenize(
        text.lower()
    )

    # --------------------------------------------------
    # Stopword removal
    # --------------------------------------------------

    stop_words = set(
        stopwords.words("english")
    )

    filtered_words = []

    for word in words:

        # Keep alphabetic words only
        if not word.isalpha():
            continue

        # Remove common English words
        if word in stop_words:
            continue

        # Ignore very short words
        if len(word) < 3:
            continue

        filtered_words.append(word)

    if not filtered_words:
        return {
            "status": "error",
            "message": "No meaningful words found.",
        }

    # --------------------------------------------------
    # Word frequency
    # --------------------------------------------------

    frequency = Counter(
        filtered_words
    )

    # --------------------------------------------------
    # Generate Word Cloud
    # --------------------------------------------------

    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        max_words=100,
        collocations=False,
    ).generate_from_frequencies(
        frequency
    )

    # --------------------------------------------------
    # Save image
    # --------------------------------------------------

    wordcloud.to_file(
        output_path
    )

    # --------------------------------------------------
    # Close matplotlib figure
    # --------------------------------------------------

    plt.close()

    # --------------------------------------------------
    # Return information
    # --------------------------------------------------

    return {
        "status": "success",
        "output_path": output_path,
        "total_words": len(filtered_words),
        "unique_words": len(frequency),
        "top_words": [
            {
                "word": word,
                "frequency": count,
            }
            for word, count in frequency.most_common(20)
        ],
    }