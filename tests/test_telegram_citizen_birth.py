from types import SimpleNamespace

import pytest


def test_birth_creates_l4_l1_bond_and_engine(monkeypatch):
    from runtime.onboarding import telegram_citizen_birth as birth

    calls = []
    citizens = {}

    monkeypatch.setattr(birth.registry, "citizen_for_human", lambda **_kwargs: None)
    monkeypatch.setattr(
        birth.registry,
        "get_citizen",
        lambda handle: citizens.get(handle),
    )
    monkeypatch.setattr(
        birth.registry,
        "upsert_human",
        lambda handle, **fields: calls.append(("human", handle, fields)) or handle,
    )

    def upsert_citizen(handle, **fields):
        citizens[handle] = {"handle": handle, **fields}
        calls.append(("citizen", handle, fields))
        return handle

    monkeypatch.setattr(birth.registry, "upsert_citizen", upsert_citizen)
    monkeypatch.setattr(
        birth.registry,
        "activate_bilateral_bond",
        lambda human, citizen: calls.append(("bond", human, citizen))
        or f"bond:{human}:{citizen}",
    )
    monkeypatch.setattr(
        birth,
        "ensure_citizen_l1",
        lambda handle, **kwargs: calls.append(("l1", handle, kwargs)),
    )
    monkeypatch.setattr(
        birth,
        "check_l1_exists",
        lambda handle, graph_name=None: True,
    )
    monkeypatch.setattr(
        birth,
        "_mirror_identity_to_l3",
        lambda *args: calls.append(("l3", *args)),
    )
    dispatcher = SimpleNamespace(
        bulk_load_citizen_engines=lambda handles: calls.append(("engine", handles))
    )

    result = birth.create_bonded_citizen(
        name="Nervo",
        intent="Curieux, rigoureux et bienveillant, il aide à comprendre et agir.",
        sender_name="Nicolas",
        user_id="1864364329",
        username="reyno",
        chat_id="1864364329",
        dispatcher=dispatcher,
    )

    assert result.created is True
    assert result.handle == "nervo"
    assert result.l1_graph == "l1_nervo_graph"
    assert [call[0] for call in calls] == [
        "human",
        "l1",
        "citizen",
        "bond",
        "l3",
        "engine",
    ]
    assert calls[1][2]["graph_name"] == "l1_nervo_graph"


def test_birth_preserves_one_to_one_existing_bond(monkeypatch):
    from runtime.onboarding import telegram_citizen_birth as birth

    monkeypatch.setattr(
        birth.registry,
        "citizen_for_human",
        lambda **_kwargs: "nlr_ai",
    )
    monkeypatch.setattr(
        birth.registry,
        "get_citizen",
        lambda _handle: {"name": "NLR AI", "l1_graph": "l1_nlr_ai_graph"},
    )

    result = birth.create_bonded_citizen(
        name="Another",
        intent="Un autre citoyen qui ne doit pas être créé car le lien existe.",
        sender_name="Nicolas",
        user_id="1864364329",
        username="reyno",
    )

    assert result.created is False
    assert result.handle == "nlr_ai"


def test_birth_rejects_short_intent():
    from runtime.onboarding.telegram_citizen_birth import create_bonded_citizen

    with pytest.raises(ValueError, match="20 caractères"):
        create_bonded_citizen(
            name="Nervo",
            intent="Curieux",
            sender_name="Nicolas",
            user_id="1",
        )


def test_create_command_parses_and_confirms(monkeypatch):
    from runtime.bridges import telegram_bridge
    from runtime.onboarding import telegram_citizen_birth as birth

    sent = []
    monkeypatch.setattr(
        telegram_bridge,
        "send_message",
        lambda text, chat_id="", **kwargs: sent.append((text, chat_id, kwargs)),
    )
    monkeypatch.setattr(
        birth,
        "create_bonded_citizen",
        lambda **_kwargs: birth.TelegramBirthResult(
            created=True,
            handle="nervo",
            name="Nervo",
            bond_id="bond:reyno:nervo",
            l1_graph="l1_nervo_graph",
        ),
    )

    telegram_bridge._handle_create_citizen(
        "42",
        "Nicolas",
        "42",
        "reyno",
        "/create Nervo | Curieux, rigoureux et bienveillant pour comprendre le monde.",
    )

    assert len(sent) == 1
    assert "Nervo (@nervo) est né" in sent[0][0]
