#!/usr/bin/env python3
"""
Post-deploy script — runs after each Render deploy.

Steps:
  1. TOFU org self-announce (register/update endpoint + public key in L4)
  2. Bulk register all citizens in L4 + L3 (with org membership)
  3. Log deploy report as Moment in L3 graph

Every step logs to stdout (captured by Render) with timestamps.
On failure, logs the error and continues to the next step.

Usage:
    python scripts/post_deploy.py

    # Or with explicit config:
    ORG_ID=cities-of-light ENDPOINT_URL=wss://cities-of-light.onrender.com python scripts/post_deploy.py

Environment:
    ORG_ID              — org identifier (default: from .mind/citizen_id or repo name)
    ORG_NAME            — display name (default: title-cased ORG_ID)
    ENDPOINT_URL        — public wss:// or https:// URL
    WEBSITE             — org website URL
    UNIVERSE            — L3 graph name (default: lumina-prime)
    FALKORDB_HOST       — FalkorDB host (default: mind-protocol-falkordb)
    FALKORDB_PORT       — FalkorDB port (default: 6379)
    CITIZENS_DIR        — path to citizens/ directory
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ── Config ─────────────────────────────────────────────────────────────────

ORG_ID = os.environ.get("ORG_ID", "")
ORG_NAME = os.environ.get("ORG_NAME", "")
ENDPOINT_URL = os.environ.get("ENDPOINT_URL", os.environ.get("RENDER_EXTERNAL_URL", ""))
WEBSITE = os.environ.get("WEBSITE", "")
UNIVERSE = os.environ.get("UNIVERSE", os.environ.get("L3_GRAPH", "lumina-prime"))
FALKORDB_HOST = os.environ.get("FALKORDB_HOST", "mind-protocol-falkordb")
FALKORDB_PORT = int(os.environ.get("FALKORDB_PORT", "6379"))
CITIZENS_DIR = os.environ.get("CITIZENS_DIR", str(PROJECT_ROOT / "citizens"))


def log(step: str, msg: str, level: str = "INFO"):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] [post_deploy:{step}] {msg}", flush=True)


def detect_org_id() -> str:
    """Auto-detect org ID from .mind/citizen_id, repo name, or env."""
    if ORG_ID:
        return ORG_ID

    # Try .mind/citizen_id
    cid_file = PROJECT_ROOT / ".mind" / "citizen_id"
    if cid_file.exists():
        cid = cid_file.read_text().strip()
        if cid:
            return cid

    # Try repo directory name
    return PROJECT_ROOT.name


# ── Steps ──────────────────────────────────────────────────────────────────

def step_1_announce_org(org_id: str) -> dict:
    """TOFU self-announce: register org endpoint + public key in L4."""
    log("1_announce", f"Announcing org '{org_id}' to L4...")

    from runtime.l4.org_self_announce import announce_org

    result = announce_org(
        org_id=org_id,
        endpoint_url=ENDPOINT_URL,
        org_name=ORG_NAME or org_id.replace("-", " ").replace("_", " ").title(),
        website=WEBSITE,
        universe=UNIVERSE,
        falkordb_host=FALKORDB_HOST,
        falkordb_port=FALKORDB_PORT,
    )

    status = result.get("status", "unknown")
    log("1_announce", f"Result: {status}")

    if status == "claimed":
        log("1_announce", f"  TOFU CLAIM — first registration")
        log("1_announce", f"  Public key registered in L4")
        log("1_announce", f"  Endpoint: {ENDPOINT_URL}")
        if result.get("l3_mirrored"):
            log("1_announce", f"  L3 mirrored to graph: {result['l3_mirrored']}")
    elif status == "updated":
        log("1_announce", f"  Endpoint updated (signature verified)")
    elif status == "error":
        log("1_announce", f"  ERROR: {result.get('detail', '?')}", level="ERROR")

    return result


def step_2_register_citizens(org_id: str) -> int:
    """Bulk register all citizens in L4 + L3 with org membership."""
    log("2_citizens", f"Registering citizens from {CITIZENS_DIR}...")

    citizens_path = Path(CITIZENS_DIR)
    if not citizens_path.exists():
        log("2_citizens", f"  No citizens directory at {CITIZENS_DIR}", level="WARN")
        return 0

    from runtime.l4.citizen_l4_upsert import bulk_register_citizens

    count = bulk_register_citizens(
        citizens_dir=str(citizens_path),
        org_id=org_id,
        endpoint_base=ENDPOINT_URL.rstrip("/") if ENDPOINT_URL else "",
        falkordb_host=FALKORDB_HOST,
        falkordb_port=FALKORDB_PORT,
    )

    log("2_citizens", f"  Registered {count} citizens for org '{org_id}'")
    return count


def step_3_deploy_report(org_id: str, announce_result: dict, citizen_count: int, errors: list):
    """Log deploy report as Moment in L3 graph with full status breakdown."""
    log("3_report", "Writing deploy report to L3 graph...")

    try:
        from falkordb import FalkorDB

        db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
        graph = db.select_graph(UNIVERSE)

        now_s = int(time.time())
        moment_id = f"deploy_{org_id}_{now_s}"
        deploy_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Count citizens by status
        citizens_path = Path(CITIZENS_DIR)
        active = 0
        pending = 0
        no_profile = 0
        total_dirs = 0
        if citizens_path.exists():
            for d in citizens_path.iterdir():
                if not d.is_dir() or d.name.startswith("."):
                    continue
                total_dirs += 1
                profile = d / "profile.json"
                if profile.exists():
                    try:
                        p = json.loads(profile.read_text())
                        s = p.get("status", "unknown")
                        if s == "active":
                            active += 1
                        else:
                            pending += 1
                    except Exception:
                        pending += 1
                else:
                    no_profile += 1

        status_line = "ALL OK" if not errors else f"{len(errors)} ERRORS"

        content_lines = [
            f"Deploy report for {org_id} at {deploy_time}",
            f"",
            f"Status: {status_line}",
            f"Endpoint: {ENDPOINT_URL}",
            f"TOFU: {announce_result.get('status', 'skipped')}",
            f"Universe: {UNIVERSE}",
            f"",
            f"Citizens:",
            f"  Registered in L4: {citizen_count}",
            f"  Dirs on disk: {total_dirs}",
            f"  Active: {active}",
            f"  Pending: {pending}",
            f"  No profile: {no_profile}",
        ]

        if errors:
            content_lines.append(f"")
            content_lines.append(f"Errors ({len(errors)}):")
            for e in errors:
                content_lines.append(f"  - {e}")

        content = "\n".join(content_lines)
        synthesis = f"Deploy {org_id}: {status_line} | {active} active, {pending} pending, {citizen_count} registered"

        graph.query(
            "MERGE (m {id: $mid}) "
            "SET m.node_type = 'moment', m.type = 'deploy_report', "
            "    m.name = $name, m.content = $content, "
            "    m.synthesis = $syn, m.status = $status, "
            "    m.citizens_active = $active, m.citizens_pending = $pending, "
            "    m.citizens_registered = $registered, m.error_count = $errors, "
            "    m.created_at_s = $ts "
            "WITH m "
            "MATCH (o {id: $org_id}) "
            "MERGE (o)-[:link {nature: 'deployed'}]->(m)",
            {
                "mid": moment_id,
                "name": f"Deploy: {org_id} @ {deploy_time}",
                "content": content,
                "syn": synthesis,
                "status": "ok" if not errors else "degraded",
                "active": active,
                "pending": pending,
                "registered": citizen_count,
                "errors": len(errors),
                "ts": now_s,
                "org_id": org_id,
            },
        )

        log("3_report", f"  Deploy moment created: {moment_id}")
        log("3_report", f"  Citizens: {active} active, {pending} pending, {no_profile} no profile")
        if errors:
            log("3_report", f"  Errors in report: {len(errors)}", level="WARN")

    except Exception as e:
        log("3_report", f"  Could not write deploy report: {e}", level="WARN")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    start = time.time()

    log("start", "=" * 60)
    log("start", "POST-DEPLOY SCRIPT")
    log("start", "=" * 60)
    log("start", f"  Project root: {PROJECT_ROOT}")
    log("start", f"  Citizens dir: {CITIZENS_DIR}")
    log("start", f"  FalkorDB: {FALKORDB_HOST}:{FALKORDB_PORT}")
    log("start", f"  Universe: {UNIVERSE}")

    # Detect org
    org_id = detect_org_id()
    if not org_id:
        log("start", "Cannot detect ORG_ID. Set it via env or .mind/citizen_id", level="ERROR")
        sys.exit(1)

    log("start", f"  Org ID: {org_id}")
    log("start", f"  Endpoint: {ENDPOINT_URL or '(not set)'}")
    log("start", "")

    errors = []

    # Step 1: TOFU org announce
    announce_result = {}
    try:
        announce_result = step_1_announce_org(org_id)
    except Exception as e:
        log("1_announce", f"FAILED: {e}", level="ERROR")
        errors.append(f"announce: {e}")

    log("", "")

    # Step 2: Register citizens
    citizen_count = 0
    try:
        citizen_count = step_2_register_citizens(org_id)
    except Exception as e:
        log("2_citizens", f"FAILED: {e}", level="ERROR")
        errors.append(f"citizens: {e}")

    log("", "")

    # Step 3: Deploy report (includes errors list + citizen breakdown)
    try:
        step_3_deploy_report(org_id, announce_result, citizen_count, errors)
    except Exception as e:
        log("3_report", f"FAILED: {e}", level="ERROR")
        errors.append(f"report: {e}")

    # Summary
    elapsed = time.time() - start
    log("", "")
    log("done", "=" * 60)
    log("done", f"POST-DEPLOY COMPLETE in {elapsed:.1f}s")
    log("done", f"  Org: {org_id}")
    log("done", f"  TOFU: {announce_result.get('status', 'skipped')}")
    log("done", f"  Citizens: {citizen_count}")
    if errors:
        log("done", f"  Errors: {len(errors)}")
        for e in errors:
            log("done", f"    - {e}", level="ERROR")
    else:
        log("done", f"  Status: ALL OK")
    log("done", "=" * 60)

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
