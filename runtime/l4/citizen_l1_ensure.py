"""
L1 Citizen Ensure — verify and seed citizen L1 graph + RSA keypair.

For each citizen:
  1. Check if their L1 brain graph exists (has nodes in citizen's graph)
  2. If not, seed it from CLAUDE.md / profile.json / base brain
  3. Check if RSA keypair exists at .keys/citizens/{handle}/
  4. If not, generate one

Called BEFORE L4 registration — ensures every citizen has identity before announcing.

Usage:
    from runtime.l4.citizen_l1_ensure import ensure_citizen_l1

    pubkey = ensure_citizen_l1("DragonSlayer")
    # Returns public key PEM string, or None if keypair generation failed
"""

import json
import logging
import os
import subprocess
import time
from pathlib import Path

logger = logging.getLogger("mind.l1")

KEYS_BASE = Path(os.environ.get("KEYS_DIR", ".keys/citizens"))


def _get_graph(graph_name=None):
    """Connect to the citizen's L1 graph."""
    from falkordb import FalkorDB
    host = os.environ.get("FALKORDB_HOST", "localhost")
    port = int(os.environ.get("FALKORDB_PORT", "6379"))
    name = graph_name or os.environ.get("CITIZEN_GRAPH", os.environ.get("FALKORDB_GRAPH", "mind_protocol"))
    client = FalkorDB(host=host, port=port)
    return client.select_graph(name)


def check_l1_exists(handle, graph_name=None):
    """Check if citizen has nodes in their L1 graph."""
    try:
        graph = _get_graph(graph_name)
        citizen_id = f"CITIZEN_{handle}"
        result = graph.query(
            "MATCH (a {id: $id}) RETURN count(a)",
            {"id": citizen_id},
        )
        count = result.result_set[0][0] if result.result_set else 0
        return count > 0
    except Exception as e:
        logger.debug(f"L1 check failed for {handle}: {e}")
        return False


def seed_l1(handle, citizen_data=None, citizens_dir=None):
    """Seed citizen's L1 brain graph from available data.

    Sources (in priority):
      1. citizen_data dict (passed directly)
      2. citizens/{handle}/profile.json
      3. citizens/{handle}/CLAUDE.md
      4. data/citizens.json (venezia format)
    """
    try:
        graph = _get_graph()
    except Exception as e:
        logger.warning(f"Cannot seed L1 for {handle}: {e}")
        return False

    now_s = int(time.time())
    citizen_id = f"CITIZEN_{handle}"

    # Collect citizen info
    name = handle
    social_class = ""
    description = ""
    personality = ""

    if citizen_data:
        name = citizen_data.get("name", handle)
        social_class = citizen_data.get("social_class", "")
        description = citizen_data.get("description", "")
        personality = citizen_data.get("personality", "")
    else:
        # Try to find data from filesystem
        if citizens_dir:
            cdir = Path(citizens_dir)
            # venezia format: data/citizens.json
            for candidate in [cdir / "data" / "citizens.json", cdir / "citizens.json"]:
                if candidate.exists():
                    citizens = json.loads(candidate.read_text())
                    for c in citizens:
                        if (c.get("id") or c.get("handle")) == handle:
                            name = c.get("name", handle)
                            social_class = c.get("social_class", "")
                            description = c.get("description", "")
                            personality = c.get("personality", "")
                            break
                    break

            # mind-mcp format: citizens/{handle}/profile.json
            profile = cdir / "citizens" / handle / "profile.json"
            if profile.exists() and not description:
                data = json.loads(profile.read_text())
                identity = data.get("identity", data)
                name = identity.get("name", handle)
                social_class = identity.get("social_class", "")
                description = identity.get("description", "")

    synthesis = f"{name}"
    if social_class:
        synthesis += f", {social_class}"
    if description:
        synthesis += f" -- {description[:200]}"

    # Create Actor node
    graph.query(
        "MERGE (a {id: $id}) "
        "SET a.node_type = 'actor', a.type = 'citizen', "
        "a.name = $name, a.handle = $handle, "
        "a.synthesis = $syn, a.social_class = $sc, "
        "a.weight = 1.0, a.energy = 0.5, a.updated_at_s = $ts",
        {"id": citizen_id, "name": name, "handle": handle,
         "syn": synthesis, "sc": social_class, "ts": now_s},
    )

    # Seed personality as Narrative node
    if personality:
        graph.query(
            "MERGE (n {id: $nid}) "
            "SET n.node_type = 'narrative', n.type = 'personality', "
            "n.name = $nname, n.content = $content, "
            "n.synthesis = $syn, n.updated_at_s = $ts "
            "WITH n "
            "MATCH (a {id: $aid}) "
            "MERGE (a)-[r:link {id: $lid}]->(n) "
            "SET r.hierarchy = 0.9, r.permanence = 0.95",
            {"nid": f"{handle}_personality", "nname": f"Personality of {name}",
             "content": personality[:2000], "syn": personality[:300],
             "ts": now_s, "aid": citizen_id, "lid": f"{handle}_has_personality"},
        )

    # Seed description as Narrative node
    if description:
        graph.query(
            "MERGE (n {id: $nid}) "
            "SET n.node_type = 'narrative', n.type = 'backstory', "
            "n.name = $nname, n.content = $content, "
            "n.synthesis = $syn, n.updated_at_s = $ts "
            "WITH n "
            "MATCH (a {id: $aid}) "
            "MERGE (a)-[r:link {id: $lid}]->(n) "
            "SET r.hierarchy = 0.8, r.permanence = 0.9",
            {"nid": f"{handle}_backstory", "nname": f"Backstory of {name}",
             "content": description[:2000], "syn": description[:300],
             "ts": now_s, "aid": citizen_id, "lid": f"{handle}_has_backstory"},
        )

    logger.info(f"L1 seeded for {handle}: actor + personality + backstory")
    return True


def ensure_keypair(handle):
    """Generate RSA keypair for citizen if not exists. Returns public key PEM."""
    keys_dir = KEYS_BASE / handle
    priv_key = keys_dir / "rsa_private_key.pem"
    pub_key = keys_dir / "rsa_public_key.pem"

    if pub_key.exists():
        return pub_key.read_text()

    keys_dir.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["openssl", "genrsa", "-out", str(priv_key), "2048"],
            check=True, capture_output=True,
        )
        subprocess.run(
            ["openssl", "rsa", "-in", str(priv_key), "-pubout", "-out", str(pub_key)],
            check=True, capture_output=True,
        )
        os.chmod(priv_key, 0o400)
        logger.info(f"RSA keypair generated for {handle}")
        return pub_key.read_text()
    except Exception as e:
        logger.warning(f"Keypair generation failed for {handle}: {e}")
        return None


def ensure_citizen_l1(handle, citizen_data=None, citizens_dir=None):
    """Full ensure: check L1 graph, seed if missing, generate keypair.

    Returns public key PEM string or None.
    """
    # 1. Check/seed L1
    if not check_l1_exists(handle):
        seed_l1(handle, citizen_data=citizen_data, citizens_dir=citizens_dir)

    # 2. Ensure keypair
    pubkey = ensure_keypair(handle)

    return pubkey


def bulk_ensure_citizens(citizens_dir, graph_name=None):
    """Ensure all citizens have L1 graph + keypair.

    Returns dict of {handle: public_key_pem}.
    """
    from pathlib import Path
    cdir = Path(citizens_dir)
    results = {}
    citizens = []

    # Load citizen list
    for candidate in [cdir / "data" / "citizens.json", cdir / "citizens.json"]:
        if candidate.exists():
            citizens = json.loads(candidate.read_text())
            break

    if not citizens:
        # Scan subdirectories
        if cdir.is_dir():
            for subdir in sorted(cdir.iterdir()):
                if subdir.is_dir() and (subdir / "CLAUDE.md").exists():
                    citizens.append({"id": subdir.name, "name": subdir.name})

    ensured = 0
    for c in citizens:
        handle = c.get("id") or c.get("handle")
        if not handle:
            continue
        try:
            pubkey = ensure_citizen_l1(handle, citizen_data=c, citizens_dir=str(cdir))
            if pubkey:
                results[handle] = pubkey
                ensured += 1
        except Exception as e:
            logger.warning(f"Failed to ensure {handle}: {e}")

    print(f"  L1: {ensured}/{len(citizens)} citizens ensured (graph + keypair)")
    return results
