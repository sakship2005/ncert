from nlp_engine.analysis.similarity import compare_sentences


sentence_a = "The French language was very important to the people."

sentence_b = "The people considered their French language important."


result = compare_sentences(
    sentence_a,
    sentence_b,
)


print("\nSENTENCE SIMILARITY")
print("=" * 60)

print("\nSentence A:")
print(result["sentence_a"])

print("\nSentence B:")
print(result["sentence_b"])

print("\nTF-IDF Similarity:")
print(result["tfidf_similarity"])

print("\nSemantic Similarity:")
print(result["semantic_similarity"])