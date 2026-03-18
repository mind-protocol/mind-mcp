"""
Two-Tick Cognitive Engine — Awareness + Thought-Speed Processing

Spec: docs/cognition/l1/ALGORITHM_L1_Physics.md

Two independent tick loops run at different rates:

1. **Awareness Tick** (slow, variable rate)
   Scans external graph via a provided read function, imports new/updated
   nodes into the citizen's L1 cognitive state.  Energy for imported nodes
   is computed as: external_energy * novelty * valence * relevance.
   Duplicates are skipped; existing nodes are updated only if external
   energy grew since last import.

2. **Thought-Speed Tick** (fast, variable rate)
   Internal cognitive processing:
   - Excess energy generation on active nodes (weight-scaled)
   - Bidirectional energy dispersal through links (sqrt(weight) reception)
   - Energy decay
   - Hebbian crystallization of co-active WM pairs + new link creation
   - Periodic forgetting (dissolves weak links)
   - Conscious action firing when mean WM energy > threshold (with cooldown)

Working Memory (WM) = top 7 active nodes by energy (emergent, not hardcoded).

Co-Authored-By: Dev (@dev) <dev@mindprotocol.ai>
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field
from itertools import combinations
from typing import Callable, Optional

from .models import (
    CitizenCognitiveState,
    Link,
    LinkType,
    Node,
    NodeType,
)

logger = logging.getLogger("cognition.two_tick_engine")

# =========================================================================
# Constants
# =========================================================================

# Awareness tick
AWARENESS_ENERGY_MIN = 0.05        # floor for imported node energy
NOVELTY_BOOST_NEW = 1.0            # novelty multiplier for brand-new nodes
NOVELTY_BOOST_KNOWN = 0.3          # novelty multiplier for already-known nodes
DEFAULT_VALENCE = 0.5              # neutral valence when not provided
DEFAULT_RELEVANCE = 0.5            # base relevance when not computable

# Thought-speed tick
EXCESS_ENERGY_RATE = 0.08          # fraction of weight added as excess energy
DISPERSAL_FRACTION = 0.3           # fraction of excess energy that disperses
ENERGY_DECAY_RATE = 0.02           # per-tick multiplicative decay
HEBB_LEARNING_RATE = 0.05          # weight delta for co-active WM pairs
NEW_LINK_INITIAL_WEIGHT = 0.05     # weight for newly crystallized links
FORGETTING_PERIOD = 100            # ticks between forgetting passes
FORGETTING_WEIGHT_THRESHOLD = 0.005  # links below this dissolve
CONSCIOUS_ACTION_THRESHOLD = 0.3   # mean WM energy to fire action
ACTION_COOLDOWN_TICKS = 3          # minimum ticks between actions

# WM
WM_SIZE = 7                        # emergent WM capacity


# =========================================================================
# Result Dataclasses
# =========================================================================

@dataclass
class AwarenessTickResult:
    """Output of a single awareness tick."""
    tick: int = 0
    nodes_imported: int = 0
    nodes_updated: int = 0
    nodes_skipped: int = 0
    total_energy_imported: float = 0.0
    clusters_scanned: int = 0
    duration_ms: float = 0.0


@dataclass
class ThoughtTickResult:
    """Output of a single thought-speed tick."""
    tick: int = 0
    wm_ids: list[str] = field(default_factory=list)
    wm_changed: bool = False
    excess_energy_generated: float = 0.0
    energy_dispersed: float = 0.0
    energy_decayed: float = 0.0
    links_crystallized: int = 0
    links_created: int = 0
    links_dissolved: int = 0
    action_fired: bool = False
    action_node_id: Optional[str] = None
    mean_wm_energy: float = 0.0
    duration_ms: float = 0.0


# =========================================================================
# Awareness Tick
# =========================================================================

def awareness_tick(
    state: CitizenCognitiveState,
    graph_read_fn: Callable[[str], list[dict]],
    tick: int,
) -> AwarenessTickResult:
    """Scan external graph and import/update nodes into L1 state.

    Args:
        state: The citizen's cognitive state (mutated in place).
        graph_read_fn: Callable that takes citizen_id and returns a list
            of cluster dicts: [{"node": {...}, "links": [...]}, ...].
            Each node dict must have at least "id", "energy".
            Optional fields: "content", "node_type", "weight",
            "valence", "relevance", "stability".
        tick: Current tick number.

    Returns:
        AwarenessTickResult with import statistics.
    """
    t0 = time.monotonic()
    result = AwarenessTickResult(tick=tick)

    try:
        clusters = graph_read_fn(state.citizen_id)
    except Exception as e:
        logger.warning(f"Awareness scan failed for {state.citizen_id}: {e}")
        result.duration_ms = (time.monotonic() - t0) * 1000
        return result

    if not clusters:
        result.duration_ms = (time.monotonic() - t0) * 1000
        return result

    result.clusters_scanned = len(clusters)

    for cluster in clusters:
        ext_node = cluster.get("node", {})
        ext_links = cluster.get("links", [])

        ext_id = ext_node.get("id")
        if not ext_id:
            continue

        ext_energy = float(ext_node.get("energy", 0.0))
        ext_valence = float(ext_node.get("valence", DEFAULT_VALENCE))
        ext_relevance = float(ext_node.get("relevance", DEFAULT_RELEVANCE))

        # Clamp valence to [0, 1] for the energy formula (negative valence
        # still imports but with reduced energy)
        valence_factor = max(0.0, min(1.0, (ext_valence + 1.0) / 2.0))
        relevance_factor = max(0.0, min(1.0, ext_relevance))

        existing = state.nodes.get(ext_id)

        if existing is not None:
            # Node already in L1 -- update only if external energy grew
            novelty = NOVELTY_BOOST_KNOWN
            import_energy = (
                ext_energy * novelty * valence_factor * relevance_factor
            )
            import_energy = max(import_energy, AWARENESS_ENERGY_MIN)

            if ext_energy > existing.energy:
                delta = import_energy - existing.energy
                if delta > 0:
                    existing.energy = import_energy
                    existing.last_activated_at = time.time()
                    existing.activation_count += 1
                    result.nodes_updated += 1
                    result.total_energy_imported += delta
                else:
                    result.nodes_skipped += 1
            else:
                result.nodes_skipped += 1
        else:
            # Brand new node -- import into L1
            novelty = NOVELTY_BOOST_NEW
            import_energy = (
                ext_energy * novelty * valence_factor * relevance_factor
            )
            import_energy = max(import_energy, AWARENESS_ENERGY_MIN)

            # Resolve node type
            nt_str = ext_node.get("node_type", "concept")
            try:
                node_type = NodeType(nt_str)
            except ValueError:
                node_type = NodeType.CONCEPT

            new_node = Node(
                id=ext_id,
                node_type=node_type,
                content=ext_node.get("content", ext_id),
                energy=import_energy,
                weight=float(ext_node.get("weight", 0.1)),
                stability=float(ext_node.get("stability", 0.0)),
                origin_citizen=ext_node.get("origin_citizen", ""),
            )
            new_node.last_activated_at = time.time()
            new_node.activation_count = 1
            state.add_node(new_node)

            result.nodes_imported += 1
            result.total_energy_imported += import_energy

            # Import links from this cluster that connect to existing nodes
            for ext_link in ext_links:
                src = ext_link.get("source_id", "")
                tgt = ext_link.get("target_id", "")
                if not src or not tgt:
                    continue
                # Only create link if both endpoints exist in L1
                if src in state.nodes and tgt in state.nodes:
                    # Avoid duplicate links
                    exists = any(
                        l.source_id == src and l.target_id == tgt
                        for l in state.links
                    )
                    if not exists:
                        lt_str = ext_link.get("link_type", "associates")
                        try:
                            link_type = LinkType(lt_str)
                        except ValueError:
                            link_type = LinkType.ASSOCIATES

                        new_link = Link(
                            source_id=src,
                            target_id=tgt,
                            link_type=link_type,
                            weight=float(ext_link.get("weight", 0.1)),
                        )
                        state.add_link(new_link)

    result.duration_ms = (time.monotonic() - t0) * 1000
    logger.debug(
        f"Awareness tick #{tick} for {state.citizen_id}: "
        f"{result.nodes_imported} imported, {result.nodes_updated} updated, "
        f"{result.nodes_skipped} skipped ({result.duration_ms:.1f}ms)"
    )
    return result


# =========================================================================
# TwoTickEngine — Stateful wrapper used by the dispatcher
# =========================================================================

class TwoTickEngine:
    """Stateful wrapper around awareness_tick() and thought_tick().

    Holds the citizen's cognitive state, tick counters, and an optional
    graph_read_fn.  The dispatcher creates one instance per citizen and
    calls .awareness_tick() / .thought_tick() on the background loop.
    """

    def __init__(
        self,
        state: CitizenCognitiveState,
        graph_read_fn: Optional[Callable[[str], list[dict]]] = None,
    ):
        self.state = state
        self.graph_read_fn = graph_read_fn
        self._awareness_tick_counter: int = 0
        self._thought_tick_counter: int = 0
        self._last_action_tick: int = 0
        self._current_orientation: Optional[str] = None

    # -- Awareness tick (slow: scan external graph) -----------------------

    def awareness_tick(self) -> AwarenessTickResult:
        """Run one awareness tick.  Returns AwarenessTickResult."""
        self._awareness_tick_counter += 1
        if self.graph_read_fn is None:
            # No graph reader — return empty result
            return AwarenessTickResult(tick=self._awareness_tick_counter)
        return awareness_tick(
            self.state,
            self.graph_read_fn,
            self._awareness_tick_counter,
        )

    # -- Thought tick (fast: internal cognitive processing) ----------------

    def thought_tick(self) -> ThoughtTickResult:
        """Run one thought-speed tick.  Returns ThoughtTickResult."""
        self._thought_tick_counter += 1
        result = thought_tick(
            self.state,
            self._thought_tick_counter,
            last_action_tick=self._last_action_tick,
        )
        if result.action_fired:
            self._last_action_tick = self._thought_tick_counter
        # Derive orientation from dominant drive
        self._current_orientation = self._derive_orientation()
        return result

    # -- Helpers -----------------------------------------------------------

    def _derive_orientation(self) -> str:
        """Derive behavioral orientation from the current limbic state."""
        limbic = self.state.limbic
        best_drive = "explore"
        best_intensity = 0.0

        _DRIVE_TO_ORIENTATION = {
            "curiosity": "explore",
            "care": "care",
            "achievement": "act",
            "self_preservation": "verify",
            "novelty_hunger": "explore",
            "frustration": "escalate",
            "affiliation": "socialize",
            "rest_regulation": "rest",
        }

        for drive_name, drive in limbic.drives.items():
            if drive.intensity > best_intensity:
                best_intensity = drive.intensity
                best_drive = _DRIVE_TO_ORIENTATION.get(drive_name, "explore")

        return best_drive


# =========================================================================
# Thought-Speed Tick
# =========================================================================

def thought_tick(
    state: CitizenCognitiveState,
    tick: int,
    last_action_tick: int = 0,
) -> ThoughtTickResult:
    """Execute one thought-speed tick of internal cognitive processing.

    Args:
        state: The citizen's cognitive state (mutated in place).
        tick: Current tick number.
        last_action_tick: Tick number when the last conscious action fired
            (used for cooldown gating).

    Returns:
        ThoughtTickResult with processing statistics.
    """
    t0 = time.monotonic()
    result = ThoughtTickResult(tick=tick)

    # Snapshot previous WM for change detection
    prev_wm_ids = list(state.wm.node_ids)

    # ------------------------------------------------------------------
    # Step 1: Excess energy generation on active nodes (weight-scaled)
    # ------------------------------------------------------------------
    for node in state.nodes.values():
        if node.energy > 0.0:
            excess = EXCESS_ENERGY_RATE * node.weight
            node.energy += excess
            result.excess_energy_generated += excess

    # ------------------------------------------------------------------
    # Step 2: Bidirectional energy dispersal through links
    #
    # Each link disperses energy in both directions.
    # Reception is modulated by sqrt(weight) of the receiving node.
    # ------------------------------------------------------------------
    # Build adjacency for efficiency
    link_index: dict[str, list[Link]] = {}
    for link in state.links:
        link_index.setdefault(link.source_id, []).append(link)
        link_index.setdefault(link.target_id, []).append(link)

    dispersal_buffer: dict[str, float] = {}

    for node in state.nodes.values():
        if node.energy <= 0.0:
            continue
        dispersal_amount = node.energy * DISPERSAL_FRACTION
        if dispersal_amount < 0.001:
            continue

        connected_links = link_index.get(node.id, [])
        if not connected_links:
            continue

        # Compute total affinity for normalization
        total_affinity = 0.0
        neighbors: list[tuple[str, float]] = []
        for link in connected_links:
            neighbor_id = (
                link.target_id if link.source_id == node.id
                else link.source_id
            )
            neighbor = state.nodes.get(neighbor_id)
            if neighbor is None:
                continue
            # Reception scaled by sqrt(weight) of receiving node
            reception = math.sqrt(max(neighbor.weight, 0.01))
            affinity = link.weight * reception * (1.0 - link.friction)
            if affinity > 0:
                neighbors.append((neighbor_id, affinity))
                total_affinity += affinity

        if total_affinity == 0.0:
            continue

        # Distribute dispersal proportionally
        for neighbor_id, affinity in neighbors:
            share = (affinity / total_affinity) * dispersal_amount
            dispersal_buffer[neighbor_id] = (
                dispersal_buffer.get(neighbor_id, 0.0) + share
            )

        # Drain source
        node.energy -= dispersal_amount
        if node.energy < 0.0:
            node.energy = 0.0
        result.energy_dispersed += dispersal_amount

    # Apply incoming energy
    for node_id, incoming in dispersal_buffer.items():
        node = state.nodes.get(node_id)
        if node is not None:
            node.energy += incoming

    # ------------------------------------------------------------------
    # Step 3: Energy decay
    # ------------------------------------------------------------------
    for node in state.nodes.values():
        if node.energy > 0.0:
            decay = node.energy * ENERGY_DECAY_RATE
            node.energy -= decay
            if node.energy < 0.0:
                node.energy = 0.0
            result.energy_decayed += decay

    # ------------------------------------------------------------------
    # Step 4: WM selection — top N nodes by energy (emergent)
    # ------------------------------------------------------------------
    active_nodes = sorted(
        state.nodes.values(),
        key=lambda n: n.energy,
        reverse=True,
    )
    new_wm_ids = [n.id for n in active_nodes[:WM_SIZE] if n.energy > 0.0]

    # Update WM
    old_wm_set = set(prev_wm_ids)
    new_wm_set = set(new_wm_ids)

    # Clear old WM flags
    for nid in old_wm_set - new_wm_set:
        node = state.nodes.get(nid)
        if node:
            node.in_working_memory = False

    # Set new WM flags
    for nid in new_wm_set:
        node = state.nodes.get(nid)
        if node:
            node.in_working_memory = True

    state.wm.node_ids = new_wm_ids
    result.wm_ids = list(new_wm_ids)
    result.wm_changed = new_wm_set != old_wm_set

    if result.wm_changed:
        state.wm.stability_ticks = 0
    else:
        state.wm.stability_ticks += 1

    # ------------------------------------------------------------------
    # Step 5: Hebbian crystallization of co-active WM pairs
    #
    # Strengthen existing links between WM pairs.
    # Create new ASSOCIATES links between unconnected WM nodes.
    # ------------------------------------------------------------------
    wm_nodes = [state.nodes[nid] for nid in new_wm_ids if nid in state.nodes]

    if len(wm_nodes) >= 2:
        # Build a fast link lookup set
        existing_pairs: set[tuple[str, str]] = set()
        link_map: dict[tuple[str, str], list[Link]] = {}
        for link in state.links:
            pair_fwd = (link.source_id, link.target_id)
            pair_rev = (link.target_id, link.source_id)
            existing_pairs.add(pair_fwd)
            existing_pairs.add(pair_rev)
            link_map.setdefault(pair_fwd, []).append(link)
            link_map.setdefault(pair_rev, []).append(link)

        now = time.time()
        for node_a, node_b in combinations(wm_nodes, 2):
            if node_a.energy < 0.01 or node_b.energy < 0.01:
                continue

            pair = (node_a.id, node_b.id)
            pair_rev = (node_b.id, node_a.id)

            # Hebb: weight += LEARNING_RATE * min(energy_a, energy_b)
            coact_signal = min(node_a.energy, node_b.energy)
            delta = HEBB_LEARNING_RATE * coact_signal

            # Check for existing links in either direction
            links_fwd = link_map.get(pair, [])
            links_rev = link_map.get(pair_rev, [])
            all_links = links_fwd + links_rev

            if all_links:
                # Strengthen existing
                for link in all_links:
                    link.weight += delta
                    link.co_activation_count += 1
                    link.last_co_activated_at = now
                result.links_crystallized += len(all_links)
            else:
                # Create new link between unconnected WM nodes
                new_link = Link(
                    source_id=node_a.id,
                    target_id=node_b.id,
                    link_type=LinkType.ASSOCIATES,
                    weight=NEW_LINK_INITIAL_WEIGHT,
                    co_activation_count=1,
                    last_co_activated_at=now,
                )
                state.add_link(new_link)
                # Update lookup for remaining pairs in this tick
                existing_pairs.add(pair)
                existing_pairs.add(pair_rev)
                link_map.setdefault(pair, []).append(new_link)
                link_map.setdefault(pair_rev, []).append(new_link)
                result.links_created += 1

    # ------------------------------------------------------------------
    # Step 6: Periodic forgetting — dissolve weak links
    # ------------------------------------------------------------------
    if tick > 0 and tick % FORGETTING_PERIOD == 0:
        to_remove: list[Link] = []
        for link in state.links:
            if link.weight < FORGETTING_WEIGHT_THRESHOLD and not link.is_structural:
                to_remove.append(link)
        for link in to_remove:
            state.remove_link(link)
        result.links_dissolved = len(to_remove)

    # ------------------------------------------------------------------
    # Step 7: Conscious action firing
    #
    # When mean WM energy > threshold AND cooldown has elapsed,
    # fire the highest-energy action-capable process node in WM.
    # ------------------------------------------------------------------
    if wm_nodes:
        mean_energy = sum(n.energy for n in wm_nodes) / len(wm_nodes)
        result.mean_wm_energy = mean_energy

        cooldown_ok = (tick - last_action_tick) >= ACTION_COOLDOWN_TICKS

        if mean_energy > CONSCIOUS_ACTION_THRESHOLD and cooldown_ok:
            # Find the best action node in WM
            action_candidates = [
                n for n in wm_nodes
                if n.node_type == NodeType.PROCESS and n.is_action_node
            ]
            if action_candidates:
                best = max(action_candidates, key=lambda n: n.energy)
                result.action_fired = True
                result.action_node_id = best.id

    # Update tick count
    state.tick_count = tick

    result.duration_ms = (time.monotonic() - t0) * 1000
    logger.debug(
        f"Thought tick #{tick} for {state.citizen_id}: "
        f"WM=[{', '.join(result.wm_ids[:3])}...] "
        f"changed={result.wm_changed} "
        f"action={result.action_fired} "
        f"({result.duration_ms:.1f}ms)"
    )
    return result
