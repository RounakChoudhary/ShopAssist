import chromadb
from rag.models import RetrievedChunk


class VectorStore:
    def __init__(self, db_path):
        self.db_path = db_path
        self.client = None
        self.collection = None

    def connect(self):
        if self.client is None:
            self.client = chromadb.PersistentClient(path=self.db_path)
        return self.client

    def create_collection(self, collection_name):
        if self.client is None:
            raise RuntimeError("Call connect() before create_collection().")
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        return self.collection

    def add_chunks(self, embedded_chunks):
        if self.collection is None:
            raise RuntimeError("Call create_collection() before add_chunks().")
        if not embedded_chunks:
            return
        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for embedded_chunk in embedded_chunks:
            chunk = embedded_chunk.chunk
            embeddings.append(embedded_chunk.embedding)
            documents.append(chunk.content)
            metadata = {
                "filename": chunk.filename,
                "section_title": chunk.section_title,
                "chunk_index": chunk.chunk_index,
            }
            metadatas.append(metadata)
            chunk_id = f"{chunk.filename}_{chunk.chunk_index}"
            ids.append(chunk_id)
        self.collection.upsert(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

    def query(self, query_embedding, top_k):
        if self.collection is None:
            raise RuntimeError("Call create_collection() before query().")
        if top_k < 1:
            raise ValueError("top_k must be greater than or equal to 1.")
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=top_k
        )
        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        retrieved_chunks = []
        for doc, metadata, distance in zip(docs, metadatas, distances):
            retrieved_chunk = RetrievedChunk(
                content=doc,
                filename=metadata["filename"],
                section_title=metadata["section_title"],
                chunk_index=metadata["chunk_index"],
                score=distance,
            )
            retrieved_chunks.append(retrieved_chunk)
        return retrieved_chunks
