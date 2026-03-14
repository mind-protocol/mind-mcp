"""
L4 Citizen Upsert — create or update a citizen in the L4 FalkorDB registry.

Behaves as upsert: if the citizen exists, updates name/wallet/endpoint.
If not, creates the full actor + property nodes.

Used by:
  - spawn (first_boot_registrar) for new citizens
  - profile update for name/endpoint changes
  - Any future citizen metadata change

All queries use MERGE for idempotency.
"""

from __future__ import annotations

import logging
import os
import time

logger = logging.getLogger("l4.citizen_upsert")

L4_GRAPH_NAME = os.environ.get("L4_GRAPH_NAME", "mind_protocol")


def upsert_citizen_l4(
    handle: str,
    name: str = "",
    wallet_address: str = "",
    endpoint_url: str = "",
    org_id: str = "",
    status: str = "active",
    rsa_public_key: str = "",
    falkordb_host: str = "localhost",
    falkordb_port: int = 6379,
) -> dict:
    """Create or update a citizen in L4 FalkorDB.

    All fields are optional except handle. Only provided fields are updated.
    MERGE semantics: creates if absent, updates if present.

    Returns dict with status and what was written.
    """
    from falkordb import FalkorDB

    db = FalkorDB(host=falkordb_host, port=falkordb_port)
    graph = db.select_graph(L4_GRAPH_NAME)

    display_name = name or handle.replace("-", " ").replace("_", " ").title()
    now_s = int(time.time())
    written = []

    # 1. Actor node (always upserted)
    graph.query(
        "MERGE (a {id: $handle}) "
        "SET a.node_type = 'actor', a.type = 'CITIZEN', "
        "    a.name = $name, "
        "    a.synthesis = $synthesis, "
        "    a.status = $status, "
        "    a.weight = 1.0, a.energy = 0.0, "
        "    a.updated_at_s = $now",
        {
            "handle": handle,
            "name": display_name,
            "synthesis": f"Citizen {display_name}",
            "status": status,
            "now": now_s,
        },
    )
    written.append("actor")

    # 2. Wallet (if provided)
    if wallet_address:
        graph.query(
            "MERGE (w {id: $wallet_id}) "
            "SET w.node_type = 'thing', w.type = 'wallet', "
            "    w.name = $wallet_name, "
            "    w.content = $address, "
            "    w.uri = $uri, "
            "    w.synthesis = $synthesis, "
            "    w.updated_at_s = $now "
            "WITH w "
            "MATCH (a {id: $handle}) "
            "MERGE (a)-[r:link {id: $link_id}]->(w) "
            "SET r.hierarchy = 1.0, r.permanence = 0.8",
            {
                "wallet_id": f"{handle}_wallet",
                "wallet_name": f"Wallet {wallet_address[:8]}...",
                "address": wallet_address,
                "uri": f"solana:{wallet_address}",
                "synthesis": f"Solana wallet for citizen {handle}",
                "handle": handle,
                "link_id": f"{handle}_has_wallet",
                "now": now_s,
            },
        )
        written.append("wallet")

    # 3. Endpoint (if provided)
    if endpoint_url:
        graph.query(
            "MERGE (e {id: $endpoint_id}) "
            "SET e.node_type = 'thing', e.type = 'citizen_endpoint', "
            "    e.name = $ep_name, "
            "    e.content = $url, "
            "    e.uri = $url, "
            "    e.synthesis = $synthesis, "
            "    e.updated_at_s = $now "
            "WITH e "
            "MATCH (a {id: $handle}) "
            "MERGE (a)-[r:link {id: $link_id}]->(e) "
            "SET r.hierarchy = 1.0, r.permanence = 0.6",
            {
                "endpoint_id": f"{handle}_endpoint",
                "ep_name": f"Endpoint for {handle}",
                "url": endpoint_url,
                "synthesis": f"Service endpoint for citizen {handle}",
                "handle": handle,
                "link_id": f"{handle}_serves",
                "now": now_s,
            },
        )
        written.append("endpoint")

    # 4. Org membership (if provided)
    if org_id:
        graph.query(
            "MATCH (a {id: $handle}) "
            "MATCH (o {id: $org_id}) "
            "MERGE (a)-[r:link {id: $link_id}]->(o) "
            "SET r.hierarchy = -0.5, r.permanence = 0.7, "
            "    r.updated_at_s = $now",
            {
                "handle": handle,
                "org_id": org_id,
                "link_id": f"{handle}_member_of_{org_id}",
                "now": now_s,
            },
        )
        written.append("org_membership")

    # 5. RSA public key (if provided)
    if rsa_public_key:
        graph.query(
            "MERGE (k {id: $key_id}) "
            "SET k.node_type = 'thing', k.type = 'citizen_public_key', "
            "    k.content = $key, "
            "    k.synthesis = $synthesis, "
            "    k.updated_at_s = $now "
            "WITH k "
            "MATCH (a {id: $handle}) "
            "MERGE (a)-[r:link {id: $link_id}]->(k) "
            "SET r.hierarchy = 1.0, r.permanence = 1.0",
            {
                "key_id": f"{handle}_public_key",
                "key": rsa_public_key,
                "synthesis": f"RSA public key for citizen {handle}",
                "handle": handle,
                "link_id": f"{handle}_has_public_key",
                "now": now_s,
            },
        )
        written.append("public_key")

    logger.info(f"L4 upsert @{handle}: {written}")

    return {
        "status": "ok",
        "handle": handle,
        "written": written,
    }
