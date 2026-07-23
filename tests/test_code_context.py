import json
from pathlib import Path

from mcp.tools.code_context_handler import handle_code_context
from mcp.tools.context import ServerContext
from runtime.code_context import change_context, enrich_code_path, impact, path_candidates, related_tests


class QueryResult:
    def __init__(self, rows):
        self.result_set = rows


class FakeGraph:
    def __init__(self, roots=None, traversal=None, error=None):
        self.roots = roots or []
        self.traversal = traversal or []
        self.error = error
        self.calls = []

    def query(self, cypher, params):
        self.calls.append((cypher, params))
        if self.error:
            raise RuntimeError(self.error)
        if "MATCH path=" in cypher:
            return QueryResult(self.traversal)
        return QueryResult(self.roots)


class FakeClient:
    def __init__(self, graphs):
        self.graphs = graphs

    def list_graphs(self):
        return list(self.graphs)

    def select_graph(self, name):
        return self.graphs[name]


def test_path_candidates_include_relative_and_windows_variants(tmp_path):
    candidates = path_candidates("runtime/example.py", tmp_path)

    assert "runtime/example.py" in candidates
    assert "runtime\\example.py" in candidates
    assert str((tmp_path / "runtime/example.py").resolve()).replace("\\", "/").lower() in candidates


def test_enrich_code_path_scans_all_graphs_and_traverses_matches(tmp_path):
    design = FakeGraph(
        roots=[[7, ["Thing"], {"id": "thing-code", "path": "runtime/example.py"}]],
        traversal=[[
            9,
            ["Narrative"],
            {"id": "design-rule", "content": "Keep the operation atomic."},
            ["LINK"],
            [{"computed_type": "constrains"}],
            [7, 9],
        ]],
    )
    client = FakeClient({"design": design, "science": FakeGraph()})

    result = enrich_code_path(
        "runtime/example.py",
        project_root=tmp_path,
        depth=1,
        client=client,
    )

    assert result["graphs_scanned"] == 2
    assert result["matches"] == 1
    match = next(item for item in result["graphs"] if item["graph"] == "design")["matches"][0]
    assert match["root"]["properties"]["id"] == "thing-code"
    assert match["neighbors"][0]["properties"]["id"] == "design-rule"
    assert match["paths"][0]["relationship_types"] == ["LINK"]
    root_query, params = design.calls[0]
    assert "root.sourcePath" in root_query
    assert "runtime/example.py" in params["paths"]


def test_enrich_code_path_is_fail_open_per_graph(tmp_path):
    client = FakeClient({"offline": FakeGraph(error="connection refused"), "empty": FakeGraph()})

    result = enrich_code_path("x.py", project_root=tmp_path, client=client)

    assert result["matches"] == 0
    offline = next(item for item in result["graphs"] if item["graph"] == "offline")
    assert offline["error"] == "connection refused"


def test_handler_can_be_disabled_without_connecting(monkeypatch, tmp_path):
    monkeypatch.setenv("MIND_CODE_CONTEXT_ENABLED", "false")
    ctx = ServerContext(target_dir=Path(tmp_path))

    response = handle_code_context({"path": "runtime/example.py"}, ctx)
    payload = json.loads(response["content"][0]["text"])

    assert payload["enabled"] is False
    assert "enabled=true" in payload["message"]


class ImpactGraph:
    def query(self, cypher, params):
        if "RETURN id(root)" in cypher:
            return QueryResult([[1, ["Thing"], {"id": "code-node", "sourcePath": "runtime/example.py"}]])
        if "(root)-[rel]->(neighbor)" in cypher:
            return QueryResult([[
                2, ["MindNode"], {"id": "decision-1", "semanticType": "decision", "sourcePath": "docs/design.md"},
                "CONSTRAINS", {"justification": "approved decision"},
            ]])
        if "(neighbor)-[rel]->(root)" in cypher:
            return QueryResult([[
                3, ["MindNode"], {"id": "risk-1", "semanticType": "risk"},
                "AFFECTS", {},
            ]])
        return QueryResult([])


def test_impact_separates_directions_and_categories(tmp_path):
    client = FakeClient({"design": ImpactGraph()})

    result = impact(
        file_path="runtime/example.py", project_root=tmp_path, graph_names=["design"], client=client
    )
    anchor = result["graphs"][0]["anchors"][0]

    assert anchor["dependencies"]["outgoing"][0]["type"] == "CONSTRAINS"
    assert anchor["dependencies"]["incoming"][0]["type"] == "AFFECTS"
    assert anchor["decisions"][0]["properties"]["id"] == "decision-1"
    assert anchor["risks"][0]["properties"]["id"] == "risk-1"
    assert "docs/design.md" in anchor["affected_files"]


def test_related_tests_and_change_context_are_deterministic(tmp_path):
    (tmp_path / "runtime").mkdir()
    (tmp_path / "runtime" / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_example.py").write_text(
        "from runtime.example import VALUE\n", encoding="utf-8"
    )
    client = FakeClient({"design": ImpactGraph()})

    assert related_tests("runtime/example.py", tmp_path) == ["tests/test_example.py"]
    result = change_context(
        file_paths=["runtime/example.py"], project_root=tmp_path, graph_names=["design"], client=client
    )
    assert result["items"][0]["related_tests"] == ["tests/test_example.py"]
    assert result["items"][0]["impact"]["anchors"] == 1
