"""
Exteroception — External Sensory Awareness

DOCS: (to be created)

The citizen's awareness of what's happening in their world.
Each tick, scans L3 for new events in the citizen's Spaces
and converts them into stimuli for Law 1 injection.

Interoception = sensing yourself (drives, fatigue, WM load)
Exteroception = sensing the world (messages, events, changes)

Runs once per tick, BEFORE interoception, BEFORE Law 1 inject.
Reads: L3 graph (Spaces the citizen is in, recent Moments)
Writes: list[Stimulus] for Law 1 injection

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

# How far back to scan for new Moments (in seconds)
SCAN_WINDOW_S = 120.0  # 2 minutes — covers 2 ticks at 60s/tick


@dataclass
class SensoryChannel:
    """A single exteroceptive channel."""
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


class ExteroceptionEngine:
    """Scans L3 for new events and converts them to L1 stimuli.

    Needs a graph_query function to read L3. If not provided,
    exteroception is silent (graceful degradation).
    """

    def __init__(self):
        self.channels = {
            "new_message":     SensoryChannel("new_message",     priority=80, refractory_ticks=2),
            "new_mention":     SensoryChannel("new_mention",     priority=90, refractory_ticks=1),
            "new_actor":       SensoryChannel("new_actor",       priority=40, refractory_ticks=20),
            "space_activity":  SensoryChannel("space_activity",  priority=30, refractory_ticks=10),
            "subcall_result":  SensoryChannel("subcall_result",  priority=70, refractory_ticks=5),
        }
        self._last_scan_ts: float = 0.0
        self._seen_moment_ids: set = set()

    def tick(
        self,
        citizen_id: str,
        tick: int,
        query_fn: Optional[Callable] = None,
    ) -> list[Stimulus]:
        """Scan L3 for new events. Returns stimuli for Law 1.

        Args:
            citizen_id: this citizen's actor ID
            tick: current tick number
            query_fn: callable(cypher, params) → result_set. If None, silent.
        """
        if query_fn is None:
            return []

        now = time.time()
        since = now - SCAN_WINDOW_S
        stimuli: list[Stimulus] = []
        candidates: list[tuple[int, str, str, float, dict]] = []

        try:
            # ── Scan 1: New Moments in my Spaces ──
            rows = query_fn(
                """
                MATCH (a:Actor {id: $cid})-[:LINK]->(s:Space)<-[:LINK]-(m:Moment)
                WHERE m.timestamp > $since
                MATCH (author:Actor)-[:LINK]->(m)
                WHERE author.id <> $cid
                RETURN m.id, m.content, m.synthesis, author.id, author.name, s.name
                ORDER BY m.timestamp DESC
                LIMIT 10
                """,
                {"cid": citizen_id, "since": since},
            )

            for row in (rows or []):
                m_id, content, synthesis, author_id, author_name, space_name = row
                if m_id in self._seen_moment_ids:
                    continue
                self._seen_moment_ids.add(m_id)

                text = synthesis or (content or "")[:100]
                author = author_name or author_id or "someone"
                space = space_name or "somewhere"

                candidates.append((
                    80, "new_message",
                    f"{author} in #{space}: {text}",
                    0.4,
                    {"is_social": True, "origin_citizen": author_id or ""},
                ))

            # ── Scan 2: Direct mentions of me ──
            mention_rows = query_fn(
                """
                MATCH (m:Moment)-[:LINK]->(a:Actor {id: $cid})
                WHERE m.timestamp > $since
                MATCH (author:Actor)-[:LINK]->(m)
                WHERE author.id <> $cid
                RETURN m.id, m.content, m.synthesis, author.id, author.name
                ORDER BY m.timestamp DESC
                LIMIT 5
                """,
                {"cid": citizen_id, "since": since},
            )

            for row in (mention_rows or []):
                m_id, content, synthesis, author_id, author_name = row
                if m_id in self._seen_moment_ids:
                    continue
                self._seen_moment_ids.add(m_id)

                text = synthesis or (content or "")[:100]
                author = author_name or author_id or "someone"

                candidates.append((
                    90, "new_mention",
                    f"{author} mentioned me: {text}",
                    0.6,
                    {"is_social": True, "origin_citizen": author_id or ""},
                ))

            # ── Scan 3: Subcall results targeting me ──
            subcall_rows = query_fn(
                """
                MATCH (m:Moment)-[:LINK]->(a:Actor {id: $cid})
                WHERE m.timestamp > $since AND m.content CONTAINS 'subcall'
                RETURN m.id, m.content, m.synthesis
                ORDER BY m.timestamp DESC
                LIMIT 3
                """,
                {"cid": citizen_id, "since": since},
            )

            for row in (subcall_rows or []):
                m_id, content, synthesis = row
                if m_id in self._seen_moment_ids:
                    continue
                self._seen_moment_ids.add(m_id)

                text = synthesis or (content or "")[:100]
                candidates.append((
                    70, "subcall_result",
                    f"Someone probed my knowledge: {text}",
                    0.3,
                    {},
                ))

        except Exception as e:
            logger.debug(f"Exteroception scan failed: {e}")
            return []

        # ── Fire candidates through channel gating ──
        candidates.sort(key=lambda c: c[0], reverse=True)

        for priority, channel_name, content, energy, extra in candidates:
            if len(stimuli) >= MAX_STIMULI_PER_TICK:
                break

            ch = self.channels.get(channel_name)
            if ch and ch.can_fire(tick):
                s = Stimulus(
                    content=content,
                    energy_budget=energy,
                    source=EXTERO_SOURCE,
                    is_social=extra.get("is_social", False),
                    origin_citizen=extra.get("origin_citizen", ""),
                )
                stimuli.append(s)
                ch.fire(tick)

        # Rearm channels
        for ch in self.channels.values():
            ch.try_rearm(tick)

        # Prune seen IDs (keep last 200)
        if len(self._seen_moment_ids) > 200:
            self._seen_moment_ids = set(list(self._seen_moment_ids)[-100:])

        self._last_scan_ts = now
        return stimuli
