import json
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.orchestrator import graph_alarms  # noqa: E402
from runtime.orchestrator.graph_temporal_desires import (  # noqa: E402
    process_temporal_desires,
    read_temporal_desire_frame,
    validate_due_alarm,
)


def _database_reachable() -> bool:
    try:
        return bool(graph_alarms._client().connection.execute_command("PING"))
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _database_reachable(),
    reason="FalkorDB not reachable on FALKORDB_HOST:FALKORDB_PORT",
)


@pytest.fixture
def temporal_graph():
    handle = f"pytesttemporal{uuid.uuid4().hex[:8]}"
    graph = graph_alarms.select_graph(handle)
    yield handle, graph
    try:
        graph.delete()
    except Exception:
        pass


def _seed_expectation(graph, now: datetime, *, threshold: float = 0.5):
    graph.query(
        """
        CREATE (w:L1Node {
            id: 'wish:test', nodeType: 'Narrative', semanticType: 'Wish',
            status: 'active', weight: 1.0, createdAt: $now
        })
        CREATE (o:L1Node {
            id: 'objective:test', nodeType: 'Narrative', semanticType: 'Objective',
            status: 'active', progress: 0.0, createdAt: $now
        })
        CREATE (w)-[:SEEKS_REALIZATION {
            commitment: 1.0,
            category: 'operational_progress',
            baseClockRate: 1.0,
            patienceTauSeconds: 100.0,
            baseThreshold: $threshold,
            releaseThreshold: 0.4,
            subjectiveAgeSeconds: 0.0,
            lastIntegratedAt: $now,
            heldClockRate: 1.0,
            effectiveThreshold: $threshold,
            generation: 0,
            alarmArmed: true,
            measurementStatus: 'observed',
            createdAt: $now
        }]->(o)
        """,
        {"now": now.isoformat(), "threshold": threshold},
    )


def test_graph_tick_materializes_one_stable_alarm_and_frame(temporal_graph):
    handle, graph = temporal_graph
    now = datetime(2026, 7, 23, 12, 0, 0)
    _seed_expectation(graph, now)

    first = process_temporal_desires(handle, now)
    wakes = graph_alarms.list_wakes(handle)
    assert len(wakes) == 1
    assert wakes[0]["semanticType"] == "Alarm"
    assert wakes[0]["reason"] == "temporal_desire_threshold"
    first_alarm_id = wakes[0]["id"]
    first_scheduled = wakes[0]["scheduledFor"]

    process_temporal_desires(handle, now + timedelta(seconds=10))
    wakes = graph_alarms.list_wakes(handle)
    assert [wake["id"] for wake in wakes] == [first_alarm_id]
    assert wakes[0]["scheduledFor"] == first_scheduled

    frame = read_temporal_desire_frame(handle)
    assert frame["wakeLoad"]["scheduledAlarmCount"] == 1
    assert frame["activeExpectations"][0]["heldClockRate"] == 1.0
    assert first["activeExpectations"][0]["affectModifiers"]["status"] == "not_measured"


def test_progress_moment_reduces_pressure_and_invalidates_alarm(temporal_graph):
    handle, graph = temporal_graph
    now = datetime(2026, 7, 23, 12, 0, 0)
    _seed_expectation(graph, now)
    process_temporal_desires(handle, now)
    old_alarm = graph_alarms.list_wakes(handle)[0]

    progress_at = now + timedelta(seconds=20)
    graph.query(
        """
        MATCH (o {id: 'objective:test'})
        CREATE (m:L1Node {
            id: 'moment:progress:test', nodeType: 'Moment',
            semanticType: 'Progress', createdAt: $at
        })-[:PROGRESSES {delta: 0.5, relief: 0.5, confidence: 1.0}]->(o)
        """,
        {"at": progress_at.isoformat()},
    )

    process_temporal_desires(handle, progress_at)

    assert graph_alarms.list_wakes(handle) == []
    all_wakes = graph_alarms.list_wakes(handle, include_fired=True)
    assert [wake["status"] for wake in all_wakes] == ["cancelled"]
    assert all_wakes[0]["id"] == old_alarm["id"]
    progress = graph.query(
        "MATCH (o {id: 'objective:test'}) RETURN o.progress"
    ).result_set[0][0]
    assert progress == 0.5


def test_due_alarm_is_revalidated_against_relation_generation(temporal_graph):
    handle, graph = temporal_graph
    now = datetime(2026, 7, 23, 12, 0, 0)
    _seed_expectation(graph, now, threshold=0.2)
    process_temporal_desires(handle, now)
    wake = graph_alarms.list_wakes(handle)[0]
    due_at = datetime.fromisoformat(wake["scheduledFor"])

    process_temporal_desires(handle, due_at)
    wake = graph_alarms.due_wakes(handle, due_at)[0]
    valid, measurement = validate_due_alarm(handle, wake, due_at)

    assert valid is True
    assert measurement["channel"] == "interoception.temporal_desire"
    assert measurement["pressure"] + 1e-8 >= measurement["threshold"]

    stale = dict(wake)
    stale["relationGeneration"] += 1
    assert validate_due_alarm(handle, stale, due_at)[0] is False


def test_graph_declared_affect_and_subentity_policies_modulate_next_interval(
    temporal_graph,
):
    handle, graph = temporal_graph
    now = datetime(2026, 7, 23, 12, 0, 0)
    _seed_expectation(graph, now)
    payload = {
        "emotions": {"anxiety": 0.8},
        "drives": {},
        "workspaceSubentities": {"subentity:senex": 1.0},
        "expiresAt": (now + timedelta(minutes=5)).isoformat(),
    }
    graph.query(
        """
        MATCH (w {id: 'wish:test'})
        CREATE (a:L1Node {
            id: 'affect:anxiety', nodeType: 'Thing', semanticType: 'Affect'
        })
        CREATE (s:L1Node {
            id: 'subentity:senex', nodeType: 'Actor', semanticType: 'Subentity'
        })
        CREATE (a)-[:TEMPORALLY_BIASES {
            clockBias: 0.9, thresholdBias: -0.15, compatibility: 1.0
        }]->(w)
        CREATE (s)-[:TEMPORALLY_BIASES {
            clockBias: 0.2, thresholdBias: -0.05, compatibility: 1.0
        }]->(w)
        CREATE (snapshot:RuntimeState {
            id: 'interoception-current',
            data: $data,
            expiresAt: $expires
        })
        """,
        {
            "data": json.dumps(payload),
            "expires": payload["expiresAt"],
        },
    )

    frame = process_temporal_desires(handle, now)
    current = frame["activeExpectations"][0]

    assert current["heldClockRate"] > 1.0
    assert current["threshold"] < 0.5
    assert current["affectModifiers"]["status"] == "observed"
    assert current["subentityModifiers"]["status"] == "observed"
