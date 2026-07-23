import json

from runtime.orchestrator import claude_invoker


def test_sense_snapshot_for_wake_calls_sense_and_bounds_spaces(monkeypatch):
    calls = []
    payload = {
        "id": "workspace-actor-nlr",
        "version": 51,
        "activeTask": {"id": "task-export"},
        "questionLedger": {"large": "must not enter the prompt"},
        "situatedEnvironment": {
            "measurementStatus": "observed",
            "spaces": [
                {
                    "id": "space-home",
                    "nodes": [{"id": f"node-{index}"} for index in range(30)],
                }
            ],
        },
    }

    def fake_sense(args, ctx=None):
        calls.append(args)
        return {
            "content": [{
                "type": "text",
                "text": json.dumps(payload),
            }],
        }

    monkeypatch.setattr("mcp.tools.sense_handler.handle_sense", fake_sense)

    snapshot = json.loads(
        claude_invoker._sense_snapshot_for_wake("nlr_ai")
    )

    assert calls == [{"handle": "nlr_ai"}]
    assert snapshot["activeTask"]["id"] == "task-export"
    assert "questionLedger" not in snapshot
    assert len(snapshot["situatedEnvironment"]["spaces"][0]["nodes"]) == 20


def test_citizen_prompt_is_grounded_in_automatic_sense(monkeypatch):
    monkeypatch.setattr(
        claude_invoker,
        "_sense_snapshot_for_wake",
        lambda handle: json.dumps({
            "citizen": handle,
            "activeTask": {"id": "task-export"},
        }),
    )
    monkeypatch.setattr(
        claude_invoker,
        "build_citizen_prompt",
        lambda citizen, task_text, session_id, mode, cognitive_context="": task_text,
    )

    prompt = claude_invoker._build_prompt(
        request={},
        session_id="session-1",
        mode="partner",
        voice_text="did you call sense()?",
        sender="NLR",
        is_citizen_session=True,
        citizen_data={"handle": "nlr_ai"},
        is_task=False,
        task_cwd=None,
        metadata={},
    )

    assert "called `sense()` for this wake" in prompt
    assert '"id": "task-export"' in prompt
    assert "did you call sense()?" in prompt
