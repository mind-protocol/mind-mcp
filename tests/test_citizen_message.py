from unittest.mock import patch

from mcp.tools.citizen_message_handler import (
    TALK_SCHEMA,
    THINK_SCHEMA,
    handle_self_think,
    handle_talk,
)


def _text(result):
    return result["content"][0]["text"]


def test_talk_and_think_expose_distinct_intentions():
    assert TALK_SCHEMA["name"] == "talk"
    assert TALK_SCHEMA["inputSchema"]["required"] == ["target", "message"]
    assert THINK_SCHEMA["name"] == "think"
    assert THINK_SCHEMA["inputSchema"]["required"] == ["message"]
    assert "self-stimulates" in THINK_SCHEMA["description"]


def test_talk_delivers_to_requested_citizen(monkeypatch):
    monkeypatch.setenv("CITIZEN_HANDLE", "nlr")

    with patch(
        "runtime.orchestrator.claude_invoker.quick_call",
        return_value="Voici mon avis.",
    ) as quick_call:
        result = handle_talk({"target": "@forge", "message": "Regarde ceci."})

    quick_call.assert_called_once_with(
        "forge", "Regarde ceci.", caller_handle="nlr"
    )
    assert "@forge responds" in _text(result)


def test_think_uses_same_delivery_path_with_self_as_target(monkeypatch):
    monkeypatch.setenv("CITIZEN_HANDLE", "@nlr")

    with patch(
        "runtime.orchestrator.claude_invoker.quick_call",
        return_value="Je poursuis cette idée.",
    ) as quick_call:
        result = handle_self_think({"message": "Pense davantage à ce sujet."})

    quick_call.assert_called_once_with(
        "nlr", "Pense davantage à ce sujet.", caller_handle="nlr"
    )
    assert "Self-stimulus sent to @nlr" in _text(result)


def test_messages_must_not_be_empty(monkeypatch):
    monkeypatch.setenv("CITIZEN_HANDLE", "nlr")

    talk_result = handle_talk({"target": "forge", "message": "  "})
    think_result = handle_self_think({"message": ""})

    assert talk_result["isError"] is True
    assert think_result["isError"] is True


def test_server_exposes_new_tools_and_consult_replaces_gemini_think():
    from mcp.server import TOOL_DISPATCH, TOOL_SCHEMAS

    schemas = {schema["name"]: schema for schema in TOOL_SCHEMAS}
    assert {"talk", "think", "consult"} <= schemas.keys()
    assert TOOL_DISPATCH["think"][0] is handle_self_think
    assert TOOL_DISPATCH["talk"][0] is handle_talk
