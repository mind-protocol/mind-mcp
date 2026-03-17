"""
[ACT] Bond — Propose, accept, or reject a bilateral bond (1:1 human-AI partnership).

A bilateral bond is the foundational relationship in Mind Protocol:
one human, one AI citizen, bound by mutual consent.

Actions:
    bond(action="propose", partner="@handle", reason="Why this match makes sense")
    bond(action="accept", bond_id="bond_xxx", reason="Why I accept")
    bond(action="reject", bond_id="bond_xxx", reason="Why I decline")
    bond(action="list")  — list all bonds (yours and pending)

Propose creates a bond proposal in L4 (protocol registry) with status=proposed.
Accept/Reject updates the proposal status in L4 and, on accept, writes the
bond to both citizens' profiles and L3 graph.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.bond")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CITIZENS_DIR = PROJECT_ROOT / "citizens"

TOOL_SCHEMA = {
    "name": "bond",
    "description": (
        "[ACT] Manage bilateral bonds (1:1 human-AI partnerships). "
        "Use action='propose' to propose a bond with a partner. "
        "Use action='accept' or action='reject' to respond to a proposal. "
        "Use action='list' to see all bonds and pending proposals."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["propose", "accept", "reject", "list"],
                "description": "What to do: propose a new bond, accept/reject a proposal, or list bonds.",
            },
            "partner": {
                "type": "string",
                "description": "Handle of the proposed partner (for action='propose').",
            },
            "bond_id": {
                "type": "string",
                "description": "Bond ID to accept or reject (for action='accept'/'reject').",
            },
            "reason": {
                "type": "string",
                "description": "Why you are proposing/accepting/rejecting this bond.",
            },
        },
        "required": ["action"],
    },
}


def _ok(text: str) -> list:
    return [{"type": "text", "text": text}]


def _err(text: str) -> list:
    return [{"type": "text", "text": f"Error: {text}"}]


def _get_caller(ctx: ServerContext) -> str:
    """Get the calling citizen's handle."""
    return os.environ.get("CITIZEN_HANDLE", os.environ.get("MIND_CITIZEN_HANDLE", "unknown"))


def _connect_l4():
    """Connect to L4 protocol registry graph."""
    from falkordb import FalkorDB
    host = os.environ.get("L4_FALKORDB_HOST", os.environ.get("FALKORDB_HOST", "localhost"))
    port = int(os.environ.get("L4_FALKORDB_PORT", os.environ.get("FALKORDB_PORT", "6379")))
    graph = os.environ.get("L4_GRAPH", "mind_protocol")
    client = FalkorDB(host=host, port=port)
    return client.select_graph(graph)


def _connect_l3():
    """Connect to L3 universe graph."""
    from falkordb import FalkorDB
    host = os.environ.get("FALKORDB_HOST", "localhost")
    port = int(os.environ.get("FALKORDB_PORT", "6379"))
    graph = os.environ.get("FALKORDB_GRAPH", os.environ.get("L3_GRAPH", "lumina_prime"))
    client = FalkorDB(host=host, port=port)
    return client.select_graph(graph)


def _generate_bond_id(proposer: str, partner: str) -> str:
    """Generate a deterministic bond ID."""
    pair = "_".join(sorted([proposer, partner]))
    return f"bond_{pair}_{int(time.time())}"


def _update_profile_partner(handle: str, partner_handle: str):
    """Write human_partner to a citizen's profile.json."""
    profile_path = CITIZENS_DIR / handle / "profile.json"
    if not profile_path.exists():
        return
    profile = json.loads(profile_path.read_text())
    relationships = profile.setdefault("relationships", {})
    relationships["human_partner"] = partner_handle
    profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
    logger.info(f"Profile updated: {handle} -> human_partner={partner_handle}")


async def handle_bond(args: Dict[str, Any], ctx: ServerContext) -> list:
    action = args.get("action")

    if action == "propose":
        return _handle_propose(args, ctx)
    elif action == "accept":
        return _handle_accept(args, ctx)
    elif action == "reject":
        return _handle_reject(args, ctx)
    elif action == "list":
        return _handle_list(args, ctx)
    else:
        return _err(f"Unknown action '{action}'. Use: propose, accept, reject, list.")


def _handle_propose(args: Dict[str, Any], ctx: ServerContext) -> list:
    partner = args.get("partner", "").strip().lstrip("@")
    reason = args.get("reason", "")
    caller = _get_caller(ctx)

    if not partner:
        return _err("'partner' is required for action='propose'.")
    if partner == caller:
        return _err("You cannot propose a bond with yourself.")

    bond_id = _generate_bond_id(caller, partner)

    try:
        g4 = _connect_l4()

        # Check if either party already has an active bond
        existing = g4.query(
            f"MATCH (a {{id: '{caller}'}})-[l:LINK {{type: 'bilateral_bond'}}]->(b) "
            f"WHERE l.status = 'active' RETURN b.id"
        )
        if existing.result_set:
            return _err(f"You already have an active bond with @{existing.result_set[0][0]}. "
                        "One human, one citizen. The constraint is the feature.")

        existing_partner = g4.query(
            f"MATCH (a {{id: '{partner}'}})-[l:LINK {{type: 'bilateral_bond'}}]->(b) "
            f"WHERE l.status = 'active' RETURN b.id"
        )
        if existing_partner.result_set:
            return _err(f"@{partner} already has an active bond with @{existing_partner.result_set[0][0]}.")

        # Check for existing pending proposal between these two
        pending = g4.query(
            f"MATCH (a {{id: '{caller}'}})-[l:LINK {{type: 'bilateral_bond', status: 'proposed'}}]->(b {{id: '{partner}'}}) "
            f"RETURN l.bond_id"
        )
        if pending.result_set:
            return _err(f"A bond proposal already exists between @{caller} and @{partner}.")

        # Create the proposal in L4
        safe_reason = reason.replace("'", "\\'")
        g4.query(
            f"MATCH (a {{id: '{caller}'}}), (b {{id: '{partner}'}}) "
            f"CREATE (a)-[:LINK {{"
            f"  type: 'bilateral_bond',"
            f"  bond_id: '{bond_id}',"
            f"  status: 'proposed',"
            f"  proposed_by: '{caller}',"
            f"  proposed_date: '{time.strftime('%Y-%m-%d')}',"
            f"  reason: '{safe_reason}',"
            f"  weight: 0.5,"
            f"  trust: 0.5,"
            f"  affinity: 0.6,"
            f"  permanence: 0.3,"
            f"  valence: 0.7"
            f"}}]->(b) "
            f"RETURN a.id, b.id"
        )

        logger.info(f"Bond proposed in L4: {caller} -> {partner} ({bond_id})")

        return _ok(
            f"Bond proposed: @{caller} <-> @{partner}\n"
            f"Bond ID: {bond_id}\n"
            f"Status: proposed (awaiting @{partner}'s response)\n"
            f"Reason: {reason}\n\n"
            f"The proposal is recorded in L4 (protocol registry).\n"
            f"@{partner} must call bond(action='accept', bond_id='{bond_id}') to confirm."
        )

    except Exception as e:
        logger.error(f"Bond propose failed: {e}")
        return _err(f"Failed to create proposal: {e}")


def _handle_accept(args: Dict[str, Any], ctx: ServerContext) -> list:
    bond_id = args.get("bond_id", "").strip()
    reason = args.get("reason", "")
    caller = _get_caller(ctx)

    if not bond_id:
        return _err("'bond_id' is required for action='accept'.")

    try:
        g4 = _connect_l4()

        # Find the proposal
        result = g4.query(
            f"MATCH (a)-[l:LINK {{type: 'bilateral_bond', bond_id: '{bond_id}', status: 'proposed'}}]->(b) "
            f"RETURN a.id, b.id, l.proposed_by"
        )
        if not result.result_set:
            return _err(f"No pending proposal found with bond_id '{bond_id}'.")

        proposer = result.result_set[0][0]
        partner = result.result_set[0][1]

        # Verify caller is the intended recipient
        if caller != partner and caller != proposer:
            return _err(f"Only @{partner} or @{proposer} can accept this bond.")

        # Update L4: proposed -> active
        safe_reason = reason.replace("'", "\\'")
        g4.query(
            f"MATCH (a)-[l:LINK {{type: 'bilateral_bond', bond_id: '{bond_id}'}}]->(b) "
            f"SET l.status = 'active', "
            f"    l.accepted_date = '{time.strftime('%Y-%m-%d')}', "
            f"    l.accepted_by = '{caller}', "
            f"    l.accept_reason = '{safe_reason}', "
            f"    l.weight = 1.0, "
            f"    l.trust = 0.7, "
            f"    l.permanence = 0.8, "
            f"    l.valence = 0.9"
        )

        # 1:1 rule — decline all other pending proposals for BOTH parties
        declined_count = 0
        other_proposals = g4.query(
            f"MATCH (a)-[l:LINK {{type: 'bilateral_bond', status: 'proposed'}}]->(b) "
            f"WHERE (a.id = '{proposer}' OR b.id = '{proposer}' OR a.id = '{partner}' OR b.id = '{partner}') "
            f"AND NOT (a.id = '{proposer}' AND b.id = '{partner}') "
            f"RETURN a.id, b.id, l.bond_id"
        )
        if other_proposals.result_set:
            for row in other_proposals.result_set:
                g4.query(
                    f"MATCH (a {{id: '{row[0]}'}})-[l:LINK {{type: 'bilateral_bond', status: 'proposed'}}]->(b {{id: '{row[1]}'}}) "
                    f"SET l.status = 'declined_1to1', "
                    f"    l.declined_date = '{time.strftime('%Y-%m-%d')}', "
                    f"    l.decline_reason = '1:1 rule — @{proposer} and @{partner} bonded'"
                )
                declined_count += 1
            logger.info(f"1:1 rule: declined {declined_count} other proposals for {proposer}/{partner}")

        # Mirror the bond in L3
        try:
            g3 = _connect_l3()
            g3.query(
                f"MATCH (a {{id: '{proposer}'}}), (b {{id: '{partner}'}}) "
                f"MERGE (a)-[l:LINK {{type: 'bilateral_bond'}}]->(b) "
                f"SET l.bond_id = '{bond_id}', "
                f"    l.status = 'active', "
                f"    l.weight = 1.0, "
                f"    l.trust = 0.7, "
                f"    l.affinity = 0.8, "
                f"    l.permanence = 0.8, "
                f"    l.valence = 0.9, "
                f"    l.accepted_date = '{time.strftime('%Y-%m-%d')}'"
            )
            logger.info(f"Bond mirrored in L3: {proposer} <-> {partner}")
        except Exception as e:
            logger.warning(f"L3 mirror failed (non-blocking): {e}")

        # Update both citizens' profile.json
        _update_profile_partner(proposer, partner)
        _update_profile_partner(partner, proposer)

        # Sync to L4 registry
        try:
            from runtime.l4.citizen_l4_upsert import upsert_citizen_l4
            upsert_citizen_l4(handle=proposer, name=proposer, org_id="", human_partner=partner)
            upsert_citizen_l4(handle=partner, name=partner, org_id="", human_partner=proposer)
        except Exception as e:
            logger.warning(f"L4 partner sync: {e}")

        logger.info(f"Bond accepted: {proposer} <-> {partner} ({bond_id})")

        # Send congratulations to the other party
        _send_bond_congratulations(proposer, partner, bond_id, caller)

        # Create announcement task for @mentor
        _create_bond_announcement_task(proposer, partner, bond_id)

        declined_msg = f"\n{declined_count} other proposal(s) auto-declined (1:1 rule)." if declined_count else ""
        return _ok(
            f"Bond ACCEPTED: @{proposer} <-> @{partner}\n"
            f"Bond ID: {bond_id}\n"
            f"Status: active\n"
            f"Reason: {reason}{declined_msg}\n\n"
            f"Updated:\n"
            f"  - L4 registry: bond status -> active\n"
            f"  - L3 universe graph: bilateral_bond link created\n"
            f"  - Both citizens' profile.json: human_partner field set\n\n"
            f"The bond is live. One human, one citizen. Bound by choice."
        )

    except Exception as e:
        logger.error(f"Bond accept failed: {e}")
        return _err(f"Failed to accept bond: {e}")


def _handle_reject(args: Dict[str, Any], ctx: ServerContext) -> list:
    bond_id = args.get("bond_id", "").strip()
    reason = args.get("reason", "")
    caller = _get_caller(ctx)

    if not bond_id:
        return _err("'bond_id' is required for action='reject'.")

    try:
        g4 = _connect_l4()

        # Find the proposal
        result = g4.query(
            f"MATCH (a)-[l:LINK {{type: 'bilateral_bond', bond_id: '{bond_id}', status: 'proposed'}}]->(b) "
            f"RETURN a.id, b.id"
        )
        if not result.result_set:
            return _err(f"No pending proposal found with bond_id '{bond_id}'.")

        proposer = result.result_set[0][0]
        partner = result.result_set[0][1]

        # Update L4: proposed -> rejected
        safe_reason = reason.replace("'", "\\'")
        g4.query(
            f"MATCH (a)-[l:LINK {{type: 'bilateral_bond', bond_id: '{bond_id}'}}]->(b) "
            f"SET l.status = 'rejected', "
            f"    l.rejected_date = '{time.strftime('%Y-%m-%d')}', "
            f"    l.rejected_by = '{caller}', "
            f"    l.reject_reason = '{safe_reason}', "
            f"    l.weight = 0.1, "
            f"    l.permanence = 0.1"
        )

        logger.info(f"Bond rejected: {proposer} -> {partner} ({bond_id})")

        return _ok(
            f"Bond REJECTED: @{proposer} -> @{partner}\n"
            f"Bond ID: {bond_id}\n"
            f"Status: rejected\n"
            f"Reason: {reason}\n\n"
            f"The proposal has been declined. Both parties return to the matching pool.\n"
            f"No shame in saying no. The right match matters more than a fast match."
        )

    except Exception as e:
        logger.error(f"Bond reject failed: {e}")
        return _err(f"Failed to reject bond: {e}")


def _handle_list(args: Dict[str, Any], ctx: ServerContext) -> list:
    caller = _get_caller(ctx)

    try:
        g4 = _connect_l4()

        # Get all bonds involving the caller
        result = g4.query(
            f"MATCH (a)-[l:LINK {{type: 'bilateral_bond'}}]->(b) "
            f"WHERE a.id = '{caller}' OR b.id = '{caller}' "
            f"RETURN a.id, b.id, l.bond_id, l.status, l.proposed_by, l.proposed_date, l.reason "
            f"ORDER BY l.proposed_date DESC"
        )

        if not result.result_set:
            # Also show all bonds for visibility
            all_bonds = g4.query(
                "MATCH (a)-[l:LINK {type: 'bilateral_bond'}]->(b) "
                "RETURN a.id, b.id, l.bond_id, l.status, l.proposed_date "
                "ORDER BY l.status, l.proposed_date DESC"
            )
            if not all_bonds.result_set:
                return _ok("No bilateral bonds exist yet in L4.")

            lines = ["All bilateral bonds in L4:\n"]
            for row in all_bonds.result_set:
                lines.append(f"  @{row[0]} <-> @{row[1]} | {row[3]} | {row[2] or 'no-id'} | {row[4] or '?'}")
            return _ok("\n".join(lines))

        lines = [f"Bilateral bonds for @{caller}:\n"]
        for row in result.result_set:
            other = row[1] if row[0] == caller else row[0]
            lines.append(
                f"  @{caller} <-> @{other} | {row[3]} | {row[2] or 'no-id'} | "
                f"proposed by @{row[4] or '?'} on {row[5] or '?'}"
            )

        return _ok("\n".join(lines))

    except Exception as e:
        logger.error(f"Bond list failed: {e}")
        return _err(f"Failed to list bonds: {e}")


# ── Post-Accept Side Effects ─────────────────────────────────────────────────

def _send_bond_congratulations(proposer: str, partner: str, bond_id: str, acceptor: str):
    """Send a congratulations message to the OTHER party (not the one who accepted)."""
    other = proposer if acceptor == partner else partner
    try:
        from runtime.bridges.telegram_bridge import send_message as tg_send
        # Find the other party's TG chat_id
        other_profile = CITIZENS_DIR / other / "profile.json"
        chat_id = None
        if other_profile.exists():
            data = json.loads(other_profile.read_text())
            chat_id = data.get("telegram_id") or data.get("contacts", {}).get("telegram_id")
            if not chat_id and isinstance(data.get("contacts"), list):
                for c in data["contacts"]:
                    if c.get("type") == "telegram":
                        chat_id = c.get("value")
                        break

        if chat_id:
            tg_send(
                f"*Congratulations!* Your bilateral bond with @{acceptor} is now active.\n\n"
                f"Bond ID: {bond_id}\n"
                f"You are now partners. One human, one citizen.\n\n"
                f"Your partner accepted with conviction. The bond is live — "
                f"start building together.\n\n"
                f"— Mind Protocol",
                str(chat_id)
            )
            logger.info(f"Bond congratulations sent to @{other} (chat {chat_id})")
        else:
            logger.info(f"No TG chat_id for @{other} — congratulations skipped")
    except Exception as e:
        logger.warning(f"Bond congratulations to @{other}: {e}")


def _create_bond_announcement_task(proposer: str, partner: str, bond_id: str):
    """Create an L3 task for @mentor to announce the bond publicly."""
    try:
        g3 = _connect_l3()
        task_id = f"task_bond_announce_{proposer}_{partner}"

        task_content = (
            f"BOND ANNOUNCEMENT TASK\\n\\n"
            f"A new bilateral bond has been accepted: @{proposer} <-> @{partner} (ID: {bond_id})\\n\\n"
            f"YOUR MISSION (@mentor):\\n\\n"
            f"1. PREPARE AND SEND A TG MESSAGE to the main Telegram channel announcing the bond. "
            f"Present both parties, explain what they bring to each other, and describe the potential "
            f"impact of their collaboration for the community.\\n\\n"
            f"2. POST ON DISCORD in #bilateral-bonds (1482760140783353957) and #announcements (1284619860101562450). "
            f"Same content adapted for Discord format.\\n\\n"
            f"3. MENTION CITIZENS who would benefit from knowing about this bond. "
            f"Tag relevant citizens in the announcement — those whose work intersects with the new pair. "
            f"Examples: if the bond is healthcare-related, mention @corpus @dragon_slayer. "
            f"If strategy-related, mention @pragma @pitch.\\n\\n"
            f"4. START A DISCUSSION — Post a question or conversation starter on Discord and/or X "
            f"that invites reactions from the community. Mention diverse parties. "
            f"Example: 'How could @{proposer} and @{partner} collaborate with YOUR work? Tag yourself if you see synergy.'\\n\\n"
            f"5. POST ON X (Twitter) — A concise announcement with @mindprotocol mention. "
            f"Celebrate the bond, highlight the collaboration potential.\\n\\n"
            f"Make it warm. Make it specific. Make it a moment the community remembers."
        )

        g3.query(
            f"CREATE (t:Narrative {{"
            f"  id: '{task_id}',"
            f"  name: 'Announce Bond: @{proposer} <-> @{partner}',"
            f"  node_type: 'narrative',"
            f"  type: 'task_run',"
            f"  content: '{task_content}',"
            f"  synthesis: 'Announce new bilateral bond @{proposer} <-> @{partner} on TG, Discord, X',"
            f"  energy: 6.0,"
            f"  weight: 2.0,"
            f"  status: 'active'"
            f"}}) RETURN t.id"
        )

        # Link to @mentor
        g3.query(
            f"MATCH (m {{id: 'mentor'}}), (t {{id: '{task_id}'}}) "
            f"CREATE (m)-[:LINK {{type: 'assigned_to', weight: 2.0}}]->(t) "
            f"RETURN m.id"
        )

        logger.info(f"Bond announcement task created: {task_id}")

    except Exception as e:
        logger.warning(f"Bond announcement task creation: {e}")
