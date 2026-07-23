import json
from types import SimpleNamespace

from mcp import server
from mcp.tools import recall_handler
from mcp.tools.recall_handler import (
    VIRTUAL_L1_SPACE_PREFIX,
    _space_closure,
    handle_recall,
)
from runtime.cognition.recall import (
    RecallGraphLink,
    RecallGraphNode,
    run_recall,
)


class QueryResult:
    def __init__(self, rows=None):
        self.result_set = rows or []


class FakeRecallGraph:
    def __init__(self):
        self.calls = []
        self.node_rows = [
            ["space:mind", "Mind", "Space", "Space", [0.0, 1.0], 0.0, 1.0, 0.5, 1.0, "active", "unknown"],
            ["memory:aurore", "Aurore likes gardens", "memory", "Memory", [1.0, 0.0], 0.0, 1.0, 0.4, 0.9, "", "reported"],
            ["concept:music", "Music theory", "concept", "Concept", [0.0, 1.0], 0.0, 1.0, 0.3, 0.8, "", "confirmed"],
            ["subentity:relation", "Relational facet", "Actor", "Subentity", [1.0, 0.0], 0.8, 1.0, 0.5, 1.0, "active", "unknown"],
        ]
        self.link_rows = [
            ["space:mind", "memory:aurore", "CONTAINS", 1.0, 1.0, 0.0, 0.5, 0.0],
            ["space:mind", "concept:music", "CONTAINS", 1.0, 1.0, 0.0, 0.5, 0.0],
            ["space:mind", "subentity:relation", "CONTAINS", 1.0, 1.0, 0.0, 0.5, 0.0],
        ]

    def query(self, query, params=None):
        params = params or {}
        self.calls.append((query, params))
        if "MATCH (s {id: $space_id}) RETURN s.id" in query:
            return QueryResult([[params["space_id"]]])
        if "RETURN n.id, coalesce(n.content" in query:
            return QueryResult(self.node_rows)
        if "RETURN a.id, b.id, type(r)" in query:
            return QueryResult(self.link_rows)
        if "CREATE (moment:Moment" in query:
            return QueryResult([[params["moment_id"]]])
        return QueryResult([])


def _nodes():
    return [
        RecallGraphNode(
            id="memory:aurore",
            content="Aurore likes gardens",
            node_type="memory",
            embedding=[1.0, 0.0],
            epistemic_status="reported",
        ),
        RecallGraphNode(
            id="concept:music",
            content="Music theory",
            node_type="concept",
            embedding=[0.0, 1.0],
            epistemic_status="confirmed",
        ),
        RecallGraphNode(
            id="subentity:relation",
            content="Relational facet",
            node_type="actor",
            semantic_type="Subentity",
            embedding=[1.0, 0.0],
            energy=0.8,
            status="active",
        ),
    ]


def test_recall_includes_every_space_node_and_injects_only_one_budget():
    nodes = _nodes()
    outcome = run_recall(
        citizen_id="nlr",
        moment_id="moment:recall:test",
        question="What do I remember about Aurore?",
        question_embedding=[1.0, 0.0],
        nodes=nodes,
        links=[],
        energy=1.0,
        max_ticks=4,
    )

    assert outcome.stimulus_node_count == len(nodes) + 1
    assert outcome.injected_energy == 1.0
    assert set(outcome.final_energies) == {node.id for node in nodes}
    assert outcome.results[0].node_id == "memory:aurore"
    assert outcome.results[0].epistemic_status == "reported"


def test_recall_routes_to_semantically_relevant_active_subentity():
    outcome = run_recall(
        citizen_id="nlr",
        moment_id="moment:recall:test",
        question="Aurore",
        question_embedding=[1.0, 0.0],
        nodes=_nodes(),
        links=[],
        max_ticks=2,
    )

    assert outcome.selection.parent_id == "subentity:relation"
    assert outcome.selection.semantic > 0.99
    assert outcome.recall_subentity_id.startswith("se_")


def test_space_closure_is_transitive_and_does_not_include_external_neighbor():
    nodes = {
        "space:root": RecallGraphNode("space:root", node_type="Space", semantic_type="Space"),
        "space:child": RecallGraphNode("space:child", node_type="Space", semantic_type="Space"),
        "memory:inside": RecallGraphNode("memory:inside", node_type="memory"),
        "memory:outside": RecallGraphNode("memory:outside", node_type="memory"),
    }
    links = [
        {"source": "space:root", "target": "space:child", "relation": "CONTAINS", "weight": 1.0, "activation_gain": 1.0, "friction": 0.0, "trust": 0.5, "hierarchy": 0.0},
        {"source": "memory:inside", "target": "space:child", "relation": "OCCURS_IN", "weight": 1.0, "activation_gain": 1.0, "friction": 0.0, "trust": 0.5, "hierarchy": 0.0},
        {"source": "memory:inside", "target": "memory:outside", "relation": "ASSOCIATES", "weight": 1.0, "activation_gain": 1.0, "friction": 0.0, "trust": 0.5, "hierarchy": 0.0},
    ]

    closure_nodes, closure_links = _space_closure("space:root", nodes, links)

    assert {node.id for node in closure_nodes} == {
        "space:root",
        "space:child",
        "memory:inside",
    }
    assert {(link.source_id, link.target_id) for link in closure_links} == {
        ("space:root", "space:child"),
        ("memory:inside", "space:child"),
    }


def test_virtual_l1_space_contains_the_complete_legacy_graph():
    nodes = {
        "memory:a": RecallGraphNode("memory:a", node_type="memory"),
        "concept:b": RecallGraphNode("concept:b", node_type="concept"),
    }
    links = [
        {"source": "memory:a", "target": "concept:b", "relation": "ASSOCIATES", "weight": 1.0, "activation_gain": 1.0, "friction": 0.0, "trust": 0.5, "hierarchy": 0.0},
    ]

    closure_nodes, closure_links = _space_closure(
        f"{VIRTUAL_L1_SPACE_PREFIX}l1_nlr",
        nodes,
        links,
    )

    assert {node.id for node in closure_nodes} == {"memory:a", "concept:b"}
    assert len(closure_links) == 1


def test_handler_creates_moment_persists_results_and_keeps_full_stimulus():
    graph = FakeRecallGraph()
    ctx = SimpleNamespace(
        recall_graph=graph,
        recall_graph_name="l1_nlr",
        graph_queries=SimpleNamespace(_embed_fn=lambda _text: [1.0, 0.0]),
    )

    response = handle_recall(
        {
            "question": "What do I remember about Aurore?",
            "spaceId": "space:mind",
            "handle": "nlr",
            "maxTicks": 3,
            "topK": 1,
        },
        ctx,
    )
    payload = json.loads(response["content"][0]["text"])

    assert payload["status"] == "completed"
    assert payload["spaceId"] == "space:mind"
    assert payload["stimulusNodeCount"] == 5  # 4 Space nodes + central question
    assert len(payload["results"]) == 1
    assert payload["allResultCount"] > len(payload["results"])
    assert any("CREATE (moment:Moment" in query for query, _ in graph.calls)
    assert any("UNWIND $updates AS update" in query for query, _ in graph.calls)
    assert any("ROUTED_TO" in query for query, _ in graph.calls)
    persisted = next(
        params
        for query, params in graph.calls
        if "moment.resultNodeIdsJson" in query
    )
    assert len(json.loads(persisted["result_node_ids_json"])) == payload["allResultCount"]


def test_recall_is_registered_as_mutating_mcp_tool():
    assert "recall" in server.TOOL_DISPATCH
    schema = next(item for item in server.TOOL_SCHEMAS if item["name"] == "recall")
    assert schema["annotations"]["readOnlyHint"] is False
    assert schema["inputSchema"]["required"] == ["question"]


def test_handler_marks_created_moment_failed_when_execution_breaks():
    graph = FakeRecallGraph()
    ctx = SimpleNamespace(
        recall_graph=graph,
        recall_graph_name="l1_nlr",
        graph_queries=SimpleNamespace(_embed_fn=lambda _text: [1.0, 0.0]),
    )

    response = handle_recall(
        {
            "question": "Aurore?",
            "spaceId": "space:mind",
            "handle": "nlr",
            "maxTicks": "not-an-integer",
        },
        ctx,
    )
    payload = json.loads(response["content"][0]["text"])

    assert payload["status"] == "failed"
    assert payload["code"] == "invalid_arguments"
    assert any(
        "moment.failureReason" in query
        for query, _ in graph.calls
    )


def test_handler_rejects_a_different_citizen_handle(monkeypatch):
    monkeypatch.setattr(recall_handler, "detect_citizen_handle", lambda: "nervo")

    response = handle_recall(
        {"question": "Private memory?", "handle": "nlr"},
        SimpleNamespace(),
    )
    payload = json.loads(response["content"][0]["text"])

    assert payload["status"] == "failed"
    assert payload["code"] == "sovereignty_violation"
