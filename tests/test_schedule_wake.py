from datetime import datetime
from unittest.mock import patch

from mcp.tools import alarm_handler
from mcp.tools.schedule_wake_handler import handle_schedule_wake
from runtime.orchestrator.alarm_watcher import AlarmWatcher


def test_schedule_wake_stores_prompt_and_optional_place_in_the_l1_graph():
    stored = {}

    def fake_create_wake(**kwargs):
        stored.update(kwargs)
        return {
            "id": "wake-test",
            "prompt": kwargs["prompt"],
            "place": kwargs["place"] or "",
            "createdAt": datetime.now().isoformat(),
        }

    with patch.object(alarm_handler.graph_alarms, "create_wake", side_effect=fake_create_wake):
        result = handle_schedule_wake({
            "time": "2099-01-02T09:30:00",
            "prompt": "Review the broadcast brief",
            "place": "space:mind-protocol:hall",
        })

    assert result.get("isError") is not True
    assert stored["handle"] == "system"
    assert stored["prompt"] == "Review the broadcast brief"
    assert stored["place"] == "space:mind-protocol:hall"
    assert stored["repeat"] == "once"
    assert stored["scheduled_for"].startswith("2099-01-02T09:30")


def test_hhmm_in_the_past_schedules_the_next_occurrence():
    parsed = datetime.fromisoformat(alarm_handler._parse_time("00:00"))
    assert parsed > datetime.now()


def test_alarm_watcher_forwards_prompt_and_place():
    queued = []
    watcher = AlarmWatcher(enqueue_fn=queued.append)
    alarm = {
        "id": "alarm_test",
        "prompt": "Continue the presentation",
        "place": "space:mind-protocol:hall",
    }
    with patch(
        "runtime.citizens.autonomy_gate._get_citizen_tier_and_level",
        return_value=(3, 7),
    ):
        watcher._fire_alarm("mind", alarm)

    assert queued[0]["voice_text"] == (
        "[WAKE @ space:mind-protocol:hall] Continue the presentation"
    )
    assert queued[0]["metadata"]["wake_prompt"] == "Continue the presentation"
    assert queued[0]["metadata"]["place"] == "space:mind-protocol:hall"
