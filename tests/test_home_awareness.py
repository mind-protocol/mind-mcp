from home_server import _configured_citizen_handles
from runtime.cognition.graph_reader_for_awareness_tick import citizen_actor_ids


def test_explicit_http_citizen_is_loaded_without_a_filesystem_profile(monkeypatch):
    monkeypatch.setenv("MIND_HTTP_CITIZEN", "nlr_ai")
    monkeypatch.delenv("MIND_CITIZEN_HANDLE", raising=False)
    monkeypatch.delenv("MIND_CITIZEN_HANDLES", raising=False)

    assert _configured_citizen_handles() == ["nlr_ai"]


def test_l3_actor_aliases_cover_the_body_suit_projection():
    assert citizen_actor_ids("nlr_ai") == [
        "nlr_ai",
        "CITIZEN_nlr_ai",
        "actor-nlr-ai",
        "l3-actor-nlr-ai",
    ]
