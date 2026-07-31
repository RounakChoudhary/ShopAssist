from unittest.mock import Mock, patch

import numpy as np

from rag.embedding import get_embedding, get_embeddings


@patch("rag.embedding.get_embedding_model")
def test_get_embedding(mock_get_model):
    model = Mock()
    model.encode.return_value = np.array([0.1, 0.2, 0.3])
    mock_get_model.return_value = model

    result = get_embedding("What is the return policy?")

    np.testing.assert_array_equal(result, [0.1, 0.2, 0.3])
    model.encode.assert_called_once_with("What is the return policy?")


@patch("rag.embedding.get_embedding_model")
def test_get_embeddings(mock_get_model):
    model = Mock()
    model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
    mock_get_model.return_value = model

    result = get_embeddings(["return policy", "cancellation policy"])

    assert result.shape == (2, 2)
    model.encode.assert_called_once_with(
        ["return policy", "cancellation policy"]
    )