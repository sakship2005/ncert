from nlp_engine.retrieval.chunking import create_chunks
from nlp_engine.retrieval.vector_store import VectorStore


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


store = VectorStore()

store.add_chunks(chunks)


print("\nFAISS VECTOR STORE")
print("=" * 60)

print("Chunks added:", store.size())


query = "Why was the French language important?"

results = store.search(
    query,
    top_k=3,
)


print("\nQuery:")
print(query)

print("\nMost relevant chunks:")

for result in results:

    print("\nChunk:", result["chunk_id"])

    print(
        "Similarity:",
        result["similarity"],
    )

    print(
        "Text:",
        result["text"],
    )

print("\n" + "=" * 60)