import os
import re
import json
import nltk
from collections import Counter
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from groq import Groq

try:
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    nltk.download("averaged_perceptron_tagger", quiet=True)
    nltk.download("averaged_perceptron_tagger_eng", quiet=True)
except Exception:
    pass

lemmatizer = WordNetLemmatizer()


def get_wordnet_pos(tag: str):
    if tag.startswith("J"):
        return wn.ADJ
    if tag.startswith("V"):
        return wn.VERB
    if tag.startswith("N"):
        return wn.NOUN
    if tag.startswith("R"):
        return wn.ADV
    return None


def count_syllables(word: str) -> int:
    """Rough syllable count for English words."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    matches = re.findall(r'[aeiouy]{1,2}', word)
    return max(len(matches), 1)


def is_hindi_text(text: str) -> bool:
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
    # OCR and PDF extraction often include Latin headings, page numbers, and
    # metadata, so a Hindi chapter should not require 15% Devanagari text.
    return devanagari_chars >= 20 or devanagari_chars > (len(text) * 0.05)


def extract_vocabulary(text: str, min_word_length: int = 6, top_n: int = 20) -> list[dict]:
    """Basic vocabulary extractor compatible with existing callers."""
    res = extract_difficult_words(text, top_n=top_n)
    return [
        {
            "word": item["word"],
            "frequency": item.get("frequency", 1),
            "pos": item.get("pos", "noun"),
            "definition": item.get("definition", ""),
            "length": len(item["word"]),
        }
        for item in res
    ]


def extract_difficult_words(
    text: str,
    top_n: int = 25,
    language: str = "auto",
) -> list[dict]:
    """
    Detects difficult or uncommon words from the chapter text.
    Returns for each word:
    - word
    - definition
    - simple_meaning
    - synonyms
    - example
    - hindi_meaning
    - marathi_meaning
    - frequency
    """
    if not text or not text.strip():
        return []

    # Prefer the language selected for the uploaded book. Script detection is
    # retained for legacy books and mixed-language text.
    is_hindi = language in {"hi", "both", "mr"} or (
        language in {"auto", ""} and is_hindi_text(text)
    )

    # ── HINDI CHAPTER VOCABULARY ──────────────────────────────────────────────
    if is_hindi:
        words = re.findall(r'[\u0900-\u097F]+', text)
        stop_words = {
            "के", "का", "की", "में", "से", "है", "हैं", "और", "ने", "पर", "को", "भी", "था",
            "थी", "थे", "यह", "वह", "तो", "ही", "एक", "इस", "उस", "किया", "कर", "गया",
            "रहा", "रही", "रहे", "हुए", "होने", "बाद", "लिए", "दिया", "सकता", "सकते", "सकती",
            "जाता", "जाती", "गए", "गई", "कहा", "बोला", "सुना", "नहीं", "था।", "है।"
        }
        candidates = [w for w in words if len(w) >= 4 and w not in stop_words]
        counts = Counter(candidates).most_common(top_n * 2)

        # Select top distinctive words
        selected = [word for word, count in counts[:top_n]]

        # Use Groq to provide accurate simple meanings, synonyms, and examples
            groq_key = os.getenv("GROQ_API_KEY", "")
        try:
            client = Groq(api_key=groq_key)
            prompt = f"""तुम एक हिंदी भाषा और साहित्य के शिक्षक हो।
नीचे दिए गए अध्याय के कठिन शब्दों की एक सूची दी गई है:
{', '.join(selected[:15])}

प्रत्येक शब्द के लिए एक JSON सरणी बनाओ जिसमें ये फ़ील्ड हों:

केवल वैध JSON सरणी वापस करो, कोई अन्य पाठ नहीं।"""

            resp = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1000,
            )
            raw = resp.choices[0].message.content.strip()
            # Clean markdown code block if present
            raw = re.sub(r"^```(?:json)?", "", raw)
            raw = re.sub(r"```$", "", raw).strip()
            data = json.loads(raw)
            if isinstance(data, list):
                for item in data:
                    item["frequency"] = dict(counts).get(item.get("word", ""), 1)
                return data
        except Exception as e:
            print(f"[Vocabulary] Groq Hindi vocab lookup fallback: {e}")

        # Fallback offline Hindi vocab
        results = []
        for word, count in counts[:top_n]:
            results.append({
                "word": word,
                "pos": "संज्ञा/विशेषण",
                "definition": f"अध्याय में प्रयुक्त महत्वपूर्ण शब्द '{word}'",
                "simple_meaning": f"पाठ के संदर्भ में '{word}' का अध्ययन महत्वपूर्ण है।",
                "synonyms": [f"समानार्थी {word}"],
                "example": f"पाठ में '{word}' का विशेष उपयोग किया गया है।",
                "hindi_meaning": word,
                "marathi_meaning": word,
                "frequency": count,
            })
        return results

    # ── ENGLISH CHAPTER VOCABULARY ────────────────────────────────────────────
    words = nltk.word_tokenize(text)
    try:
        tagged_words = nltk.pos_tag(words)
    except Exception:
        tagged_words = [(w, "NN") for w in words]

    stop_words = set(stopwords.words("english"))
    stop_words.update(["chapter", "exercise", "question", "answer", "student", "teacher", "reprint"])

    word_freq = Counter()
    word_tags = {}

    for word, tag in tagged_words:
        w_lower = word.lower()
        if not re.match(r"^[a-zA-Z]{5,}$", w_lower):
            continue
        if w_lower in stop_words:
            continue
        word_freq[w_lower] += 1
        if w_lower not in word_tags:
            word_tags[w_lower] = tag

    # Rank by length and syllable complexity
    def score_word(w):
        length = len(w)
        syllables = count_syllables(w)
        freq = word_freq[w]
        return (syllables * 2) + length - (freq * 0.5)

    candidates = sorted(word_freq.keys(), key=score_word, reverse=True)[:top_n]

    results = []
    for w in candidates:
        pos_code = get_wordnet_pos(word_tags.get(w, "NN"))
        synsets = wn.synsets(w, pos=pos_code) if pos_code else wn.synsets(w)

        definition = "Important vocabulary term from the chapter."
        synonyms = []
        example = f"The author described the situation using the word '{w}'."

        if synsets:
            s0 = synsets[0]
            definition = s0.definition()
            if s0.examples():
                example = s0.examples()[0]
            for s in synsets[:3]:
                for lemma in s.lemmas():
                    if lemma.name().lower() != w and lemma.name() not in synonyms:
                        synonyms.append(lemma.name().replace("_", " "))
                    if len(synonyms) >= 3:
                        break
                if len(synonyms) >= 3:
                    break

        results.append({
            "word": w.capitalize(),
            "pos": word_tags.get(w, "Noun"),
            "definition": definition,
            "simple_meaning": f"Refers to: {definition}",
            "synonyms": synonyms or ["contextual meaning", "key term"],
            "example": example.capitalize(),
            "hindi_meaning": "संदर्भ में समझें",
            "marathi_meaning": "संदर्भात समजून घ्या",
            "frequency": word_freq[w],
        })

    # Optional quick Groq batch translation/meaning enrichment
    if results:
        sample_words = [r["word"] for r in results[:10]]
        groq_key = os.getenv("GROQ_API_KEY", "")
        try:
            client = Groq(api_key=groq_key)
            prompt = f"""For these NCERT vocabulary words: {', '.join(sample_words)}
Return a JSON dictionary mapping each word to {{"hindi": "हिंदी अर्थ", "marathi": "मराठी अर्थ", "simple": "Simple 1-line definition"}}.
Return only valid JSON."""
            resp = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=600,
            )
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r"^```(?:json)?", "", raw)
            raw = re.sub(r"```$", "", raw).strip()
            meanings = json.loads(raw)
            for r in results:
                w = r["word"]
                if w in meanings:
                    r["hindi_meaning"] = meanings[w].get("hindi", r["hindi_meaning"])
                    r["marathi_meaning"] = meanings[w].get("marathi", r["marathi_meaning"])
                    if meanings[w].get("simple"):
                        r["simple_meaning"] = meanings[w]["simple"]
        except Exception:
            pass

    return results