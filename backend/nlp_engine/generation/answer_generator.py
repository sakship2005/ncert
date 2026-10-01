from functools import lru_cache

from transformers import (
    MarianMTModel,
    MarianTokenizer,
    pipeline,
)


QA_MODEL_NAME = "deepset/roberta-base-squad2"


@lru_cache(maxsize=1)
def _get_qa_pipeline():
    return pipeline(
        "question-answering",
        model=QA_MODEL_NAME,
        tokenizer=QA_MODEL_NAME,
        device=-1,
    )


@lru_cache(maxsize=1)
def _get_translation_models():
    en_to_hi_name = "Helsinki-NLP/opus-mt-en-hi"
    hi_to_en_name = "Helsinki-NLP/opus-mt-hi-en"
    return (
        MarianTokenizer.from_pretrained(en_to_hi_name),
        MarianMTModel.from_pretrained(en_to_hi_name),
        MarianTokenizer.from_pretrained(hi_to_en_name),
        MarianMTModel.from_pretrained(hi_to_en_name),
    )


def _translate(text: str, source: str, target: str) -> str:
    if source == target or not text.strip():
        return text

    if {source, target} != {"en", "hi"}:
        return text

    en_to_hi_tokenizer, en_to_hi_model, hi_to_en_tokenizer, hi_to_en_model = _get_translation_models()
    if source == "hi":
        tokenizer, model = hi_to_en_tokenizer, hi_to_en_model
    else:
        tokenizer, model = en_to_hi_tokenizer, en_to_hi_model

    inputs = tokenizer([text], return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(**inputs, max_length=512, num_beams=4)
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


def answer_question(
    question: str,
    context: str,
    language: str = "en",
) -> dict:
    """Extract an answer span from retrieved NCERT context."""

    if not question or not question.strip():
        return {"answer": "Please provide a question.", "score": 0.0}

    if not context or not context.strip():
        return {
            "answer": "I could not find relevant information in the provided NCERT material.",
            "score": 0.0,
        }

    effective_question = question
    if language == "hi":
        try:
            effective_question = _translate(question, "hi", "en")
        except Exception as error:
            print(f"[qa] Hindi-to-English translation error: {error}")

    try:
        result = _get_qa_pipeline()(
            question=effective_question,
            context=context[:4000],
            max_answer_len=150,
            handle_impossible_answer=True,
        )
        answer = result.get("answer", "").strip()
        score = float(result.get("score", 0.0))
    except Exception as error:
        return {
            "answer": f"QA model error: {error}",
            "score": 0.0,
        }

    if not answer or score < 0.05:
        answer = "The answer to this question could not be found clearly in the retrieved NCERT text."

    if language == "hi" and answer:
        try:
            answer = _translate(answer, "en", "hi")
        except Exception as error:
            print(f"[qa] English-to-Hindi translation error: {error}")

    return {
        "answer": answer,
        "score": round(score, 4),
        "english_question": effective_question,
    }


def generate_answer(
    question: str,
    context: str,
    language: str = "en",
) -> str:
    return answer_question(question, context, language)["answer"]