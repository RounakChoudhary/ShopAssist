import pytest
from unittest.mock import Mock, patch

from rag.models import RetrievedChunk
from rag.retriever import Retriever


@patch("rag.retriever.get_embedding")
def test_retrieve(mock_get_embedding):
    mock_get_embedding.return_value = [0.1, 0.2, 0.3]

    vector_store = Mock()

    expected = [
        RetrievedChunk(
            content="Refunds are allowed.",
            filename="policy.md",
            section_title="# Refund Policy",
            chunk_index=0,
            score=0.01,
        )
    ]

    vector_store.query.return_value = expected

    retriever = Retriever(vector_store)

    results = retriever.retrieve(
        query="refund policy",
        top_k=1,
    )

    mock_get_embedding.assert_called_once_with("refund policy")

    vector_store.query.assert_called_once_with(
        query_embedding=[0.1, 0.2, 0.3],
        top_k=1,
    )

    assert results == expected




def test_retrieve_invalid_top_k():
    retriever = Retriever(Mock())

    with pytest.raises(ValueError):
        retriever.retrieve(
            query="refund",
            top_k=0,
        )
