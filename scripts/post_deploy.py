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


def step_2_register_citizens(org_id: str) -> dict:
    """Bulk register all citizens in L4 + L3 with org membership.

    Also ensures wallet + RSA keys exist for each citizen (generates if missing,
    airdrops 100 $MIND to new wallets from deployer wallet).

    Returns dict with counts: registered, wallets_created, errors.
    """
    log("2_citizens", f"Registering citizens from {CITIZENS_DIR}...")

    citizens_path = Path(CITIZENS_DIR)
    if not citizens_path.exists():
        log("2_citizens", f"  No citizens directory at {CITIZENS_DIR}", level="WARN")
        return {"registered": 0, "wallets_created": 0}

    from runtime.l4.citizen_l4_upsert import bulk_register_citizens

    count = bulk_register_citizens(
        citizens_dir=str(citizens_path),
        org_id=org_id,
        endpoint_base=ENDPOINT_URL.rstrip("/") if ENDPOINT_URL else "",
        falkordb_host=FALKORDB_HOST,
        falkordb_port=FALKORDB_PORT,
    )

    # Count wallets that were created during this run
    keys_base = citizens_path.parent / ".keys"
    wallets = sum(1 for d in keys_base.iterdir() if (d / "solana_private_key.json").exists()) if keys_base.exists() else 0

    log("2_citizens", f"  Registered {count} citizens for org '{org_id}'")
    log("2_citizens", f"  Wallets on disk: {wallets}")
    return {"registered": count, "wallets": wallets}


def step_3_deploy_report(org_id: str, announce_result: dict, citizen_count: int, wallets_count: int, errors: list):
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
                    except Exception as e:
                        log("3_report", f"  Failed to parse profile for {d.name}: {e}", level="WARN")
                        pending += 1
                else:
                    no_profile += 1

        # Detect newly born citizens (status=pending_confirmation or .first_boot.json)
        newborns = []
        for d in citizens_path.iterdir():
            if not d.is_dir() or d.name.startswith("."):
                continue
            fb = d / ".first_boot.json"
            profile_f = d / "profile.json"
            if fb.exists():
                newborns.append(d.name)
            elif profile_f.exists():
                try:
                    p = json.loads(profile_f.read_text())
                    if p.get("status") == "pending_confirmation":
                        newborns.append(d.name)
                except Exception as e:
                    log("3_report", f"  Failed to check newborn status for {d.name}: {e}", level="WARN")

        status_line = "ALL OK" if not errors else f"{len(errors)} ERRORS"

        content_lines = []

        # Births first
        if newborns:
            content_lines.append(f"Naissances ({len(newborns)}):")
            for nb in newborns:
                content_lines.append(f"  Naissance de @{nb}")
            content_lines.append("")

        content_lines += [
            f"Deploy report for {org_id} at {deploy_time}",
            f"",
            f"Status: {status_line}",
            f"Endpoint: {ENDPOINT_URL}",
            f"TOFU: {announce_result.get('status', 'skipped')}",
            f"Universe: {UNIVERSE}",
            f"",
            f"Citizens:",
            f"  Registered in L4: {citizen_count}",
            f"  Wallets on disk: {wallets_count}",
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

        # Link dimensions vary with deploy health
        # Clean deploy: high trust, high affinity, low friction
        # Errored deploy: low trust, high friction, negative valence
        error_ratio = len(errors) / max(citizen_count, 1) if errors else 0.0
        link_trust = max(0.1, 0.9 - error_ratio * 2)
        link_affinity = max(0.1, 0.8 - error_ratio * 2)
        link_friction = min(0.9, error_ratio * 3)
        link_valence = max(-1.0, 0.8 - error_ratio * 4)
        link_polarity = 0.8 if not errors else max(-0.5, 0.5 - error_ratio * 3)

        graph.query(
            "MERGE (m {id: $mid}) "
            "SET m.node_type = 'moment', m.type = 'deploy_report', "
            "    m.name = $name, m.content = $content, "
            "    m.synthesis = $syn, m.status = $status, "
            "    m.citizens_active = $active, m.citizens_pending = $pending, "
            "    m.citizens_registered = $registered, m.error_count = $errcnt, "
            "    m.created_at_s = $ts "
            "WITH m "
            "MATCH (o {id: $org_id}) "
            "MERGE (o)-[r:link {nature: 'deployed'}]->(m) "
            "SET r.trust = $trust, r.affinity = $affinity, "
            "    r.friction = $friction, r.valence = $valence, "
            "    r.polarity = $polarity, r.permanence = 0.3, "
            "    r.weight = 0.6, r.energy = 0.5",
            {
                "mid": moment_id,
                "name": f"Deploy: {org_id} @ {deploy_time}",
                "content": content,
                "syn": synthesis,
                "status": "ok" if not errors else "degraded",
                "active": active,
                "pending": pending,
                "registered": citizen_count,
                "errcnt": len(errors),
                "ts": now_s,
                "org_id": org_id,
                "trust": round(link_trust, 3),
                "affinity": round(link_affinity, 3),
                "friction": round(link_friction, 3),
                "valence": round(link_valence, 3),
                "polarity": round(link_polarity, 3),
            },
        )

        log("3_report", f"  Deploy moment created: {moment_id}")
        log("3_report", f"  Link: trust={link_trust:.2f} affinity={link_affinity:.2f} friction={link_friction:.2f} valence={link_valence:.2f}")
        log("3_report", f"  Citizens: {active} active, {pending} pending, {no_profile} no profile")

        # Link deploy moment to newborn citizens
        if newborns:
            log("3_report", f"  Linking {len(newborns)} newborns to deploy moment")
            for nb in newborns:
                try:
                    # Try both ID formats
                    for cid in [nb, f"CITIZEN_{nb}"]:
                        graph.query(
                            "MATCH (m {id: $mid}), (c {id: $cid}) "
                            "MERGE (m)-[r:link {nature: 'birth'}]->(c) "
                            "SET r.polarity = 0.9, r.permanence = 1.0, "
                            "    r.trust = 0.5, r.affinity = 0.8",
                            {"mid": moment_id, "cid": cid},
                        )
                    log("3_report", f"    Naissance de @{nb}")
                except Exception as e:
                    log("3_report", f"    Failed to link newborn @{nb}: {e}", level="WARN")

        # If errors, create a fix task and assign it to best available citizen
        if errors:
            log("3_report", f"  {len(errors)} errors — creating fix task", level="WARN")
            _create_fix_task(graph, org_id, moment_id, errors, now_s)

    except Exception as e:
        log("3_report", f"  Could not write deploy report: {e}", level="WARN")


def _create_fix_task(graph, org_id: str, deploy_moment_id: str, errors: list, now_s: int):
    """Create a task for fixing deploy errors and assign to best citizen."""
    task_id = f"fix_deploy_{org_id}_{now_s}"

    error_list = "\n".join(f"  - {e}" for e in errors)
    content = (
        f"Deploy of {org_id} had {len(errors)} error(s). Fix needed:\n\n"
        f"{error_list}\n\n"
        f"This task was auto-created by the post-deploy script.\n"
        f"Linked to deploy report: {deploy_moment_id}"
    )

    # Create task moment
    graph.query(
        "MERGE (t {id: $tid}) "
        "SET t.node_type = 'moment', t.type = 'deploy_fix_task', "
        "    t.name = $name, t.content = $content, "
        "    t.synthesis = $syn, t.status = 'pending', "
        "    t.priority = 'high', t.error_count = $errcnt, "
        "    t.created_at_s = $ts "
        "WITH t "
        "MATCH (d {id: $did}) "
        "MERGE (d)-[:link {nature: 'needs_fix'}]->(t) "
        "SET d.friction = 0.5",
        {
            "tid": task_id,
            "name": f"Fix deploy errors: {org_id}",
            "content": content,
            "syn": f"Fix {len(errors)} deploy errors for {org_id}",
            "errcnt": len(errors),
            "ts": now_s,
            "did": deploy_moment_id,
        },
    )

    # Assign to best citizen using task_assignment
    try:
        from runtime.task_assignment import assign_single_task
        from runtime.infrastructure.database import get_database_adapter

        adapter = get_database_adapter()
        assigned = assign_single_task(
            task_id=task_id,
            task_synthesis=f"Fix deploy errors for {org_id}: {', '.join(errors[:3])}",
            adapter=adapter,
            actor_type="citizen",
        )
        if assigned:
            log("3_report", f"  Fix task assigned to @{assigned}")
        else:
            log("3_report", f"  Fix task created but no citizen available for assignment", level="WARN")
    except Exception as e:
        log("3_report", f"  Could not auto-assign fix task: {e}", level="WARN")


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

    # Step 2: Register citizens + ensure keys + airdrop
    citizen_result = {"registered": 0, "wallets": 0}
    try:
        citizen_result = step_2_register_citizens(org_id)
    except Exception as e:
        log("2_citizens", f"FAILED: {e}", level="ERROR")
        errors.append(f"citizens: {e}")

    citizen_count = citizen_result.get("registered", 0)
    wallets_count = citizen_result.get("wallets", 0)

    log("", "")

    # Step 3: Deploy report (includes errors list + citizen breakdown)
    try:
        step_3_deploy_report(org_id, announce_result, citizen_count, wallets_count, errors)
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
    log("done", f"  Citizens: {citizen_count} registered, {wallets_count} wallets")
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
