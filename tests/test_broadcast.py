from unittest.mock import patch

from mcp.tools.broadcast_handler import DEFAULT_BROADCAST_CHAT_ID, handle_broadcast


def test_broadcast_targets_the_fixed_telegram_channel(monkeypatch):
    monkeypatch.delenv("MIND_TELEGRAM_BROADCAST_CHAT_ID", raising=False)
    with patch("mcp.tools.broadcast_handler.handle_send") as send:
        send.return_value = {"content": [{"type": "text", "text": "sent"}]}
        result = handle_broadcast({
            "title": "Release ready",
            "context": "The release needed final verification.",
            "message": "The release passed its checks.",
            "impact": "Agents can now use the new workflow safely.",
            "status": "Validated.",
            "next_step": "Monitor the rollout.",
            "category": "milestone",
        })

    assert result["content"][0]["text"] == "sent"
    send.assert_called_once_with({
        "platform": "telegram",
        "chat_id": DEFAULT_BROADCAST_CHAT_ID,
        "message": (
            "📣 *MILESTONE*\n\n*Release ready*\n\n"
            "*Context*\nThe release needed final verification.\n\n"
            "*What changed*\nThe release passed its checks.\n\n"
            "*Why it matters*\nAgents can now use the new workflow safely.\n\n"
            "*Status*\nValidated.\n\n*Next step*\nMonitor the rollout."
        ),
        "handle": "mind",
    })


def test_broadcast_rejects_an_empty_announcement():
    result = handle_broadcast({"message": "  "})
    assert "title, context, message, impact, status" in result["content"][0]["text"]
