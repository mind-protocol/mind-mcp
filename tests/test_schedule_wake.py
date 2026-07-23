import json
from datetime import datetime
from unittest.mock import patch

from mcp.tools import alarm_handler
from mcp.tools.schedule_wake_handler import handle_schedule_wake
from runtime.orchestrator.alarm_watcher import AlarmWatcher


def test_schedule_wake_persists_prompt_and_optional_place(tmp_path, monkeypatch):
    alarm_file = tmp_path / "system" / "alarms.jsonl"
    monkeypatch.setattr(alarm_handler, "_get_alarms_file", lambda handle: alarm_file)

    result = handle_schedule_wake({
        "time": "2099-01-02T09:30:00",
        "prompt": "Review the broadcast brief",
        "place": "space:mind-protocol:hall",
    })

    alarm = json.loads(alarm_file.read_text(encoding="utf-8").strip())
    assert result.get("isError") is not True
    assert alarm["prompt"] == "Review the broadcast brief"
    assert alarm["place"] == "space:mind-protocol:hall"
    assert alarm["repeat"] is None
    assert alarm["active"] is True


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
