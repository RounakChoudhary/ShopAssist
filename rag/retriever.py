from rag.embedding import get_embedding
from rag.vector_store import VectorStore


class Retriever:
    """
    Retrieves the most relevant document chunks for a given user query
    using vector similarity search.
    """

    def __init__(self, vector_store: VectorStore):
        """
        Initialize the retriever with a configured vector store.

        Args:
            vector_store: Vector store used for similarity search.
        """
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int):
        """
        Retrieve the top-k most relevant chunks for the given query.

        Args:
            query: User's search query.
            top_k: Number of relevant chunks to retrieve.

        Returns:
            list[RetrievedChunk]: Retrieved chunks ranked by similarity.
        """
        if top_k < 1:
            raise ValueError("top_k must be greater than or equal to 1.")
        query_embedding = get_embedding(query)

        retrieved_chunks = self.vector_store.query(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        return retrieved_chunks
