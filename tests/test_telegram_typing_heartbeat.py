import threading

from runtime.orchestrator import dispatcher


def test_typing_heartbeat_repeats_until_stopped():
    stop_event = threading.Event()
    calls = []

    def send_typing(chat_id):
        calls.append(chat_id)
        if len(calls) == 3:
            stop_event.set()

    dispatcher._telegram_typing_heartbeat(
        "1864364329",
        stop_event,
        interval=0.001,
        send_typing_fn=send_typing,
    )

    assert calls == ["1864364329"] * 3


def test_dispatcher_starts_and_stops_telegram_heartbeat(monkeypatch):
    instance = dispatcher.Dispatcher.__new__(dispatcher.Dispatcher)
    instance._telegram_typing_sessions = {}
    started = threading.Event()

    def heartbeat(_chat_id, stop_event):
        started.set()
        stop_event.wait(1)

    monkeypatch.setattr(dispatcher, "_telegram_typing_heartbeat", heartbeat)

    instance._start_telegram_typing(
        "session-1",
        {
            "source": "telegram",
            "metadata": {"chat_id": "1864364329"},
        },
    )

    assert started.wait(1)
    stop_event, _thread = instance._telegram_typing_sessions["session-1"]
    instance._stop_telegram_typing("session-1")

    assert stop_event.is_set()
    assert "session-1" not in instance._telegram_typing_sessions


def test_non_telegram_session_does_not_start_heartbeat():
    instance = dispatcher.Dispatcher.__new__(dispatcher.Dispatcher)
    instance._telegram_typing_sessions = {}

    instance._start_telegram_typing(
        "session-1",
        {
            "source": "whatsapp",
            "metadata": {"chat_id": "chat"},
        },
    )

    assert instance._telegram_typing_sessions == {}
