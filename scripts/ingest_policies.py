from pathlib import Path

from rag.ingest import IngestionPipeline
from rag.vector_store import VectorStore

# Initialize vector store
from config import (
    CHROMA_DB_PATH,
    CHROMA_COLLECTION_NAME,
    POLICY_FOLDER,
)

vector_store = VectorStore(str(CHROMA_DB_PATH))
vector_store.connect()
vector_store.create_collection(CHROMA_COLLECTION_NAME)

# Create ingestion pipeline
pipeline = IngestionPipeline(vector_store)

# Ingest all markdown files
summary = pipeline.ingest(Path(POLICY_FOLDER))

print(summary)