import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)
    nltk.download("averaged_perceptron_tagger", quiet=True)
    nltk.download("averaged_perceptron_tagger_eng", quiet=True)
except Exception:
    pass

nlp_spacy = None
try:
    import spacy
    nlp_spacy = spacy.load("en_core_web_sm")
except Exception:
    nlp_spacy = None


def extract_concepts(
    text: str,
    top_n: int = 20,
) -> list[dict]:
    """
    Extract meaningful concepts from NCERT text.
    Concepts are primarily identified from:
    - nouns
    - proper nouns
    - noun phrases
    """
    if not text or not text.strip():
        return []

    # If spaCy is available, use it
    if nlp_spacy is not None:
        try:
            document = nlp_spacy(text[:25000])
            concepts = Counter()
            for token in document:
                if token.is_stop or token.is_punct:
                    continue
                if token.pos_ in {"NOUN", "PROPN"}:
                    w = token.lemma_.lower().strip()
                    if len(w) >= 3:
                        concepts[w] += 1
            for chunk in document.noun_chunks:
                phrase = chunk.text.strip().lower()
                if phrase and len(phrase.split()) >= 2 and len(phrase.split()) <= 4:
                    concepts[phrase] += 1
            sorted_concepts = concepts.most_common(top_n)
            return [{"concept": k, "count": v} for k, v in sorted_concepts]
        except Exception:
            pass

    # NLTK / Regex fallback (fast, robust, no heavy spaCy dependency required)
    is_hindi = len(re.findall(r'[\u0900-\u097F]', text)) > (len(text) * 0.15)
    if is_hindi:
        words = re.findall(r'[\u0900-\u097F]{3,}', text)
        stops = {"और", "था", "थी", "थे", "है", "हैं", "का", "के", "की", "में", "से", "पर", "ने", "को", "भी", "यह", "वह"}
        filtered = [w for w in words if w not in stops]
        counts = Counter(filtered).most_common(top_n)
        return [{"concept": k, "count": v} for k, v in counts]

    # English NLTK POS tagging
    words = word_tokenize(text)
    try:
        tagged = nltk.pos_tag(words)
    except Exception:
        tagged = [(w, "NN") for w in words]

    stop_words = set(stopwords.words("english"))
    stop_words.update(["chapter", "exercise", "question", "answer", "student", "teacher", "reprint", "page"])

    concepts = Counter()
    for w, pos in tagged:
        w_clean = w.lower().strip()
        if len(w_clean) < 3 or not w_clean.isalpha():
            continue
        if w_clean in stop_words:
            continue
        if pos in ("NN", "NNS", "NNP", "NNPS"):
            concepts[w_clean] += 1

    # Extract 2-word noun compounds
    for i in range(len(tagged) - 1):
        w1, pos1 = tagged[i]
        w2, pos2 = tagged[i + 1]
        w1_c, w2_c = w1.lower().strip(), w2.lower().strip()
        if (
            pos1 in ("NN", "NNP", "JJ")
            and pos2 in ("NN", "NNP")
            and w1_c not in stop_words
            and w2_c not in stop_words
            and w1_c.isalpha()
            and w2_c.isalpha()
        ):
            concepts[f"{w1_c} {w2_c}"] += 2

    return [{"concept": k, "count": v} for k, v in concepts.most_common(top_n)]