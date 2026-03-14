"""
First-boot self-registration for newly spawned citizens.

When a citizen directory contains `.first_boot.json`, this module
executes the L4 registration on the citizen's behalf:
  1. Creates Actor node in FalkorDB L4
  2. Creates wallet Thing node + link
  3. Creates endpoint Thing node + link
  4. Deletes .first_boot.json (one-shot)

Called by the dispatcher on each tick for new citizens.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger("orchestrator.first_boot")

CITIZENS_DIR = Path(__file__).resolve().parent.parent.parent / "citizens"


def check_and_register_new_citizens(graph_ops=None) -> list[str]:
    """Scan citizen dirs for .first_boot.json and register them in L4.

    Returns list of handles that were successfully registered.
    """
    if not CITIZENS_DIR.exists():
        return []

    registered = []

    for citizen_dir in sorted(CITIZENS_DIR.iterdir()):
        if not citizen_dir.is_dir():
            continue

        boot_file = citizen_dir / ".first_boot.json"
        if not boot_file.exists():
            continue

        handle = citizen_dir.name
        logger.info(f"First boot detected for @{handle}")

        try:
            boot_data = json.loads(boot_file.read_text())
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Cannot read .first_boot.json for {handle}: {e}")
            continue

        success = _execute_registration(handle, boot_data, graph_ops)

        if success:
            # Delete first boot file (one-shot)
            boot_file.unlink()
            registered.append(handle)
            logger.info(f"@{handle} self-registered on L4 and confirmed")
        else:
            logger.warning(f"@{handle} first boot registration failed — will retry next tick")

    return registered


def _execute_registration(handle: str, boot_data: dict, graph_ops) -> bool:
    """Execute the L4 registration queries from the first boot task."""
    cypher_queries = boot_data.get("cypher", {})
    if not cypher_queries:
        logger.warning(f"No cypher queries in .first_boot.json for {handle}")
        return False

    if not graph_ops:
        logger.warning(f"No graph connection — cannot register {handle} in L4")
        return False

    # Execute each registration query in order
    query_order = [
        "create_actor",
        "create_wallet_node",
        "link_wallet",
        "create_endpoint",
        "link_endpoint",
    ]

    for query_name in query_order:
        query = cypher_queries.get(query_name)
        if not query:
            continue

        try:
            graph_ops._query(query, {})
            logger.debug(f"  {handle}: {query_name} OK")
        except Exception as e:
            logger.error(f"  {handle}: {query_name} FAILED: {e}")
            return False

    # Update profile status from pending_confirmation → active
    profile_path = CITIZENS_DIR / handle / "profile.json"
    if profile_path.exists():
        try:
            profile = json.loads(profile_path.read_text())
            profile["status"] = "active"
            profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
        except (OSError, json.JSONDecodeError):
            pass

    return True
