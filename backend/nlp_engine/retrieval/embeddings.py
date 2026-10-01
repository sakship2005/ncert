from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

# Load the embedding model once
model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """
    Convert a single text into a semantic embedding.
    """

    if not text or not text.strip():
        return []

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:
    """
    Convert multiple texts into semantic embeddings.
    """

    if not texts:
        return []

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


def get_embedding_dimension() -> int:
    """
    Return the size of the embedding vector.
    """

    return model.get_embedding_dimension()