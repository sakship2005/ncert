from nlp_engine.generation.answer_generator import generate_answer


context = """
M. Hamel was the French teacher in the school.
He told the students that this was their last
French lesson because an order had come from
Berlin to teach only German in the schools of
Alsace and Lorraine.

M. Hamel explained that the French language was
important and that the people should protect
and learn their own language.
"""


question = "Why was the French language important?"


answer = generate_answer(
    question=question,
    context=context,
)


print("\nAI TUTOR ANSWER")
print("=" * 60)
print(answer)