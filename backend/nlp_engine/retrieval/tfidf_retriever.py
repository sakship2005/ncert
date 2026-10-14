"""
TF-IDF based chunk retriever.

Tier 1 retrieval: keyword overlap between the user query
and pre-chunked chapter text.  Fast, zero-cost, no embeddings.
"""

import math
import re
import string
from collections import Counter


# ---------------------------------------------------------------------------
# Minimal stop-word list (extend as needed)
# ---------------------------------------------------------------------------
_STOP_WORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "for",
    "of", "and", "or", "but", "not", "with", "this", "that", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do",
    "does", "did", "will", "would", "could", "should", "may", "might",
    "can", "from", "by", "as", "into", "through", "during", "about",
    "what", "which", "who", "when", "where", "how", "why", "so", "if",
    "also", "just", "each", "both", "more", "than", "then", "its",
}


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = text.split()
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 2]


# ---------------------------------------------------------------------------
# TF-IDF index (built in-memory per chapter)
# ---------------------------------------------------------------------------
class TFIDFIndex:
    """
    Lightweight TF-IDF index over a list of text chunks.
    Build once per chapter, then call .search() repeatedly.
    """

    def __init__(self, chunks: list[dict]):
        """
        chunks: list of dicts produced by chunking.create_chunks()
        Each dict must have at least {"chunk_id": ..., "text": ...}
        """
        self.chunks = chunks
        self._tokenized: list[list[str]] = [
            _tokenize(c["text"]) for c in chunks
        ]
        self._idf: dict[str, float] = self._build_idf()

    # ------------------------------------------------------------------
    def _build_idf(self) -> dict[str, float]:
        n = len(self._tokenized)
        df: Counter = Counter()
        for tokens in self._tokenized:
            df.update(set(tokens))
        idf = {}
        for term, freq in df.items():
            idf[term] = math.log((n + 1) / (freq + 1)) + 1.0  # smoothed
        return idf

    def _tf(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        c = Counter(tokens)
        total = len(tokens)
        return {t: count / total for t, count in c.items()}

    def _score(self, query_tokens: list[str], doc_tokens: list[str]) -> float:
        if not query_tokens or not doc_tokens:
            return 0.0
        doc_tf = self._tf(doc_tokens)
        score = 0.0
        for term in query_tokens:
            if term in doc_tf:
                idf = self._idf.get(term, 1.0)
                score += doc_tf[term] * idf
        return score

    # ------------------------------------------------------------------
    def search(
        self,
        query: str,
        top_k: int = 4,
        min_score: float = 0.01,
    ) -> list[dict]:
        """
        Return the top_k most relevant chunks for *query*.
        Each result is the original chunk dict with an added
        "tfidf_score" key.
        """
        q_tokens = _tokenize(query)
        if not q_tokens:
            return []

        scored = []
        for i, (chunk, doc_tokens) in enumerate(
            zip(self.chunks, self._tokenized)
        ):
            s = self._score(q_tokens, doc_tokens)
            if s >= min_score:
                result = chunk.copy()
                result["tfidf_score"] = round(s, 4)
                scored.append(result)

        scored.sort(key=lambda x: x["tfidf_score"], reverse=True)
        return scored[:top_k]

    def coverage(self, query: str) -> float:
        """
        Fraction of query tokens that appear at least once in the corpus.
        Used to decide whether Tier 1 has enough signal.
        """
        q_tokens = set(_tokenize(query))
        if not q_tokens:
            return 0.0
        all_tokens = set(t for doc in self._tokenized for t in doc)
        hits = q_tokens & all_tokens
        return len(hits) / len(q_tokens)