from mcp.tools import send_handler


def test_repairs_windows_mojibake_without_touching_valid_unicode():
    corrupted = (
        "Correctif dÃ©ployÃ© â€” partenaire rÃ©solu. "
        "Jâ€™ai appelÃ© sense()."
    )
    expected = (
        "Correctif déployé — partenaire résolu. "
        "J’ai appelé sense()."
    )

    assert send_handler._repair_utf8_mojibake(corrupted) == expected
    assert send_handler._repair_utf8_mojibake(expected) == expected


def test_handle_send_repairs_message_before_dispatch(monkeypatch):
    received = {}
    monkeypatch.setattr(
        send_handler,
        "_send_telegram",
        lambda args: received.update(args) or {"content": []},
    )

    send_handler.handle_send({
        "platform": "telegram",
        "chat_id": "123",
        "message": "RÃ©veil validÃ©",
    })

    assert received["message"] == "Réveil validé"


def test_resolve_partner_uses_canonical_l4_registry(monkeypatch):
    records = {
        "nlr_ai": {"human_partner": "reyno"},
        "reyno": {
            "type": "human",
            "tg_chat_id": "1864364329",
            "tg_user_id": "ignored",
        },
    }

    monkeypatch.setattr(
        "runtime.l4.citizen_registry.get_citizen",
        lambda handle: records.get(handle),
    )

    assert send_handler._resolve_partner("nlr_ai") == {
        "partner_handle": "reyno",
        "tg_id": "1864364329",
    }


def test_send_partner_routes_without_mutating_input(monkeypatch):
    args = {
        "platform": "partner",
        "handle": "nlr_ai",
        "message": "hello",
    }
    monkeypatch.setattr(
        send_handler,
        "_resolve_partner",
        lambda _handle: {
            "partner_handle": "reyno",
            "tg_id": "1864364329",
        },
    )
    sent = {}
    monkeypatch.setattr(
        send_handler,
        "_send_telegram",
        lambda routed: sent.update(routed) or {"content": []},
    )

    send_handler._send_partner(args)

    assert args == {
        "platform": "partner",
        "handle": "nlr_ai",
        "message": "hello",
    }
    assert sent["platform"] == "telegram"
    assert sent["chat_id"] == "1864364329"


def test_mind_service_identity_uses_configured_human_fallback(monkeypatch):
    monkeypatch.setenv("MIND_DEFAULT_HUMAN_CHAT_ID", "12345")
    monkeypatch.setattr(send_handler, "_resolve_partner", lambda _handle: {})
    sent = {}
    monkeypatch.setattr(
        send_handler,
        "_send_telegram",
        lambda routed: sent.update(routed) or {"content": []},
    )

    send_handler._send_partner({
        "platform": "partner",
        "handle": "mind",
        "message": "system wake",
    })

    assert sent["platform"] == "telegram"
    assert sent["chat_id"] == "12345"
