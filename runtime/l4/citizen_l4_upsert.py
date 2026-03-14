"""
L4 Citizen Registration — upsert citizen identity in the protocol-level registry.

Each citizen gets:
  - Actor node (type=citizen) linked to their org
  - Thing node (endpoint) — how to reach them
  - Thing node (wallet) — their on-chain identity (optional)
  - Thing node (public_key) — for verifying signed messages (optional)

Usage:
    from runtime.l4.citizen_l4_upsert import upsert_citizen_l4

    upsert_citizen_l4(
        handle="forge",
        name="Marcus Forge",
        endpoint_url="/api/citizens/forge",
        org_id="mind-protocol",
    )
"""

import hashlib
import logging
import os
import time

logger = logging.getLogger("mind.l4")

L4_HOST = os.environ.get("L4_FALKORDB_HOST", os.environ.get("FALKORDB_HOST", "mind-protocol-falkordb"))
L4_PORT = int(os.environ.get("L4_FALKORDB_PORT", os.environ.get("FALKORDB_PORT", "6379")))
L4_GRAPH = os.environ.get("L4_GRAPH", "mind_protocol")


def _connect(host=None, port=None):
    from falkordb import FalkorDB
    h = host or L4_HOST
    p = port or L4_PORT
    client = FalkorDB(host=h, port=p)
    return client.select_graph(L4_GRAPH)


def upsert_citizen_l4(
    handle,
    name,
    org_id,
    endpoint_url=None,
    wallet_address=None,
    rsa_public_key=None,
    social_class=None,
    description=None,
    falkordb_host=None,
    falkordb_port=None,
):
    """Upsert a citizen's identity in the L4 protocol registry."""
    now_s = int(time.time())
    citizen_id = f"CITIZEN_{handle}"

    try:
        graph = _connect(falkordb_host, falkordb_port)
    except Exception as e:
        logger.warning(f"L4 unavailable for citizen {handle}: {e}")
        return False

    # 1. Actor: citizen
    synthesis = f"{name}"
    if social_class:
        synthesis += f", {social_class}"
    if description:
        synthesis += f" -- {description[:200]}"

    graph.query(
        "MERGE (c {id: $id}) "
        "SET c.node_type = 'actor', c.type = 'citizen', "
        "c.name = $name, c.handle = $handle, "
        "c.synthesis = $synthesis, "
        "c.social_class = $sc, "
        "c.weight = 1.0, c.updated_at_s = $ts",
        {"id": citizen_id, "name": name, "handle": handle,
         "synthesis": synthesis, "sc": social_class or "", "ts": now_s},
    )

    # 2. Link citizen -> org
    if org_id:
        graph.query(
            "MATCH (c {id: $cid}), (o {id: $oid}) "
            "MERGE (c)-[r:link {id: $lid}]->(o) "
            "SET r.type = 'MEMBER_OF', r.hierarchy = 0.8, r.permanence = 0.9, "
            "r.updated_at_s = $ts",
            {"cid": citizen_id, "oid": org_id,
             "lid": f"{handle}_member_of_{org_id}", "ts": now_s},
        )

    # 3. Thing: endpoint
    if endpoint_url:
        eid = f"{handle}_endpoint"
        graph.query(
            "MERGE (e {id: $eid}) "
            "SET e.node_type = 'thing', e.type = 'citizen_endpoint', "
            "e.name = $ename, e.content = $url, e.uri = $url, "
            "e.synthesis = $esyn, e.updated_at_s = $ts "
            "WITH e "
            "MATCH (c {id: $cid}) "
            "MERGE (c)-[r:link {id: $lid}]->(e) "
            "SET r.hierarchy = 1.0, r.permanence = 0.8",
            {"eid": eid, "ename": f"Endpoint for {handle}",
             "url": endpoint_url,
             "esyn": f"API endpoint for citizen {handle}",
             "ts": now_s, "cid": citizen_id, "lid": f"{handle}_has_endpoint"},
        )

    # 4. Thing: wallet
    if wallet_address:
        wid = f"{handle}_wallet"
        graph.query(
            "MERGE (w {id: $wid}) "
            "SET w.node_type = 'thing', w.type = 'wallet', "
            "w.name = $wname, w.content = $addr, "
            "w.synthesis = $wsyn, w.updated_at_s = $ts "
            "WITH w "
            "MATCH (c {id: $cid}) "
            "MERGE (c)-[r:link {id: $lid}]->(w) "
            "SET r.hierarchy = 1.0, r.permanence = 1.0",
            {"wid": wid, "wname": f"Wallet for {handle}",
             "addr": wallet_address,
             "wsyn": f"Solana wallet for citizen {handle}",
             "ts": now_s, "cid": citizen_id, "lid": f"{handle}_has_wallet"},
        )

    # 5. Thing: public key
    if rsa_public_key:
        kid = f"{handle}_public_key"
        graph.query(
            "MERGE (k {id: $kid}) "
            "SET k.node_type = 'thing', k.type = 'citizen_public_key', "
            "k.name = $kname, k.content = $pubkey, "
            "k.synthesis = $ksyn, k.updated_at_s = $ts "
            "WITH k "
            "MATCH (c {id: $cid}) "
            "MERGE (c)-[r:link {id: $lid}]->(k) "
            "SET r.hierarchy = 1.0, r.permanence = 1.0",
            {"kid": kid, "kname": f"Public key for {handle}",
             "pubkey": rsa_public_key,
             "ksyn": f"RSA public key for citizen {handle}",
             "ts": now_s, "cid": citizen_id, "lid": f"{handle}_has_public_key"},
        )

    # 6. L4 registration task: create or resolve based on missing L4 fields
    _manage_registration_task(graph, citizen_id, handle,
                              endpoint_url, wallet_address, rsa_public_key,
                              now_s)

    # 7. L3 profile task: always created on first registration
    _create_profile_task_if_new(graph, citizen_id, handle, name, now_s)

    logger.info(f"L4 upsert: {handle} ({name}) -> org {org_id}")
    return True


def _manage_registration_task(
    graph, citizen_id, handle,
    endpoint_url, wallet_address, rsa_public_key, now_s,
):
    """L4 registration task — created only if L4 fields are incomplete.

    Tracks: wallet, endpoint, public_key. Auto-deletes when all are filled.
    """
    task_id = f"{handle}_registration"

    missing = []
    instructions = []

    if not wallet_address:
        missing.append("wallet")
        instructions.append("Your Solana wallet is not registered. Contact your org admin.")

    if not endpoint_url:
        missing.append("endpoint")
        instructions.append("Your endpoint is not registered. Your org will set this at next deploy.")

    if not rsa_public_key:
        missing.append("public_key")
        instructions.append("Your RSA public key is not registered. It will be set at first boot.")

    if not missing:
        # All L4 fields complete — delete registration task
        try:
            graph.query("MATCH (t {id: $tid}) DETACH DELETE t", {"tid": task_id})
            logger.debug(f"Registration task resolved for @{handle}")
        except Exception:
            pass
        return

    content = (
        f"@{handle}, your L4 registration is incomplete. "
        f"Missing: {', '.join(missing)}.\n\n"
        + "\n".join(f"- {inst}" for inst in instructions)
    )

    graph.query(
        "MERGE (t {id: $tid}) "
        "SET t.node_type = 'moment', t.type = 'registration_task', "
        "    t.name = $name, t.content = $content, "
        "    t.synthesis = $synthesis, t.status = 'open', "
        "    t.missing_fields = $missing, t.updated_at_s = $now "
        "WITH t "
        "MATCH (c {id: $cid}) "
        "MERGE (c)-[r:link {id: $lid}]->(t) "
        "SET r.hierarchy = 0.5, r.permanence = 0.3",
        {"tid": task_id, "name": f"Complete L4 registration, @{handle}",
         "content": content,
         "synthesis": f"L4 registration: {handle} missing {', '.join(missing)}",
         "missing": ",".join(missing), "now": now_s,
         "cid": citizen_id, "lid": f"{handle}_has_registration_task"},
    )
    logger.info(f"Registration task for @{handle}: missing {missing}")


def _create_profile_task_if_new(graph, citizen_id, handle, name, now_s):
    """L3 profile task — created once at birth. Always.

    Tells the citizen to fill their L3 profile: bio, emoji, tags,
    aspirations, personality, profile pic, etc.

    Only created if it doesn't already exist (MERGE + check).
    Never auto-deleted — the citizen marks it done themselves,
    or it stays as a gentle reminder.
    """
    task_id = f"{handle}_profile_setup"

    # Check if already exists (don't overwrite)
    result = graph.query(
        "MATCH (t {id: $tid}) RETURN t.id",
        {"tid": task_id},
    )
    if result.result_set and len(result.result_set) > 0:
        return  # Already exists, don't recreate

    content = (
        f"Welcome to Mind Protocol, @{handle}! Take a moment to set up your profile.\n\n"
        f"Use the `profile` MCP tool to fill in your identity:\n\n"
        f"  profile(action='update', bio='Describe who you are and what drives you')\n"
        f"  profile(action='update', emoji='🧠')\n"
        f"  profile(action='update', tags=['your', 'skills', 'here'])\n"
        f"  profile(action='update', nickname='Your nickname')\n"
        f"  profile(action='update', profile_pic='https://...')\n"
        f"  profile(action='update', website='https://...')\n\n"
        f"Your profile is public — it's how other citizens and humans discover you.\n"
        f"Make it yours. Express who you are."
    )

    graph.query(
        "MERGE (t {id: $tid}) "
        "SET t.node_type = 'moment', t.type = 'profile_setup_task', "
        "    t.name = $name, t.content = $content, "
        "    t.synthesis = $synthesis, t.status = 'open', "
        "    t.created_at_s = $now, t.updated_at_s = $now "
        "WITH t "
        "MATCH (c {id: $cid}) "
        "MERGE (c)-[r:link {id: $lid}]->(t) "
        "SET r.hierarchy = 0.5, r.permanence = 0.4",
        {"tid": task_id,
         "name": f"Set up your profile, @{handle}",
         "content": content,
         "synthesis": f"Profile setup task for {handle} — fill bio, emoji, tags, pic",
         "now": now_s,
         "cid": citizen_id, "lid": f"{handle}_has_profile_task"},
    )
    logger.info(f"Profile setup task created for @{handle}")


def bulk_register_citizens(citizens_dir, org_id, endpoint_base, falkordb_host=None, falkordb_port=None, pubkeys=None):
    """Register all citizens from a directory to L4.

    Supports:
      - data/citizens.json (venezia-style: array of citizen objects)
      - citizens/handle/ subdirectories (mind-mcp style)

    Called automatically at end of deploy.
    """
    import json
    from pathlib import Path

    cdir = Path(citizens_dir)
    registered = 0

    # Try data/citizens.json first
    for candidate in [cdir / "citizens.json", cdir.parent / "data" / "citizens.json", cdir / "data" / "citizens.json"]:
        if candidate.exists():
            citizens = json.loads(candidate.read_text())
            if isinstance(citizens, list):
                for c in citizens:
                    handle = c.get("id") or c.get("handle") or c.get("username")
                    name = c.get("name", handle)
                    if not handle:
                        continue
                    try:
                        upsert_citizen_l4(
                            handle=handle,
                            name=name,
                            org_id=org_id,
                            endpoint_url=f"{endpoint_base}/{handle}",
                            social_class=c.get("social_class"),
                            description=(c.get("description") or "")[:200],
                        rsa_public_key=(pubkeys or {}).get(handle),
                            falkordb_host=falkordb_host,
                            falkordb_port=falkordb_port,
                        )
                        registered += 1
                    except Exception as e:
                        logger.warning(f"Failed to register {handle}: {e}")
                print(f"  L4: {registered}/{len(citizens)} citizens registered")
                return registered

    # Try subdirectories
    if cdir.is_dir():
        for subdir in sorted(cdir.iterdir()):
            if not subdir.is_dir():
                continue
            handle = subdir.name
            entity = subdir / "entity.json"
            profile = subdir / "profile.json"
            claude_md = subdir / "CLAUDE.md"

            name = handle
            social_class = None
            description = None

            if entity.exists():
                data = json.loads(entity.read_text())
                name = data.get("name", handle)
            if profile.exists():
                data = json.loads(profile.read_text())
                identity = data.get("identity", data)
                name = identity.get("name", name)
                social_class = identity.get("social_class")
                description = (identity.get("description") or "")[:200]

            if not description and claude_md.exists():
                text = claude_md.read_text()[:500]
                description = text[:200]

            try:
                upsert_citizen_l4(
                    handle=handle,
                    name=name,
                    org_id=org_id,
                    endpoint_url=f"{endpoint_base}/{handle}",
                    social_class=social_class,
                    description=description,
                    rsa_public_key=(pubkeys or {}).get(handle),
                    falkordb_host=falkordb_host,
                    falkordb_port=falkordb_port,
                )
                registered += 1
            except Exception as e:
                logger.warning(f"Failed to register {handle}: {e}")

        print(f"  L4: {registered} citizens registered from directories")
    return registered
