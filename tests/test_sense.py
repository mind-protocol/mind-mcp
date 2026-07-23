import json
from types import SimpleNamespace

from mcp.tools import sense_handler


def _write_workspace(tmp_path):
    path = tmp_path / "global-workspace.json"
    workspace = {
        "id": "workspace-actor-nlr",
        "actorId": "actor-nlr",
        "version": 42,
        "mode": "execute_task",
        "activeNodeIds": ["task-current"],
        "sense": {"handle": "nlr_ai"},
    }
    path.write_text(json.dumps({"citizens": {"actor-nlr": workspace}}), encoding="utf-8")
    return path, workspace


def test_sense_returns_the_complete_global_workspace(monkeypatch, tmp_path):
    path, workspace = _write_workspace(tmp_path)
    monkeypatch.setenv("MIND_GLOBAL_WORKSPACE_PATH", str(path))
    environment = {
        "measurementStatus": "observed",
        "spaces": [{"id": "space-current", "nodes": [{"id": "nearby-node"}]}],
    }
    monkeypatch.setattr(
        sense_handler,
        "_read_situated_environment",
        lambda *args, **kwargs: environment,
    )

    result = sense_handler.handle_sense(
        {"handle": "nlr_ai"},
        SimpleNamespace(disable_home_bridge=True),
    )

    assert json.loads(result["content"][0]["text"]) == {
        **workspace,
        "situatedEnvironment": environment,
    }


def test_sense_matches_actor_and_transport_identifiers(monkeypatch, tmp_path):
    path, workspace = _write_workspace(tmp_path)
    monkeypatch.setenv("MIND_GLOBAL_WORKSPACE_PATH", str(path))

    for identity in ("nlr_ai", "actor-nlr", "l3-actor-nlr"):
        assert sense_handler._read_global_workspace(identity) == workspace


def test_sense_reports_missing_workspace_without_inventing_state(monkeypatch, tmp_path):
    monkeypatch.setenv("MIND_GLOBAL_WORKSPACE_PATH", str(tmp_path / "missing.json"))
    monkeypatch.setattr(sense_handler, "_workspace_path_candidates", lambda: iter(()))

    result = sense_handler.handle_sense(
        {"handle": "nlr_ai"},
        SimpleNamespace(disable_home_bridge=True),
    )
    payload = json.loads(result["content"][0]["text"])

    assert payload == {
        "status": "unavailable",
        "citizen": "nlr",
        "reason": "No current Global Workspace was found for this citizen.",
    }


def test_sense_has_no_perceptual_layers_or_sense_node_queries():
    assert not hasattr(sense_handler, "_get_exteroception")
    assert not hasattr(sense_handler, "_get_interoception")
    assert not hasattr(sense_handler, "_get_senses")


class QueryResult:
    def __init__(self, rows=None):
        self.result_set = rows or []


class FakeGraph:
    def __init__(self, responses):
        self.responses = iter(responses)

    def query(self, query, params=None):
        return QueryResult(next(self.responses))


class FakeDB:
    def __init__(self, graph):
        self.graph = graph

    def list_graphs(self):
        return ["l3_ecosystem"]

    def select_graph(self, name):
        assert name == "l3_ecosystem"
        return self.graph


def test_sense_includes_nodes_directly_present_in_the_citizens_spaces():
    graph = FakeGraph([
        [["actor-nlr", "space-garden", "Garden", "LOCATED_IN"]],
        [[
            "moment-nearby",
            "Nearby Moment",
            "Moment",
            "observation",
            "Something happened here",
            0.8,
            "active",
            "LOCATED_IN",
        ]],
        [[
            "thing-contained",
            "Contained Thing",
            "Thing",
            "tool",
            "A tool in the garden",
            0.3,
            "active",
            "CONTAINS",
        ]],
    ])

    environment = sense_handler._read_situated_environment(
        "nlr_ai",
        actor_id="actor-nlr",
        db=FakeDB(graph),
    )

    assert environment["measurementStatus"] == "observed"
    assert environment["spaces"][0]["id"] == "space-garden"
    assert {
        node["id"] for node in environment["spaces"][0]["nodes"]
    } == {"moment-nearby", "thing-contained"}
    assert all(
        "presenceRelation" in node
        for node in environment["spaces"][0]["nodes"]
    )


def test_space_access_without_location_is_not_treated_as_presence():
    graph = FakeGraph([
        [],  # no LOCATED_IN
        [],  # no currentSpaceId
    ])

    environment = sense_handler._read_situated_environment(
        "nlr_ai",
        actor_id="actor-nlr",
        db=FakeDB(graph),
    )

    assert environment["measurementStatus"] == "known_absent"
    assert environment["spaces"] == []


def test_stdio_sense_can_read_workspace_from_home_server(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"text": '{"id":"workspace-remote"}'}).encode()

    monkeypatch.setattr(sense_handler, "_workspace_path_candidates", lambda: iter(()))
    monkeypatch.setattr(sense_handler.urllib.request, "urlopen", lambda *args, **kwargs: Response())

    result = sense_handler.handle_sense({"handle": "nlr_ai"}, SimpleNamespace())

    assert json.loads(result["content"][0]["text"]) == {"id": "workspace-remote"}
