from types import SimpleNamespace

from mcp import server


def test_sense_dispatch_reloads_the_handler_before_each_call(monkeypatch):
    calls = []
    current_module = SimpleNamespace(
        handle_sense=lambda arguments, ctx: {
            "arguments": arguments,
            "ctx": ctx,
            "version": "fresh",
        }
    )

    monkeypatch.setattr(server.importlib, "invalidate_caches", lambda: calls.append("invalidate"))
    monkeypatch.setattr(
        server.importlib,
        "reload",
        lambda module: calls.append(module) or current_module,
    )

    handler, needs_ctx = server.TOOL_DISPATCH["sense"]
    ctx = object()
    result = handler({"handle": "nlr"}, ctx)

    assert needs_ctx is True
    assert calls == ["invalidate", server.sense_handler_module]
    assert result == {
        "arguments": {"handle": "nlr"},
        "ctx": ctx,
        "version": "fresh",
    }
