import os
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp.tools.sense_handler import _read_situated_environment  # noqa: E402


def _database():
    try:
        from falkordb import FalkorDB

        db = FalkorDB(
            host=os.environ.get("FALKORDB_HOST", "localhost"),
            port=int(os.environ.get("FALKORDB_PORT", "6379")),
        )
        db.connection.execute_command("PING")
        return db
    except Exception:
        return None


DB = _database()
pytestmark = pytest.mark.skipif(DB is None, reason="FalkorDB is not reachable")


def test_situated_environment_reads_direct_presence_but_not_access(monkeypatch):
    graph_name = f"pytest_sense_space_{uuid.uuid4().hex[:10]}"
    graph = DB.select_graph(graph_name)
    monkeypatch.setenv("MIND_SENSE_SPACE_GRAPHS", graph_name)
    try:
        graph.query(
            """
            CREATE (actor {
                id: 'actor-nlr', nodeType: 'Actor', semanticType: 'CitizenAI'
            })
            CREATE (room {
                id: 'space:studio', name: 'Studio', nodeType: 'Space'
            })
            CREATE (remote {
                id: 'space:remote', name: 'Remote', nodeType: 'Space'
            })
            CREATE (moment {
                id: 'moment:music', name: 'Music playing',
                nodeType: 'Moment', energy: 0.8
            })
            CREATE (tool {
                id: 'thing:synth', name: 'Synth',
                nodeType: 'Thing', energy: 0.5
            })
            CREATE (elsewhere {
                id: 'thing:remote-only', name: 'Remote only', nodeType: 'Thing'
            })
            CREATE (actor)-[:LOCATED_IN]->(room)
            CREATE (actor)-[:HAS_ACCESS]->(remote)
            CREATE (moment)-[:OCCURS_IN]->(room)
            CREATE (room)-[:CONTAINS]->(tool)
            CREATE (remote)-[:CONTAINS]->(elsewhere)
            """
        )

        result = _read_situated_environment("nlr", actor_id="actor-nlr", db=DB)

        assert result["measurementStatus"] == "observed"
        assert len(result["spaces"]) == 1
        space = result["spaces"][0]
        assert space["id"] == "space:studio"
        assert space["locationEvidence"] == "LOCATED_IN"
        assert {node["id"] for node in space["nodes"]} == {
            "moment:music",
            "thing:synth",
        }
    finally:
        graph.delete()
