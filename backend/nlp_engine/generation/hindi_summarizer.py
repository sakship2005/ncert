"""
hindi_summarizer.py  -  improved hybrid summarizer (MBart stays the main summarizer)

Pipeline
  clean input -> chunk -> key-sentence selection -> MBart N-best candidates
  -> rerank candidates by grounding in the source -> sentence-level grounding filter
  -> cross-chunk dedupe -> Groq as a source-checked *editor* (not the author)
  -> fallbacks (extractive sentences / raw MBart draft) so output is never empty or invented

The public API is unchanged, so it is a drop-in replacement:
  load_model, summarize_chapter, local_summarize, groq_merge, normalize_text,
  clean_summary_output, split_into_sentences, chunk_text, is_good_summary
"""

import os
import re
import math
from collections import Counter
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

# Ensure protobuf python implementation to avoid SentencePiece descriptor issue
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import torch
from transformers import AlbertTokenizer, MBartForConditionalGeneration
from groq import Groq

# ── CONFIG ────────────────────────────────────────────────────────────────────
DEFAULT_MODEL_DIR_WORKSPACE = Path(__file__).resolve().parents[3] / "hindi_summarizer"
DEFAULT_MODEL_DIR_PROJECT = Path("C:/Users/saksh/nlp_project/hindi_summarizer")
DEFAULT_GROQ_KEY = os.getenv("GROQ_API_KEY", "")
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
FALLBACK_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "llama-3.1-8b-instant",
]

HINDI_LANG_TOKEN = "<2hi>"
MAX_INPUT_LEN = 512          # hard limit of the model input

# ---- tuning knobs (start here if quality or speed is not right) --------------
CHUNK_INPUT_TOKENS = 350     # size of a chapter chunk
SELECT_TOKENS = 280          # key-sentence budget actually fed to MBart per chunk
NUM_BEAMS = 6                # beam width (lower = faster on CPU)
NUM_CANDIDATES = 3           # N-best candidates per chunk (must be <= NUM_BEAMS)
CAND_MAX_LEN = 160           # max tokens per chunk summary
CAND_MIN_LEN = 25            # min tokens per chunk summary (auto-reduced for short input)
NO_REPEAT_NGRAM = 4
REPETITION_PENALTY = 1.15
MIN_UNIQUE_RATIO = 0.45      # below this a summary is treated as a repetition loop
MIN_CAND_GROUNDING = 0.35    # candidate rejected if less of it is found in the source
MIN_SENT_GROUNDING = 0.50    # sentence dropped if less of it is found in the source
MIN_FINAL_GROUNDING = 0.50   # Groq output rejected if less of it is found in the source
DEDUP_SIM = 0.60             # Jaccard similarity above which a sentence is a duplicate

EXERCISE_MARKERS = (
    "लिखिए", "बताइए", "समझाइए", "कीजिए", "करिए", "चुनिए",
    "उत्तर दीजिए", "वर्णन कीजिए", "स्पष्ट कीजिए", "कहिए",
)

# Cached model state
_cached_tokenizer = None
_cached_model = None
_cached_device = None
_cached_hi_id = None


def resolve_model_dir() -> str:
    """Find the valid directory containing the Hindi summarizer model files."""
    env_dir = os.getenv("HINDI_MODEL_DIR")
    candidates = []
    if env_dir:
        candidates.append(Path(env_dir))
    candidates.extend([DEFAULT_MODEL_DIR_PROJECT, DEFAULT_MODEL_DIR_WORKSPACE])
    for path in candidates:
        if path.exists() and (
            (path / "model.safetensors").exists()
            or (path / "pytorch_model.bin").exists()
            or (path / "config.json").exists()
        ):
            return str(path)
    return str(DEFAULT_MODEL_DIR_PROJECT)


# ── 1. LOAD MODEL (Cached Singleton) ──────────────────────────────────────────
def load_model(model_dir: Optional[str] = None):
    global _cached_tokenizer, _cached_model, _cached_device, _cached_hi_id

    if _cached_model is not None and _cached_tokenizer is not None:
        return _cached_tokenizer, _cached_model, _cached_device, _cached_hi_id

    target_dir = model_dir or resolve_model_dir()
    print(f"[HindiSummarizer] Loading model from: {target_dir}")

    tokenizer = AlbertTokenizer.from_pretrained(
        target_dir,
        do_lower_case=False,
        use_fast=False,
        keep_accents=True,
    )
    model = MBartForConditionalGeneration.from_pretrained(target_dir)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()

    hi_id = tokenizer._convert_token_to_id_with_added_voc(HINDI_LANG_TOKEN)
    pad_id = tokenizer._convert_token_to_id_with_added_voc("<pad>")
    eos_id = tokenizer._convert_token_to_id_with_added_voc("</s>")

    model.generation_config.decoder_start_token_id = hi_id
    model.generation_config.forced_bos_token_id = hi_id
    model.generation_config.pad_token_id = pad_id
    model.generation_config.eos_token_id = eos_id

    print(f"[HindiSummarizer] Model loaded successfully on {device} (hi_id={hi_id})")

    _cached_tokenizer = tokenizer
    _cached_model = model
    _cached_device = device
    _cached_hi_id = hi_id

    return tokenizer, model, device, hi_id


# ── 2. TEXT UTILITIES ─────────────────────────────────────────────────────────
_PUNCT = re.compile(r"[।॥,.!?;:()\[\]{}\"'“”‘’\-–—/|]")


def words(text: str) -> list:
    """Whitespace tokenisation (python's \\w breaks Devanagari at the matras)."""
    return _PUNCT.sub(" ", text).split()


def deva_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum("\u0900" <= c <= "\u097F" for c in letters) / len(letters)


def normalize_text(text: str) -> str:
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


_EXERCISE_HEAD = re.compile(
    r"^\s*(प्रश्न[\s\-–]*अभ्यास|अभ्यास|EXERCISES?|Exercises?)\s*$", re.M
)
_NOISE_LINE = re.compile(
    r"^\s*(\d{1,3}|[०-९]{1,3})\s*$"                 # bare page numbers
    r"|Reprint\s*\d{4}(-\d{2,4})?"                   # "Reprint 2025-26"
    r"|©\s*NCERT"                                    # copyright line
    r"|not\s+to\s+be\s+republished",
    re.I,
)


def clean_chapter_input(text: str) -> str:
    """Remove the exercise section and PDF noise BEFORE summarising."""
    text = text.replace("\r", "\n")

    # cut the exercise section, but only if it sits in the last 40% of the chapter
    for m in _EXERCISE_HEAD.finditer(text):
        if m.start() > len(text) * 0.6 and m.start() > 200:
            text = text[: m.start()]
            break

    lines = [ln for ln in text.split("\n") if ln.strip() and not _NOISE_LINE.search(ln)]
    return normalize_text(" ".join(lines))


def clean_summary_output(summary: str, target_language: str = "hi") -> str:
    """Remove exercise-style sentences and return one readable paragraph."""
    if not summary or not summary.strip():
        return ""

    original = normalize_text(summary)
    markers = EXERCISE_MARKERS if target_language == "hi" else ()
    kept = []
    for sentence in re.split(r"(?<=[।.!?])\s+", original):
        s = sentence.strip()
        if not s or "?" in s:
            continue
        if re.match(r"^\s*\d+\s*[.)]", s):
            continue
        if any(m in s for m in markers):
            continue
        kept.append(s)

    return " ".join(kept).strip() or original   # never return an empty string


def split_into_sentences(text: str, max_words: int = 60) -> list:
    text = normalize_text(text)
    parts = re.split(r"(?<=[।!?])\s+|\n+", text)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        w = p.split()
        if len(w) <= max_words:
            out.append(p)
        else:  # PDF text with missing dandas: break very long "sentences"
            for i in range(0, len(w), max_words):
                out.append(" ".join(w[i:i + max_words]))
    return out


def _tok_len(tokenizer, text: str) -> int:
    return len(tokenizer(text, add_special_tokens=False)["input_ids"])


def _chunk_sentences(sentences: list, tokenizer, max_tokens: int = CHUNK_INPUT_TOKENS) -> list:
    """Group sentences into chunks of <= max_tokens. Returns a list of sentence lists."""
    overhead = _tok_len(tokenizer, f" </s> {HINDI_LANG_TOKEN}")
    chunks, current, used = [], [], overhead
    for sent in sentences:
        n = _tok_len(tokenizer, sent)
        if current and used + n > max_tokens:
            chunks.append(current)
            current, used = [], overhead
        current.append(sent)
        used += n
    if current:
        chunks.append(current)
    return chunks


def chunk_text(text: str, tokenizer, max_tokens: int = CHUNK_INPUT_TOKENS) -> list:
    """Backward-compatible: returns chunks as strings."""
    return [" ".join(c) for c in _chunk_sentences(split_into_sentences(text), tokenizer, max_tokens)]


# ── 3. EXTRACTIVE PRE-SELECTION ───────────────────────────────────────────────
def build_idf(sentences: list) -> dict:
    """IDF over the whole chapter (sentence = document)."""
    n = len(sentences)
    df = Counter(w for s in sentences for w in set(words(s)))
    return {w: math.log((n + 1) / (c + 0.5)) for w, c in df.items()}


def _sentence_score(sentence: str, idf: dict) -> float:
    ws = words(sentence)
    if len(ws) < 4:
        return 0.0
    return sum(idf.get(w, 0.0) for w in ws) / (len(ws) ** 0.7)


def select_key_sentences(sentences: list, tokenizer, idf: dict, max_tokens: int = SELECT_TOKENS) -> list:
    """Keep the most informative sentences (original order) within a token budget.

    A small model trained on few examples does much better on short, dense input
    than on a full 450-token chunk with filler sentences.
    """
    lens = [_tok_len(tokenizer, s) for s in sentences]
    if sum(lens) <= max_tokens:
        return list(sentences)

    scores = []
    for i, s in enumerate(sentences):
        sc = _sentence_score(s, idf)
        if i == 0:
            sc *= 1.15                   # openers usually introduce the topic
        if "?" in s:
            sc *= 0.3                    # activity / exercise questions
        scores.append(sc)

    chosen, used = [], 0
    for i in sorted(range(len(sentences)), key=lambda k: scores[k], reverse=True):
        if used + lens[i] > max_tokens:
            continue
        chosen.append(i)
        used += lens[i]
    if not chosen:
        chosen = [0]
    return [sentences[i] for i in sorted(chosen)]


def extractive_fallback(key_sentences: list, idf: dict, n: int = 2) -> str:
    """Used when MBart produces nothing usable: top-n key sentences, original order."""
    if not key_sentences:
        return ""
    top = sorted(range(len(key_sentences)),
                 key=lambda i: _sentence_score(key_sentences[i], idf), reverse=True)[:n]
    return " ".join(key_sentences[i] for i in sorted(top))


# ── 4. QUALITY / GROUNDING CHECKS ─────────────────────────────────────────────
def is_good_summary(text: str, min_unique: float = MIN_UNIQUE_RATIO) -> bool:
    """False if the summary looks like a repetition loop or is too short."""
    ws = words(text)
    if len(ws) < 8:
        return False
    return len(set(ws)) / len(ws) >= min_unique


def overlap(text: str, source_words: set) -> float:
    """Fraction of the text's words that also occur in the source (grounding score)."""
    ws = set(words(text))
    return len(ws & source_words) / max(len(ws), 1)


def score_candidate(cand: str, source_words: set, source_is_hindi: bool) -> float:
    """Higher is better; -1 means reject."""
    ws = words(cand)
    if len(ws) < 8:
        return -1.0
    if "?" in cand or any(m in cand for m in EXERCISE_MARKERS):
        return -1.0
    if source_is_hindi and deva_ratio(cand) < 0.6:
        return -1.0                       # drifted into English / garbage
    uniq = len(set(ws)) / len(ws)
    if uniq < MIN_UNIQUE_RATIO:
        return -1.0
    tri = [tuple(ws[i:i + 3]) for i in range(len(ws) - 2)]
    if tri and len(set(tri)) / len(tri) < 0.9:
        return -1.0                       # repeated phrases
    ov = overlap(cand, source_words)
    if ov < MIN_CAND_GROUNDING:
        return -1.0                       # likely hallucinated
    return 0.6 * ov + 0.25 * uniq + 0.15 * min(len(ws) / 50, 1.0)


def pick_best(cands: list, source_words: set, source_is_hindi: bool = True) -> str:
    scored = [(score_candidate(c, source_words, source_is_hindi), c) for c in cands if c.strip()]
    if not scored:
        return ""
    best_score, best = max(scored, key=lambda x: x[0])
    return best if best_score > 0 else ""


def keep_grounded(summary: str, source_words: set, min_ov: float = MIN_SENT_GROUNDING) -> str:
    """Drop sentences that are mostly made of words not present in the source."""
    kept = []
    for s in re.split(r"(?<=[।.!?])\s+", normalize_text(summary)):
        if len(words(s)) >= 3 and overlap(s, source_words) >= min_ov:
            kept.append(s)
    return " ".join(kept)


def dedupe_sentences(sentences: list, max_sim: float = DEDUP_SIM) -> list:
    kept, kept_sets = [], []
    for s in sentences:
        ws = set(words(s))
        if not ws:
            continue
        if all(len(ws & k) / len(ws | k) < max_sim for k in kept_sets):
            kept.append(s)
            kept_sets.append(ws)
    return kept


# ── 5. LOCAL MODEL (MBart) ────────────────────────────────────────────────────
def generate_candidates(tokenizer, model, device, hi_id, text: str) -> list:
    """N-best generation: beam search returns several summaries, we rerank later."""
    text = normalize_text(text)
    if not text:
        return []

    enc = tokenizer(
        f"{text} </s> {HINDI_LANG_TOKEN}",
        max_length=MAX_INPUT_LEN,
        truncation=True,
        return_tensors="pt",
        add_special_tokens=False,
    )
    enc.pop("token_type_ids", None)
    in_len = int(enc["input_ids"].shape[1])
    enc = {k: v.to(device) for k, v in enc.items()}

    max_len = min(CAND_MAX_LEN, max(40, int(in_len * 0.8)))
    min_len = min(CAND_MIN_LEN, max(10, in_len // 5))   # don't force padding on short input
    n_ret = min(NUM_CANDIDATES, NUM_BEAMS)

    with torch.no_grad():
        out = model.generate(
            **enc,
            num_beams=NUM_BEAMS,
            num_return_sequences=n_ret,
            max_length=max_len,
            min_length=min_len,
            no_repeat_ngram_size=NO_REPEAT_NGRAM,
            repetition_penalty=REPETITION_PENALTY,
            length_penalty=1.0,
            early_stopping=True,
            decoder_start_token_id=hi_id,
            forced_bos_token_id=hi_id,
        )
    return [
        tokenizer.decode(o, skip_special_tokens=True, clean_up_tokenization_spaces=False).strip()
        for o in out
    ]


def local_summarize(tokenizer, model, device, hi_id, text: str, is_final: bool = False) -> str:
    """Backward-compatible single-text summary (best of N candidates)."""
    cands = generate_candidates(tokenizer, model, device, hi_id, text)
    best = pick_best(cands, set(words(text)), source_is_hindi=deva_ratio(text) > 0.5)
    return best or (cands[0] if cands else "")


# ── 6. GROQ AS A SOURCE-CHECKED EDITOR ────────────────────────────────────────
_LANG_RULES = {
    "hi": "उत्तर केवल स्पष्ट और सुरुचिपूर्ण हिंदी (देवनागरी) में दो।",
    "mr": "कृपया अंतिम सारांश शुद्ध आणि प्रवाही मराठीमध्ये लिहा।",
    "en": "Write the final summary in clear, fluent English.",
}


def groq_edit(draft: str, source_excerpt: str, target_language: str = "hi",
              n_sentences: tuple = (6, 9)):
    """Polish the MBart draft using the source text as ground truth.

    Returns (text, status). If Groq is unavailable or drifts away from the source,
    the MBart draft is returned instead, so the output is always grounded.
    """
    api_key = os.getenv("GROQ_API_KEY") or DEFAULT_GROQ_KEY
    if not api_key:
        return draft, "no_groq_key"

    client = Groq(api_key=api_key)
    lang_rule = _LANG_RULES.get(target_language, _LANG_RULES["hi"])
    lo, hi = n_sentences

    prompt = f"""तुम NCERT पाठ्यपुस्तक के सारांश-संपादक हो।
नीचे (क) अध्याय के मूल पाठ के मुख्य अंश और (ख) एक मसौदा सारांश दिया है।
तुम्हारा काम मसौदे को सुधारकर एक सुसंगत अंतिम सारांश बनाना है।

नियम:
- केवल मूल पाठ के अंशों में मौजूद जानकारी का प्रयोग करो; कोई नई जानकारी मत जोड़ो।
- नाम, स्थान, तिथियाँ, संख्याएँ और पारिभाषिक शब्द मूल पाठ के अनुसार सही रखो।
- मसौदे की जो बातें मूल पाठ से मेल नहीं खातीं, उन्हें ठीक करो या हटा दो।
- दोहराव हटाओ और घटनाओं/संकल्पनाओं का क्रम तार्किक रखो।
- अभ्यास-प्रश्न या निर्देश शामिल मत करो।
- सारांश लगभग {lo}-{hi} वाक्यों का हो।
- {lang_rule}
- केवल सारांश लिखो, कोई भूमिका या टिप्पणी नहीं।

(क) मूल पाठ के मुख्य अंश:
{source_excerpt}

(ख) मसौदा सारांश:
{draft}

अंतिम सारांश:"""

    source_words = set(words(source_excerpt)) | set(words(draft))
    models = [DEFAULT_GROQ_MODEL] + [m for m in FALLBACK_GROQ_MODELS if m != DEFAULT_GROQ_MODEL]
    last_error = None

    for model_name in models:
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500,
            )
            out = (resp.choices[0].message.content or "").strip()
            out = re.sub(r"<think>.*?</think>", "", out, flags=re.S).strip()
            if not out:
                continue
            if target_language == "hi":
                # Hindi output must stay Hindi and stay close to the source
                if deva_ratio(out) < 0.6 or overlap(out, source_words) < MIN_FINAL_GROUNDING:
                    print(f"[HindiSummarizer] Groq output rejected (not grounded) -> using MBart draft")
                    return draft, "groq_rejected"
            return out, "groq_edit"
        except Exception as e:  # try the next model
            last_error = e
            continue

    print(f"[HindiSummarizer] Groq failed ({last_error}); using MBart draft.")
    return draft, "groq_failed"


def groq_merge(good_summaries: list, total_chunks: int, target_language: str = "hi") -> str:
    """Backward-compatible wrapper (older code may still import this)."""
    draft = " ".join(good_summaries)
    text, _ = groq_edit(draft, draft, target_language)
    return text


# ── 7. FULL PIPELINE ──────────────────────────────────────────────────────────
def summarize_chapter(
    chapter_text: str,
    target_language: str = "hi",
    tokenizer=None,
    model=None,
    device=None,
    hi_id=None,
) -> dict:
    """
    1. Clean the chapter (drop exercises, page numbers).
    2. Chunk it, keep only the key sentences of each chunk.
    3. MBart generates N candidates per chunk; the most source-grounded one wins.
    4. Ungrounded sentences are dropped; duplicates across chunks are removed.
    5. Groq edits the draft against the source text (rejected if it drifts).
    """
    if not chapter_text or not chapter_text.strip():
        return {"summary": "Chapter text is empty.", "mode": "none",
                "chunks_total": 0, "chunks_used": 0}

    if tokenizer is None or model is None:
        tokenizer, model, device, hi_id = load_model()

    cleaned = clean_chapter_input(chapter_text)
    all_sents = split_into_sentences(cleaned)
    if not all_sents:
        return {"summary": "Could not create text chunks for chapter.", "mode": "failed",
                "chunks_total": 0, "chunks_used": 0}

    print("\n" + "=" * 60)
    idf = build_idf(all_sents)
    chunks = _chunk_sentences(all_sents, tokenizer, CHUNK_INPUT_TOKENS)
    total = len(chunks)
    print(f"[HindiSummarizer] {len(all_sents)} sentences -> {total} chunks")

    drafts, excerpts, raw_best = [], [], []
    n_mbart, n_fallback = 0, 0

    for i, sents in enumerate(chunks, 1):
        chunk_str = " ".join(sents)
        src_words = set(words(chunk_str))
        src_is_hindi = deva_ratio(chunk_str) > 0.5

        key = select_key_sentences(sents, tokenizer, idf, SELECT_TOKENS)
        key_str = " ".join(key)
        excerpts.append(key_str)

        cands = generate_candidates(tokenizer, model, device, hi_id, key_str)
        best = pick_best(cands, src_words, src_is_hindi)
        raw_best.append(best or (cands[0] if cands else ""))

        grounded = keep_grounded(best, src_words) if best else ""
        if grounded and is_good_summary(grounded):
            drafts.append(grounded)
            n_mbart += 1
            print(f"  Chunk {i}/{total}: [MBART OK] {grounded[:50]}...")
        else:
            fb = extractive_fallback(key, idf)
            if fb:
                drafts.append(fb)
                n_fallback += 1
            print(f"  Chunk {i}/{total}: [EXTRACTIVE FALLBACK]")

    # cross-chunk dedupe at sentence level
    draft_sents = [s for d in drafts for s in re.split(r"(?<=[।.!?])\s+", d) if s.strip()]
    draft = " ".join(dedupe_sentences(draft_sents))
    if not draft.strip():
        return {"summary": "Could not generate a summary for this chapter.", "mode": "failed_quality",
                "chunks_total": total, "chunks_used": 0, "raw_chunk_summaries": raw_best}

    # Groq edit (source excerpts capped so the prompt stays small)
    cap = max(400, 7000 // max(total, 1))
    source_excerpt = " ".join(e[:cap] for e in excerpts)
    lo = min(max(4, 2 * total), 10)
    final, status = groq_edit(draft, source_excerpt, target_language, (lo, lo + 3))

    final = clean_summary_output(final, target_language)
    print(f"[HindiSummarizer] Done: {n_mbart} MBart chunks, {n_fallback} fallback, groq={status}")

    return {
        "summary": final,
        "mode": f"mbart_rerank+{status}",
        "chunks_total": total,
        "chunks_used": n_mbart + n_fallback,
        "mbart_chunks": n_mbart,
        "fallback_chunks": n_fallback,
        "good_chunk_summaries": drafts,
        "raw_chunk_summaries": raw_best,
    }
