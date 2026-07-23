import json

from runtime.graph_diff import graph_diff


class QueryResult:
    def __init__(self, rows):
        self.result_set = rows


class RuntimeGraph:
    def query(self, cypher, params=None):
        if "MATCH (node)" in cypher:
            return QueryResult([
                ["n1", ["MindNode"], {
                    "id": "n1",
                    "name": "Runtime name",
                    "nodeType": "narrative",
                    "semanticType": "axiom",
                }],
                ["n4", ["MindNode"], {
                    "id": "n4", "nodeType": "narrative", "semanticType": "protocol"
                }],
                ["n3", ["MindNode"], {"id": "n3", "name": "Runtime only"}],
            ])
        return QueryResult([
            ["n1", "REL", "n3", {"justification": "runtime"}],
        ])


class Client:
    def select_graph(self, name):
        assert name == "design_graph"
        return RuntimeGraph()


def test_graph_diff_reports_runtime_only_missing_and_property_drift(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "design.json").write_text(json.dumps({
        "nodes": [
            {"id": "n1", "name": "Canonical name", "nodeType": "axiom", "role": "narrative"},
            {"id": "n2", "name": "Missing runtime"},
            {"id": "n4", "nodeType": "protocol"},
        ],
        "links": [
            {"source": "n1", "type": "REL", "target": "n2", "justification": "canonical"},
        ],
    }), encoding="utf-8")
    manifest = tmp_path / "graphs.json"
    manifest.write_text(json.dumps({"graphs": [{
        "id": "design",
        "status": "active",
        "falkorGraph": "design_graph",
        "dataDir": "data",
        "datasets": [{"id": "design", "file": "design.json"}],
    }]}), encoding="utf-8")

    result = graph_diff(manifest, client=Client())
    design = result["graphs"][0]

    assert result["clean"] is False
    assert design["runtime_only"]["nodes"] == ["n3"]
    assert design["missing_from_runtime"]["nodes"] == ["n2"]
    assert design["runtime_only"]["links"][0] == {"source": "n1", "type": "REL", "target": "n3"}
    assert design["missing_from_runtime"]["links"][0] == {"source": "n1", "type": "REL", "target": "n2"}
    assert design["property_changes"]["nodes"][0]["properties"]["name"] == {
        "canonical": "Canonical name", "runtime": "Runtime name"
    }
