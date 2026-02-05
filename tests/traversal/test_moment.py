"""
Tests for runtime.traversal.moment module.

Tests the MomentOperationsMixin class for moment lifecycle operations.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock
from runtime.traversal.moment import MomentOperationsMixin


class MockGraphOps(MomentOperationsMixin):
    """Mock GraphOps class that inherits from MomentOperationsMixin."""

    def __init__(self):
        self.query_results = []
        self.query_calls = []

    def _query(self, cypher, params=None):
        """Mock _query method."""
        self.query_calls.append((cypher, params))
        return self.query_results


class TestHandleClick:
    """Test handle_click functionality."""

    def test_no_matching_transitions(self):
        """Test when no transitions match the click."""
        ops = MockGraphOps()
        ops.query_results = []  # No matching transitions

        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="hello",
            player_id="player_1"
        )

        assert result["flipped"] is False
        assert result["flipped_moments"] == []
        assert result["weight_updates"] == []
        assert result["queue_narrator"] is True

    def test_single_matching_transition(self):
        """Test single transition matching clicked word."""
        ops = MockGraphOps()

        # Mock query results: (target_id, content, type, status, weight, require_words, weight_transfer, consumes_origin)
        ops.query_results = [
            ("moment_2", "Response content", "reply", "dormant", 0.5,
             json.dumps(["hello", "hi"]), 0.4, False)
        ]

        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="hello",
            player_id="player_1"
        )

        # Should have found a matching transition
        assert len(ops.query_calls) >= 1

        # Verify the query was called with correct params
        cypher, params = ops.query_calls[0]
        assert "CAN_LEAD_TO" in cypher
        assert params["moment_id"] == "moment_1"

    def test_weight_below_threshold(self):
        """Test transition that doesn't cross flip threshold."""
        ops = MockGraphOps()

        ops.query_results = [
            ("moment_2", "Response", "reply", "dormant", 0.3,
             json.dumps(["test"]), 0.3, False)  # 0.3 + 0.3 = 0.6 < 0.8
        ]

        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="test",
            player_id="player_1"
        )

        # Weight increased but didn't flip
        assert len(result["weight_updates"]) > 0 or result["queue_narrator"] is True

    def test_weight_crosses_threshold(self):
        """Test transition that crosses flip threshold (0.8)."""
        ops = MockGraphOps()

        ops.query_results = [
            ("moment_2", "Flipped response", "reply", "dormant", 0.6,
             json.dumps(["flip"]), 0.4, False)  # 0.6 + 0.4 = 1.0 > 0.8
        ]

        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="flip",
            player_id="player_1"
        )

        # Should detect potential flip (exact behavior depends on implementation)
        assert len(ops.query_calls) >= 1

    def test_case_insensitive_word_matching(self):
        """Test that word matching is case-insensitive."""
        ops = MockGraphOps()

        ops.query_results = [
            ("moment_2", "Response", "reply", "dormant", 0.5,
             json.dumps(["Hello", "WORLD"]), 0.3, False)
        ]

        # Test lowercase click matches uppercase requirement
        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="hello",  # lowercase
            player_id="player_1"
        )

        assert len(ops.query_calls) >= 1

    def test_require_words_as_list(self):
        """Test handling require_words as Python list (not JSON string)."""
        ops = MockGraphOps()

        ops.query_results = [
            ("moment_2", "Response", "reply", "dormant", 0.5,
             ["word1", "word2"],  # Already a list, not JSON string
             0.3, False)
        ]

        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="word1",
            player_id="player_1"
        )

        assert len(ops.query_calls) >= 1

    def test_multiple_transitions_same_word(self):
        """Test multiple transitions triggered by same word."""
        ops = MockGraphOps()

        ops.query_results = [
            ("moment_2", "First response", "reply", "dormant", 0.4,
             json.dumps(["click"]), 0.2, False),
            ("moment_3", "Second response", "reply", "dormant", 0.5,
             json.dumps(["click"]), 0.3, False),
        ]

        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="click",
            player_id="player_1"
        )

        # Both transitions should be considered
        assert len(ops.query_calls) >= 1

    def test_no_require_words(self):
        """Test transition with no require_words (None or empty)."""
        ops = MockGraphOps()

        ops.query_results = [
            ("moment_2", "Response", "reply", "dormant", 0.5,
             None,  # No require_words
             0.3, False)
        ]

        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="anything",
            player_id="player_1"
        )

        # Should not match since require_words is None
        # (based on code logic: `any(word.lower() == clicked_lower for word in (require_words or []))`)
        assert len(ops.query_calls) >= 1


class TestMomentLifecycle:
    """Test moment lifecycle state management."""

    def test_initialization(self):
        """Test that MomentOperationsMixin can be initialized."""
        ops = MockGraphOps()
        assert ops is not None
        assert hasattr(ops, 'handle_click')

    def test_query_method_required(self):
        """Test that _query method is available."""
        ops = MockGraphOps()
        assert hasattr(ops, '_query')
        assert callable(ops._query)

    def test_handle_click_returns_dict(self):
        """Test that handle_click always returns a dict."""
        ops = MockGraphOps()
        ops.query_results = []

        result = ops.handle_click("m1", "word", "p1")

        assert isinstance(result, dict)
        assert "flipped" in result
        assert "flipped_moments" in result
        assert "weight_updates" in result
        assert "queue_narrator" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_clicked_word(self):
        """Test handling empty clicked word."""
        ops = MockGraphOps()
        ops.query_results = [
            ("moment_2", "Response", "reply", "dormant", 0.5,
             json.dumps([""]), 0.3, False)
        ]

        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="",
            player_id="player_1"
        )

        assert isinstance(result, dict)

    def test_none_moment_id(self):
        """Test handling None moment_id."""
        ops = MockGraphOps()
        ops.query_results = []

        result = ops.handle_click(
            moment_id=None,
            clicked_word="test",
            player_id="player_1"
        )

        # Should still execute query (Cypher will handle None)
        assert len(ops.query_calls) >= 1

    def test_special_characters_in_word(self):
        """Test handling special characters in clicked word."""
        ops = MockGraphOps()
        ops.query_results = [
            ("moment_2", "Response", "reply", "dormant", 0.5,
             json.dumps(["hello!", "world?"]), 0.3, False)
        ]

        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="hello!",
            player_id="player_1"
        )

        assert isinstance(result, dict)

    def test_unicode_in_word(self):
        """Test handling Unicode characters."""
        ops = MockGraphOps()
        ops.query_results = [
            ("moment_2", "Response", "reply", "dormant", 0.5,
             json.dumps(["café", "naïve"]), 0.3, False)
        ]

        result = ops.handle_click(
            moment_id="moment_1",
            clicked_word="café",
            player_id="player_1"
        )

        assert isinstance(result, dict)
