import json
from unittest.mock import patch

from mcp.tools import inject_cluster_handler as handler


def test_successful_cluster_ingestion_triggers_cognitive_ticks(tmp_path, monkeypatch):
    workspace_path = tmp_path / "workspace.json"
    workspace_path.write_text(json.dumps({
        "nodes": [{
            "id": "space:root:main",
            "node_type": "space",
            "name": "Root",
            "content": "Existing graph anchor",
        }],
        "links": [],
    }))
    monkeypatch.setattr(handler, "WORKSPACE_PATH", workspace_path)

    cluster_yaml = """
nodes:
  - id: narrative:test:idea
    node_type: narrative
    name: Stimulus idea
    content: A newly added cluster node.
links:
  - source_id: narrative:test:idea
    target_id: space:root:main
"""
    with patch.object(handler, "get_embedding", return_value=None), patch.object(
        handler, "detect_citizen", return_value="nlr"
    ), patch.object(
        handler,
        "trigger_cognitive_ticks",
        return_value={"moment_id": "moment:mcp_stimulus:cluster"},
    ) as trigger_ticks:
        result = handler.handle_inject_cluster({"yaml": cluster_yaml})

    trigger_ticks.assert_called_once()
    call = trigger_ticks.call_args.kwargs
    assert call["target"] == "nlr"
    assert call["source"] == "mcp:inject_cluster"
    assert call["metadata"]["intent"] == "inject_cluster"
    assert call["metadata"]["mutation_count"] == 2
    assert "narrative:test:idea" in call["content"]
    assert result["structuredContent"]["stimulus"]["moment_id"].endswith("cluster")

