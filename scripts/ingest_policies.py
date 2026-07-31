from config import CHROMA_COLLECTION_NAME, CHROMA_DB_PATH, POLICY_FOLDER
from rag.ingest import IngestionPipeline
from rag.vector_store import VectorStore


def main() -> None:
    store = VectorStore(str(CHROMA_DB_PATH))
    store.connect()
    store.create_collection(CHROMA_COLLECTION_NAME)

    pipeline = IngestionPipeline(store)
    summary = pipeline.ingest(POLICY_FOLDER)

    print(
        "Policy ingestion complete: "
        f"{summary['documents']} documents, "
        f"{summary['chunks']} chunks, "
        f"{summary['embedded_chunks']} embeddings."
    )


if __name__ == "__main__":
    main()