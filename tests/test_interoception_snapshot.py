import json
from types import SimpleNamespace

from runtime.cognition.interoception_snapshot import (
    SNAPSHOT_ID,
    build_interoception_snapshot,
    publish_interoception_snapshot,
    read_interoception_snapshot,
    resolve_l1_graph_name,
)
from runtime.cognition.models import CitizenCognitiveState, Node, NodeType


class QueryResult:
    def __init__(self, rows=None):
        self.result_set = rows or []


class FakeGraph:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.calls = []

    def query(self, query, params=None):
        self.calls.append((query, params or {}))
        return QueryResult(self.rows)


class FakeDB:
    def __init__(self, graphs):
        self.graphs = graphs

    def list_graphs(self):
        return list(self.graphs)

    def select_graph(self, name):
        return self.graphs[name]


def make_state():
    state = CitizenCognitiveState(citizen_id="nlr_ai")
    state.nodes["focus"] = Node(
        id="focus",
        node_type=NodeType.CONCEPT,
        content="Current focus",
        energy=0.75,
    )
    state.wm.node_ids = ["focus"]
    state.tick_count = 42
    state.limbic.drives["curiosity"].intensity = 0.8
    state.limbic.emotions["satisfaction"] = 0.6
    state.metabolism = SimpleNamespace(circadian_phase=lambda: 0.7)
    return state


def test_build_snapshot_captures_live_state():
    payload = build_interoception_snapshot(
        make_state(),
        orientation="explore",
        engine_instance_id="engine-1",
        observed_at=1000.0,
    )

    assert payload["id"] == SNAPSHOT_ID
    assert payload["schemaVersion"] == "1.0"
    assert payload["citizen"] == "nlr_ai"
    assert payload["tick"] == 42
    assert payload["energy"] == 0.75
    assert payload["drives"]["curiosity"] == 0.8
    assert payload["emotions"]["satisfaction"] == 0.6
    assert payload["workingMemory"] == {
        "used": 1,
        "capacity": 7,
        "nodeIds": ["focus"],
    }
    assert payload["orientation"] == "explore"
    assert payload["circadianPhase"] == 0.7


def test_resolver_prefers_existing_live_graph(monkeypatch):
    monkeypatch.delenv("L1_GRAPH", raising=False)
    db = FakeDB({"l1_nlr_ai": FakeGraph(), "brain_nlr_ai": FakeGraph()})

    assert resolve_l1_graph_name("actor-nlr-ai", db=db) == "l1_nlr_ai"


def test_publish_is_one_atomic_graph_query():
    graph = FakeGraph()

    payload = publish_interoception_snapshot(
        make_state(),
        orientation="explore",
        observed_at=1000.0,
        graph=graph,
    )

    assert len(graph.calls) == 1
    query, params = graph.calls[0]
    assert "MERGE (s:RuntimeState {id: $id})" in query
    assert params["id"] == SNAPSHOT_ID
    stored = json.loads(params["data"])
    assert stored["tick"] == 42
    assert payload["observedAtEpoch"] == 1000.0


def test_read_classifies_fresh_snapshot():
    payload = build_interoception_snapshot(make_state(), observed_at=1000.0)
    graph = FakeGraph([[json.dumps(payload), 1000.0, "1.0"]])
    db = FakeDB({"l1_nlr_ai": graph})

    result = read_interoception_snapshot(
        "nlr_ai",
        now=1010.0,
        stale_after_seconds=30.0,
        db=db,
    )

    assert result["freshness"] == "fresh"
    assert result["ageSeconds"] == 10.0
    assert result["graphName"] == "l1_nlr_ai"


def test_read_classifies_stale_snapshot():
    payload = build_interoception_snapshot(make_state(), observed_at=1000.0)
    graph = FakeGraph([[json.dumps(payload), 1000.0, "1.0"]])
    db = FakeDB({"l1_nlr_ai": graph})

    result = read_interoception_snapshot(
        "nlr_ai",
        now=1031.0,
        stale_after_seconds=30.0,
        db=db,
    )

    assert result["freshness"] == "stale"
    assert result["ageSeconds"] == 31.0


def test_read_returns_none_when_no_snapshot_exists():
    db = FakeDB({"l1_nlr_ai": FakeGraph([])})

    assert read_interoception_snapshot("nlr_ai", db=db) is None
