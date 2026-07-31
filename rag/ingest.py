from pathlib import Path

from rag.loader import get_policy_files, read_policy_files
from rag.chunker import chunk_document_by_headings
from rag.embedding import get_embeddings
from rag.models import EmbeddedChunk
from rag.vector_store import VectorStore


class IngestionPipeline:
    """
    Coordinates the document ingestion pipeline by loading,
    chunking, embedding, and storing documents in the vector database.
    """

    def __init__(self, vector_store: VectorStore):
        """
        Initialize the retriever with a configured vector store.

        Args:
            vector_store: Vector store used for similarity search.
        """
        self.vector_store = vector_store

    def ingest(self, folder: Path):
        """
        Ingest all markdown documents from the given folder into the vector store.

        Args:
            folder: Path containing markdown documents.

        Returns:
            A summary of the ingestion process.
        """

        # Load markdown documents from the specified folder
        files = get_policy_files(folder)
        documents = read_policy_files(files)

        # Split each document into heading-based chunks
        all_chunks = []
        for document in documents:
            chunks = chunk_document_by_headings(document)
            all_chunks.extend(chunks)

        # Generate embeddings for every chunk
        chunk_texts = [
            f"Document: {chunk.filename}\n"
            f"Section: {chunk.section_title}\n\n"
            f"{chunk.content}"
            for chunk in all_chunks
        ]
        embeddings = get_embeddings(chunk_texts)

        # Pair each chunk with its corresponding embedding
        embedded_chunks = []
        for chunk, embedding in zip(all_chunks, embeddings):
            embedded_chunks.append(
                EmbeddedChunk(chunk=chunk, embedding=embedding.tolist())
            )

        # Persist embedded chunks in the vector store
        self.vector_store.add_chunks(embedded_chunks)

        # Return ingestion summary
        return {
            "documents": len(documents),
            "chunks": len(all_chunks),
            "embedded_chunks": len(embedded_chunks),
        }
