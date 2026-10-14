"""
NCERT Chapter Summarizer — Fully Offline NLP Pipeline
======================================================
English chapters  → LSA (Latent Semantic Analysis) via SVD on TF-IDF
Hindi/Marathi     → TF-IDF sentence ranking

For Hindi/Marathi output from English chapters:
  → Helsinki-NLP/opus-mt-en-hi  (already in transformers cache)

No external API calls. Pure classical NLP + local HuggingFace model.
"""

import re
import numpy as np
from collections import Counter
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer


# ── NOISE / EXERCISE FILTERS ──────────────────────────────────────────────────

_STOP_HEADINGS = {
    "think about the text", "thinking about the text",
    "thinking about language", "working with words",
    "working with language", "noticing form",
    "understanding the text", "things to do",
    "activities", "activity", "questions", "exercise",
    "exercises", "writing", "grammar", "vocabulary",
    "discussion", "speaking", "reading comprehension",
    "let's discuss", "language work", "glossary",
    "about the author", "about the text",
    "comprehension check", "oral comprehension check",
}

_NOISE_PATTERNS = [
    r"_\s*_",                           # blanks __ __ __
    r"^\s*\d+[\.\)]\s",                 # 1. 2. 3.
    r"^\s*[a-d][\.\)]\s",              # a. b. c.
    r"^\s*\([ivxlcdm]+\)",             # (i) (ii)
    r"^\s*Q\s*\d+",                    # Q1 Q2
    r"\?\s*$",                          # ends with ? (exercise question)
    r"how did\b",                       # question starters
    r"what did\b",
    r"why did\b",
    r"describe\b",
    r"explain\b",
    r"reprint\s+\d{4}",
    r"^page\s+\d+",
    r"^\s*\d+\s*$",
]

_NOISE_RE = [re.compile(p, re.IGNORECASE) for p in _NOISE_PATTERNS]


def _is_noisy(s: str) -> bool:
    s = s.strip()
    if not s or len(s.split()) < 6:
        return True
    if s[0].islower():
        return True
    for pat in _NOISE_RE:
        if pat.search(s):
            return True
    return False


def _truncate_at_exercise(text: str) -> str:
    """Cut everything from the first exercise/glossary heading onward."""
    lines = text.splitlines()
    result = []
    for line in lines:
        norm = re.sub(r"\s+", " ", line).strip().lower()
        if norm in _STOP_HEADINGS:
            break
        if re.match(
            r"^(think about|working with|noticing form|understanding the|"
            r"activity|exercise|vocabulary|glossary|comprehension check|"
            r"oral comprehension)",
            norm,
        ):
            break
        result.append(line)
    return "\n".join(result)


# ── SENTENCE SPLITTERS ────────────────────────────────────────────────────────

def _split_english(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    raw = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in raw if len(s.strip()) >= 25 and not _is_noisy(s.strip())]


def _split_hindi(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    raw = re.split(r"(?<=[।!?.])\s+|\n+", text)
    out = []
    for s in raw:
        s = s.strip()
        if len(s) < 10:
            continue
        if len(re.findall(r"[\u0900-\u097F]", s)) < 3:
            continue
        out.append(s)
    return out


# ── 1. LSA SUMMARIZER (English) ───────────────────────────────────────────────

def _lsa_summarize(text: str, num_sentences: int = 6) -> list[str]:
    """
    LSA extractive summarization.
    Returns a list of selected sentences (caller joins them).

    Steps:
    1. Strip exercise section
    2. Filter noisy sentences
    3. TF-IDF matrix [sentences × terms]
    4. SVD → latent semantic dimensions
    5. Score sentences → pick top N in original order
    """
    text = _truncate_at_exercise(text)
    sentences = _split_english(text)

    if not sentences:
        return []
    if len(sentences) <= num_sentences:
        return sentences

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=1000,
        ngram_range=(1, 2),
        min_df=1,
    )
    try:
        matrix = vectorizer.fit_transform(sentences).toarray()
    except ValueError:
        return sentences[:num_sentences]

    if matrix.shape[1] == 0:
        return sentences[:num_sentences]

    # SVD — core of LSA
    U, S, Vt = np.linalg.svd(matrix, full_matrices=False)

    k = min(5, len(S))
    scores = np.zeros(len(sentences))
    for i in range(k):
        scores += S[i] * (U[:, i] ** 2)

    # Penalise fragments and overly long sentences
    for i, s in enumerate(sentences):
        wc = len(s.split())
        if wc < 8:
            scores[i] *= 0.2
        elif wc > 65:
            scores[i] *= 0.7

    top_idx = sorted(np.argsort(scores)[-num_sentences:])
    return [sentences[i] for i in top_idx]


# ── 2. TF-IDF SENTENCE RANKING (Hindi / Marathi) ─────────────────────────────

HINDI_STOPS = {
    "और","था","थी","थे","है","हैं","का","के","की","में","से","पर","ने",
    "को","भी","यह","वह","तो","ही","एक","इस","उस","नहीं","गया","गई","गए",
    "लिए","बाद","कहा","किया","हो","जो","कि","अब","जब","तब","वे","हम",
    "आप","मैं","हुए","होने","सकता","सकती","सकते","जाता","जाती","बोला",
    "सुना","उन्होंने","उसने","उसका","उसकी","उसके","इनका","इनकी","इनके",
}

MARATHI_STOPS = {
    "आणि","होते","होता","होती","आहे","आहेत","च्या","ला","ने","मध्ये",
    "वर","हे","ती","तो","त्या","एक","या","तर","पण","म्हणून","झाले",
    "झाली","झाला","केले","केली","केला",
}


def _tfidf_summarize_hindi(text: str, num_sentences: int = 6, lang: str = "hi") -> list[str]:
    """
    TF-IDF sentence ranking for Hindi/Marathi.
    Returns list of selected sentences.
    """
    sentences = _split_hindi(text)
    if not sentences:
        return []
    if len(sentences) <= num_sentences:
        return sentences

    stops = MARATHI_STOPS if lang == "mr" else HINDI_STOPS
    all_words = re.findall(r"[\u0900-\u097F]{3,}", text)
    filtered = [w for w in all_words if w not in stops]
    if not filtered:
        return sentences[:num_sentences]

    freq = Counter(filtered)
    max_f = max(freq.values())
    norm = {w: c / max_f for w, c in freq.items()}

    def score(s: str) -> float:
        words = [w for w in re.findall(r"[\u0900-\u097F]{3,}", s) if w not in stops]
        return sum(norm.get(w, 0) for w in words) / max(len(words), 1) if words else 0.0

    ranked = sorted(enumerate(sentences), key=lambda x: score(x[1]), reverse=True)
    top = sorted(ranked[:num_sentences], key=lambda x: x[0])
    return [s for _, s in top]


# ── 3. OFFLINE TRANSLATION (English → Hindi/Marathi) ─────────────────────────

@lru_cache(maxsize=1)
def _get_en_hi_model():
    """Load Helsinki-NLP English→Hindi model once and cache it."""
    from transformers import MarianTokenizer, MarianMTModel
    name = "Helsinki-NLP/opus-mt-en-hi"
    print(f"[Summarizer] Loading translation model {name}...")
    tokenizer = MarianTokenizer.from_pretrained(name)
    model = MarianMTModel.from_pretrained(name)
    model.eval()
    return tokenizer, model


def _translate_en_to_hi(sentences: list[str]) -> list[str]:
    """Translate a list of English sentences to Hindi offline."""
    try:
        tokenizer, model = _get_en_hi_model()
        translated = []
        for sent in sentences:
            inputs = tokenizer(
                [sent], return_tensors="pt",
                truncation=True, max_length=512, padding=True,
            )
            outputs = model.generate(**inputs, max_length=512, num_beams=4)
            t = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            translated.append(t if t else sent)
        return translated
    except Exception as e:
        print(f"[Summarizer] Translation failed: {e}. Returning English.")
        return sentences


# ── 4. PUBLIC API ─────────────────────────────────────────────────────────────

def summarize_offline(
    text: str,
    source_lang: str = "en",
    target_lang: str = "en",
    num_sentences: int = 6,
) -> dict:
    """
    Main entry point called by nlp.py.

    Routing:
      English chapter + English output  → LSA only
      English chapter + Hindi output    → LSA + Helsinki offline translation
      English chapter + Marathi output  → LSA + Helsinki offline translation
      Hindi/Marathi chapter             → TF-IDF sentence ranking
    """
    if not text or not text.strip():
        return {
            "summary": "Chapter text is empty.",
            "mode": "none", "method": "none",
            "chunks_total": 0, "chunks_used": 0,
        }

    if source_lang == "en":
        selected = _lsa_summarize(text, num_sentences)
        total = len(_split_english(_truncate_at_exercise(text)))

        if target_lang in {"hi", "mr"} and selected:
            print(f"[Summarizer] Translating {len(selected)} sentences to {target_lang}...")
            selected = _translate_en_to_hi(selected)
            mode = "lsa_extractive + offline_translation"
            method = "LSA (SVD on TF-IDF) → Helsinki-NLP/opus-mt-en-hi"
        else:
            mode = "lsa_extractive"
            method = "LSA — Singular Value Decomposition on TF-IDF sentence matrix"

    else:
        selected = _tfidf_summarize_hindi(text, num_sentences, source_lang)
        total = len(_split_hindi(text))
        mode = "tfidf_extractive"
        method = "TF-IDF sentence ranking — normalized word-frequency scoring"

    summary = " ".join(selected) if selected else "Could not extract a summary from this chapter."

    return {
        "summary": summary,
        "mode": mode,
        "method": method,
        "chunks_total": total,
        "chunks_used": len(selected),
    }


def generate_extractive_summary(text: str, num_sentences: int = 5) -> dict:
    """Backward-compatible wrapper."""
    selected = _lsa_summarize(text, num_sentences)
    return {"summary": " ".join(selected), "sentences": selected}