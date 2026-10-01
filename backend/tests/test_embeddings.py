from nlp_engine.retrieval.embeddings import (
    generate_embedding,
    generate_embeddings,
    get_embedding_dimension,
)


text1 = "M. Hamel was the French teacher in the school."
text2 = "The teacher taught French to the students."
text3 = "The weather was very cold today."


embedding1 = generate_embedding(text1)

print("Embedding dimension:", len(embedding1))
print("First 10 values:", embedding1[:10])


texts = [
    text1,
    text2,
    text3,
]

embeddings = generate_embeddings(texts)

print("\nNumber of embeddings:", len(embeddings))
print("Embedding dimension:", len(embeddings[0]))

print("\nModel dimension:", get_embedding_dimension())