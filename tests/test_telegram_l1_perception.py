from runtime.cognition.models import CitizenCognitiveState
from runtime.cognition.two_tick_engine import awareness_tick


def test_awareness_imports_direct_telegram_message_with_provenance():
    state = CitizenCognitiveState(citizen_id="nlr")

    def read_graph(_citizen_id):
        return [{
            "node": {
                "id": "moment_telegram_123",
                "node_type": "memory",
                "content": "Bonjour, voici mon message",
                "energy": 1.2,
                "weight": 0.2,
                "stability": 0.1,
                "valence": 0.0,
                "relevance": 1.0,
                "partner_relevance": 1.0,
                "origin_citizen": "reyno",
                "origin_date": 1_784_830_000.0,
            },
            "links": [],
        }]

    result = awareness_tick(state, read_graph, tick=1)

    assert result.nodes_imported == 1
    perceived = state.nodes["moment_telegram_123"]
    assert perceived.content == "Bonjour, voici mon message"
    assert perceived.origin_citizen == "reyno"
    assert perceived.origin_date == 1_784_830_000.0
    assert perceived.partner_relevance == 1.0
    assert perceived.energy > 0.0


def test_graph_enricher_uses_stable_event_id_and_direct_recipient(monkeypatch):
    from scripts import graph_enricher

    class FakeResult:
        result_set = []

    class FakeGraph:
        def __init__(self):
            self.calls = []

        def query(self, query, params=None):
            self.calls.append((query, params or {}))
            return FakeResult()

    graph = FakeGraph()
    monkeypatch.setattr(graph_enricher, "_get_graph", lambda: graph)
    monkeypatch.setattr(
        graph_enricher,
        "_stimulate_space_citizens",
        lambda *_args, **_kwargs: None,
    )

    kwargs = dict(
        platform="telegram",
        channel_id="1864364329",
        channel_name="dm_1864364329",
        author_name="Nicolas",
        author_handle="reyno",
        content="Salut mon citoyen",
        recipient_handles=["nlr"],
        event_id="4242:73",
        platform_user_id="1864364329",
    )
    first_id = graph_enricher.on_message(**kwargs)
    second_id = graph_enricher.on_message(**kwargs)

    assert first_id == second_id
    delivery_calls = [
        (query, params) for query, params in graph.calls
        if "perception_energy" in query
    ]
    assert len(delivery_calls) == 2
    assert all(params["handle"] == "nlr" for _, params in delivery_calls)
    assert all(params["event_id"] == "4242:73" for _, params in delivery_calls)


def test_telegram_routes_graph_event_to_l1_before_dispatch(monkeypatch):
    from runtime.bridges import telegram_bridge
    from scripts import citizen_wake, graph_enricher

    seen = []
    enqueued = []

    monkeypatch.setattr(telegram_bridge, "_enqueue_fn", enqueued.append)
    monkeypatch.setattr(telegram_bridge, "check_rate_limit", lambda *_: None)
    monkeypatch.setattr(telegram_bridge, "_log_message", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(telegram_bridge, "send_typing", lambda *_: None)
    monkeypatch.setattr(
        telegram_bridge,
        "_resolve_partner_for_sender",
        lambda *_args, **_kwargs: "nlr",
    )
    monkeypatch.setattr(
        graph_enricher,
        "on_message",
        lambda **kwargs: seen.append(("graph", kwargs)) or "moment_stable",
    )
    monkeypatch.setattr(
        citizen_wake,
        "_inject_l1_stimulus",
        lambda *args, **kwargs: seen.append(("l1", args, kwargs)) or True,
    )

    handled = telegram_bridge.process_update({
        "update_id": 4242,
        "message": {
            "message_id": 73,
            "from": {"id": 1864364329, "first_name": "Nicolas", "username": "reyno"},
            "chat": {"id": 1864364329, "type": "private"},
            "text": "Salut mon citoyen",
        },
    })

    assert handled is True
    assert [entry[0] for entry in seen] == ["graph", "l1"]
    assert seen[0][1]["recipient_handles"] == ["nlr"]
    assert seen[0][1]["event_id"] == "4242:73"
    assert enqueued[0]["metadata"]["citizen_handle"] == "nlr"
    assert enqueued[0]["metadata"]["l1_perceived"] is True
    assert enqueued[0]["metadata"]["l1_moment_id"] == "moment_stable"
