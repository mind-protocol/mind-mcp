"""
Tests for L1 Stimulus Injector for Partner Data.

Validates:
- Energy levels per modality
- PartnerStimulus structure
- Edge cases: missing synthesis, missing content

DOCS: docs/human_integration/IMPLEMENTATION_Human_Integration.md
"""

import pytest

from runtime.ingestion.l1_stimulus_injector_for_partner_data import (
    MODALITY_ENERGY,
    PartnerStimulus,
    inject_partner_stimulus,
)


def _make_node(source="voice_message", synthesis="Test synthesis", **overrides):
    """Helper to create a minimal partner node dict."""
    node = {
        "id": "test_node_1",
        "content": {"source": source},
        "synthesis": synthesis,
        "modality": source,
        "partner_relevance": 0.85,
    }
    node.update(overrides)
    return node


class TestInjectPartnerStimulus:
    """L1 stimulus creation from partner nodes."""

    def test_returns_partner_stimulus(self):
        """Injection returns a PartnerStimulus object."""
        node = _make_node()
        stim = inject_partner_stimulus("citizen_1", node)
        assert isinstance(stim, PartnerStimulus)

    def test_voice_energy_level(self):
        """Voice messages use high energy (0.5)."""
        node = _make_node(source="voice_message")
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.energy_budget == pytest.approx(0.5)

    def test_garmin_energy_level(self):
        """Garmin data uses low energy (0.2)."""
        node = _make_node(source="garmin")
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.energy_budget == pytest.approx(0.2)

    def test_desktop_energy_level(self):
        """Desktop screenshots use lowest energy (0.15)."""
        node = _make_node(source="desktop_screenshot")
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.energy_budget == pytest.approx(0.15)

    def test_blockchain_energy_level(self):
        """Blockchain data uses moderate energy (0.3)."""
        node = _make_node(source="blockchain")
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.energy_budget == pytest.approx(0.3)

    def test_direct_chat_energy_level(self):
        """Direct chat uses conversational energy (0.4)."""
        node = _make_node(source="direct_chat")
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.energy_budget == pytest.approx(0.4)

    def test_energy_override(self):
        """Explicit energy parameter overrides modality default."""
        node = _make_node(source="garmin")
        stim = inject_partner_stimulus("citizen_1", node, energy=0.9)
        assert stim.energy_budget == pytest.approx(0.9)

    def test_stimulus_carries_node_id(self):
        """Stimulus references the partner node that spawned it."""
        node = _make_node()
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.node_id == "test_node_1"

    def test_stimulus_is_social(self):
        """Partner stimuli are always marked as social."""
        node = _make_node()
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.is_social is True

    def test_stimulus_is_novelty(self):
        """Partner stimuli are marked as novelty (fresh external input)."""
        node = _make_node()
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.is_novelty is True

    def test_stimulus_source_is_partner(self):
        """Stimulus source is 'partner'."""
        node = _make_node()
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.source == "partner"

    def test_stimulus_content_is_synthesis(self):
        """Stimulus content comes from the node's synthesis field."""
        node = _make_node(synthesis="Partner said: hello world")
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.content == "Partner said: hello world"

    def test_missing_synthesis_raises(self):
        """Node without synthesis raises ValueError."""
        node = _make_node(synthesis=None)
        with pytest.raises(ValueError, match="synthesis"):
            inject_partner_stimulus("citizen_1", node)

    def test_empty_synthesis_raises(self):
        """Node with empty synthesis raises ValueError."""
        node = _make_node(synthesis="")
        with pytest.raises(ValueError, match="synthesis"):
            inject_partner_stimulus("citizen_1", node)

    def test_missing_content_raises(self):
        """Node without content raises ValueError."""
        node = {"id": "x", "synthesis": "test", "modality": "voice_message"}
        node["content"] = None
        with pytest.raises(ValueError, match="content"):
            inject_partner_stimulus("citizen_1", node)

    def test_unknown_modality_default_energy(self):
        """Unknown modality gets default energy of 0.3."""
        node = _make_node(source="unknown_source")
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.energy_budget == pytest.approx(0.3)

    def test_partner_relevance_carried(self):
        """Partner relevance from the node is carried on the stimulus."""
        node = _make_node()
        node["partner_relevance"] = 0.92
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.partner_relevance == pytest.approx(0.92)

    def test_target_node_ids_set(self):
        """Target node IDs includes the partner node's ID."""
        node = _make_node()
        stim = inject_partner_stimulus("citizen_1", node)
        assert stim.target_node_ids == ["test_node_1"]
