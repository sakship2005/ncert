import os
import re
import json

from google import genai
from google.genai import types as genai_types

GEMINI_MODEL = "gemini-3.5-flash-lite"


def _build_prompt(context: str, total: int, qtypes: list[str], language: str) -> str:
    type_instructions = []
    if "mcq" in qtypes:
        type_instructions.append(
            '"mcq": question with exactly 4 options array, correct_index integer 0-3, explanation string'
        )
    if "true_false" in qtypes:
        type_instructions.append(
            '"true_false": a factual statement as question, correct_bool JSON boolean true or false, explanation string'
        )
    if "fill_blank" in qtypes:
        type_instructions.append(
            '"fill_blank": sentence with ___ replacing ONE key word, correct_answer string, explanation string'
        )
    if "multi" in qtypes:
        type_instructions.append(
            '"multi": question with exactly 4 options array, correct_indices array of 2+ correct integer indexes, explanation string'
        )

    if language == "hi":
        lang_note = "Write ALL questions, options, and explanations in Hindi (Devanagari script)."
    elif language == "mr":
        lang_note = "Write ALL questions, options, and explanations in Marathi (Devanagari script)."
    else:
        lang_note = "Write all questions in clear formal English suitable for Class 6-12 school exams."

    return f"""You are an NCERT exam question paper setter for Indian school students.
{lang_note}

TASK: Generate exactly {total} high-quality exam questions from the chapter text below.
- Questions must test understanding, NOT just word matching
- Use formal exam language: "Which of the following...", "According to the chapter...", "State whether True or False:"
- Every question must have a clear, unambiguous correct answer found in the chapter
- Distribute question types evenly: {', '.join(qtypes)}

REQUIRED JSON FORMAT — each object must have these exact fields by type:

MCQ:        {{"id":1, "type":"mcq", "question":"...", "options":["A","B","C","D"], "correct_index":0, "explanation":"..."}}
True/False: {{"id":2, "type":"true_false", "question":"State whether True or False: ...", "correct_bool":true, "explanation":"..."}}
Fill blank: {{"id":3, "type":"fill_blank", "question":"The ___ of a number are numbers that divide it exactly.", "correct_answer":"factors", "explanation":"..."}}
Multi:      {{"id":4, "type":"multi", "question":"Which of the following are prime numbers?", "options":["2","4","7","9"], "correct_indices":[0,2], "explanation":"..."}}

OUTPUT RULES:
- Return ONLY the JSON array, nothing else
- Start with [ end with ]
- No markdown, no ```json, no explanation text outside the array
- correct_bool must be JSON true or false (NOT the string "true")
- correct_index must be an integer (NOT a string)
- correct_indices must be array of integers

CHAPTER TEXT:
{context[:5000]}

Generate {total} questions now:"""


def _parse_json_safe(raw: str) -> list:
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw).strip()

    # Try direct parse
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Extract [...] block
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group(0))
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    # Recover truncated JSON — keep everything up to last complete }
    try:
        last_brace = raw.rfind("}")
        if last_brace > 0:
            arr_start = raw.find("[")
            if arr_start != -1:
                candidate = raw[arr_start: last_brace + 1] + "]"
                result = json.loads(candidate)
                if isinstance(result, list):
                    print(f"[QuizGenerator] Recovered truncated JSON: {len(result)} items")
                    return result
    except json.JSONDecodeError:
        pass

    raise ValueError(f"Unparseable response. Starts with: {raw[:200]}")


def _sanitize(q: dict, new_id: int) -> dict | None:
    if not isinstance(q, dict):
        return None

    qtype = str(q.get("type", "")).strip()
    question = str(q.get("question", "")).strip()

    if not qtype or not question:
        print(f"[QuizGenerator] Drop — missing type/question: {list(q.keys())}")
        return None

    q["id"] = new_id
    q["type"] = qtype

    if qtype == "mcq":
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) < 2:
            print(f"[QuizGenerator] Drop MCQ — bad options: {opts}")
            return None
        while len(opts) < 4:
            opts.append("None of the above")
        q["options"] = opts[:4]
        ci = q.get("correct_index")
        # Handle string integers from model
        try:
            ci = int(ci)
        except (TypeError, ValueError):
            ci = 0
        q["correct_index"] = max(0, min(ci, 3))

    elif qtype == "true_false":
        cb = q.get("correct_bool")
        if isinstance(cb, str):
            q["correct_bool"] = cb.strip().lower() == "true"
        elif not isinstance(cb, bool):
            print(f"[QuizGenerator] true_false — fixing bad correct_bool: {cb}")
            q["correct_bool"] = True

    elif qtype == "fill_blank":
        ans = q.get("correct_answer", "")
        if not ans:
            print(f"[QuizGenerator] Drop fill_blank — no correct_answer")
            return None
        if "___" not in question:
            # Try to replace the answer word in the question
            replaced = re.sub(re.escape(str(ans)), "___", question, count=1, flags=re.IGNORECASE)
            q["question"] = replaced if "___" in replaced else question.rstrip("?. ") + " (___)"

    elif qtype == "multi":
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) < 2:
            print(f"[QuizGenerator] Drop multi — bad options: {opts}")
            return None
        while len(opts) < 4:
            opts.append("None of the above")
        q["options"] = opts[:4]
        ci_list = q.get("correct_indices")
        if not isinstance(ci_list, list):
            q["correct_indices"] = [0, 1]
        else:
            fixed = []
            for x in ci_list:
                try:
                    ix = int(x)
                    if 0 <= ix <= 3:
                        fixed.append(ix)
                except (TypeError, ValueError):
                    pass
            q["correct_indices"] = fixed if fixed else [0, 1]
    else:
        print(f"[QuizGenerator] Drop — unknown type: {qtype}")
        return None

    if not q.get("explanation"):
        q["explanation"] = "Refer to the chapter for more details."

    return q


def generate_interactive_quiz(
    context: str,
    total_questions: int = 35,
    types: list[str] = None,
    language: str = "en",
) -> dict:
    if not context or not context.strip():
        return {"status": "error", "questions": [], "message": "Context is empty."}

    qtypes = [t for t in (types or []) if t != "short_answer"]
    if not qtypes:
        qtypes = ["mcq", "true_false", "fill_blank", "multi"]

    total_questions = max(10, min(total_questions, 40))

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return {"status": "error", "questions": [],
                "message": "GEMINI_API_KEY not set in .env"}

    try:
        client = genai.Client(api_key=api_key)
        all_cleaned = []

        # Max 20 per batch to stay well within token limits
        batches = []
        remaining = total_questions
        while remaining > 0:
            batches.append(min(remaining, 20))
            remaining -= batches[-1]

        for idx, batch_size in enumerate(batches):
            print(f"[QuizGenerator] Batch {idx+1}/{len(batches)} — requesting {batch_size} questions")
            prompt = _build_prompt(context, batch_size, qtypes, language)

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=min(batch_size * 160 + 600, 8000),
                ),
            )

            raw = response.text.strip()
            print(f"[QuizGenerator] Raw ({len(raw)} chars), first 300:\n{raw[:300]}\n")

            try:
                parsed = _parse_json_safe(raw)
            except ValueError as e:
                print(f"[QuizGenerator] Batch {idx+1} parse failed: {e}")
                continue

            print(f"[QuizGenerator] Parsed {len(parsed)} items from batch {idx+1}")

            start_id = len(all_cleaned) + 1
            for i, q in enumerate(parsed, start_id):
                clean = _sanitize(q, i)
                if clean:
                    all_cleaned.append(clean)

            print(f"[QuizGenerator] Valid so far: {len(all_cleaned)}")

        if not all_cleaned:
            return {
                "status": "error",
                "questions": [],
                "message": "Quiz generation returned no valid questions. Check backend logs for details.",
            }

        for i, q in enumerate(all_cleaned, 1):
            q["id"] = i

        return {"status": "success", "total": len(all_cleaned), "questions": all_cleaned}

    except Exception as e:
        import traceback
        print(f"[QuizGenerator] Fatal: {e}")
        traceback.print_exc()
        return {"status": "error", "questions": [], "message": f"Quiz generation failed: {e}"}