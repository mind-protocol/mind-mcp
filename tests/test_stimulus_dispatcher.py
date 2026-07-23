import threading
from types import SimpleNamespace
from unittest.mock import Mock

from runtime.orchestrator import dispatcher as dispatcher_module


def test_stimulus_runs_awareness_then_thought_on_one_live_engine(monkeypatch):
    events = []

    class FakeEngine:
        _awareness_tick_counter = 0
        _thought_tick_counter = 0
        _current_orientation = "observe"

        def awareness_tick(self):
            events.append("awareness")
            self._awareness_tick_counter += 1
            return SimpleNamespace(nodes_imported=1)

        def thought_tick(self):
            events.append("thought")
            self._thought_tick_counter += 1
            return SimpleNamespace(
                wm_changed=False,
                action_fired=False,
                action_node_id=None,
            )

    monkeypatch.setattr(dispatcher_module, "TwoTickEngine", FakeEngine)
    monkeypatch.setattr(dispatcher_module, "TWO_TICK_AVAILABLE", True)

    dispatcher = dispatcher_module.Dispatcher.__new__(dispatcher_module.Dispatcher)
    dispatcher._citizen_engines = {"nlr": FakeEngine()}
    dispatcher._citizen_states = {"nlr": SimpleNamespace()}
    dispatcher._citizen_tick_locks = {"nlr": threading.RLock()}
    dispatcher._last_awareness_tick = {}
    dispatcher._last_thought_tick = {}
    dispatcher._last_interoception_snapshot = {}
    dispatcher._ensure_citizen_engine = Mock()
    dispatcher._publish_interoception_snapshot = Mock()
    dispatcher._fire_conscious_action = Mock()

    result = dispatcher.process_stimulus("nlr", source="mcp:think")

    assert events == ["awareness", "thought"]
    assert result["awareness_tick"] == 1
    assert result["thought_tick"] == 1
    assert result["imported_nodes"] == 1
    dispatcher._fire_conscious_action.assert_not_called()
