import os
import re
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
DEFAULT_MODEL_DIR_PROJECT   = Path("C:/Users/saksh/nlp_project/hindi_summarizer")
DEFAULT_GROQ_KEY            = os.getenv("GROQ_API_KEY", "")
DEFAULT_GROQ_MODEL          = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
FALLBACK_GROQ_MODELS        = [
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
]

HINDI_LANG_TOKEN   = "<2hi>"
MAX_INPUT_LEN      = 512
MAX_TARGET_LEN     = 300
CHUNK_INPUT_TOKENS = 450
MIN_UNIQUE_RATIO   = 0.45   # chunk summaries below this are flagged as repetition/noise

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

    hi_id  = tokenizer._convert_token_to_id_with_added_voc(HINDI_LANG_TOKEN)
    pad_id = tokenizer._convert_token_to_id_with_added_voc("<pad>")
    eos_id = tokenizer._convert_token_to_id_with_added_voc("</s>")

    model.generation_config.decoder_start_token_id = hi_id
    model.generation_config.forced_bos_token_id    = hi_id
    model.generation_config.pad_token_id           = pad_id
    model.generation_config.eos_token_id           = eos_id

    print(f"[HindiSummarizer] Model loaded successfully on {device} (hi_id={hi_id})")

    _cached_tokenizer = tokenizer
    _cached_model = model
    _cached_device = device
    _cached_hi_id = hi_id

    return tokenizer, model, device, hi_id


# ── 2. TEXT UTILITIES ─────────────────────────────────────────────────────────
def normalize_text(text: str) -> str:
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_summary_output(summary: str) -> str:
    """Remove Hindi exercise prompts and return one readable paragraph."""
    if not summary or not summary.strip():
        return ""

    sentences = re.split(r"(?<=[।.!?])\s+", normalize_text(summary))
    exercise_markers = (
        "लिखिए", "बताइए", "समझाइए", "कीजिए", "करिए", "चुनिए",
        "उत्तर दीजिए", "वर्णन कीजिए", "स्पष्ट कीजिए", "कहिए",
        "write", "answer", "explain", "discuss",
    )
    cleaned = []
    for sentence in sentences:
        text = sentence.strip()
        lower = text.lower()
        if not text or "?" in text:
            continue
        if re.match(r"^\s*\d+\s*[.)]", text):
            continue
        if any(marker in lower for marker in exercise_markers):
            continue
        cleaned.append(text)

    return " ".join(cleaned).strip()


def split_into_sentences(text: str) -> list:
    text = normalize_text(text)
    # Split on Devanagari danda, English punctuation, or newlines
    parts = re.split(r"(?<=[।!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, tokenizer, max_tokens: int = CHUNK_INPUT_TOKENS) -> list:
    sentences = split_into_sentences(text)
    if not sentences:
        return []

    def token_len(t):
        enc = tokenizer(
            f"{t} </s> {HINDI_LANG_TOKEN}",
            add_special_tokens=False,
            truncation=False,
        )
        return len(enc["input_ids"])

    chunks, current = [], []
    for sent in sentences:
        candidate = " ".join(current + [sent]).strip()
        if current and token_len(candidate) > max_tokens:
            chunks.append(" ".join(current).strip())
            current = [sent]
        else:
            current.append(sent)
    if current:
        chunks.append(" ".join(current).strip())
    return chunks


# ── 3. QUALITY CHECK ──────────────────────────────────────────────────────────
def is_good_summary(text: str, min_unique: float = MIN_UNIQUE_RATIO) -> bool:
    """
    Returns False if the summary looks like a repetition loop or garbage.
    Checks:
      - unique-word ratio (repetition loops score very low)
      - minimum length
    """
    words = text.split()
    if len(words) < 8:
        return False
    unique_ratio = len(set(words)) / len(words)
    return unique_ratio >= min_unique


# ── 4. LOCAL MODEL SUMMARIZE (single chunk) ───────────────────────────────────
def local_summarize(tokenizer, model, device, hi_id, text: str, is_final: bool = False) -> str:
    text = normalize_text(text)
    if not text:
        return ""

    formatted = f"{text} </s> {HINDI_LANG_TOKEN}"
    enc = tokenizer(
        formatted,
        max_length=MAX_INPUT_LEN,
        truncation=True,
        return_tensors="pt",
        add_special_tokens=False,
    )
    enc.pop("token_type_ids", None)
    enc = {k: v.to(device) for k, v in enc.items()}

    if is_final:
        params = dict(
            max_length=350,
            min_length=80,
            num_beams=6,
            no_repeat_ngram_size=3,
            repetition_penalty=1.3,
            length_penalty=1.0,
            early_stopping=True,
            decoder_start_token_id=hi_id,
            forced_bos_token_id=hi_id,
        )
    else:
        params = dict(
            max_length=MAX_TARGET_LEN,
            min_length=50,
            num_beams=5,
            no_repeat_ngram_size=3,
            repetition_penalty=1.3,
            length_penalty=1.2,
            early_stopping=True,
            decoder_start_token_id=hi_id,
            forced_bos_token_id=hi_id,
        )

    with torch.no_grad():
        out = model.generate(**enc, **params)

    return tokenizer.decode(out[0], skip_special_tokens=True,
                            clean_up_tokenization_spaces=False).strip()


# ── 5. GROQ FINAL MERGE ───────────────────────────────────────────────────────
def groq_merge(good_summaries: list, total_chunks: int, target_language: str = "hi") -> str:
    """
    Sends only the clean chunk summaries to Groq for a final merged synthesis.
    Supports Hindi, Marathi, and English final summaries.
    """
    api_key = os.getenv("GROQ_API_KEY") or DEFAULT_GROQ_KEY
    if not api_key:
        return "\n\n".join(good_summaries)
    groq_client = Groq(api_key=api_key)

    numbered = ""
    for i, s in enumerate(good_summaries, 1):
        numbered += f"--- भाग {i} का सारांश ---\n{s}\n\n"

    lang_instructions = {
        "hi": "उत्तर केवल स्पष्ट और सुरुचिपूर्ण हिंदी में दो।",
        "mr": "कृपया अंतिम सारांश शुद्ध आणि प्रवाही मराठीमध्ये लिहा।",
        "en": "Provide the final comprehensive summary in clear, fluent English.",
    }
    lang_rule = lang_instructions.get(target_language, lang_instructions["hi"])

    prompt = f"""तुम एक विशेषज्ञ NCERT साहित्य और विषय विशेषज्ञ हो।
नीचे अध्याय के {len(good_summaries)} पाठ-भाग या स्थानीय सारांश दिए गए हैं।
ये स्थानीय मॉडल द्वारा बनाए गए chunk summaries हैं। इन्हें मिलाकर एक
सुसंगत, प्रवाहमय, सटीक और संपूर्ण सारांश लिखो। अध्याय या पुस्तक की अतिरिक्त
जानकारी मत मांगो और केवल दिए गए summaries के आधार पर उत्तर दो।

नियम:
- मुख्य पात्रों के नाम, ऐतिहासिक घटनाएँ, स्थान और मुख्य संकल्पनाएँ बिल्कुल सही रखो
- दोहराव (repetition) बिल्कुल मत करो
- कोई मनगढ़ंत या असंबद्ध बात मत जोड़ो
- घटनाओं और संकल्पनाओं का क्रम सही रखो
- {lang_rule}

{numbered}
अंतिम सारांश:"""

    # Try preferred model and fall back if unavailable
    candidate_models = [DEFAULT_GROQ_MODEL] + [m for m in FALLBACK_GROQ_MODELS if m != DEFAULT_GROQ_MODEL]
    last_error = None

    for model_name in candidate_models:
        try:
            response = groq_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            continue

    # If Groq fails completely, combine good chunk summaries directly
    print(f"[HindiSummarizer] Groq synthesis failed ({last_error}), returning combined chunk summaries.")
    return "\n\n".join(s for s in good_summaries if s.strip())


# ── 6. FULL PIPELINE (Chapter-by-Chapter) ──────────────────────────────────────
def summarize_chapter(
    chapter_text: str,
    target_language: str = "hi",
    tokenizer=None,
    model=None,
    device=None,
    hi_id=None,
) -> dict:
    """
    Summarize a single chapter using the hybrid pipeline:
    1. Chunks the chapter text (<= 450 tokens).
    2. Runs local fine-tuned MBart-50 model on each chunk.
    3. Filters out repetitive / low-quality summaries via quality check.
    4. Merges good chunk summaries using Groq into a coherent final summary.
    """
    if not chapter_text or not chapter_text.strip():
        return {
            "summary": "Chapter text is empty.",
            "mode": "none",
            "chunks_total": 0,
            "chunks_used": 0,
        }

    if tokenizer is None or model is None:
        tokenizer, model, device, hi_id = load_model()

    print("\n" + "=" * 60)
    print("[HindiSummarizer] STEP 1: Splitting chapter into chunks...")
    chunks = chunk_text(chapter_text, tokenizer)
    total_chunks = len(chunks)
    print(f"[HindiSummarizer] Total chunks: {total_chunks}")

    if not chunks:
        return {
            "summary": "Could not create text chunks for chapter.",
            "mode": "failed",
            "chunks_total": 0,
            "chunks_used": 0,
        }

    # ── Single chunk: always use Groq to polish the local model output ───────
    if total_chunks == 1:
        print("[HindiSummarizer] Single chunk — generating directly with local model...")
        local_summary = local_summarize(tokenizer, model, device, hi_id, chunks[0], is_final=True)
        summary = groq_merge([local_summary], total_chunks=1, target_language=target_language)
        if not summary.strip():
            summary = local_summary or chapter_text[:1500]
        summary = clean_summary_output(summary)
        mode = "local_single_chunk_plus_groq"
        return {
            "summary": summary,
            "mode": mode,
            "chunks_total": 1,
            "chunks_used": 1,
            "raw_chunk_summaries": [local_summary],
        }

    # ── Multiple chunks: summarize each, filter repetition ─────────────────────
    print("[HindiSummarizer] STEP 2: Summarizing each chunk with local model...")
    good_summaries = []
    bad_chunk_count = 0
    all_raw = []

    for i, chunk in enumerate(chunks, 1):
        raw = local_summarize(tokenizer, model, device, hi_id, chunk, is_final=False)
        all_raw.append(raw)
        words = raw.split()
        unique_ratio = len(set(words)) / max(len(words), 1)

        if is_good_summary(raw):
            good_summaries.append(raw)
            print(f"  Chunk {i}/{total_chunks}: [OK] unique={unique_ratio:.0%} -> {raw[:50]}...")
        else:
            bad_chunk_count += 1
            print(f"  Chunk {i}/{total_chunks}: [SKIPPED] unique={unique_ratio:.0%}")

    print(f"[HindiSummarizer] {len(good_summaries)}/{total_chunks} chunks passed quality check.")

    if not good_summaries:
        print("[HindiSummarizer] All chunks failed quality check. Falling back to local pass on full text.")
        fallback_summary = local_summarize(tokenizer, model, device, hi_id, chapter_text[:1500], is_final=True)
        if not fallback_summary.strip():
            fallback_summary = chapter_text[:1500]
        return {
            "summary": clean_summary_output(fallback_summary),
            "mode": "local_fallback",
            "chunks_total": total_chunks,
            "chunks_used": 0,
            "raw_chunk_summaries": all_raw,
        }

    # ── Step 3: Groq merges clean chunk summaries ──────────────────────────────
    print("[HindiSummarizer] STEP 3: Sending clean summaries to Groq for final merge...")
    final_summary = groq_merge(good_summaries, total_chunks=total_chunks, target_language=target_language)
    if not final_summary.strip():
        final_summary = " ".join(good_summaries)
    final_summary = clean_summary_output(final_summary)

    return {
        "summary": final_summary,
        "mode": "hybrid_local_mbart_plus_groq",
        "chunks_total": total_chunks,
        "chunks_used": len(good_summaries),
        "good_chunk_summaries": good_summaries,
        "raw_chunk_summaries": all_raw,
    }
