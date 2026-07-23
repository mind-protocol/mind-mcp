from pathlib import Path


def test_cli_executable_uses_resolved_windows_shim(monkeypatch):
    from runtime.orchestrator import claude_invoker

    expected = str(Path("C:/npm/gemini.CMD"))
    monkeypatch.setattr(
        claude_invoker.shutil,
        "which",
        lambda name: expected if name == "gemini" else None,
    )

    assert claude_invoker._cli_executable("gemini") == expected
    assert claude_invoker._cli_executable("missing-cli") == "missing-cli"


def test_cli_executable_prefers_configured_path(monkeypatch, tmp_path):
    from runtime.orchestrator import claude_invoker

    configured = tmp_path / "codex.exe"
    configured.touch()
    monkeypatch.setenv("CODEX_CLI_PATH", str(configured))
    monkeypatch.setattr(claude_invoker.shutil, "which", lambda name: "wrong")

    assert claude_invoker._cli_executable("codex") == str(configured)


def test_invoke_codex_is_ephemeral_read_only_and_text_only(monkeypatch, tmp_path):
    from runtime.orchestrator import claude_invoker

    captured = {}

    class FakeProcess:
        returncode = 0

        def communicate(self, input=None, timeout=None):
            captured["input"] = input
            captured["timeout"] = timeout
            return ("Bonjour depuis le citoyen.", "")

    def fake_popen(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return FakeProcess()

    monkeypatch.setattr(claude_invoker, "_cli_executable", lambda name: "codex.exe")
    monkeypatch.setattr(claude_invoker.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(claude_invoker, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(claude_invoker, "registry_citizen_data", lambda handle: None)

    response, voice = claude_invoker.invoke_codex(
        {
            "mode": "partner",
            "source": "telegram",
            "voice_text": "Bonjour",
            "sender": "Nicolas",
            "metadata": {},
        },
        "test-session",
    )

    assert response == "Bonjour depuis le citoyen."
    assert voice is None
    assert "--ephemeral" in captured["cmd"]
    assert captured["cmd"][captured["cmd"].index("--sandbox") + 1] == "read-only"
    assert "--ignore-user-config" in captured["cmd"]
    assert "--ignore-rules" in captured["cmd"]
    assert captured["kwargs"]["encoding"] == "utf-8"
    assert "do not call tools" in captured["input"]
    assert "Return only the message" in captured["input"]
