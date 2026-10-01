from nlp_engine.analysis.concepts import extract_concepts
from nlp_engine.generation.answer_generator import answer_question
from nlp_engine.generation.question_generator import generate_questions


def generate_interactive_quiz(
    context: str,
    total_questions: int = 8,
    types: list[str] = None,
    language: str = "en",
) -> dict:
    """
    Generate rich interactive quiz questions from chapter context:
    Supports:
    - 'mcq': Multiple Choice Questions with 4 options, correct answer index, explanation
    - 'true_false': True/False statements with correct boolean and explanation
    - 'fill_blank': Sentence with blank (___), correct word, and clue
    - 'short_answer': Concise question, model answer, key points
    """
    if not context or not context.strip():
        return {"status": "error", "questions": [], "message": "Context is empty."}

    if types is None:
        types = ["mcq", "true_false", "fill_blank", "short_answer"]

    try:
        generated = generate_questions(context, min(max(total_questions, 1), 10))
        concepts = [item["concept"] for item in extract_concepts(context, top_n=12)]
        questions = []

        for index, generated_question in enumerate(generated, 1):
            question_text = generated_question["question"]
            qa_result = answer_question(
                question_text,
                context,
                language if language in {"en", "hi"} else "en",
            )
            answer = qa_result["answer"]
            if not answer or qa_result["score"] < 0.05:
                continue

            question_type = types[(index - 1) % len(types)]
            item = {
                "id": len(questions) + 1,
                "type": question_type,
                "question": question_text,
                "answer": answer,
                "explanation": f"Answer extracted from the NCERT chapter (confidence {qa_result['score']:.2f}).",
            }

            if question_type == "mcq":
                distractors = [concept for concept in concepts if concept.lower() != answer.lower()]
                options = [answer] + distractors[:3]
                while len(options) < 4:
                    options.append("Not stated in the chapter")
                item["options"] = options[:4]
                item["correct_index"] = 0
            elif question_type == "true_false":
                item["correct_bool"] = True
            elif question_type == "fill_blank":
                item["correct_answer"] = answer

            questions.append(item)

            if len(questions) >= total_questions:
                break

        return {
            "status": "success",
            "total": len(questions),
            "questions": questions,
        }
    except Exception as e:
        print(f"[QuizGenerator] QnA quiz error: {e}")
        # Do NOT return hardcoded chapter-specific questions here — a fixed
        # fallback ("M. Hamel", "Vive La France!") would silently show a
        # student the wrong chapter's quiz with no indication it failed.
        # Fail honestly instead so the frontend can show a retry prompt.
        return {
            "status": "error",
            "questions": [],
            "message": (
                "Quiz generation is temporarily unavailable for this chapter "
                "(the local question or answer model could not complete the request). "
                "Please try again in a moment."
            ),
        }