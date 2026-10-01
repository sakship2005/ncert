from nlp_engine.generation.question_generator import (
    generate_questions
)


context = """
M. Hamel was the French teacher in the school.
He told the students that this was their last
French lesson because an order had come from
Berlin to teach only German in the schools of
Alsace and Lorraine.

M. Hamel explained that the French language was
important and that the people should protect it
and learn their own language.

Franz was surprised because he had not expected
the announcement that it would be his last French
lesson.
"""


questions = generate_questions(
    context=context,
    number_of_questions=5,
)


print("\nGENERATED QUESTIONS")
print("=" * 60)

for number, question in enumerate(
    questions,
    start=1,
):
    print(f"\nQuestion {number}")
    print("Type:", question["type"])
    print("Difficulty:", question["difficulty"])
    print("Question:", question["question"])
    print("Answer:", question["answer"])