"""
Tests for runtime.traversal.embedding module.

Tests the EmbeddingService class for generating semantic embeddings.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from runtime.traversal.embedding import EmbeddingService, get_embedding_service


class TestEmbeddingService:
    """Test EmbeddingService initialization and basic functionality."""

    def test_init_default_model(self):
        """Test service initializes with default model."""
        service = EmbeddingService()
        assert service.model_name == "sentence-transformers/all-mpnet-base-v2"
        assert service.dimension == 768
        assert service.model is None  # Lazy loading

    def test_init_custom_model(self):
        """Test service initializes with custom model."""
        service = EmbeddingService(model_name="custom-model")
        assert service.model_name == "custom-model"
        assert service.dimension == 768

    @patch('sentence_transformers.SentenceTransformer')
    def test_load_model(self, mock_st):
        """Test lazy model loading."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st.return_value = mock_model

        service = EmbeddingService()
        service._load_model()

        mock_st.assert_called_once_with("sentence-transformers/all-mpnet-base-v2")
        assert service.model == mock_model
        assert service.dimension == 768

    def test_load_model_missing_dependency(self):
        """Test error when sentence-transformers not installed."""
        service = EmbeddingService()

        with patch.dict('sys.modules', {'sentence_transformers': None}):
            with pytest.raises(ImportError, match="sentence-transformers is required"):
                service._load_model()


class TestEmbedText:
    """Test text embedding functionality."""

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_simple_text(self, mock_st):
        """Test embedding simple text."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_embedding = np.array([0.1] * 768)
        mock_model.encode.return_value = mock_embedding
        mock_st.return_value = mock_model

        service = EmbeddingService()
        result = service.embed("Hello world")

        assert isinstance(result, list)
        assert len(result) == 768
        assert all(isinstance(x, float) for x in result)
        mock_model.encode.assert_called_once_with("Hello world", normalize_embeddings=True)

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_empty_text(self, mock_st):
        """Test embedding empty text returns zero vector."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st.return_value = mock_model

        service = EmbeddingService()
        result = service.embed("")

        assert isinstance(result, list)
        assert len(result) == 768
        assert all(x == 0.0 for x in result)
        mock_model.encode.assert_not_called()

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_whitespace_only(self, mock_st):
        """Test embedding whitespace-only text returns zero vector."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st.return_value = mock_model

        service = EmbeddingService()
        result = service.embed("   \n\t  ")

        assert isinstance(result, list)
        assert len(result) == 768
        assert all(x == 0.0 for x in result)


class TestEmbedBatch:
    """Test batch embedding functionality."""

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_batch_multiple_texts(self, mock_st):
        """Test embedding multiple texts in batch."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_embeddings = np.array([[0.1] * 768, [0.2] * 768, [0.3] * 768])
        mock_model.encode.return_value = mock_embeddings
        mock_st.return_value = mock_model

        service = EmbeddingService()
        texts = ["First text", "Second text", "Third text"]
        result = service.embed_batch(texts)

        assert isinstance(result, list)
        assert len(result) == 3
        assert all(len(emb) == 768 for emb in result)
        mock_model.encode.assert_called_once()

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_batch_empty_list(self, mock_st):
        """Test embedding empty list returns empty list."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st.return_value = mock_model

        service = EmbeddingService()
        result = service.embed_batch([])

        assert result == []
        mock_model.encode.assert_not_called()

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_batch_with_empty_strings(self, mock_st):
        """Test batch embedding handles empty strings."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_embeddings = np.array([[0.1] * 768, [0.2] * 768, [0.3] * 768])
        mock_model.encode.return_value = mock_embeddings
        mock_st.return_value = mock_model

        service = EmbeddingService()
        texts = ["First", "", "Third"]
        result = service.embed_batch(texts)

        # Empty strings should be replaced with single space
        call_args = mock_model.encode.call_args[0][0]
        assert call_args[1] == " "


class TestNodeEmbedding:
    """Test node embedding functionality."""

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_character_node(self, mock_st):
        """Test embedding character node."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.array([0.1] * 768)
        mock_st.return_value = mock_model

        service = EmbeddingService()
        node = {
            'type': 'character',
            'name': 'Alice',
            'backstory_wound': 'Lost her family',
            'values': ['justice', 'loyalty']
        }
        result = service.embed_node(node)

        assert len(result) == 768
        # Check that character-specific text was created
        call_args = mock_model.encode.call_args[0][0]
        assert 'Alice' in call_args
        assert 'Lost her family' in call_args

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_place_node(self, mock_st):
        """Test embedding place node."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.array([0.1] * 768)
        mock_st.return_value = mock_model

        service = EmbeddingService()
        node = {
            'type': 'place',
            'name': 'The Tavern',
            'place_type': 'inn',
            'mood': 'lively'
        }
        result = service.embed_node(node)

        assert len(result) == 768
        call_args = mock_model.encode.call_args[0][0]
        assert 'Tavern' in call_args
        assert 'lively' in call_args

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_generic_node(self, mock_st):
        """Test embedding node with unknown type uses fallback."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.array([0.1] * 768)
        mock_st.return_value = mock_model

        service = EmbeddingService()
        node = {
            'type': 'unknown_type',
            'name': 'Something',
            'content': 'Some content'
        }
        result = service.embed_node(node)

        assert len(result) == 768
        call_args = mock_model.encode.call_args[0][0]
        assert 'Something' in call_args
        assert 'Some content' in call_args


class TestLinkEmbedding:
    """Test link embedding functionality."""

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_simple_link(self, mock_st):
        """Test embedding basic link."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.array([0.1] * 768)
        mock_st.return_value = mock_model

        service = EmbeddingService()
        props = {
            'name': 'knows',
            'direction': 'forward'
        }
        result = service.embed_link(props, 'RELATES')

        assert len(result) == 768
        call_args = mock_model.encode.call_args[0][0]
        assert 'RELATES' in call_args
        assert 'knows' in call_args
        assert 'forward' in call_args

    @patch('sentence_transformers.SentenceTransformer')
    def test_embed_link_with_emotions(self, mock_st):
        """Test embedding link with emotions."""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.array([0.1] * 768)
        mock_st.return_value = mock_model

        service = EmbeddingService()
        props = {
            'name': 'loves',
            'emotions': [['joy', 0.8], ['trust', 0.6]]
        }
        result = service.embed_link(props, 'FEELS')

        assert len(result) == 768
        call_args = mock_model.encode.call_args[0][0]
        assert 'joy' in call_args or 'trust' in call_args


class TestSimilarity:
    """Test vector similarity calculations."""

    def test_similarity_identical_vectors(self):
        """Test similarity of identical vectors is 1.0."""
        service = EmbeddingService()
        vec = [1.0, 0.0, 0.0]
        similarity = service.similarity(vec, vec)
        assert abs(similarity - 1.0) < 0.001

    def test_similarity_orthogonal_vectors(self):
        """Test similarity of orthogonal vectors is 0.0."""
        service = EmbeddingService()
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        similarity = service.similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 0.001

    def test_similarity_opposite_vectors(self):
        """Test similarity of opposite vectors is -1.0."""
        service = EmbeddingService()
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [-1.0, 0.0, 0.0]
        similarity = service.similarity(vec1, vec2)
        assert abs(similarity - (-1.0)) < 0.001

    def test_similarity_normalized_vectors(self):
        """Test similarity with normalized vectors."""
        service = EmbeddingService()
        # Normalized vectors
        vec1 = [0.6, 0.8, 0.0]
        vec2 = [0.8, 0.6, 0.0]
        similarity = service.similarity(vec1, vec2)
        assert 0.9 < similarity < 1.0  # Should be high but not 1.0


class TestSingleton:
    """Test singleton pattern for embedding service."""

    def test_get_embedding_service_singleton(self):
        """Test get_embedding_service returns same instance."""
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        assert service1 is service2

    def test_singleton_preserves_state(self):
        """Test singleton preserves model state."""
        service = get_embedding_service()
        service.custom_attr = "test_value"

        service2 = get_embedding_service()
        assert hasattr(service2, 'custom_attr')
        assert service2.custom_attr == "test_value"
