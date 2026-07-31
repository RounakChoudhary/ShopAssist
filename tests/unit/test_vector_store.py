import pytest
from rag.vector_store import VectorStore
from rag.models import Chunk, EmbeddedChunk


@pytest.fixture
def store(tmp_path):
    """A fresh, persistent Chroma database for each test."""
    return VectorStore(str(tmp_path / "chroma"))


def test_connect_is_idempotent(store):
    client = store.connect()

    assert client is not None
    assert store.client is client
    assert store.connect() is client


def test_create_collection_requires_connection(store):
    with pytest.raises(RuntimeError, match="connect"):
        store.create_collection("test_collection")


def test_create_collection_reuses_named_collection(store):
    store.connect()

    collection = store.create_collection("test_collection")

    assert collection is not None
    assert store.collection is collection

    same_collection = store.create_collection("test_collection")
    assert same_collection.name == "test_collection"


def test_add_and_query_chunks_preserves_chunk_data(store):
    store.connect()
    store.create_collection("test_collection")

    chunk = Chunk(
        filename="policy.md",
        section_title="Returns",
        chunk_index=0,
        content="Products can be returned within 30 days.",
    )

    embedded_chunk = EmbeddedChunk(
        chunk=chunk,
        embedding=[0.1, 0.2, 0.3],
    )

    store.add_chunks([embedded_chunk])

    results = store.query(
        query_embedding=[0.1, 0.2, 0.3],
        top_k=1,
    )

    assert len(results) == 1

    retrieved = results[0]

    assert retrieved.content == chunk.content
    assert retrieved.filename == chunk.filename
    assert retrieved.section_title == chunk.section_title
    assert retrieved.chunk_index == chunk.chunk_index
    assert retrieved.score == pytest.approx(0.0, abs=1e-6)


def test_add_chunks_requires_collection(store):
    with pytest.raises(RuntimeError, match="create_collection"):
        store.add_chunks([])


def test_query_requires_collection(store):
    with pytest.raises(RuntimeError, match="create_collection"):
        store.query(query_embedding=[0.1, 0.2, 0.3], top_k=1)


def test_add_chunks_accepts_empty_list(store):
    store.connect()
    store.create_collection("test_collection")

    store.add_chunks([])

    assert store.collection.count() == 0
