import faiss
import numpy as np

from nlp_engine.retrieval.embeddings import (
    generate_embeddings,
)


class VectorStore:
    """
    FAISS-based semantic vector store
    for NCERT text chunks.
    """

    def __init__(self):
        self.index = None
        self.chunks = []

    def add_chunks(
        self,
        chunks: list[dict],
    ):
        """
        Convert chunks into embeddings
        and add them to the FAISS index.
        """

        if not chunks:
            return

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = generate_embeddings(texts)

        vectors = np.array(
            embeddings,
            dtype="float32",
        )

        dimension = vectors.shape[1]

        # Inner product works as cosine similarity
        # because our embeddings are normalized.
        if self.index is None:
            self.index = faiss.IndexFlatIP(
                dimension
            )

        self.index.add(vectors)

        self.chunks.extend(chunks)

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """
        Search for the most semantically relevant
        NCERT chunks.
        """

        if not query or not query.strip():
            return []

        if self.index is None:
            return []

        query_embedding = generate_embeddings(
            [query]
        )

        query_vector = np.array(
            query_embedding,
            dtype="float32",
        )

        scores, indices = self.index.search(
            query_vector,
            min(top_k, len(self.chunks)),
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0:
                continue

            result = self.chunks[index].copy()

            result["similarity"] = round(
                float(score),
                4,
            )

            results.append(result)

        return results

    def size(self) -> int:
        """
        Return the number of stored chunks.
        """

        if self.index is None:
            return 0

        return self.index.ntotal