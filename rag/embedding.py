from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
import numpy as np

try:
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
except Exception as e:
    raise RuntimeError(f"Failed to load embedding model '{EMBEDDING_MODEL}'.") from e


def get_embedding(text: str) -> np.ndarray:
    """
    Generate an embedding for a single user query.

    Args:
        text (str): User query.

    Returns:
        np.ndarray: Embedding vector.
    """
    return embedding_model.encode(text)


def get_embeddings(texts: list[str]) -> np.ndarray:
    """
        Generate embeddings for multiple document chunks.

    Args:
        texts (list[str]): List of document chunks.

    Returns:
        np.ndarray: Embedding vectors.
    """
    return embedding_model.encode(texts)
