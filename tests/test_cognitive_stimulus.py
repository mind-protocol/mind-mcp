import json
from unittest.mock import patch

import pytest

from mcp.tools.cognitive_stimulus import (
    CognitiveStimulusError,
    trigger_cognitive_ticks,
)


class _Response:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return self._body


def test_bridge_sends_stimulus_to_single_home_server_tick_owner(monkeypatch):
    monkeypatch.setenv("MIND_HOME_SERVER_URL", "http://127.0.0.1:8765")
    with patch(
        "mcp.tools.cognitive_stimulus.urlopen",
        return_value=_Response({
            "status": "processed",
            "moment_id": "moment:mcp_stimulus:1",
            "ticks": {"awareness_tick": 4, "thought_tick": 3},
        }),
    ) as open_url:
        result = trigger_cognitive_ticks(
            target="@nlr",
            content="Observe ceci.",
            source="mcp:think",
            caller="@nlr",
        )

    request = open_url.call_args.args[0]
    payload = json.loads(request.data)
    assert request.full_url == "http://127.0.0.1:8765/api/cognition/stimulus"
    assert payload["target_handle"] == "nlr"
    assert payload["caller_handle"] == "nlr"
    assert result["ticks"]["thought_tick"] == 3


def test_bridge_rejects_non_processed_response():
    with patch(
        "mcp.tools.cognitive_stimulus.urlopen",
        return_value=_Response({"status": "ignored", "detail": "no engine"}),
    ):
        with pytest.raises(CognitiveStimulusError, match="no engine"):
            trigger_cognitive_ticks(
                target="nlr",
                content="Observe ceci.",
                source="mcp:think",
            )
