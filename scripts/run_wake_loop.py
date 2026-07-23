"""Standalone wake-delivery loop.

Runs the AlarmWatcher and delivers each fired wake straight to Telegram. This
guarantees a scheduled wake reaches the human WITHOUT requiring the full
orchestrator daemon (Dispatcher + LLM invocation), whose delivery depends on
Claude Code CLI / account health that may not be available.

Side effect that matters: because it runs the AlarmWatcher, it keeps the
orchestrator heartbeat fresh — so ``schedule_wake`` / ``alarm`` stop emitting the
"WILL NOT FIRE" warning while this loop is up.

Usage:
    python scripts/run_wake_loop.py

Env:
    WAKE_NOTIFY_CHAT_ID   Telegram chat to notify (default: NICOLAS_CHAT_ID).
    MIND_CITIZENS_DIR     Where alarms.jsonl live (shared with schedule_wake).

Note: run exactly ONE delivery loop. Two AlarmWatchers (this + home_server)
would double-fire, since fired-id dedupe is per-process.
"""

from __future__ import annotations

import logging
import os
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.orchestrator.alarm_watcher import AlarmWatcher  # noqa: E402
from mcp.tools.send_handler import handle_send, NICOLAS_CHAT_ID  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("wake_loop")

NOTIFY_CHAT_ID = os.environ.get("WAKE_NOTIFY_CHAT_ID", NICOLAS_CHAT_ID)


def deliver(item: dict) -> None:
    """Deliver one fired wake to Telegram. Never raise — a bad item must not kill the loop."""
    meta = (item or {}).get("metadata", {}) or {}
    handle = meta.get("citizen_handle", "system")
    prompt = (
        meta.get("wake_prompt")
        or item.get("voice_text")
        or meta.get("alarm_reason")
        or "Scheduled wake"
    )
    try:
        res = handle_send({
            "platform": "telegram",
            "chat_id": NOTIFY_CHAT_ID,
            "message": f"⏰ [WAKE @{handle}] {prompt}",
            "handle": handle,
        })
        text = res.get("content", [{}])[0].get("text", "") if isinstance(res, dict) else str(res)
        logger.info(f"Delivered wake for @{handle}: {text}")
    except Exception as exc:
        logger.exception(f"Failed to deliver wake for @{handle}: {exc}")


def main() -> None:
    watcher = AlarmWatcher(enqueue_fn=deliver)
    watcher.start()
    logger.info(f"Wake loop started — delivering wakes to Telegram chat {NOTIFY_CHAT_ID}.")

    stop = {"flag": False}

    def _handle_signal(*_a):
        stop["flag"] = True

    for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
        if sig is not None:
            try:
                signal.signal(sig, _handle_signal)
            except Exception:
                pass

    try:
        while not stop["flag"]:
            time.sleep(1)
    finally:
        watcher.stop()
        logger.info("Wake loop stopped.")


if __name__ == "__main__":
    main()
