"""
Tests for Consent Gate & Bond Validator.

Validates:
- V2: Privacy consent verified before ingestion
- V4: Consent revocation destroys content
- V6: Active bond required for ingestion
- Grant/check/revoke lifecycle for all valid streams
- Edge cases: unknown streams, missing consent, double revocation

DOCS: docs/human_integration/ALGORITHM_Human_Integration.md
      docs/human_integration/VALIDATION_Human_Integration.md
"""

import pytest

from runtime.ingestion.consent_gate_and_bond_validator import (
    VALID_STREAMS,
    check_bond_active,
    check_consent,
    grant_consent,
    revoke_consent,
)


# ── Mock Graph Adapter ────────────────────────────────────────────────────


class MockGraphAdapter:
    """In-memory graph adapter for testing consent operations."""

    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.links: list[dict] = []
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

    def query_links(self, source_id=None, target_id=None, link_type=None):
        results = []
        for link in self.links:
            if source_id and link.get("src_id") != source_id:
                continue
            if target_id and link.get("dst_id") != target_id:
                continue
            if link_type and link.get("type") != link_type:
                continue
            results.append(link)
        return results

    def _matches_filters(self, node, filters):
        for key, value in filters.items():
            if "." in key:
                # Handle nested key like "content.stream"
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


@pytest.fixture
def graph_with_bond(graph):
    """Graph with an active pairing bond for citizen_1."""
    graph.links.append({
        "src_id": "citizen_1",
        "dst_id": "human_alice",
        "type": "pairing_bond",
        "props": {"status": "active"},
    })
    return graph


# ── Tests: check_consent ──────────────────────────────────────────────────


class TestCheckConsent:
    """V2: Privacy consent verified before ingestion."""

    def test_no_consent_record_returns_false(self, graph):
        """No consent node exists — stream inactive."""
        assert check_consent("citizen_1", "voice", graph) is False

    def test_granted_consent_returns_true(self, graph):
        """Consent node with status=granted — ingestion allowed."""
        grant_consent("citizen_1", "voice", "human_alice", graph)
        assert check_consent("citizen_1", "voice", graph) is True

    def test_revoked_consent_returns_false(self, graph):
        """Consent node with status=revoked — ingestion blocked."""
        grant_consent("citizen_1", "voice", "human_alice", graph)
        revoke_consent("citizen_1", "voice", graph)
        assert check_consent("citizen_1", "voice", graph) is False

    def test_unknown_stream_raises_error(self, graph):
        """Invalid stream name must raise ValueError."""
        with pytest.raises(ValueError, match="Unknown stream"):
            check_consent("citizen_1", "invalid_stream", graph)

    def test_all_valid_streams_accepted(self, graph):
        """All six defined streams are accepted without error."""
        for stream in VALID_STREAMS:
            # Should not raise, just return False (no consent)
            result = check_consent("citizen_1", stream, graph)
            assert result is False

    def test_consent_is_per_citizen(self, graph):
        """Consent for citizen_1 does not apply to citizen_2."""
        grant_consent("citizen_1", "voice", "human_alice", graph)
        assert check_consent("citizen_1", "voice", graph) is True
        assert check_consent("citizen_2", "voice", graph) is False

    def test_consent_is_per_stream(self, graph):
        """Consent for voice does not grant consent for garmin."""
        grant_consent("citizen_1", "voice", "human_alice", graph)
        assert check_consent("citizen_1", "voice", graph) is True
        assert check_consent("citizen_1", "garmin", graph) is False


# ── Tests: grant_consent ──────────────────────────────────────────────────


class TestGrantConsent:
    """Consent node creation and re-granting."""

    def test_grant_creates_node(self, graph):
        """Granting consent creates a consent_record node."""
        node_id = grant_consent("citizen_1", "garmin", "human_alice", graph)
        assert node_id is not None
        assert node_id in graph.nodes

    def test_grant_sets_correct_fields(self, graph):
        """Consent node has correct type, weight, stability, and relevance."""
        node_id = grant_consent("citizen_1", "garmin", "human_alice", graph)
        node = graph.nodes[node_id]
        assert node["node_type"] == "thing"
        assert node["type"] == "consent_record"
        assert node["partner_relevance"] == 1.0
        assert node["weight"] == 5.0
        assert node["stability"] == 0.9

    def test_grant_content_has_stream_and_status(self, graph):
        """Consent node content has stream, status, and timestamps."""
        node_id = grant_consent("citizen_1", "desktop", "human_alice", graph)
        content = graph.nodes[node_id]["content"]
        assert content["stream"] == "desktop"
        assert content["status"] == "granted"
        assert content["granted_at"] is not None
        assert content["revoked_at"] is None
        assert content["human_id"] == "human_alice"

    def test_re_grant_updates_existing_node(self, graph):
        """Re-granting consent updates the existing node instead of creating a new one."""
        first_id = grant_consent("citizen_1", "voice", "human_alice", graph)
        revoke_consent("citizen_1", "voice", graph)
        second_id = grant_consent("citizen_1", "voice", "human_alice", graph)
        assert first_id == second_id
        content = graph.nodes[first_id]["content"]
        assert content["status"] == "granted"

    def test_grant_unknown_stream_raises(self, graph):
        """Granting consent for invalid stream raises ValueError."""
        with pytest.raises(ValueError, match="Unknown stream"):
            grant_consent("citizen_1", "invalid", "human_alice", graph)

    def test_grant_with_custom_scope(self, graph):
        """Custom scope and granularity are stored."""
        node_id = grant_consent(
            "citizen_1", "garmin", "human_alice", graph,
            scope="hr, stress, hrv",
            granularity="selected_metrics",
        )
        content = graph.nodes[node_id]["content"]
        assert content["scope"] == "hr, stress, hrv"
        assert content["granularity"] == "selected_metrics"


# ── Tests: revoke_consent ─────────────────────────────────────────────────


class TestRevokeConsent:
    """V4: Consent revocation destroys content."""

    def test_revoke_marks_consent_revoked(self, graph):
        """Revoking sets the consent node status to 'revoked'."""
        node_id = grant_consent("citizen_1", "voice", "human_alice", graph)
        revoke_consent("citizen_1", "voice", graph)
        content = graph.nodes[node_id]["content"]
        assert content["status"] == "revoked"
        assert content["revoked_at"] is not None

    def test_revoke_redacts_related_nodes(self, graph):
        """V4: All nodes from the revoked stream have content nullified."""
        grant_consent("citizen_1", "voice", "human_alice", graph)

        # Simulate partner memory nodes created from voice
        graph.create_node({
            "id": "memory_1",
            "node_type": "moment",
            "type": "partner_memory",
            "citizen_id": "citizen_1",
            "content": {"source": "voice_message", "raw_transcript": "hello"},
            "weight": 1.0,
            "energy": 0.5,
            "synthesis": "Partner said: hello",
        })
        graph.create_node({
            "id": "memory_2",
            "node_type": "moment",
            "type": "partner_memory",
            "citizen_id": "citizen_1",
            "content": {"source": "voice_message", "raw_transcript": "goodbye"},
            "weight": 1.0,
            "energy": 0.5,
            "synthesis": "Partner said: goodbye",
        })

        count = revoke_consent("citizen_1", "voice", graph)
        assert count == 2

        for nid in ["memory_1", "memory_2"]:
            node = graph.nodes[nid]
            assert node["content"] is None
            assert node["weight"] == 0.0
            assert node["energy"] == 0.0
            assert "Redacted" in node["synthesis"]

    def test_revoke_does_not_affect_other_streams(self, graph):
        """Revoking voice does not redact garmin nodes."""
        grant_consent("citizen_1", "voice", "human_alice", graph)
        grant_consent("citizen_1", "garmin", "human_alice", graph)

        graph.create_node({
            "id": "garmin_node",
            "node_type": "actor",
            "type": "partner_state",
            "citizen_id": "citizen_1",
            "content": {"source": "garmin", "metric": "heart_rate"},
            "weight": 1.0,
            "energy": 0.3,
            "synthesis": "Partner HR: 75",
        })

        revoke_consent("citizen_1", "voice", graph)
        garmin_node = graph.nodes["garmin_node"]
        assert garmin_node["content"] is not None
        assert garmin_node["weight"] == 1.0

    def test_revoke_nonexistent_consent_raises(self, graph):
        """Revoking consent that was never granted raises RuntimeError."""
        with pytest.raises(RuntimeError, match="No consent record found"):
            revoke_consent("citizen_1", "voice", graph)

    def test_revoke_returns_redacted_count(self, graph):
        """Revoke returns the number of nodes redacted."""
        grant_consent("citizen_1", "desktop", "human_alice", graph)
        count = revoke_consent("citizen_1", "desktop", graph)
        assert count == 0  # no data nodes to redact

    def test_revoke_unknown_stream_raises(self, graph):
        """Revoking an unknown stream raises ValueError."""
        with pytest.raises(ValueError, match="Unknown stream"):
            revoke_consent("citizen_1", "invalid", graph)


# ── Tests: check_bond_active ──────────────────────────────────────────────


class TestCheckBondActive:
    """V6: Active bond required for ingestion."""

    def test_no_bond_returns_false(self, graph):
        """No pairing bond link — ingestion blocked."""
        assert check_bond_active("citizen_1", graph) is False

    def test_active_bond_returns_true(self, graph_with_bond):
        """Active pairing bond — ingestion allowed."""
        assert check_bond_active("citizen_1", graph_with_bond) is True

    def test_dissolved_bond_returns_false(self, graph):
        """Bond with status != 'active' — ingestion blocked."""
        graph.links.append({
            "src_id": "citizen_1",
            "dst_id": "human_alice",
            "type": "pairing_bond",
            "props": {"status": "dissolved"},
        })
        assert check_bond_active("citizen_1", graph) is False

    def test_bond_as_target(self, graph):
        """Bond where citizen is the target, not source."""
        graph.links.append({
            "src_id": "human_alice",
            "dst_id": "citizen_1",
            "type": "pairing_bond",
            "props": {"status": "active"},
        })
        assert check_bond_active("citizen_1", graph) is True

    def test_bond_for_different_citizen(self, graph_with_bond):
        """Bond for citizen_1 does not satisfy citizen_2."""
        assert check_bond_active("citizen_2", graph_with_bond) is False

    def test_cooldown_bond_returns_false(self, graph):
        """Bond in cooldown state — ingestion blocked."""
        graph.links.append({
            "src_id": "citizen_1",
            "dst_id": "human_alice",
            "type": "pairing_bond",
            "props": {"status": "cooldown"},
        })
        assert check_bond_active("citizen_1", graph) is False
