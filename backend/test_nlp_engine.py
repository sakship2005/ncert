from nlp_engine.analysis.keywords import extract_keywords
from nlp_engine.analysis.concepts import extract_concepts
from nlp_engine.analysis.entities import extract_entities
from nlp_engine.analysis.topics import extract_topics
from nlp_engine.analysis.vocabulary import extract_vocabulary

TEXT = """
The Last Lesson is a story about Franz and his
teacher M. Hamel. Franz arrives late at school
and discovers that it is the last French lesson.

The order has come from Berlin that only German
will be taught in the schools of Alsace and
Lorraine.

M. Hamel explains the importance of the French
language and expresses his sadness.

The villagers also attend the final lesson.
"""


def main():

    print("=" * 60)
    print("NCERT NLP ENGINE TEST")
    print("=" * 60)

    # ==================================================
    # KEYWORD EXTRACTION
    # ==================================================

    print()
    print("KEYWORDS")
    print("-" * 60)

    keywords = extract_keywords(
        TEXT,
        top_n=15,
    )

    if not keywords:
        print("No keywords found.")

    else:

        for item in keywords:

            print(
                f"{item['keyword']:<30}"
                f"{item['score']}"
            )

    # ==================================================
    # CONCEPT EXTRACTION
    # ==================================================

    print()
    print("CONCEPTS")
    print("-" * 60)

    concepts = extract_concepts(
        TEXT,
        top_n=15,
    )

    if not concepts:
        print("No concepts found.")

    else:

        for item in concepts:

            print(
                f"{item['concept']:<30}"
                f"{item['frequency']}"
            )

    # ==================================================
    # NAMED ENTITY RECOGNITION
    # ==================================================

    print()
    print("NAMED ENTITIES")
    print("-" * 60)

    entities = extract_entities(
        TEXT
    )

    if not entities:
        print("No named entities found.")

    else:

        for entity in entities:

            print(
                f"{entity['text']:<25}"
                f"{entity['label']:<15}"
                f"{entity['description']}"
            )

    # ==================================================
    # TOPIC EXTRACTION
    # ==================================================

    print()
    print("TOPICS")
    print("-" * 60)

    topics = extract_topics(
        TEXT,
        num_topics=3,
        words_per_topic=8,
    )

    if not topics:

        print("No topics found.")

    else:

        for topic in topics:

            print(
                f"Topic {topic['topic']}: "
                f"{', '.join(topic['keywords'])}"
            )

        # ==================================================
    # VOCABULARY
    # ==================================================

    print()
    print("DIFFICULT WORDS / VOCABULARY")
    print("-" * 60)

    vocabulary = extract_vocabulary(
        TEXT,
        min_word_length=6,
        top_n=15,
    )

    if not vocabulary:

        print("No vocabulary found.")

    else:

        for item in vocabulary:

            print(
                f"{item['word']:<20}"
                f"Frequency: {item['frequency']:<5}"
                f"Difficulty: "
                f"{item['difficulty_score']:<6}"
                f"{item['definition']}"
            )


    # ==================================================
    # COMPLETED
    # ==================================================

    print()
    print("=" * 60)
    print("NLP ENGINE TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()