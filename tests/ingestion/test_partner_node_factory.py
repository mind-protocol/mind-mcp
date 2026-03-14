"""
Tests for Partner Node Factory & Relevance Scorer.

Validates:
- V1: All partner nodes have partner_relevance >= 0.7
- V3: Only approved human sources can create partner nodes
- self_relevance clamped to <= 0.3 for partner data
- Relevance scoring by modality and content modifiers
- Node structure correctness

DOCS: docs/human_integration/ALGORITHM_Human_Integration.md
      docs/human_integration/VALIDATION_Human_Integration.md
"""

import pytest

from runtime.ingestion.partner_node_factory_and_relevance_scorer import (
    APPROVED_HUMAN_SOURCES,
    BASE_SCORES,
    MAX_SELF_RELEVANCE,
    MIN_PARTNER_RELEVANCE,
    create_partner_node,
    score_relevance,
)


# ── Tests: score_relevance ────────────────────────────────────────────────


class TestScoreRelevance:
    """ALGORITHM: score_partner_relevance."""

    def test_base_scores_for_all_modalities(self):
        """Each modality returns its expected base score."""
        for modality, expected in BASE_SCORES.items():
            score = score_relevance(modality)
            assert score == expected, (
                f"Modality '{modality}' expected {expected}, got {score}"
            )

    def test_unknown_modality_gets_minimum(self):
        """Unknown modality returns MIN_PARTNER_RELEVANCE (0.7)."""
        score = score_relevance("unknown_source")
        assert score == MIN_PARTNER_RELEVANCE

    def test_all_scores_at_least_minimum(self):
        """No modality returns a score below 0.7."""
        for modality in BASE_SCORES:
            score = score_relevance(modality)
            assert score >= MIN_PARTNER_RELEVANCE

    def test_all_scores_at_most_one(self):
        """No modality returns a score above 1.0."""
        for modality in BASE_SCORES:
            score = score_relevance(modality)
            assert score <= 1.0

    def test_emotional_content_boosts_score(self):
        """High emotion scores increase relevance."""
        base = score_relevance("direct_chat")
        boosted = score_relevance("direct_chat", {
            "emotion_scores": {"sadness": 0.9, "joy": 0.1},
        })
        assert boosted > base
        assert boosted == pytest.approx(base + 0.10, abs=0.01)

    def test_moderate_emotion_smaller_boost(self):
        """Moderate emotion (0.5 < max <= 0.8) gives smaller boost."""
        base = score_relevance("direct_chat")
        boosted = score_relevance("direct_chat", {
            "emotion_scores": {"anxiety": 0.6},
        })
        assert boosted > base
        assert boosted == pytest.approx(base + 0.05, abs=0.01)

    def test_low_emotion_no_boost(self):
        """Emotion below 0.5 gives no boost."""
        base = score_relevance("direct_chat")
        same = score_relevance("direct_chat", {
            "emotion_scores": {"anxiety": 0.3},
        })
        assert same == base

    def test_self_reference_boosts_score(self):
        """Self-referential language increases relevance."""
        base = score_relevance("direct_chat")
        boosted = score_relevance("direct_chat", {
            "text": "I feel overwhelmed today",
        })
        assert boosted > base

    def test_decision_language_boosts_score(self):
        """Decision language increases relevance."""
        base = score_relevance("direct_chat")
        boosted = score_relevance("direct_chat", {
            "text": "I decided to quit my job",
        })
        assert boosted > base

    def test_distress_markers_boost_score(self):
        """Distress markers increase relevance."""
        base = score_relevance("direct_chat")
        boosted = score_relevance("direct_chat", {
            "text": "I'm scared and can't cope",
        })
        assert boosted > base

    def test_score_clamped_at_one(self):
        """Even with all modifiers stacked, score never exceeds 1.0."""
        score = score_relevance("voice_message", {
            "text": "I feel scared, I decided I believe I can't cope",
            "emotion_scores": {"fear": 0.95, "anxiety": 0.9},
        })
        assert score <= 1.0

    def test_score_clamped_at_minimum(self):
        """Score never drops below 0.7 regardless of input."""
        score = score_relevance("unknown_source", {})
        assert score >= MIN_PARTNER_RELEVANCE

    def test_empty_signals_no_crash(self):
        """Empty content_signals dict does not crash."""
        score = score_relevance("voice_message", {})
        assert score == BASE_SCORES["voice_message"]

    def test_none_signals_returns_base(self):
        """None content_signals returns base score."""
        score = score_relevance("voice_message", None)
        assert score == BASE_SCORES["voice_message"]


# ── Tests: create_partner_node ────────────────────────────────────────────


class TestCreatePartnerNode:
    """Node factory — creates correctly structured partner model nodes."""

    def test_creates_node_with_required_fields(self):
        """Node dict has all required fields."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="moment",
            type_label="partner_memory",
            content={"source": "voice_message", "raw_transcript": "hello world"},
            modality="voice_message",
        )
        assert "id" in node
        assert node["node_type"] == "moment"
        assert node["type"] == "partner_memory"
        assert node["citizen_id"] == "citizen_1"
        assert node["content"]["source"] == "voice_message"
        assert node["modality"] == "voice_message"
        assert "synthesis" in node
        assert "created_at" in node

    def test_v1_partner_relevance_at_least_minimum(self):
        """V1: partner_relevance is always >= 0.7."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="moment",
            type_label="partner_memory",
            content={"source": "voice_message", "raw_transcript": "hi"},
            modality="voice_message",
        )
        assert node["partner_relevance"] >= MIN_PARTNER_RELEVANCE

    def test_v1_explicit_relevance_below_minimum_raises(self):
        """V1: Explicitly setting partner_relevance < 0.7 raises ValueError."""
        with pytest.raises(ValueError, match="below minimum"):
            create_partner_node(
                citizen_id="citizen_1",
                node_type="moment",
                type_label="partner_memory",
                content={"source": "voice_message", "raw_transcript": "hi"},
                modality="voice_message",
                partner_relevance=0.5,
            )

    def test_self_relevance_clamped(self):
        """Self_relevance is clamped to MAX_SELF_RELEVANCE (0.3)."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="moment",
            type_label="partner_memory",
            content={"source": "voice_message", "raw_transcript": "hi"},
            modality="voice_message",
            self_relevance=0.9,
        )
        assert node["self_relevance"] <= MAX_SELF_RELEVANCE

    def test_self_relevance_below_max_preserved(self):
        """Self_relevance below the max is preserved as-is."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="moment",
            type_label="partner_memory",
            content={"source": "voice_message", "raw_transcript": "hi"},
            modality="voice_message",
            self_relevance=0.1,
        )
        assert node["self_relevance"] == 0.1

    def test_v3_unapproved_source_raises(self):
        """V3: Creating a node from an unapproved source raises ValueError."""
        with pytest.raises(ValueError, match="not an approved human data source"):
            create_partner_node(
                citizen_id="citizen_1",
                node_type="moment",
                type_label="partner_memory",
                content={"source": "ai_introspection", "text": "I think..."},
                modality="ai_introspection",
            )

    def test_invalid_node_type_raises(self):
        """Invalid node_type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid node_type"):
            create_partner_node(
                citizen_id="citizen_1",
                node_type="invalid_type",
                type_label="partner_memory",
                content={"source": "voice_message"},
                modality="voice_message",
            )

    def test_explicit_partner_relevance_used(self):
        """Explicit partner_relevance overrides auto-scoring."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="moment",
            type_label="partner_memory",
            content={"source": "voice_message", "raw_transcript": "hi"},
            modality="voice_message",
            partner_relevance=0.95,
        )
        assert node["partner_relevance"] == 0.95

    def test_auto_synthesis_for_memory(self):
        """Auto-generated synthesis for partner_memory includes transcript."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="moment",
            type_label="partner_memory",
            content={"source": "voice_message", "raw_transcript": "I am happy"},
            modality="voice_message",
        )
        assert "Partner said" in node["synthesis"]
        assert "I am happy" in node["synthesis"]

    def test_auto_synthesis_for_state(self):
        """Auto-generated synthesis for partner_state includes metric."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="actor",
            type_label="partner_state",
            content={"source": "garmin", "metric": "heart_rate", "value": 85},
            modality="garmin",
        )
        assert "heart_rate" in node["synthesis"]

    def test_auto_synthesis_for_transaction(self):
        """Auto-generated synthesis for partner_transaction includes direction."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="moment",
            type_label="partner_transaction",
            content={
                "source": "blockchain",
                "direction": "sent",
                "amount": 100,
                "token": "MIND",
            },
            modality="blockchain",
        )
        assert "sent" in node["synthesis"]
        assert "MIND" in node["synthesis"]

    def test_custom_synthesis_used(self):
        """Explicit synthesis string overrides auto-generation."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="moment",
            type_label="partner_memory",
            content={"source": "voice_message", "raw_transcript": "hi"},
            modality="voice_message",
            synthesis="Custom synthesis text",
        )
        assert node["synthesis"] == "Custom synthesis text"

    def test_node_id_contains_type_label(self):
        """Generated ID includes the type_label prefix."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="moment",
            type_label="partner_memory",
            content={"source": "voice_message", "raw_transcript": "hi"},
            modality="voice_message",
        )
        assert node["id"].startswith("partner_memory_")

    def test_all_approved_sources_accepted(self):
        """All approved human sources can create nodes without error."""
        type_map = {
            "voice_message": ("moment", "partner_memory"),
            "voice_emotion": ("actor", "partner_state"),
            "direct_chat": ("moment", "partner_memory"),
            "ai_conversation": ("moment", "partner_memory"),
            "garmin": ("actor", "partner_state"),
            "desktop_screenshot": ("thing", "partner_concept"),
            "blockchain": ("moment", "partner_transaction"),
        }
        for source, (ntype, tlabel) in type_map.items():
            node = create_partner_node(
                citizen_id="citizen_1",
                node_type=ntype,
                type_label=tlabel,
                content={"source": source},
                modality=source,
            )
            assert node["partner_relevance"] >= MIN_PARTNER_RELEVANCE

    def test_care_affinity_stored(self):
        """care_affinity dimension is stored on the node."""
        node = create_partner_node(
            citizen_id="citizen_1",
            node_type="moment",
            type_label="partner_memory",
            content={"source": "voice_message", "raw_transcript": "hi"},
            modality="voice_message",
            care_affinity=0.8,
        )
        assert node["care_affinity"] == 0.8
