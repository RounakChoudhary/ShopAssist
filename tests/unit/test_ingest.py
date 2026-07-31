from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np

from rag.ingest import IngestionPipeline
from rag.models import (
    Document,
    Chunk,
)


@patch("rag.ingest.get_embeddings")
@patch("rag.ingest.chunk_document_by_headings")
@patch("rag.ingest.read_policy_files")
@patch("rag.ingest.get_policy_files")
def test_ingest_pipeline(
    mock_get_files,
    mock_read_files,
    mock_chunker,
    mock_get_embeddings,
):
    mock_get_files.return_value = [
        Path("policy.md")
    ]

    mock_read_files.return_value = [
        Document(
            filename="policy.md",
            content="# Refund\nRefunds are allowed.",
        )
    ]

    mock_chunker.return_value = [
        Chunk(
            filename="policy.md",
            section_title="# Refund",
            chunk_index=0,
            content="Refunds are allowed.",
        )
    ]

    mock_get_embeddings.return_value = np.array(
        [
            [0.1, 0.2, 0.3]
        ]
    )

    vector_store = Mock()

    pipeline = IngestionPipeline(vector_store)

    summary = pipeline.ingest(Path("data"))

    vector_store.add_chunks.assert_called_once()

    assert summary["documents"] == 1
    assert summary["chunks"] == 1
    assert summary["embedded_chunks"] == 1