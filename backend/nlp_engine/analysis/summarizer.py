import re

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from nlp_engine.retrieval.embeddings import (
    generate_embeddings,
)

from nlp_engine.analysis.chapter_content import (
    extract_chapter_content,
)


# ============================================================
# SENTENCE SPLITTING
# ============================================================

def split_into_sentences(text: str) -> list[str]:
    """
    Split chapter text into individual sentences.
    """

    if not text or not text.strip():
        return []

    # Normalize whitespace first
    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    # Sentence boundary detection
    sentences = re.split(
        r"(?<=[.!?])\s+(?=[A-Z\"“])",
        text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ============================================================
# PDF NOISE REMOVAL
# ============================================================

def remove_pdf_noise(sentence: str) -> str:
    """
    Remove common PDF extraction artifacts.
    """

    if not sentence:
        return ""

    sentence = sentence.strip()

    # Remove common page markers
    sentence = re.sub(
        r"Reprint\s+\d{4}-\d{2}",
        "",
        sentence,
        flags=re.IGNORECASE,
    )

    sentence = re.sub(
        r"The Last Lesson\s*/\s*\d+",
        "",
        sentence,
        flags=re.IGNORECASE,
    )

    # Remove isolated page numbers
    sentence = re.sub(
        r"\s+\d+\s*$",
        "",
        sentence,
    )

    # Fix spaces before punctuation
    sentence = re.sub(
        r"\s+([,.!?;:])",
        r"\1",
        sentence,
    )

    # Normalize multiple spaces
    sentence = re.sub(
        r"\s+",
        " ",
        sentence,
    )

    return sentence.strip()


# ============================================================
# COMMON PDF WORD-JOIN FIXES
# ============================================================

def fix_common_word_joins(sentence: str) -> str:
    """
    Fix common word-joining errors caused by PDF extraction.

    This is intentionally conservative so that valid
    words are not accidentally changed.
    """

    if not sentence:
        return ""

    replacements = {
        "infrontof": "in front of",
        "inthe": "in the",
        "onthe": "on the",
        "tothe": "to the",
        "ofthe": "of the",
        "forthe": "for the",
        "fromthe": "from the",
        "withthe": "with the",
        "atthe": "at the",
        "bythe": "by the",
        "andthe": "and the",
        "fromhis": "from his",
        "fromher": "from her",
        "inhis": "in his",
        "inher": "in her",
        "withhis": "with his",
        "withher": "with her",
        "tome": "to me",
        "forme": "for me",
        "tohim": "to him",
        "toher": "to her",
        "withme": "with me",
        "beinglate": "being late",
        "toldme": "told me",
        "shallgive": "shall give",
        "justhow": "just how",
        "andnow": "and now",
        "wasin": "was in",
        "sawme": "saw me",
        "everythinglooked": "everything looked",
        "sittingmotionless": "sitting motionless",
    }

    for wrong, correct in replacements.items():

        sentence = re.sub(
            rf"\b{wrong}\b",
            correct,
            sentence,
            flags=re.IGNORECASE,
        )

    return sentence


# ============================================================
# SENTENCE CLEANING
# ============================================================

def clean_sentence(sentence: str) -> str:
    """
    Apply all sentence-level cleaning.
    """

    if not sentence:
        return ""

    sentence = remove_pdf_noise(
        sentence
    )

    sentence = fix_common_word_joins(
        sentence
    )

    sentence = re.sub(
        r"\s+",
        " ",
        sentence,
    )

    return sentence.strip()


# ============================================================
# EXERCISE DETECTION
# ============================================================

def is_exercise_sentence(sentence: str) -> bool:
    """
    Detect obvious NCERT exercise/question sentences.

    This is an additional safety layer after the
    chapter-content extraction step.
    """

    if not sentence:
        return True

    text = sentence.strip().lower()

    # Direct question
    if "?" in text:
        return True

    patterns = [
        r"^what\b",
        r"^why\b",
        r"^how\b",
        r"^who\b",
        r"^where\b",
        r"^when\b",
        r"^which\b",

        r"^answer\b",
        r"^discuss\b",
        r"^explain\b",
        r"^describe\b",
        r"^narrate\b",
        r"^write\b",
        r"^find\b",
        r"^find out\b",
        r"^identify\b",
        r"^compare\b",
        r"^complete\b",
        r"^choose\b",
        r"^select\b",
        r"^pick out\b",
        r"^give reason\b",
        r"^give reasons\b",
        r"^say why\b",
        r"^make a list\b",
        r"^list\b",
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            text,
        ):
            return True

    return False


# ============================================================
# SENTENCE VALIDATION
# ============================================================

def is_valid_sentence(sentence: str) -> bool:
    """
    Decide whether a sentence is suitable for
    extractive summarization.
    """

    if not sentence:
        return False

    sentence = sentence.strip()

    # Too short
    if len(sentence.split()) < 7:
        return False

    # Too long
    if len(sentence.split()) > 80:
        return False

    # Exercise/question
    if is_exercise_sentence(
        sentence
    ):
        return False

    # Obvious instructional material
    lower = sentence.lower()

    instructional_terms = [
        "this shall help pupils",
        "this will help pupils",
        "these help pupils",
        "students should",
        "students may",
        "students need",
        "teacher should",
        "learning outcome",
        "learning outcomes",
        "noticing form",
        "suggested activity",
        "follow-up activity",
    ]

    for term in instructional_terms:

        if term in lower:
            return False

    # Remove obvious MCQ options
    if re.match(
        r"^\([a-z]\)",
        sentence,
        flags=re.IGNORECASE,
    ):
        return False

    if re.match(
        r"^[a-z]\.",
        sentence,
        flags=re.IGNORECASE,
    ):
        return False

    if re.match(
        r"^\d+\.",
        sentence,
    ):
        return False

    # Lowercase beginning usually indicates a PDF fragment
    if sentence[0].islower():
        return False

    return True


# ============================================================
# FILTER SENTENCES
# ============================================================

def filter_sentences(
    sentences: list[str],
) -> list[str]:
    """
    Clean and filter sentences before semantic analysis.
    """

    cleaned = []

    for sentence in sentences:

        sentence = clean_sentence(
            sentence
        )

        if not sentence:
            continue

        if not is_valid_sentence(
            sentence
        ):
            continue

        cleaned.append(
            sentence
        )

    return cleaned


# ============================================================
# SENTENCE IMPORTANCE
# ============================================================

def calculate_sentence_importance(
    sentences: list[str],
    embeddings: np.ndarray,
) -> np.ndarray:
    """
    Calculate semantic importance of each sentence.

    A sentence is considered important when it is
    semantically close to the overall chapter meaning.
    """

    if len(sentences) == 0:
        return np.array([])

    # Overall chapter representation
    document_embedding = np.mean(
        embeddings,
        axis=0,
    )

    document_embedding = (
        document_embedding
        / (
            np.linalg.norm(
                document_embedding
            )
            + 1e-10
        )
    )

    scores = cosine_similarity(
        embeddings,
        document_embedding.reshape(
            1,
            -1,
        ),
    ).flatten()

    return scores


# ============================================================
# POSITION IMPORTANCE
# ============================================================

def calculate_position_scores(
    sentence_count: int,
) -> np.ndarray:
    """
    Give a small structural importance to sentences
    based on their position in the chapter.

    Earlier and later sentences receive slightly
    higher importance because they often contain
    introductions or conclusions.
    """

    if sentence_count == 0:
        return np.array([])

    scores = []

    for index in range(
        sentence_count
    ):

        position = index / max(
            sentence_count - 1,
            1,
        )

        # Slight preference for beginning/end
        edge_distance = min(
            position,
            1 - position,
        )

        edge_score = 1 - edge_distance

        scores.append(
            edge_score
        )

    scores = np.array(
        scores,
        dtype=float,
    )

    # Normalize between 0 and 1
    if scores.max() != scores.min():

        scores = (
            scores - scores.min()
        ) / (
            scores.max()
            - scores.min()
        )

    return scores


# ============================================================
# REDUNDANCY REMOVAL
# ============================================================

def remove_redundancy(
    sentences: list[str],
    embeddings: np.ndarray,
    importance_scores: np.ndarray,
    position_scores: np.ndarray,
    num_sentences: int,
    similarity_threshold: float = 0.78,
) -> list[dict]:
    """
    Select important sentences while avoiding
    sentences that repeat the same information.
    """

    if not sentences:
        return []

    selected_indices = []

    remaining_indices = list(
        range(len(sentences))
    )

    # Normalize importance
    if (
        importance_scores.max()
        != importance_scores.min()
    ):

        normalized_importance = (
            importance_scores
            - importance_scores.min()
        ) / (
            importance_scores.max()
            - importance_scores.min()
        )

    else:

        normalized_importance = (
            np.ones(
                len(importance_scores)
            )
        )

    while (
        remaining_indices
        and len(selected_indices)
        < num_sentences
    ):

        best_index = None
        best_score = -1

        for index in remaining_indices:

            importance = (
                normalized_importance[
                    index
                ]
            )

            position_score = (
                position_scores[index]
            )

            # Diversity score
            diversity = 1.0

            if selected_indices:

                selected_embeddings = (
                    embeddings[
                        selected_indices
                    ]
                )

                similarities = cosine_similarity(
                    embeddings[index].reshape(
                        1,
                        -1,
                    ),
                    selected_embeddings,
                )[0]

                max_similarity = float(
                    similarities.max()
                )

                diversity = (
                    1
                    - max_similarity
                )

            # Final score
            score = (
                0.60 * importance
                + 0.30 * diversity
                + 0.10 * position_score
            )

            # Do not select almost identical
            # sentences.
            if selected_indices:

                selected_embeddings = (
                    embeddings[
                        selected_indices
                    ]
                )

                similarities = cosine_similarity(
                    embeddings[index].reshape(
                        1,
                        -1,
                    ),
                    selected_embeddings,
                )[0]

                if (
                    float(similarities.max())
                    >= similarity_threshold
                ):
                    continue

            if score > best_score:

                best_score = score
                best_index = index

        if best_index is None:
            break

        selected_indices.append(
            best_index
        )

        remaining_indices.remove(
            best_index
        )

    # Restore original chapter order
    selected_indices.sort()

    results = []

    for index in selected_indices:

        results.append({
            "position": index + 1,
            "score": round(
                float(
                    importance_scores[
                        index
                    ]
                ),
                4,
            ),
            "sentence": sentences[index],
        })

    return results


# ============================================================
# MAIN EXTRACTIVE SUMMARIZER
# ============================================================

def generate_extractive_summary(
    text: str,
    num_sentences: int = 5,
) -> dict:
    """
    Generate an extractive summary of NCERT chapter content.

    Pipeline:

    Raw chapter text
        ↓
    Chapter content extraction
        ↓
    Sentence segmentation
        ↓
    Sentence cleaning
        ↓
    Exercise filtering
        ↓
    Sentence embeddings
        ↓
    Semantic importance
        ↓
    Redundancy reduction
        ↓
    Original chapter order
    """

    if not text or not text.strip():

        return {
            "summary": "",
            "sentences": [],
            "total_sentences": 0,
        }

    # --------------------------------------------------------
    # STEP 1
    # Extract actual chapter content
    # --------------------------------------------------------

    chapter_content = (
        extract_chapter_content(
            text
        )
    )

    if not chapter_content:

        return {
            "summary": "",
            "sentences": [],
            "total_sentences": 0,
        }

    # --------------------------------------------------------
    # STEP 2
    # Split into sentences
    # --------------------------------------------------------

    sentences = split_into_sentences(
        chapter_content
    )

    # --------------------------------------------------------
    # STEP 3
    # Clean and filter sentences
    # --------------------------------------------------------

    sentences = filter_sentences(
        sentences
    )

    if not sentences:

        return {
            "summary": "",
            "sentences": [],
            "total_sentences": 0,
        }

    # --------------------------------------------------------
    # STEP 4
    # Generate sentence embeddings
    # --------------------------------------------------------

    embeddings = generate_embeddings(
        sentences
    )

    embeddings = np.array(
        embeddings,
        dtype=float,
    )

    if embeddings.size == 0:

        return {
            "summary": "",
            "sentences": [],
            "total_sentences": 0,
        }

    # --------------------------------------------------------
    # STEP 5
    # Calculate semantic importance
    # --------------------------------------------------------

    importance_scores = (
        calculate_sentence_importance(
            sentences,
            embeddings,
        )
    )

    # --------------------------------------------------------
    # STEP 6
    # Calculate structural position
    # --------------------------------------------------------

    position_scores = (
        calculate_position_scores(
            len(sentences)
        )
    )

    # --------------------------------------------------------
    # STEP 7
    # Select important and diverse sentences
    # --------------------------------------------------------

    num_sentences = min(
        num_sentences,
        len(sentences),
    )

    selected = remove_redundancy(
        sentences=sentences,
        embeddings=embeddings,
        importance_scores=importance_scores,
        position_scores=position_scores,
        num_sentences=num_sentences,
        similarity_threshold=0.78,
    )

    # --------------------------------------------------------
    # STEP 8
    # Build final summary
    # --------------------------------------------------------

    summary_sentences = [
        item["sentence"]
        for item in selected
    ]

    summary = " ".join(
        summary_sentences
    )

    # --------------------------------------------------------
    # RETURN NLP RESULTS
    # --------------------------------------------------------

    return {
        "summary": summary,
        "sentences": selected,
        "total_sentences": len(sentences),
        "content_characters": len(
            chapter_content
        ),
    }