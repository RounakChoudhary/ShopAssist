from config import CHROMA_COLLECTION_NAME, CHROMA_DB_PATH
from rag.retriever import Retriever
from rag.vector_store import VectorStore


def main() -> None:
    store = VectorStore(str(CHROMA_DB_PATH))
    store.connect()
    store.create_collection(CHROMA_COLLECTION_NAME)

    retriever = Retriever(store)
    results = retriever.retrieve(
        query="How can I cancel my order?",
        top_k=3,
    )

    for index, chunk in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(f"Source: {chunk.filename}")
        print(f"Section: {chunk.section_title}")
        print(f"Distance: {chunk.score:.4f}")
        print(chunk.content)


if __name__ == "__main__":
    main()