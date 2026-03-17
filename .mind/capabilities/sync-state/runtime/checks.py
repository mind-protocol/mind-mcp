"""
Health Checks: sync-state

Decorator-based health checks for sync state freshness.
Detects stale SYNC files, YAML drift, missing ingestion, and blocked modules.

DOCS: capabilities/sync-state/HEALTH.md
"""

import re
from datetime import datetime, timedelta
from pathlib import Path

from runtime.capability import check, Signal, triggers


# =============================================================================
# CONSTANTS
# =============================================================================

SYNC_STALE_DAYS = 14
BLOCKED_STALE_DAYS = 7


# =============================================================================
# HEALTH CHECKS
# =============================================================================

@check(
    id="sync_freshness",
    triggers=[
        triggers.cron.daily(),
    ],
    on_problem="STALE_SYNC",
    task="TASK_update_sync",
)
def sync_freshness(ctx) -> dict:
    """
    H1: Check if SYNC files are fresh (updated within 14 days).

    Scans all SYNC files and checks LAST_UPDATED field.
    Returns CRITICAL if >= 5 stale SYNC files.
    Returns DEGRADED if any stale.
    Returns HEALTHY if all fresh.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")
    threshold = datetime.now() - timedelta(days=SYNC_STALE_DAYS)

    stale_syncs = []

    docs_path = root / "docs"
    if not docs_path.exists():
        return Signal.healthy(message="No docs directory")

    for sync_path in docs_path.rglob("SYNC*.md"):
        try:
            content = sync_path.read_text()
        except Exception:
            continue

        match = re.search(r"LAST_UPDATED:\s*(\d{4}-\d{2}-\d{2})", content)
        if not match:
            stale_syncs.append({
                "path": str(sync_path),
                "last_updated": None,
                "days_stale": "unknown",
            })
            continue

        try:
            last_updated = datetime.strptime(match.group(1), "%Y-%m-%d")
            if last_updated < threshold:
                stale_syncs.append({
                    "path": str(sync_path),
                    "last_updated": match.group(1),
                    "days_stale": (datetime.now() - last_updated).days,
                })
        except ValueError:
            stale_syncs.append({
                "path": str(sync_path),
                "last_updated": match.group(1),
                "days_stale": "parse_error",
            })

    if not stale_syncs:
        return Signal.healthy(message="All SYNC files are fresh")

    if len(stale_syncs) >= 5:
        return Signal.critical(
            stale_count=len(stale_syncs),
            stale_files=[s["path"] for s in stale_syncs],
            details=stale_syncs,
        )

    return Signal.degraded(
        stale_count=len(stale_syncs),
        stale_files=[s["path"] for s in stale_syncs],
        details=stale_syncs,
    )


@check(
    id="yaml_drift",
    triggers=[
        triggers.cron.daily(),
        triggers.file.on_modify("docs/**"),
    ],
    on_problem="YAML_DRIFT",
    task="TASK_regenerate_yaml",
)
def yaml_drift(ctx) -> dict:
    """
    H2: Check if modules.yaml matches file system reality.

    Compares modules listed in YAML to actual directories in docs/.
    Returns DEGRADED if drift detected.
    Returns HEALTHY if in sync.
    """
    import yaml

    root = Path(ctx.project_root) if ctx.project_root else Path(".")

    yaml_path = root / ".mind" / "modules.yaml"
    if not yaml_path.exists():
        return Signal.degraded(
            drifted=True,
            error="modules.yaml not found",
        )

    try:
        with open(yaml_path) as f:
            yaml_content = yaml.safe_load(f) or {}
    except Exception as e:
        return Signal.degraded(
            drifted=True,
            error=f"Failed to parse modules.yaml: {e}",
        )

    # Get modules from YAML
    yaml_modules = set()
    modules = yaml_content.get("modules", [])
    if isinstance(modules, list):
        for m in modules:
            if isinstance(m, dict):
                yaml_modules.add(m.get("name", ""))
            elif isinstance(m, str):
                yaml_modules.add(m)

    # Get modules from file system
    docs_path = root / "docs"
    fs_modules = set()

    if docs_path.exists():
        for item in docs_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                has_sync = (item / "SYNC.md").exists()
                has_patterns = (item / "PATTERNS.md").exists()
                if has_sync or has_patterns:
                    fs_modules.add(item.name)

    missing_from_yaml = list(fs_modules - yaml_modules)
    extra_in_yaml = list(yaml_modules - fs_modules)

    if not missing_from_yaml and not extra_in_yaml:
        return Signal.healthy(modules_count=len(fs_modules))

    return Signal.degraded(
        drifted=True,
        missing_from_yaml=missing_from_yaml,
        extra_in_yaml=extra_in_yaml,
    )


@check(
    id="ingestion_coverage",
    triggers=[
        triggers.cron.daily(),
    ],
    on_problem="DOCS_NOT_INGESTED",
    task="TASK_ingest_docs",
)
def ingestion_coverage(ctx) -> dict:
    """
    H3: Check if all docs on disk exist in graph.

    Compares docs/**/*.md to doc nodes in graph.
    Returns CRITICAL if >= 10 docs not ingested.
    Returns DEGRADED if any docs missing from graph.
    Returns HEALTHY if all ingested.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")

    docs_path = root / "docs"
    docs_on_disk = set()

    if docs_path.exists():
        for doc_path in docs_path.rglob("*.md"):
            rel_path = str(doc_path.relative_to(root))
            docs_on_disk.add(rel_path)

    if not docs_on_disk:
        return Signal.healthy(on_disk=0, in_graph=0)

    # Query graph for ingested docs
    docs_in_graph = set()
    try:
        result = ctx.query_nodes(
            node_type="concept",
            filters={"type": "doc"},
        )
        if result:
            for row in result:
                path = row.get("path")
                if path:
                    docs_in_graph.add(path)
    except Exception:
        return Signal.degraded(
            on_disk=len(docs_on_disk),
            in_graph=0,
            message="Graph not available for verification",
        )

    not_ingested = list(docs_on_disk - docs_in_graph)

    if not not_ingested:
        return Signal.healthy(
            on_disk=len(docs_on_disk),
            in_graph=len(docs_in_graph),
        )

    if len(not_ingested) >= 10:
        return Signal.critical(
            on_disk=len(docs_on_disk),
            in_graph=len(docs_in_graph),
            not_ingested=not_ingested[:10],
            not_ingested_count=len(not_ingested),
        )

    return Signal.degraded(
        on_disk=len(docs_on_disk),
        in_graph=len(docs_in_graph),
        not_ingested=not_ingested,
        not_ingested_count=len(not_ingested),
    )


@check(
    id="blocked_modules",
    triggers=[
        triggers.cron.daily(),
    ],
    on_problem="MODULE_BLOCKED",
    task="TASK_unblock_module",
)
def blocked_modules(ctx) -> dict:
    """
    H4: Check for modules with STATUS: BLOCKED.

    Returns CRITICAL if any module blocked > 7 days.
    Returns DEGRADED if any module blocked.
    Returns HEALTHY if no blocked modules.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")

    blocked = []
    docs_path = root / "docs"

    if not docs_path.exists():
        return Signal.healthy(message="No docs directory")

    for sync_path in docs_path.rglob("SYNC*.md"):
        try:
            content = sync_path.read_text()
        except Exception:
            continue

        if not re.search(r"STATUS:\s*BLOCKED", content, re.IGNORECASE):
            continue

        module = sync_path.parent.name

        blocker_match = re.search(
            r"(?:BLOCKED|Blocker|Blocking)[:\s]+([^\n]+)", content, re.IGNORECASE
        )
        blocker_reason = blocker_match.group(1).strip() if blocker_match else "Unknown"

        updated_match = re.search(r"LAST_UPDATED:\s*(\d{4}-\d{2}-\d{2})", content)
        days_blocked = None
        since_date = None

        if updated_match:
            try:
                since_date = updated_match.group(1)
                blocked_since = datetime.strptime(since_date, "%Y-%m-%d")
                days_blocked = (datetime.now() - blocked_since).days
            except ValueError:
                pass

        blocked.append({
            "module": module,
            "path": str(sync_path),
            "reason": blocker_reason,
            "since": since_date,
            "days_blocked": days_blocked,
        })

    if not blocked:
        return Signal.healthy(message="No blocked modules")

    long_blocked = [b for b in blocked if (b.get("days_blocked") or 0) > BLOCKED_STALE_DAYS]

    if long_blocked:
        return Signal.critical(
            blocked_count=len(blocked),
            blocked=blocked,
            long_blocked_count=len(long_blocked),
        )

    return Signal.degraded(
        blocked_count=len(blocked),
        blocked=blocked,
    )


# =============================================================================
# REGISTRY
# =============================================================================

CHECKS = [
    sync_freshness,
    yaml_drift,
    ingestion_coverage,
    blocked_modules,
]
