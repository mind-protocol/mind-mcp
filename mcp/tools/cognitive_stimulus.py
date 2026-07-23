"""Bridge MCP tool events to the single live cognitive tick owner."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class CognitiveStimulusError(RuntimeError):
    """Raised when a tool event could not reach the live cognitive engine."""


def detect_citizen() -> str:
    """Resolve the current citizen from explicit runtime identity signals."""
    handle = _normalize_handle(os.getenv("CITIZEN_HANDLE"))
    if handle:
        return handle

    parts = Path.cwd().parts
    for index, part in enumerate(parts):
        if part.lower() == "citizens" and index + 1 < len(parts):
            return _normalize_handle(parts[index + 1])

    actor_id = _normalize_handle(os.getenv("ACTOR_ID"))
    for prefix in ("citizen_", "agent_", "actor_"):
        if actor_id.startswith(prefix):
            return actor_id[len(prefix):]
    return actor_id or "mind"


def trigger_cognitive_ticks(
    *,
    target: str,
    content: str,
    source: str,
    caller: str | None = None,
    metadata: Dict[str, Any] | None = None,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """Persist one stimulus Moment and synchronously run awareness + thought."""
    normalized_target = _normalize_handle(target)
    normalized_content = str(content or "").strip()
    if not normalized_target:
        raise CognitiveStimulusError("stimulus target is required")
    if not normalized_content:
        raise CognitiveStimulusError("stimulus content is required")

    base_url = os.environ.get(
        "MIND_HOME_SERVER_URL", "http://127.0.0.1:8765"
    ).rstrip("/")
    payload = {
        "target_handle": normalized_target,
        "caller_handle": _normalize_handle(caller) or detect_citizen(),
        "content": normalized_content,
        "source": str(source or "mcp").strip() or "mcp",
        "metadata": metadata or {},
    }
    request = Request(
        f"{base_url}/api/cognition/stimulus",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise CognitiveStimulusError(
            f"Home Server rejected the stimulus ({exc.code}): {detail}"
        ) from exc
    except (URLError, OSError, TimeoutError) as exc:
        raise CognitiveStimulusError(
            f"Home Server cognitive ingress is unavailable: {exc}"
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CognitiveStimulusError(
            "Home Server returned an invalid cognitive tick response"
        ) from exc

    if result.get("status") != "processed":
        raise CognitiveStimulusError(
            str(result.get("detail") or "cognitive stimulus was not processed")
        )
    return result


def _normalize_handle(value: Any) -> str:
    return str(value or "").strip().lstrip("@").lower()
