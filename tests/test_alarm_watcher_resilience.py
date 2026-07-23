"""Wakes live in the L1 graph, and one broken citizen must never silence the others.

Two failure modes are pinned here:

  - A citizen whose graph is unreachable or malformed used to abort the entire scan,
    every 30s, for everyone.
  - A delivery that raises used to consume the wake and stop the scan.

The graph itself is faked: these tests are about the watcher's fault isolation, not
about FalkorDB. See test_graph_alarms.py for the store's own contract.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.orchestrator import graph_alarms  # noqa: E402
from runtime.orchestrator.alarm_watcher import AlarmWatcher  # noqa: E402


def _wake(wake_id: str, prompt: str, minutes_ago: int = 1, repeat: str = "once") -> dict:
    return {
        "id": wake_id,
        "nodeType": "Moment",
        "semanticType": "task",
        "prompt": prompt,
        "scheduledFor": (datetime.now() - timedelta(minutes=minutes_ago)).isoformat(),
        "status": "dormant",
        "repeat": repeat,
        "place": "",
    }


@pytest.fixture
def sovereign():
    """Fire every wake in autonomous mode, whatever the citizen's tier."""
    with patch(
        "runtime.citizens.autonomy_gate._get_citizen_tier_and_level",
        return_value=(3, 7),
    ):
        yield


def test_wakes_are_read_from_the_citizen_l1_graph(sovereign):
    fired = []
    watcher = AlarmWatcher(enqueue_fn=fired.append)

    with patch.object(graph_alarms, "list_citizen_handles", return_value=["nlr"]), \
         patch.object(graph_alarms, "due_wakes", return_value=[_wake("wake-1", "Réveil — travaille")]), \
         patch.object(graph_alarms, "mark_fired", return_value=True) as mark:
        watcher._scan_alarms()

    assert [item["metadata"]["alarm_id"] for item in fired] == ["wake-1"]
    assert fired[0]["metadata"]["citizen_handle"] == "nlr"
    mark.assert_called_once()


def test_one_unreachable_graph_does_not_silence_the_others(sovereign):
    """A citizen whose graph explodes costs only that citizen."""
    fired = []
    watcher = AlarmWatcher(enqueue_fn=fired.append)

    def due(handle, now=None):
        if handle == "broken":
            raise RuntimeError("connection refused")
        return [_wake("wake-nlr", "Réveil parallèle")]

    with patch.object(graph_alarms, "list_citizen_handles", return_value=["broken", "nlr"]), \
         patch.object(graph_alarms, "due_wakes", side_effect=due), \
         patch.object(graph_alarms, "mark_fired", return_value=True):
        watcher._scan_alarms()

    assert [item["metadata"]["alarm_id"] for item in fired] == ["wake-nlr"]


def test_failed_delivery_leaves_the_wake_dormant(sovereign):
    """A wake that could not be delivered is not consumed, and does not stop the scan."""
    delivered = []

    def enqueue(item):
        if item["metadata"]["alarm_id"] == "wake-boom":
            raise RuntimeError("telegram down")
        delivered.append(item["metadata"]["alarm_id"])

    watcher = AlarmWatcher(enqueue_fn=enqueue)
    wakes = [_wake("wake-boom", "Celui qui explose"), _wake("wake-ok", "Celui qui passe")]

    with patch.object(graph_alarms, "list_citizen_handles", return_value=["nlr"]), \
         patch.object(graph_alarms, "due_wakes", return_value=wakes), \
         patch.object(graph_alarms, "mark_fired", return_value=True) as mark:
        watcher._scan_alarms()

    assert delivered == ["wake-ok"]
    # Only the delivered wake was consumed; the failed one stays dormant for the retry.
    assert [call.args[1] for call in mark.call_args_list] == ["wake-ok"]


def test_a_repeating_wake_is_rescheduled_not_consumed(sovereign):
    watcher = AlarmWatcher(enqueue_fn=lambda item: None)
    wake = _wake("wake-daily", "Réveil quotidien", repeat="daily")

    with patch.object(graph_alarms, "list_citizen_handles", return_value=["nlr"]), \
         patch.object(graph_alarms, "due_wakes", return_value=[wake]), \
         patch.object(graph_alarms, "mark_fired") as mark, \
         patch.object(graph_alarms, "reschedule", return_value=True) as reschedule:
        watcher._scan_alarms()

    mark.assert_not_called()
    handle, wake_id, next_at = reschedule.call_args.args
    assert (handle, wake_id) == ("nlr", "wake-daily")
    assert next_at > datetime.now()


def test_parallel_wakes_all_fire_in_one_scan(sovereign):
    """No lock, no serialisation: every due wake fires in the same scan."""
    fired = []
    watcher = AlarmWatcher(enqueue_fn=fired.append)
    wakes = [_wake(f"wake-{i}", f"Réveil parallèle {i}") for i in range(5)]

    with patch.object(graph_alarms, "list_citizen_handles", return_value=["nlr"]), \
         patch.object(graph_alarms, "due_wakes", return_value=wakes), \
         patch.object(graph_alarms, "mark_fired", return_value=True):
        watcher._scan_alarms()

    assert len(fired) == 5


def test_a_wake_never_fires_twice_in_one_session(sovereign):
    """The graph marks it fired; the in-memory set is the second line of defence."""
    fired = []
    watcher = AlarmWatcher(enqueue_fn=fired.append)
    wake = _wake("wake-once", "Une seule fois")

    with patch.object(graph_alarms, "list_citizen_handles", return_value=["nlr"]), \
         patch.object(graph_alarms, "due_wakes", return_value=[wake]), \
         patch.object(graph_alarms, "mark_fired", return_value=True):
        watcher._scan_alarms()
        watcher._scan_alarms()  # the store failed to update — the watcher must still hold

    assert len(fired) == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
