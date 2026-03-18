#!/usr/bin/env python3
"""WAHA Watchdog — monitors WhatsApp bridge health, auto-restarts, creates tasks.

Run: python3 scripts/waha_watchdog.py
Cron: */5 * * * * python3 scripts/waha_watchdog.py

Checks every run:
1. Is the WAHA container running?
2. Is the session WORKING?
3. Can we reach the API?

If down: restart container, log incident, create task for @dev via Discord.
"""

import json
import subprocess
import time
import logging
import os
import requests
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("waha_watchdog")

# Config
WAHA_CONTAINER = os.environ.get("WAHA_CONTAINER", "waha-send")
WAHA_PORT = os.environ.get("WAHA_PORT", "3002")
WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "240df5fea5d54886b2c77387f6287a55")
WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_ARSENAL_WEBHOOK", "")
STATE_FILE = Path(__file__).parent.parent / "shrine" / "state" / "waha_watchdog.json"

def _load_state() -> dict:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
    except Exception:
        pass
    return {"last_check": None, "status": "unknown", "downtime_start": None, "restart_count": 0, "incidents": []}

def _save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))

def check_container_running() -> bool:
    """Check if Docker container is running."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", WAHA_CONTAINER],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() == "true"
    except Exception:
        return False

def check_api_healthy() -> dict:
    """Check WAHA API and session status."""
    try:
        resp = requests.get(
            f"http://localhost:{WAHA_PORT}/api/sessions/{WAHA_SESSION}",
            headers={"X-Api-Key": WAHA_API_KEY},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            return {"ok": True, "status": data.get("status", "unknown"), "me": data.get("me")}
        return {"ok": False, "status": f"HTTP {resp.status_code}"}
    except requests.ConnectionError:
        return {"ok": False, "status": "connection_refused"}
    except Exception as e:
        return {"ok": False, "status": str(e)}

def restart_container() -> bool:
    """Restart the WAHA Docker container."""
    try:
        subprocess.run(["docker", "start", WAHA_CONTAINER], capture_output=True, timeout=15)
        time.sleep(10)  # Wait for startup
        return check_container_running()
    except Exception:
        return False

def notify_discord(message: str):
    """Send alert to Discord #the-arsenal channel via MCP send tool."""
    try:
        # Use the MCP send tool indirectly via a simple HTTP call to home_server
        # Or write to a notification file that the home_server picks up
        alert_file = Path(__file__).parent.parent / "shrine" / "state" / "waha_alerts.jsonl"
        with open(alert_file, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "severity": "critical"
            }) + "\n")
        logger.info(f"Alert logged: {message}")
    except Exception as e:
        logger.error(f"Failed to log alert: {e}")

def main():
    state = _load_state()
    now = datetime.now().isoformat()
    state["last_check"] = now

    # Step 1: Check container
    container_running = check_container_running()

    if not container_running:
        logger.warning(f"WAHA container '{WAHA_CONTAINER}' is NOT running. Attempting restart...")

        if not state.get("downtime_start"):
            state["downtime_start"] = now

        restarted = restart_container()
        state["restart_count"] = state.get("restart_count", 0) + 1

        if restarted:
            logger.info("Container restarted successfully.")
            # Re-check API after restart
            api = check_api_healthy()
            if api["ok"] and api["status"] == "WORKING":
                state["status"] = "recovered"
                state["downtime_start"] = None
                notify_discord(f"⚠️ WAHA was down, auto-restarted successfully. Session: {api['status']}. Restart #{state['restart_count']}.")
            else:
                state["status"] = "restarted_but_unhealthy"
                notify_discord(f"🔴 WAHA restarted but session not WORKING (status: {api['status']}). May need QR scan. @dev please check.")
                state["incidents"].append({"time": now, "type": "restart_unhealthy", "detail": api["status"]})
        else:
            state["status"] = "restart_failed"
            notify_discord(f"🔴🔴 WAHA container restart FAILED. WhatsApp bridge is DOWN. @dev immediate attention needed.")
            state["incidents"].append({"time": now, "type": "restart_failed"})

        _save_state(state)
        return

    # Step 2: Check API health
    api = check_api_healthy()

    if not api["ok"]:
        logger.warning(f"WAHA API unhealthy: {api['status']}")
        if not state.get("downtime_start"):
            state["downtime_start"] = now
        state["status"] = f"api_error:{api['status']}"
        notify_discord(f"🟡 WAHA container running but API unhealthy: {api['status']}. @dev please check.")
        state["incidents"].append({"time": now, "type": "api_unhealthy", "detail": api["status"]})
        _save_state(state)
        return

    if api["status"] != "WORKING":
        logger.warning(f"WAHA session not WORKING: {api['status']}")
        if not state.get("downtime_start"):
            state["downtime_start"] = now
        state["status"] = api["status"]

        if api["status"] == "SCAN_QR_CODE":
            notify_discord(f"📱 WAHA needs QR scan. Session status: SCAN_QR_CODE. Open http://localhost:{WAHA_PORT}/dashboard or ask @pitch for a new QR.")
        else:
            notify_discord(f"🟡 WAHA session status: {api['status']}. Not WORKING. @dev please investigate.")

        state["incidents"].append({"time": now, "type": "session_not_working", "detail": api["status"]})
        _save_state(state)
        return

    # All good
    if state.get("downtime_start"):
        downtime_seconds = (datetime.now() - datetime.fromisoformat(state["downtime_start"])).total_seconds()
        logger.info(f"WAHA recovered after {downtime_seconds:.0f}s downtime.")
        state["downtime_start"] = None

    state["status"] = "healthy"
    state["me"] = api.get("me")
    _save_state(state)
    logger.info(f"WAHA healthy. Session: WORKING. Phone: {api.get('me', {}).get('pushName', '?')}")


if __name__ == "__main__":
    main()
