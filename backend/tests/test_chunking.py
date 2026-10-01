from nlp_engine.retrieval.chunking import create_chunks


TEXT = """
The Last Lesson is a story about Franz and his teacher M. Hamel.
Franz arrives late at school and discovers that it is the last French lesson.
The order has come from Berlin that only German will be taught in the schools of Alsace and Lorraine.
M. Hamel explains the importance of the French language and expresses his sadness.
The villagers also attend the final lesson.
They are sorry that they did not attend school regularly.
M. Hamel tells the students that their language is very important.
The final lesson becomes an emotional moment for everyone.
"""


chunks = create_chunks(
    TEXT,
    sentences_per_chunk=3,
    overlap=1,
)


print("\nCHUNKS")
print("=" * 60)

for chunk in chunks:

    print(f"\nChunk {chunk['chunk_id']}")
    print(
        f"Sentences: "
        f"{chunk['sentence_start']} - "
        f"{chunk['sentence_end']}"
    )

    print(chunk["text"])

print("\n" + "=" * 60)
print("Total chunks:", len(chunks))