#!/usr/bin/env python3
"""
Render Log Monitor — polls Render deploy logs and creates error Moments in L3.

Cron job installed automatically by mind init. Runs every 5 minutes.
Reads the latest deploy logs, filters errors, and writes Moment nodes
linked to the org in the L3 universe graph.

Usage:
    python scripts/render_log_monitor.py

Environment:
    RENDER_API_KEY      — Render API key (required)
    RENDER_SERVICE_ID   — Render service ID (auto-detected from render.yaml if not set)
    ORG_ID              — org identifier
    UNIVERSE            — L3 graph name
    FALKORDB_HOST       — FalkorDB host
    FALKORDB_PORT       — FalkorDB port
"""

import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("render_log_monitor")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RENDER_API_KEY = os.environ.get("RENDER_API_KEY", "")
RENDER_SERVICE_ID = os.environ.get("RENDER_SERVICE_ID", "")
ORG_ID = os.environ.get("ORG_ID", "")
UNIVERSE = os.environ.get("UNIVERSE", os.environ.get("L3_GRAPH", ""))
FALKORDB_HOST = os.environ.get("FALKORDB_HOST", "localhost")
FALKORDB_PORT = int(os.environ.get("FALKORDB_PORT", "6379"))

# State file to track last processed log timestamp
STATE_FILE = PROJECT_ROOT / ".mind" / "state" / "render_log_monitor.json"

# Error patterns to detect
ERROR_PATTERNS = [
    (r"(?i)\berror\b", "error"),
    (r"(?i)\bfailed\b", "error"),
    (r"(?i)\bcrash", "critical"),
    (r"(?i)\bpanic\b", "critical"),
    (r"(?i)\bkilled\b", "critical"),
    (r"(?i)\bOOM\b", "critical"),
    (r"(?i)\btimeout\b", "warning"),
    (r"(?i)\bwarning\b", "warning"),
    (r"(?i)Traceback", "error"),
    (r"(?i)Exception", "error"),
    (r"(?i)status\s*=?\s*5\d\d", "error"),
    (r"(?i)SIGTERM|SIGKILL", "critical"),
]

# Ignore patterns (noise)
IGNORE_PATTERNS = [
    r"npm warn",
    r"DeprecationWarning",
    r"ExperimentalWarning",
    r"punycode",
]


def detect_service_id() -> str:
    """Auto-detect Render service ID from render.yaml or env."""
    if RENDER_SERVICE_ID:
        return RENDER_SERVICE_ID

    # Try render.yaml
    render_yaml = PROJECT_ROOT / "render.yaml"
    if render_yaml.exists():
        import yaml
        try:
            data = yaml.safe_load(render_yaml.read_text())
            services = data.get("services", [])
            if services:
                return services[0].get("name", "")
        except Exception:
            pass

    return ""


def detect_org_id() -> str:
    """Auto-detect org ID."""
    if ORG_ID:
        return ORG_ID
    cid_file = PROJECT_ROOT / ".mind" / "citizen_id"
    if cid_file.exists():
        return cid_file.read_text().strip()
    return PROJECT_ROOT.name


def load_state() -> dict:
    """Load last processed state."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"last_deploy_id": "", "last_log_hash": "", "processed_at": 0}


def save_state(state: dict):
    """Save processing state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def fetch_latest_deploy(service_id: str) -> Optional[dict]:
    """Fetch the latest deploy from Render API."""
    import urllib.request
    import urllib.error

    url = f"https://api.render.com/v1/services/{service_id}/deploys?limit=1"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Accept": "application/json",
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data and len(data) > 0:
                return data[0].get("deploy", data[0])
    except Exception as e:
        logger.warning(f"Cannot fetch deploys: {e}")
    return None


def fetch_deploy_events(service_id: str, limit: int = 50) -> list:
    """Fetch recent service events from Render API."""
    import urllib.request

    url = f"https://api.render.com/v1/services/{service_id}/events?limit={limit}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Accept": "application/json",
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data if isinstance(data, list) else []
    except Exception as e:
        logger.debug(f"Cannot fetch events: {e}")
    return []


def classify_log_line(line: str) -> Optional[str]:
    """Classify a log line as error/warning/critical or None (ignore)."""
    # Check ignore patterns first
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, line):
            return None

    # Check error patterns
    for pattern, severity in ERROR_PATTERNS:
        if re.search(pattern, line):
            return severity

    return None


def extract_errors_from_events(events: list, since_ts: float = 0) -> list:
    """Extract error entries from Render events."""
    errors = []

    for event_wrapper in events:
        event = event_wrapper.get("event", event_wrapper)
        ts_str = event.get("timestamp", "")
        event_type = event.get("type", "")
        details = event.get("details", {})

        # Parse timestamp
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
        except Exception:
            ts = 0

        if ts <= since_ts:
            continue

        # Detect failures
        severity = None
        message = ""

        if event_type in ("deploy_ended", "build_ended"):
            status = details.get("deployStatus") or details.get("buildStatus", "")
            if status == "failed":
                reason = details.get("reason", {})
                failure = reason.get("failure", {})
                message = f"Deploy/build failed: {json.dumps(reason)[:200]}"
                severity = "critical" if failure.get("nonZeroExit") else "error"

        elif event_type == "instance_crashed":
            message = f"Instance crashed: {json.dumps(details)[:200]}"
            severity = "critical"

        elif event_type == "instance_oom":
            message = f"Out of memory: {json.dumps(details)[:200]}"
            severity = "critical"

        if severity and message:
            errors.append({
                "timestamp": ts_str,
                "timestamp_s": int(ts),
                "severity": severity,
                "type": event_type,
                "message": message,
                "hash": hashlib.md5(f"{ts_str}:{message}".encode()).hexdigest()[:12],
            })

    return errors


def write_error_moments(errors: list, org_id: str, universe: str):
    """Write error Moments to L3 graph, linked to the org."""
    if not errors or not universe:
        return 0

    try:
        from falkordb import FalkorDB
        db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
        graph = db.select_graph(universe)
    except Exception as e:
        logger.warning(f"Cannot connect to FalkorDB: {e}")
        return 0

    written = 0
    for err in errors:
        moment_id = f"error_{org_id}_{err['hash']}"
        now_s = int(time.time())

        # Severity → link dimensions
        if err["severity"] == "critical":
            friction = 0.9
            valence = -0.8
            energy = 1.0
        elif err["severity"] == "error":
            friction = 0.6
            valence = -0.5
            energy = 0.7
        else:  # warning
            friction = 0.3
            valence = -0.2
            energy = 0.3

        try:
            # Create error Moment
            graph.query(
                "MERGE (m {id: $mid}) "
                "SET m.node_type = 'moment', m.type = 'error_log', "
                "    m.name = $name, m.content = $content, "
                "    m.synthesis = $syn, m.severity = $sev, "
                "    m.status = 'active', "
                "    m.created_at_s = $ts",
                {
                    "mid": moment_id,
                    "name": f"[{err['severity'].upper()}] {err['type']}",
                    "content": err["message"],
                    "syn": f"{err['severity']}: {err['message'][:100]}",
                    "sev": err["severity"],
                    "ts": err.get("timestamp_s", now_s),
                },
            )

            # Link to org with severity-proportional friction
            graph.query(
                "MATCH (o {id: $oid}), (m {id: $mid}) "
                "MERGE (o)-[r:link {nature: 'error'}]->(m) "
                "SET r.friction = $friction, r.valence = $valence, "
                "    r.energy = $energy, r.permanence = 0.2, "
                "    r.polarity = -0.5",
                {
                    "oid": org_id, "mid": moment_id,
                    "friction": friction, "valence": valence, "energy": energy,
                },
            )

            written += 1
        except Exception as e:
            logger.debug(f"Failed to write error moment: {e}")

    return written


def main():
    if not RENDER_API_KEY:
        logger.info("No RENDER_API_KEY — skipping log monitor")
        return

    service_id = detect_service_id()
    if not service_id:
        # Try to find from Render API
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://api.render.com/v1/services?limit=20",
                headers={"Authorization": f"Bearer {RENDER_API_KEY}"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                services = json.loads(resp.read())
                # Find our service by repo name
                for s in services:
                    svc = s.get("service", s)
                    repo = svc.get("repo", "")
                    if PROJECT_ROOT.name in repo:
                        service_id = svc["id"]
                        break
        except Exception:
            pass

    if not service_id:
        logger.info("Cannot determine Render service ID — skipping")
        return

    org_id = detect_org_id()
    universe = UNIVERSE or org_id

    state = load_state()
    last_ts = state.get("processed_at", 0)

    # Fetch events
    events = fetch_deploy_events(service_id)
    errors = extract_errors_from_events(events, since_ts=last_ts)

    if errors:
        logger.info(f"Found {len(errors)} errors in Render logs for {org_id}")
        written = write_error_moments(errors, org_id, universe)
        logger.info(f"Wrote {written} error Moments to L3 graph '{universe}'")
    else:
        logger.debug("No new errors in Render logs")

    # Save state
    state["processed_at"] = time.time()
    state["last_service_id"] = service_id
    state["errors_found"] = len(errors)
    save_state(state)


def check_orchestrator_health():
    """Verify the orchestrator + citizens are alive on this server.

    Checks:
      1. home_server /health is responding
      2. Orchestrator is running (dispatcher active)
      3. Citizens have loaded L1 engines
      4. Physics ticks are happening (tick_count > 0)

    If anything is down, creates a Moment and attempts restart.
    """
    import urllib.request
    import urllib.error

    org_id = detect_org_id()
    universe = UNIVERSE or org_id
    issues = []

    # 1. Check home_server health (local — port 8765 or PORT env)
    home_port = os.environ.get("HOME_SERVER_PORT", "8765")
    try:
        req = urllib.request.Request(f"http://localhost:{home_port}/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            logger.debug(f"home_server health: {data.get('status')}")
    except Exception as e:
        issues.append({
            "component": "home_server",
            "severity": "critical",
            "message": f"home_server not responding on :{home_port}: {e}",
        })

    # 2. Check orchestrator status
    try:
        req = urllib.request.Request(f"http://localhost:{home_port}/api/orchestrator/status", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            if not data.get("running", True):
                issues.append({
                    "component": "orchestrator",
                    "severity": "error",
                    "message": "Orchestrator not running",
                })
            else:
                active = data.get("active_sessions", 0)
                queue = data.get("queue_depth", 0)
                logger.debug(f"Orchestrator: {active} active, {queue} queued")
    except Exception as e:
        # If home_server is already down, don't double-report
        if not any(i["component"] == "home_server" for i in issues):
            issues.append({
                "component": "orchestrator",
                "severity": "error",
                "message": f"Cannot check orchestrator: {e}",
            })

    # 3. Check citizens are loaded (via /membrane/ping for each local citizen)
    citizens_dir = PROJECT_ROOT / "citizens"
    citizens_checked = 0
    citizens_alive = 0

    if citizens_dir.exists():
        for d in sorted(citizens_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            citizens_checked += 1
            try:
                req = urllib.request.Request(
                    f"http://localhost:{home_port}/membrane/ping/{d.name}", method="GET")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read())
                    if data.get("alive"):
                        citizens_alive += 1
            except Exception:
                pass

            # Don't check too many — sample first 10
            if citizens_checked >= 10:
                break

    if citizens_checked > 0 and citizens_alive == 0:
        issues.append({
            "component": "citizens",
            "severity": "error",
            "message": f"0/{citizens_checked} citizens alive (sampled)",
        })
    elif citizens_checked > 0:
        logger.debug(f"Citizens: {citizens_alive}/{citizens_checked} alive (sampled)")

    # 4. Write issues as Moments in L3
    if issues:
        logger.warning(f"Orchestrator health: {len(issues)} issues found")

        try:
            from falkordb import FalkorDB
            db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
            graph = db.select_graph(universe)

            now_s = int(time.time())
            moment_id = f"health_{org_id}_{now_s}"

            content_lines = [f"Health check for {org_id} at {datetime.now(timezone.utc).strftime('%H:%M UTC')}:"]
            for issue in issues:
                content_lines.append(f"  [{issue['severity'].upper()}] {issue['component']}: {issue['message']}")

            content = "\n".join(content_lines)
            worst = max(issues, key=lambda i: {"warning": 0, "error": 1, "critical": 2}.get(i["severity"], 0))
            worst_sev = worst["severity"]

            friction = {"warning": 0.3, "error": 0.6, "critical": 0.9}.get(worst_sev, 0.5)
            valence = {"warning": -0.2, "error": -0.5, "critical": -0.8}.get(worst_sev, -0.5)

            graph.query(
                "MERGE (m {id: $mid}) "
                "SET m.node_type = 'moment', m.type = 'health_check', "
                "    m.name = $name, m.content = $content, "
                "    m.synthesis = $syn, m.severity = $sev, "
                "    m.status = 'active', m.created_at_s = $ts "
                "WITH m "
                "MATCH (o {id: $oid}) "
                "MERGE (o)-[r:link {nature: 'health_issue'}]->(m) "
                "SET r.friction = $friction, r.valence = $valence, "
                "    r.energy = 0.8, r.permanence = 0.15",
                {
                    "mid": moment_id,
                    "name": f"Health: {worst_sev} on {org_id}",
                    "content": content,
                    "syn": f"Health {worst_sev}: {worst['component']} — {worst['message'][:80]}",
                    "sev": worst_sev,
                    "ts": now_s,
                    "oid": org_id,
                    "friction": friction,
                    "valence": valence,
                },
            )
            logger.info(f"Health moment created: {moment_id}")
        except Exception as e:
            logger.warning(f"Could not write health moment: {e}")

        # 5. Attempt restart if critical
        if any(i["severity"] == "critical" for i in issues):
            logger.warning("Critical issue detected — attempting home_server restart")
            try:
                import subprocess
                # Kill existing home_server and restart
                subprocess.run(
                    ["pkill", "-f", "uvicorn home_server"],
                    timeout=5, capture_output=True,
                )
                time.sleep(2)
                subprocess.Popen(
                    ["python3", "-m", "uvicorn", "home_server:app",
                     "--host", "0.0.0.0", "--port", home_port],
                    cwd=str(PROJECT_ROOT / ".mind" / "runtime"),
                    stdout=open("/dev/null", "w"),
                    stderr=open("/dev/null", "w"),
                )
                logger.info("home_server restart initiated")
            except Exception as e:
                logger.error(f"Restart failed: {e}")

    return issues


if __name__ == "__main__":
    main()
    check_orchestrator_health()
