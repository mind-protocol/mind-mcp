"""
Exteroception — External Sensory Awareness

DOCS: docs/cognition/exteroception/

The citizen's awareness of their WORLD — Spaces, Narratives, Moments,
Things, and Actors around them. Two outputs:

1. Stimuli (per tick) → Law 1 injection
2. Awareness text (periodic) → system prompt layer

Selection is state-biased:
  relevance = base × limbic_bias × goal_alignment × habituation

Runs once per tick, BEFORE interoception, BEFORE Law 1 inject.

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional, Callable

from .tick_runner_l1_cognitive_engine import Stimulus

logger = logging.getLogger("cognition.exteroception")

MAX_STIMULI_PER_TICK = 3
EXTERO_SOURCE = "external"
SCAN_WINDOW_S = 300.0  # 5 min scan window for moments
AWARENESS_REFRESH_TICKS = 10  # regenerate awareness text every N ticks


@dataclass
class SensoryChannel:
    name: str
    priority: int
    refractory_ticks: int
    last_fired_tick: int = -999
    is_armed: bool = True

    def can_fire(self, tick: int) -> bool:
        return self.is_armed and (tick - self.last_fired_tick >= self.refractory_ticks)

    def fire(self, tick: int):
        self.is_armed = False
        self.last_fired_tick = tick

    def try_rearm(self, tick: int):
        if not self.is_armed and (tick - self.last_fired_tick >= self.refractory_ticks):
            self.is_armed = True


@dataclass
class PerceivedNode:
    """A node from L3 as perceived by the citizen."""
    id: str
    name: str
    node_type: str  # actor, space, moment, narrative, thing
    synthesis: str
    weight: float = 0.0
    energy: float = 0.0
    relevance: float = 0.0  # computed score


class ExteroceptionEngine:
    """Scans L3 and produces stimuli + awareness text."""

    def __init__(self):
        self.channels = {
            "new_message":     SensoryChannel("new_message",     priority=80, refractory_ticks=2),
            "new_mention":     SensoryChannel("new_mention",     priority=90, refractory_ticks=1),
            "narrative_shift": SensoryChannel("narrative_shift",  priority=60, refractory_ticks=15),
            "new_thing":       SensoryChannel("new_thing",        priority=40, refractory_ticks=20),
            "actor_nearby":    SensoryChannel("actor_nearby",     priority=50, refractory_ticks=10),
            "space_atmosphere": SensoryChannel("space_atmosphere", priority=30, refractory_ticks=30),
        }
        self._seen_ids: set = set()
        self._habituation: dict[str, int] = {}  # node_id → times_seen
        self._awareness_text: str = ""
        self._awareness_tick: int = -999

        # Perceived environment (refreshed periodically)
        self._my_spaces: list[PerceivedNode] = []
        self._nearby_actors: list[PerceivedNode] = []
        self._active_narratives: list[PerceivedNode] = []
        self._recent_moments: list[PerceivedNode] = []
        self._present_things: list[PerceivedNode] = []

    def tick(
        self,
        citizen_id: str,
        tick: int,
        query_fn: Optional[Callable] = None,
        drives: Optional[dict] = None,
        desires: Optional[list] = None,
    ) -> list[Stimulus]:
        """Scan L3, produce stimuli. Call every tick.

        Args:
            citizen_id: this citizen's actor ID
            tick: current tick number
            query_fn: callable(cypher, params) → result_set
            drives: current drive intensities for limbic bias
            desires: active desire node embeddings for goal alignment
        """
        if query_fn is None:
            return []

        stimuli: list[Stimulus] = []
        candidates: list[tuple[int, str, str, float, dict]] = []

        # Refresh full environment scan periodically
        if tick - self._awareness_tick >= AWARENESS_REFRESH_TICKS:
            self._scan_environment(citizen_id, query_fn)
            self._awareness_tick = tick

        now = time.time()
        since = now - SCAN_WINDOW_S

        try:
            # ── Channel 1: New Moments in my Spaces ──
            rows = _safe_query(query_fn,
                "MATCH (a:Actor {id: $cid})-[:LINK]->(s:Space)<-[:LINK]-(m:Moment) "
                "WHERE m.timestamp > $since "
                "OPTIONAL MATCH (author:Actor)-[:LINK]->(m) "
                "WHERE author.id <> $cid "
                "RETURN m.id, m.synthesis, author.name, s.name "
                "ORDER BY m.timestamp DESC LIMIT 5",
                {"cid": citizen_id, "since": since},
            )
            for row in rows:
                m_id = row[0]
                if m_id in self._seen_ids:
                    continue
                self._seen_ids.add(m_id)
                author = row[2] or "someone"
                space = row[3] or "somewhere"
                text = (row[1] or "")[:80]
                candidates.append((80, "new_message",
                    f"{author} in #{space}: {text}", 0.4,
                    {"is_social": True}))

            # ── Channel 2: Mentions of me ──
            mention_rows = _safe_query(query_fn,
                "MATCH (m:Moment)-[:LINK]->(a:Actor {id: $cid}) "
                "WHERE m.timestamp > $since "
                "OPTIONAL MATCH (author:Actor)-[:LINK]->(m) "
                "WHERE author.id <> $cid "
                "RETURN m.id, m.synthesis, author.name "
                "ORDER BY m.timestamp DESC LIMIT 3",
                {"cid": citizen_id, "since": since},
            )
            for row in mention_rows:
                m_id = row[0]
                if m_id in self._seen_ids:
                    continue
                self._seen_ids.add(m_id)
                candidates.append((90, "new_mention",
                    f"{row[2] or 'someone'} mentioned me: {(row[1] or '')[:60]}", 0.6,
                    {"is_social": True}))

            # ── Channel 3: Narrative shifts (new/changed narratives in my Spaces) ──
            if self._active_narratives:
                top_narr = self._active_narratives[0]
                hab = self._habituation.get(top_narr.id, 0)
                if hab < 3:  # not yet habituated
                    candidates.append((60, "narrative_shift",
                        f"Active narrative here: {top_narr.name}", 0.25, {}))

            # ── Channel 4: Things present ──
            if self._present_things:
                for thing in self._present_things[:2]:
                    hab = self._habituation.get(thing.id, 0)
                    if hab < 2:
                        candidates.append((40, "new_thing",
                            f"I notice: {thing.name}", 0.15, {}))
                        break

            # ── Channel 5: Actors nearby ──
            for actor in self._nearby_actors:
                hab = self._habituation.get(actor.id, 0)
                if hab < 5:
                    candidates.append((50, "actor_nearby",
                        f"{actor.name} is nearby", 0.2,
                        {"is_social": True}))
                    break

            # ── Channel 6: Space atmosphere ──
            if self._my_spaces:
                space = self._my_spaces[0]
                hab = self._habituation.get(space.id, 0)
                if hab < 2:
                    candidates.append((30, "space_atmosphere",
                        f"I'm in {space.name}", 0.1, {}))

        except Exception as e:
            logger.debug(f"Exteroception scan failed: {e}")

        # ── Fire candidates through channel gating ──
        candidates.sort(key=lambda c: c[0], reverse=True)
        for priority, channel_name, content, energy, extra in candidates:
            if len(stimuli) >= MAX_STIMULI_PER_TICK:
                break
            ch = self.channels.get(channel_name)
            if ch and ch.can_fire(tick):
                stimuli.append(Stimulus(
                    content=content,
                    energy_budget=energy,
                    source=EXTERO_SOURCE,
                    is_social=extra.get("is_social", False),
                ))
                ch.fire(tick)

        # Rearm + habituation
        for ch in self.channels.values():
            ch.try_rearm(tick)
        for node_id in self._seen_ids:
            self._habituation[node_id] = self._habituation.get(node_id, 0) + 1

        # Prune
        if len(self._seen_ids) > 500:
            self._seen_ids = set(list(self._seen_ids)[-200:])
        if len(self._habituation) > 500:
            self._habituation = dict(list(self._habituation.items())[-200:])

        return stimuli

    # ------------------------------------------------------------------
    # Full environment scan
    # ------------------------------------------------------------------

    def _scan_environment(self, citizen_id: str, query_fn: Callable):
        """Scan all node types around the citizen. Periodic, not per-tick."""

        # My Spaces
        rows = _safe_query(query_fn,
            "MATCH (a:Actor {id: $cid})-[:LINK]->(s:Space) "
            "RETURN s.id, s.name, 'space', s.synthesis, s.weight, s.energy "
            "ORDER BY s.energy DESC LIMIT 10",
            {"cid": citizen_id},
        )
        self._my_spaces = [PerceivedNode(
            id=r[0], name=r[1] or r[0], node_type="space",
            synthesis=r[3] or "", weight=float(r[4] or 0), energy=float(r[5] or 0),
        ) for r in rows]

        # Actors in my Spaces
        if self._my_spaces:
            space_ids = [s.id for s in self._my_spaces[:5]]
            rows = _safe_query(query_fn,
                "MATCH (actor:Actor)-[:LINK]->(s:Space) "
                "WHERE s.id IN $spaces AND actor.id <> $cid "
                "RETURN DISTINCT actor.id, actor.name, 'actor', '', actor.weight, actor.energy "
                "LIMIT 20",
                {"spaces": space_ids, "cid": citizen_id},
            )
            self._nearby_actors = [PerceivedNode(
                id=r[0], name=r[1] or r[0], node_type="actor",
                synthesis="", weight=float(r[4] or 0), energy=float(r[5] or 0),
            ) for r in rows]

        # Narratives in my Spaces
        if self._my_spaces:
            space_ids = [s.id for s in self._my_spaces[:5]]
            rows = _safe_query(query_fn,
                "MATCH (n:Narrative)-[:LINK]->(s:Space) "
                "WHERE s.id IN $spaces "
                "RETURN n.id, n.name, 'narrative', n.synthesis, n.weight, n.energy "
                "ORDER BY n.weight DESC LIMIT 10",
                {"spaces": space_ids},
            )
            self._active_narratives = [PerceivedNode(
                id=r[0], name=r[1] or r[0], node_type="narrative",
                synthesis=r[3] or "", weight=float(r[4] or 0), energy=float(r[5] or 0),
            ) for r in rows]

        # Things in my Spaces
        if self._my_spaces:
            space_ids = [s.id for s in self._my_spaces[:5]]
            rows = _safe_query(query_fn,
                "MATCH (t:Thing)-[:LINK]->(s:Space) "
                "WHERE s.id IN $spaces "
                "RETURN t.id, t.name, 'thing', t.synthesis, t.weight, t.energy "
                "ORDER BY t.weight DESC LIMIT 10",
                {"spaces": space_ids},
            )
            self._present_things = [PerceivedNode(
                id=r[0], name=r[1] or r[0], node_type="thing",
                synthesis=r[3] or "", weight=float(r[4] or 0), energy=float(r[5] or 0),
            ) for r in rows]

        # Recent Moments
        if self._my_spaces:
            space_ids = [s.id for s in self._my_spaces[:5]]
            rows = _safe_query(query_fn,
                "MATCH (m:Moment)-[:LINK]->(s:Space) "
                "WHERE s.id IN $spaces "
                "RETURN m.id, m.name, 'moment', m.synthesis, m.weight, m.energy "
                "ORDER BY m.timestamp DESC LIMIT 10",
                {"spaces": space_ids},
            )
            self._recent_moments = [PerceivedNode(
                id=r[0], name=r[1] or r[0], node_type="moment",
                synthesis=r[3] or "", weight=float(r[4] or 0), energy=float(r[5] or 0),
            ) for r in rows]

        logger.debug(
            f"Environment scan for {citizen_id}: "
            f"{len(self._my_spaces)} spaces, {len(self._nearby_actors)} actors, "
            f"{len(self._active_narratives)} narratives, {len(self._recent_moments)} moments, "
            f"{len(self._present_things)} things"
        )

    # ------------------------------------------------------------------
    # Awareness text (system prompt layer)
    # ------------------------------------------------------------------

    def get_awareness_text(self, citizen_id: str, metabolism=None) -> str:
        """Generate the awareness text for the system prompt.

        Called by the WM serializer when assembling the prompt.
        Returns a natural-language summary of what the citizen sees.
        """
        lines = ["## What I See Right Now"]

        # Spaces
        if self._my_spaces:
            space_names = [s.name for s in self._my_spaces[:5]]
            lines.append(f"I'm in: {', '.join(space_names)}.")
        else:
            lines.append("I'm not in any particular space right now.")

        # Actors nearby
        if self._nearby_actors:
            actor_names = [a.name for a in self._nearby_actors[:8]]
            lines.append(f"Nearby: {', '.join(actor_names)}.")

        # Narratives
        if self._active_narratives:
            narr_list = [f'"{n.name}"' for n in self._active_narratives[:5]]
            lines.append(f"Active narratives here: {', '.join(narr_list)}.")

        # Recent moments
        if self._recent_moments:
            moment_summaries = []
            for m in self._recent_moments[:3]:
                text = (m.synthesis or m.name or "")[:60]
                moment_summaries.append(text)
            if moment_summaries:
                lines.append(f"Recent: {'; '.join(moment_summaries)}.")

        # Things
        if self._present_things:
            thing_names = [t.name for t in self._present_things[:5]]
            lines.append(f"Things here: {', '.join(thing_names)}.")

        # Circadian
        if metabolism:
            phase = metabolism.circadian_phase()
            if phase < 0.2:
                lines.append("It's deep night for me — I'm drowsy.")
            elif phase < 0.4:
                lines.append("It's early/late — I'm winding down.")
            elif phase > 0.8:
                lines.append("I'm at peak alertness.")

            if metabolism.active_tonics:
                tonic_names = [t.name for t in metabolism.active_tonics]
                lines.append(f"Active frequencies: {', '.join(tonic_names)}.")

        return "\n".join(lines)


# =========================================================================
# Helper
# =========================================================================

def _safe_query(query_fn, cypher, params):
    try:
        result = query_fn(cypher, params)
        return result if result else []
    except Exception:
        return []
