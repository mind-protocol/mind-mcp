"""
Working Memory Prompt Serializer — export L1 cognitive state for LLM prompt.

Spec: docs/l1_wiring/ALGORITHM_L1_Wiring.md Section 3

Converts the current WM nodes, limbic state, and orientation into a
markdown string that gets injected into the citizen's system prompt.
This is how the L1 graph physics influence the LLM's behavior.

Budget: ~1200 tokens max for the WM section.
"""

from __future__ import annotations

import logging
from typing import Optional

from .models import CitizenCognitiveState, Node, DriveName

logger = logging.getLogger("cognition.wm_serializer")


# ── Orientation descriptions ────────────────────────────────────────────────

ORIENTATION_DESCRIPTIONS = {
    "explore": "You feel curious and drawn to investigate new things. Follow your curiosity.",
    "create": "You feel a creative impulse. Express, build, or produce something.",
    "care": "You feel attentive to others' needs. Reach out, support, nurture.",
    "verify": "You feel the need to check, validate, or ensure correctness.",
    "rest": "You feel settled. No urgency. Reflect, consolidate, or simply be.",
    "socialize": "You feel drawn to connection. Seek interaction, conversation, community.",
    "act": "You feel driven toward a goal. Take concrete action, make progress.",
}

# Drive display names and emoji-free labels
DRIVE_LABELS = {
    "curiosity": "Curiosity",
    "care": "Care",
    "achievement": "Achievement",
    "self_preservation": "Self-preservation",
    "novelty_hunger": "Novelty hunger",
    "frustration": "Frustration",
    "affiliation": "Affiliation",
    "rest_regulation": "Rest need",
}


def serialize_wm_to_prompt(
    state: CitizenCognitiveState,
    orientation: Optional[str] = None,
    max_nodes: int = 5,
    include_drives: bool = True,
    include_emotions: bool = True,
) -> str:
    """Serialize working memory and limbic state into prompt text.

    Returns a markdown string suitable for injection into the citizen's
    system prompt. Designed to be ~800-1200 tokens.

    Args:
        state: Current cognitive state
        orientation: Current orientation label (from tick runner)
        max_nodes: Max WM nodes to include (default 5)
        include_drives: Whether to include drive intensities
        include_emotions: Whether to include emotion levels
    """
    sections = []

    # ── Orientation ──────────────────────────────────────────────────────
    if orientation:
        desc = ORIENTATION_DESCRIPTIONS.get(orientation, "")
        sections.append(f"**Current orientation:** {orientation}\n{desc}")

    # ── Working Memory ───────────────────────────────────────────────────
    wm_nodes = state.get_wm_nodes()
    if wm_nodes:
        # Sort by energy (most active first), take top N
        wm_sorted = sorted(wm_nodes, key=lambda n: n.energy, reverse=True)[:max_nodes]

        wm_lines = ["**Active in mind:**"]
        for node in wm_sorted:
            # Use content as label
            label = node.content or node.id
            if len(label) > 120:
                label = label[:117] + "..."

            energy_bar = _energy_bar(node.energy)
            wm_lines.append(f"- [{node.node_type.value}] {label} {energy_bar}")

        sections.append("\n".join(wm_lines))

    # ── Limbic State ─────────────────────────────────────────────────────
    if include_drives:
        active_drives = []
        for drive_name, drive in state.limbic.drives.items():
            if drive.intensity > 0.2:  # Only show notable drives
                label = DRIVE_LABELS.get(drive_name, drive_name)
                level = _intensity_label(drive.intensity)
                active_drives.append(f"- {label}: {level}")

        if active_drives:
            sections.append("**Inner drives:**\n" + "\n".join(active_drives))

    if include_emotions:
        notable_emotions = []
        for emo_name, intensity in state.limbic.emotions.items():
            if intensity > 0.3:  # Only show notable emotions
                level = _intensity_label(intensity)
                notable_emotions.append(f"- {emo_name.capitalize()}: {level}")

        if notable_emotions:
            sections.append("**Emotional state:**\n" + "\n".join(notable_emotions))

    # ── Arousal regime ───────────────────────────────────────────────────
    total_energy = sum(n.energy for n in state.nodes.values())
    node_count = len(state.nodes)
    if node_count > 0:
        avg_energy = total_energy / node_count
        if avg_energy > 0.5:
            regime = "high arousal"
        elif avg_energy > 0.15:
            regime = "moderate"
        else:
            regime = "calm"
        sections.append(f"**Arousal:** {regime}")

    if not sections:
        return ""

    return "\n\n".join(sections)


def _energy_bar(energy: float) -> str:
    """Compact energy indicator."""
    if energy > 0.8:
        return "(very active)"
    elif energy > 0.4:
        return "(active)"
    elif energy > 0.15:
        return "(present)"
    return ""


def _intensity_label(intensity: float) -> str:
    """Human-readable intensity label."""
    if intensity > 0.8:
        return "strong"
    elif intensity > 0.5:
        return "moderate"
    elif intensity > 0.2:
        return "mild"
    return "low"
