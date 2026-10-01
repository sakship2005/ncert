import re
from collections import Counter
from functools import lru_cache

from transformers import T5ForConditionalGeneration, T5Tokenizer

from nlp_engine.analysis.concepts import extract_concepts
from nlp_engine.preprocessing.tokenizer import split_sentences


QG_MODEL_NAME = "valhalla/t5-base-qg-hl"


@lru_cache(maxsize=1)
def _get_qg_model():
    tokenizer = T5Tokenizer.from_pretrained(QG_MODEL_NAME)
    model = T5ForConditionalGeneration.from_pretrained(QG_MODEL_NAME)
    model.eval()
    return tokenizer, model


def _extract_answer_from_sentence(sentence: str) -> str:
    tokens = re.findall(r"[A-Za-z][A-Za-z'-]*", sentence)
    if not tokens:
        return ""

    proper_nouns = re.findall(
        r"\b(?:[A-Z][A-Za-z'-]*\s+){0,3}[A-Z][A-Za-z'-]*\b",
        sentence,
    )
    if proper_nouns:
        return max(proper_nouns, key=len).strip()

    concepts = extract_concepts(sentence, top_n=1)
    if concepts:
        return concepts[0]["concept"]

    return " ".join(tokens[:4])


def _generate_question_for_sentence(sentence: str) -> dict | None:
    sentence = sentence.strip()
    if len(sentence) < 30:
        return None

    answer = _extract_answer_from_sentence(sentence)
    if not answer:
        return None

    highlighted = sentence.replace(answer, f"<hl> {answer} <hl>", 1)
    input_text = f"answer: {answer} context: {highlighted}"

    try:
        tokenizer, model = _get_qg_model()
        inputs = tokenizer.encode(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        )
        outputs = model.generate(
            inputs,
            max_length=64,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=2,
        )
        question = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    except Exception as error:
        print(f"[qg] Generation error: {error}")
        return None

    if not question or not question.endswith("?") or len(question) < 10:
        return None

    return {
        "question": question,
        "answer": answer,
        "type": "short_answer",
        "difficulty": "medium",
    }


def generate_questions(
    context: str,
    number_of_questions: int = 10,
) -> list[dict]:
    """Generate grounded practice questions with the ZIP's T5 QG model."""

    if not context or not context.strip():
        return []

    requested = max(1, min(number_of_questions, 10))
    sentences = split_sentences(context)
    frequencies = Counter(re.findall(r"[A-Za-z]{3,}", context.lower()))
    ranked_sentences = sorted(
        sentences,
        key=lambda sentence: -sum(
            frequencies[word]
            for word in re.findall(r"[A-Za-z]{3,}", sentence.lower())
        ) / max(len(sentence.split()), 1),
    )

    results = []
    seen_questions = set()
    for sentence in ranked_sentences[:requested * 3]:
        if len(results) >= requested:
            break
        result = _generate_question_for_sentence(sentence)
        if result is None or result["question"].lower() in seen_questions:
            continue
        seen_questions.add(result["question"].lower())
        results.append(result)

    if len(results) < requested:
        for concept in extract_concepts(context, top_n=requested * 2):
            if len(results) >= requested:
                break
            concept_text = concept["concept"]
            question = f"What is the importance of {concept_text}?"
            if question.lower() in seen_questions:
                continue
            seen_questions.add(question.lower())
            results.append({
                "question": question,
                "answer": f"The chapter discusses {concept_text}.",
                "type": "short_answer",
                "difficulty": "medium",
            })

    return results