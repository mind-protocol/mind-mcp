"""The wake store's contract, against a real FalkorDB.

Skipped when no database is reachable — these tests exist to catch Cypher that
only breaks against the real engine, so faking the graph would defeat them.
Each test runs in its own throwaway L1 graph and drops it afterwards.
"""

import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.orchestrator import graph_alarms  # noqa: E402


def _database_reachable() -> bool:
    try:
        graph_alarms._client().connection.execute_command("PING")
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _database_reachable(), reason="FalkorDB not reachable on FALKORDB_HOST:FALKORDB_PORT"
)


@pytest.fixture
def handle():
    """A throwaway citizen, dropped with its graph at the end of the test."""
    name = f"pytest{uuid.uuid4().hex[:8]}"
    yield name
    try:
        graph_alarms.select_graph(name).delete()
    except Exception:
        pass


def _iso(minutes_from_now: int) -> str:
    return (datetime.now() + timedelta(minutes=minutes_from_now)).isoformat()


def test_a_stored_wake_is_a_dormant_moment(handle):
    wake = graph_alarms.create_wake(
        handle=handle,
        scheduled_for=_iso(30),
        prompt="Réveil — continue la présentation",
        place="space:mind-protocol:hall",
    )

    assert wake["nodeType"] == "Moment"
    assert wake["semanticType"] == "task"
    assert wake["status"] == "dormant"

    stored = graph_alarms.list_wakes(handle)
    assert [w["id"] for w in stored] == [wake["id"]]
    assert stored[0]["prompt"] == "Réveil — continue la présentation"


def test_the_citizen_is_discovered_from_the_graph_list(handle):
    graph_alarms.create_wake(handle=handle, scheduled_for=_iso(5), prompt="Peu importe")
    assert handle in graph_alarms.list_citizen_handles()


def test_only_wakes_that_are_due_come_back(handle):
    graph_alarms.create_wake(handle=handle, scheduled_for=_iso(-2), prompt="Déjà dû")
    graph_alarms.create_wake(handle=handle, scheduled_for=_iso(60), prompt="Pas encore")

    due = graph_alarms.due_wakes(handle)
    assert [w["prompt"] for w in due] == ["Déjà dû"]


def test_a_fired_wake_stops_coming_back(handle):
    wake = graph_alarms.create_wake(handle=handle, scheduled_for=_iso(-1), prompt="Une fois")

    assert graph_alarms.mark_fired(handle, wake["id"]) is True
    assert graph_alarms.due_wakes(handle) == []
    assert graph_alarms.list_wakes(handle) == []
    assert [w["status"] for w in graph_alarms.list_wakes(handle, include_fired=True)] == ["fired"]


def test_a_rescheduled_wake_stays_dormant_at_its_next_time(handle):
    wake = graph_alarms.create_wake(
        handle=handle, scheduled_for=_iso(-1), prompt="Quotidien", repeat="daily"
    )
    next_at = datetime.now() + timedelta(days=1)

    assert graph_alarms.reschedule(handle, wake["id"], next_at) is True
    assert graph_alarms.due_wakes(handle) == []
    still_there = graph_alarms.list_wakes(handle)
    assert still_there[0]["status"] == "dormant"
    assert still_there[0]["scheduledFor"] == next_at.isoformat()


def test_an_unusable_scheduledFor_is_skipped_not_fatal(handle):
    graph_alarms.create_wake(handle=handle, scheduled_for="pas une date", prompt="Cassé")
    graph_alarms.create_wake(handle=handle, scheduled_for=_iso(-1), prompt="Sain")

    assert [w["prompt"] for w in graph_alarms.due_wakes(handle)] == ["Sain"]


def test_cancelling_a_wake_removes_it_from_the_queue(handle):
    wake = graph_alarms.create_wake(handle=handle, scheduled_for=_iso(-1), prompt="Annulé")

    assert graph_alarms.cancel_wake(handle, wake["id"]) is True
    assert graph_alarms.due_wakes(handle) == []
    assert graph_alarms.cancel_wake(handle, wake["id"]) is False  # already gone


def test_ten_wakes_due_at_once_all_come_back(handle):
    """Nothing serialises the queue: ten parallel agents get ten wakes."""
    for i in range(10):
        graph_alarms.create_wake(handle=handle, scheduled_for=_iso(-1), prompt=f"Réveil {i}")

    assert len(graph_alarms.due_wakes(handle)) == 10


def test_an_unreachable_database_yields_no_wakes_instead_of_raising(handle, monkeypatch):
    monkeypatch.setenv("FALKORDB_PORT", "6399")  # nothing listens here
    assert graph_alarms.due_wakes(handle) == []
    assert graph_alarms.list_citizen_handles() == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
