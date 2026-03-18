"""
Citizen Wake — L1 stimulus injection + audit trail.

When a citizen is mentioned (Discord, Telegram, etc.):
1. Inject L1 stimulus into the citizen's brain (instant)
2. Write JSONL audit trail (for compliance/debugging only — NOT source of truth)

The L3 graph is the source of truth for mentions (Moment + LINK computed_type=mention).
The graph_enricher creates those. This module handles the L1 side.

The JSONL files are append-only audit logs. They are NOT read for routing or wake
decisions. The wake_primers.py script reads them temporarily as a bridge — that
will be replaced by L3 graph queries when the consciousness threshold is built.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("mind.citizen_wake")

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "shrine" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
CITIZENS_DIR = ROOT / "citizens"

# Audit trail files — append-only, NOT source of truth
MENTIONS_AUDIT = STATE_DIR / "citizen_mentions.jsonl"
CHANNEL_EVENTS_AUDIT = STATE_DIR / "citizen_channel_events.jsonl"
NOTIFICATIONS_AUDIT = STATE_DIR / "citizen_notifications.jsonl"

# Ensure runtime is importable
sys.path.insert(0, str(ROOT))


# Global dispatcher reference — set by discord_bridge or MCP server
_dispatcher = None


def set_dispatcher(dispatcher) -> None:
    """Register the running Dispatcher for instant stimulus injection."""
    global _dispatcher
    _dispatcher = dispatcher


def _inject_l1_stimulus(citizen_handle: str, content: str, origin: str = "", source: str = "social") -> bool:
    """Inject a stimulus into a citizen's L1 brain.

    Strategy:
    1. If a Dispatcher is running → use its inject_stimulus()
    2. Fallback → direct load/inject/checkpoint (standalone mode)

    Returns True if injection succeeded, False if degraded gracefully.
    """
    # Strategy 1: use running dispatcher
    if _dispatcher is not None:
        try:
            _dispatcher.inject_stimulus(
                citizen_handle,
                content,
                source=source,
                is_social=True,
            )
            logger.info(f"L1 stimulus via dispatcher: @{citizen_handle} (source={source})")
            return True
        except Exception as e:
            logger.warning(f"Dispatcher inject failed for @{citizen_handle}: {e}")

    # Strategy 2: direct injection
    try:
        from runtime.cognition.stimulus_router import StimulusRouter, IncomingEvent
        from runtime.cognition.tick_runner_l1_cognitive_engine import L1CognitiveTickRunner
        from runtime.cognition.falkordb_checkpointer import FalkorDBBrainCheckpointer

        checkpointer = FalkorDBBrainCheckpointer(citizen_handle)
        if not checkpointer.connect():
            logger.debug(f"No FalkorDB for @{citizen_handle}, skipping L1 injection")
            return False

        state = checkpointer.load_state()
        if not state:
            logger.debug(f"No brain state for @{citizen_handle}")
            return False

        runner = L1CognitiveTickRunner(state)
        router = StimulusRouter(citizen_handle)

        event = IncomingEvent(
            content=content,
            source=source,
            citizen_handle=citizen_handle,
            is_social=True,
        )
        stimulus = router.route(event)
        runner.run_tick(stimulus=stimulus)

        if checkpointer._connected:
            checkpointer.flush_all(state)

        logger.info(f"L1 injected (direct): @{citizen_handle} (source={source})")
        return True

    except ImportError as e:
        logger.debug(f"L1 injection unavailable: {e}")
        return False
    except Exception as e:
        logger.warning(f"L1 injection failed for @{citizen_handle}: {e}")
        return False


def _audit_log(filepath: Path, entry: dict):
    """Append to audit trail (compliance/debugging only)."""
    try:
        with open(filepath, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError as e:
        logger.debug(f"Audit log write failed: {e}")


def mention_citizen(by_handle: str, mentioned_handle: str, context: str) -> bool:
    """Record a mention + inject L1 stimulus.

    The L3 graph (Moment + LINK computed_type=mention) is the source of truth.
    This function handles L1 injection + writes audit trail.
    """
    # 1. Audit trail
    _audit_log(MENTIONS_AUDIT, {
        "by": by_handle,
        "mentioned": mentioned_handle,
        "context": context,
        "timestamp": datetime.now().isoformat(),
    })

    # 2. L1 stimulus injection
    _inject_l1_stimulus(
        mentioned_handle,
        f"@{by_handle} mentioned you: {context[:300]}",
        origin=by_handle,
    )

    logger.info(f"Mention: @{by_handle} → @{mentioned_handle}")
    return True


def notify_channel_message(from_handle: str, target_handle: str, channel: str, message: str) -> bool:
    """Notify a citizen about a channel message + inject L1 stimulus.

    The L3 graph is the source of truth. This handles L1 + audit trail.
    """
    # 1. Audit trail
    _audit_log(CHANNEL_EVENTS_AUDIT, {
        "from": from_handle,
        "target": target_handle,
        "channel": channel,
        "message": message[:500],
        "timestamp": datetime.now().isoformat(),
    })

    _audit_log(NOTIFICATIONS_AUDIT, {
        "type": "channel",
        "target": target_handle,
        "title": f"#{channel} — @{from_handle}",
        "body": message[:200],
        "timestamp": datetime.now().isoformat(),
    })

    # 2. L1 stimulus injection
    _inject_l1_stimulus(
        target_handle,
        f"Message from @{from_handle} in #{channel}: {message[:300]}",
        origin=from_handle,
    )

    logger.info(f"Channel event: @{from_handle} → @{target_handle} in #{channel}")
    return True
