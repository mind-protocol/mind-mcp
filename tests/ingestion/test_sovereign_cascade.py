"""
Tests for Sovereign Cascade Prediction Tracker.

Validates:
- V8: Cascade accuracy threshold enforced
- Prediction recording and resolution
- Alignment fidelity calculation with rolling window
- Cascade state transitions: active -> probation -> suspended
- Edge cases: insufficient data, double resolution, boundary values

DOCS: docs/human_integration/ALGORITHM_Human_Integration.md
      docs/human_integration/VALIDATION_Human_Integration.md
"""

import pytest

from runtime.ingestion.sovereign_cascade_prediction_tracker import (
    MIN_PREDICTIONS_FOR_CALIBRATION,
    ROLLING_WINDOW,
    THRESHOLD_ACTIVE,
    THRESHOLD_PROBATION,
    compute_confidence_calibration,
    get_cascade_status,
    measure_alignment_fidelity,
    record_prediction,
    resolve_prediction,
)


# ── Mock Graph Adapter ────────────────────────────────────────────────────


class MockGraphAdapter:
    """In-memory graph adapter for testing cascade operations."""

    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self._id_counter = 0

    def query_nodes(self, node_type, filters):
        results = []
        for node in self.nodes.values():
            if node_type is not None and node.get("node_type") != node_type:
                continue
            if not self._matches_filters(node, filters):
                continue
            results.append(node)
        return results

    def create_node(self, node_data):
        self._id_counter += 1
        node_id = node_data.get("id", f"node_{self._id_counter}")
        node_data["id"] = node_id
        self.nodes[node_id] = node_data
        return node_id

    def update_node(self, node_id, updates):
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} not found")
        self.nodes[node_id].update(updates)

    def _matches_filters(self, node, filters):
        for key, value in filters.items():
            if "." in key:
                parts = key.split(".")
                obj = node
                for part in parts:
                    if isinstance(obj, dict):
                        obj = obj.get(part)
                    else:
                        return False
                if obj != value:
                    return False
            else:
                if node.get(key) != value:
                    return False
        return True


@pytest.fixture
def graph():
    return MockGraphAdapter()


def _make_predictions(graph, citizen_id, count, correct_ratio, base_confidence=0.7):
    """Helper to create a batch of resolved predictions.

    Creates `count` predictions, with `correct_ratio` fraction correct.
    Predictions are resolved with incrementing timestamps for ordering.
    """
    correct_count = int(count * correct_ratio)
    prediction_ids = []

    for i in range(count):
        is_correct = i < correct_count
        pred_id = record_prediction(
            citizen_id=citizen_id,
            decision_context={
                "domain": "governance",
                "question": f"Should we do X_{i}?",
            },
            ai_prediction="yes" if is_correct else "yes",
            graph=graph,
            confidence=base_confidence,
            reasoning=f"Test prediction {i}",
        )
        human_actual = "yes" if is_correct else "no"
        resolve_prediction(pred_id, human_actual, graph)
        prediction_ids.append(pred_id)

    return prediction_ids


# ── Tests: record_prediction ──────────────────────────────────────────────


class TestRecordPrediction:
    """Recording cascade predictions."""

    def test_creates_node(self, graph):
        """Recording a prediction creates a node in the graph."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "governance", "question": "Should we vote yes?"},
            ai_prediction="yes",
            graph=graph,
        )
        assert pred_id in graph.nodes

    def test_node_has_correct_type(self, graph):
        """Prediction node has type 'cascade_prediction' and node_type 'moment'."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "economic", "question": "Buy or sell?"},
            ai_prediction="buy",
            graph=graph,
        )
        node = graph.nodes[pred_id]
        assert node["node_type"] == "moment"
        assert node["type"] == "cascade_prediction"

    def test_content_fields(self, graph):
        """Prediction content has all expected fields."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "social", "question": "Attend the event?"},
            ai_prediction="attend",
            graph=graph,
            confidence=0.85,
            reasoning="Pattern suggests yes",
        )
        content = graph.nodes[pred_id]["content"]
        assert content["domain"] == "social"
        assert content["question"] == "Attend the event?"
        assert content["ai_prediction"] == "attend"
        assert content["human_actual"] is None
        assert content["correct"] is None
        assert content["confidence"] == 0.85
        assert content["reasoning"] == "Pattern suggests yes"
        assert content["resolved_at"] is None

    def test_partner_relevance_is_high(self, graph):
        """Cascade predictions have high partner_relevance (0.95)."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "test", "question": "Test?"},
            ai_prediction="yes",
            graph=graph,
        )
        assert graph.nodes[pred_id]["partner_relevance"] == 0.95

    def test_invalid_confidence_raises(self, graph):
        """Confidence outside [0, 1] raises ValueError."""
        with pytest.raises(ValueError, match="Confidence"):
            record_prediction(
                citizen_id="citizen_1",
                decision_context={"domain": "test", "question": "Test?"},
                ai_prediction="yes",
                graph=graph,
                confidence=1.5,
            )

    def test_negative_confidence_raises(self, graph):
        """Negative confidence raises ValueError."""
        with pytest.raises(ValueError, match="Confidence"):
            record_prediction(
                citizen_id="citizen_1",
                decision_context={"domain": "test", "question": "Test?"},
                ai_prediction="yes",
                graph=graph,
                confidence=-0.1,
            )

    def test_missing_domain_raises(self, graph):
        """Missing domain in decision_context raises ValueError."""
        with pytest.raises(ValueError, match="domain"):
            record_prediction(
                citizen_id="citizen_1",
                decision_context={"question": "Test?"},
                ai_prediction="yes",
                graph=graph,
            )

    def test_missing_question_raises(self, graph):
        """Missing question in decision_context raises ValueError."""
        with pytest.raises(ValueError, match="question"):
            record_prediction(
                citizen_id="citizen_1",
                decision_context={"domain": "test"},
                ai_prediction="yes",
                graph=graph,
            )


# ── Tests: resolve_prediction ─────────────────────────────────────────────


class TestResolvePrediction:
    """Resolving predictions against human decisions."""

    def test_correct_prediction(self, graph):
        """Matching prediction returns True."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "test", "question": "Yes or no?"},
            ai_prediction="yes",
            graph=graph,
        )
        result = resolve_prediction(pred_id, "yes", graph)
        assert result is True

    def test_incorrect_prediction(self, graph):
        """Non-matching prediction returns False."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "test", "question": "Yes or no?"},
            ai_prediction="yes",
            graph=graph,
        )
        result = resolve_prediction(pred_id, "no", graph)
        assert result is False

    def test_case_insensitive_matching(self, graph):
        """Default matching is case-insensitive."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "test", "question": "Direction?"},
            ai_prediction="North",
            graph=graph,
        )
        result = resolve_prediction(pred_id, "north", graph)
        assert result is True

    def test_explicit_match_override(self, graph):
        """Explicit match parameter overrides string comparison."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "test", "question": "How?"},
            ai_prediction="carefully",
            graph=graph,
        )
        # Strings don't match, but we say it's a semantic match
        result = resolve_prediction(pred_id, "with great care", graph, match=True)
        assert result is True

    def test_resolution_updates_content(self, graph):
        """Resolution fills in human_actual, correct, and resolved_at."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "test", "question": "Test?"},
            ai_prediction="yes",
            graph=graph,
        )
        resolve_prediction(pred_id, "yes", graph)
        content = graph.nodes[pred_id]["content"]
        assert content["human_actual"] == "yes"
        assert content["correct"] is True
        assert content["resolved_at"] is not None

    def test_double_resolution_raises(self, graph):
        """Resolving an already-resolved prediction raises RuntimeError."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "test", "question": "Test?"},
            ai_prediction="yes",
            graph=graph,
        )
        resolve_prediction(pred_id, "yes", graph)
        with pytest.raises(RuntimeError, match="already resolved"):
            resolve_prediction(pred_id, "no", graph)

    def test_nonexistent_prediction_raises(self, graph):
        """Resolving a non-existent prediction ID raises RuntimeError."""
        with pytest.raises(RuntimeError, match="not found"):
            resolve_prediction("nonexistent_id", "yes", graph)

    def test_synthesis_updated_on_resolution(self, graph):
        """Synthesis is updated to reflect the outcome."""
        pred_id = record_prediction(
            citizen_id="citizen_1",
            decision_context={"domain": "test", "question": "Color?"},
            ai_prediction="blue",
            graph=graph,
        )
        resolve_prediction(pred_id, "red", graph)
        synthesis = graph.nodes[pred_id]["synthesis"]
        assert "incorrect" in synthesis
        assert "red" in synthesis


# ── Tests: measure_alignment_fidelity ─────────────────────────────────────


class TestMeasureAlignmentFidelity:
    """Rolling alignment fidelity calculation."""

    def test_insufficient_data_returns_none(self, graph):
        """Fewer than 20 resolved predictions returns None."""
        _make_predictions(graph, "citizen_1", count=10, correct_ratio=1.0)
        result = measure_alignment_fidelity("citizen_1", graph)
        assert result is None

    def test_exactly_minimum_predictions(self, graph):
        """Exactly 20 resolved predictions returns a score."""
        _make_predictions(graph, "citizen_1", count=20, correct_ratio=0.8)
        result = measure_alignment_fidelity("citizen_1", graph)
        assert result is not None
        assert result == pytest.approx(0.8, abs=0.05)

    def test_perfect_accuracy(self, graph):
        """All correct predictions yield 1.0."""
        _make_predictions(graph, "citizen_1", count=30, correct_ratio=1.0)
        result = measure_alignment_fidelity("citizen_1", graph)
        assert result == pytest.approx(1.0)

    def test_zero_accuracy(self, graph):
        """All incorrect predictions yield 0.0."""
        _make_predictions(graph, "citizen_1", count=30, correct_ratio=0.0)
        result = measure_alignment_fidelity("citizen_1", graph)
        assert result == pytest.approx(0.0)

    def test_mixed_accuracy(self, graph):
        """70% correct predictions yield ~0.7."""
        _make_predictions(graph, "citizen_1", count=50, correct_ratio=0.7)
        result = measure_alignment_fidelity("citizen_1", graph)
        assert result == pytest.approx(0.7, abs=0.05)

    def test_per_citizen_isolation(self, graph):
        """Alignment is computed per citizen, not globally."""
        _make_predictions(graph, "citizen_1", count=30, correct_ratio=1.0)
        _make_predictions(graph, "citizen_2", count=30, correct_ratio=0.0)
        result_1 = measure_alignment_fidelity("citizen_1", graph)
        result_2 = measure_alignment_fidelity("citizen_2", graph)
        assert result_1 == pytest.approx(1.0)
        assert result_2 == pytest.approx(0.0)

    def test_no_predictions_returns_none(self, graph):
        """No predictions at all returns None."""
        result = measure_alignment_fidelity("citizen_1", graph)
        assert result is None

    def test_unresolved_predictions_excluded(self, graph):
        """Unresolved predictions are not counted."""
        # Create 20 resolved + 10 unresolved
        _make_predictions(graph, "citizen_1", count=20, correct_ratio=1.0)
        for i in range(10):
            record_prediction(
                citizen_id="citizen_1",
                decision_context={"domain": "test", "question": f"Unresolved {i}"},
                ai_prediction="maybe",
                graph=graph,
            )
        result = measure_alignment_fidelity("citizen_1", graph)
        assert result == pytest.approx(1.0)


# ── Tests: get_cascade_status ─────────────────────────────────────────────


class TestGetCascadeStatus:
    """V8: Cascade accuracy threshold enforced."""

    def test_uncalibrated_with_no_data(self, graph):
        """No predictions -> 'uncalibrated'."""
        status = get_cascade_status("citizen_1", graph)
        assert status == "uncalibrated"

    def test_uncalibrated_with_insufficient_data(self, graph):
        """Too few predictions -> 'uncalibrated'."""
        _make_predictions(graph, "citizen_1", count=5, correct_ratio=1.0)
        status = get_cascade_status("citizen_1", graph)
        assert status == "uncalibrated"

    def test_active_above_threshold(self, graph):
        """Accuracy >= 0.80 -> 'active'."""
        _make_predictions(graph, "citizen_1", count=30, correct_ratio=0.90)
        status = get_cascade_status("citizen_1", graph)
        assert status == "active"

    def test_active_at_exact_threshold(self, graph):
        """Accuracy == 0.80 -> 'active'."""
        _make_predictions(graph, "citizen_1", count=25, correct_ratio=0.80)
        status = get_cascade_status("citizen_1", graph)
        assert status == "active"

    def test_probation_between_thresholds(self, graph):
        """Accuracy in [0.75, 0.80) -> 'probation'."""
        # 19/25 = 0.76 -> probation
        _make_predictions(graph, "citizen_1", count=25, correct_ratio=0.76)
        status = get_cascade_status("citizen_1", graph)
        assert status == "probation"

    def test_suspended_below_threshold(self, graph):
        """V8: Accuracy < 0.75 -> 'suspended'."""
        _make_predictions(graph, "citizen_1", count=30, correct_ratio=0.50)
        status = get_cascade_status("citizen_1", graph)
        assert status == "suspended"

    def test_v8_low_accuracy_forces_suspended(self, graph):
        """V8: Even with many predictions, low accuracy = suspended."""
        _make_predictions(graph, "citizen_1", count=100, correct_ratio=0.60)
        status = get_cascade_status("citizen_1", graph)
        assert status == "suspended"

    def test_perfect_accuracy_is_active(self, graph):
        """100% accuracy -> 'active'."""
        _make_predictions(graph, "citizen_1", count=50, correct_ratio=1.0)
        status = get_cascade_status("citizen_1", graph)
        assert status == "active"

    def test_transition_active_to_suspended(self, graph):
        """Adding wrong predictions can transition from active to suspended."""
        # Start with all correct -> active
        _make_predictions(graph, "citizen_1", count=25, correct_ratio=1.0)
        assert get_cascade_status("citizen_1", graph) == "active"

        # Add many incorrect predictions to overwhelm
        _make_predictions(graph, "citizen_1", count=75, correct_ratio=0.0)
        status = get_cascade_status("citizen_1", graph)
        assert status == "suspended"


# ── Tests: compute_confidence_calibration ─────────────────────────────────


class TestConfidenceCalibration:
    """Confidence-weighted accuracy analysis."""

    def test_insufficient_data_returns_none(self, graph):
        """Too few predictions returns None."""
        _make_predictions(graph, "citizen_1", count=5, correct_ratio=1.0)
        result = compute_confidence_calibration("citizen_1", graph)
        assert result is None

    def test_perfect_calibration(self, graph):
        """All correct with uniform confidence -> calibration = 1.0."""
        _make_predictions(
            graph, "citizen_1", count=30,
            correct_ratio=1.0, base_confidence=0.8,
        )
        result = compute_confidence_calibration("citizen_1", graph)
        assert result == pytest.approx(1.0)

    def test_zero_calibration(self, graph):
        """All incorrect -> calibration = 0.0."""
        _make_predictions(
            graph, "citizen_1", count=30,
            correct_ratio=0.0, base_confidence=0.8,
        )
        result = compute_confidence_calibration("citizen_1", graph)
        assert result == pytest.approx(0.0)

    def test_no_data_returns_none(self, graph):
        """No predictions returns None."""
        result = compute_confidence_calibration("citizen_1", graph)
        assert result is None
