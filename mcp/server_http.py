"""
MCP HTTP/SSE Transport — wraps the stdio MCP server for remote access.

Exposes the same MindServer via HTTP POST /mcp for Claude.ai's
Remote MCP connector. Uses Server-Sent Events for streaming.

Usage:
    python mcp/server_http.py              # port 3005
    python mcp/server_http.py --port 8080

Then point Claude.ai custom connector to:
    https://trusted-magpie-social.ngrok-free.app/mcp
"""

import json
import logging
import sys
import uuid
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from flask import Flask, request, Response
from mcp.server import MindServer, TOOL_SCHEMAS
from mcp.tools.inject_cluster_handler import get_embedding, cosine_similarity

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stderr)
logger = logging.getLogger("mind.http")

app = Flask(__name__)
server = MindServer()
logger.info(f"MindServer loaded ({len(TOOL_SCHEMAS)} tools)")


@app.route("/mcp", methods=["POST"])
def mcp_endpoint():
    """Handle MCP JSON-RPC requests over the Streamable HTTP transport."""
    try:
        req = request.get_json(force=True)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {e}"}}), 400

    response = server.handle_request(req)

    # Notifications (e.g. notifications/initialized) produce no body.
    # Streamable HTTP expects 202 Accepted with an empty payload — strict
    # clients (ChatGPT) break if a notification gets a JSON-RPC reply.
    if response is None:
        return Response(status=202)

    resp = Response(json.dumps(response), mimetype="application/json")

    # On initialize, hand the client a session id. Streamable HTTP clients
    # echo it back in the Mcp-Session-Id header on subsequent calls; we accept
    # any value (stateless), but emitting one keeps strict clients happy.
    if isinstance(req, dict) and req.get("method") == "initialize":
        resp.headers["Mcp-Session-Id"] = uuid.uuid4().hex

    return resp


@app.route("/sse", methods=["GET"])
def sse_endpoint():
    """SSE endpoint for MCP streaming (Claude.ai Remote MCP)."""
    def event_stream():
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"
        # Keep alive
        import time
        while True:
            yield f": keepalive\n\n"
            time.sleep(30)

    return Response(event_stream(), mimetype="text/event-stream")


# ─── Telegram Webhook ─────────────────────────────────────────────────────────
# Incoming TG messages auto-create moment:message nodes in the L3 workspace.
# Privacy rule: only group/channel messages (chat_id < 0) go to L3.
# Private messages (chat_id > 0) are dropped until L1 brain encryption is live.

WORKSPACE_PATH = Path.home() / ".mind-desktop" / "workspace.json"


def _ensure_space(ws, chat_id, chat, topic_id=None):
    """Auto-create a space:telegram node for a chat/group/channel if it doesn't exist.
    For topics (threads), creates a child space linked to the parent.
    Returns the space_id."""
    import re as _re

    parent_space_id = f"space:telegram:{chat_id}"
    node_ids = {n["id"] for n in ws["nodes"]}

    if parent_space_id not in node_ids:
        chat_title = chat.get("title", f"chat_{chat_id}")
        chat_type = chat.get("type", "")
        username = chat.get("username", "")
        url = f"https://t.me/{username}" if username else ""

        ws["nodes"].append({
            "id": parent_space_id,
            "name": chat_title,
            "node_type": "space",
            "type": chat_type,
            "energy": 0.5,
            "weight": 0.5,
            "synthesis": f"Telegram {chat_type}: {chat_title}",
            "content": json.dumps({
                "platform": "telegram",
                "chat_id": str(chat_id),
                "chat_type": chat_type,
                "title": chat_title,
                "username": username,
                "url": url,
                "description": chat.get("description", ""),
            }),
            "status": None,
            "subtype": chat_type,
            "blocked_by": None,
            "assigned_to": None,
        })
        logger.info(f"[webhook] Space created: {parent_space_id} ({chat_title})")

    if not topic_id:
        return parent_space_id

    # Topic (thread) = child space
    topic_space_id = f"space:telegram:{chat_id}_topic_{topic_id}"
    if topic_space_id not in node_ids:
        ws["nodes"].append({
            "id": topic_space_id,
            "name": f"Topic {topic_id}",
            "node_type": "space",
            "type": "topic",
            "energy": 0.3,
            "weight": 0.3,
            "synthesis": f"Telegram topic in {chat.get('title', '')}",
            "content": json.dumps({"topic_id": str(topic_id), "parent_chat_id": str(chat_id)}),
            "status": None,
            "subtype": "topic",
            "blocked_by": None,
            "assigned_to": None,
        })
        # Link topic to parent space
        ws["links"].append({
            "source_id": parent_space_id,
            "target_id": topic_space_id,
            "weight": 0.5,
            "energy": 0.1,
            "hierarchy": -1.0,
            "stability": 0.8,
            "permanence": 0.9,
            "trust": 1.0,
            "polarity": [1.0, 1.0],
        })
        logger.info(f"[webhook] Topic space created: {topic_space_id}")

    return topic_space_id


def _extract_mentions(text):
    """Extract @username mentions from message text."""
    import re as _re
    return _re.findall(r"@(\w+)", text)


@app.route("/telegram-webhook", methods=["POST"])
def telegram_webhook():
    """Receive Telegram updates → create L3 spaces, moments, and actor links.

    Privacy: private messages (chat_id > 0) are dropped.
    Public messages create:
      1. A space:telegram node for the chat (auto-created on first message)
      2. A moment:message node for the message
      3. A sender link (actor → moment) resolved by TG username
      4. Receiver links for each @mention (actor → moment)
      5. A containment link (space → moment, hierarchy -1.0)
    """
    try:
        update = request.get_json(force=True)
    except Exception:
        return "bad json", 400

    msg = update.get("message") or update.get("channel_post")
    if not msg:
        return "ok", 200

    chat = msg.get("chat", {})
    chat_id = chat.get("id", 0)
    chat_type = chat.get("type", "")
    text = msg.get("text", "")
    msg_id = msg.get("message_id", "")
    from_user = msg.get("from", {})
    sender_name = from_user.get("first_name", "") or from_user.get("username", "unknown")
    sender_username = from_user.get("username", "")
    date = msg.get("date", 0)
    topic_id = msg.get("message_thread_id")  # TG forum topic

    if not text:
        return "ok", 200

    # Privacy: only public groups/channels (with a username/invite link) go to L3.
    # Private DMs and private groups without a public handle are dropped.
    chat_username = chat.get("username", "")
    if chat_type == "private":
        logger.info(f"[webhook] Private DM from {sender_name} — skipped (Privacy First)")
        return "ok", 200
    if not chat_username:
        logger.info(f"[webhook] Private group '{chat.get('title','')}' (no public username) — skipped (Privacy First)")
        return "ok", 200

    try:
        with open(WORKSPACE_PATH, encoding="utf-8") as f:
            ws = json.load(f)

        moment_id = f"moment:telegram:{chat_id}_{msg_id}"

        # Idempotent
        if any(n["id"] == moment_id for n in ws["nodes"]):
            return "ok", 200

        # 1. Ensure space exists (auto-create group/channel/topic)
        space_id = _ensure_space(ws, chat_id, chat, topic_id)

        # 2. Salience analysis via embedding anchors (no keywords, pure vector math)
        truncated = text[:300] if len(text) > 300 else text
        chat_title = chat.get("title", f"chat_{chat_id}")

        msg_energy = 0.2
        msg_valence = 0.0

        # Structural signals (language-agnostic)
        msg_energy += min(len(text) / 1000, 0.2)  # length = effort
        msg_energy += min(text.count("@") * 0.05, 0.1)  # mentions = social signal
        msg_energy = min(msg_energy, 0.9)

        # Embedding-based sentiment: computed in step 7 (after node creation)
        # We'll update energy/valence there using anchor similarity

        ws["nodes"].append({
            "id": moment_id,
            "name": f"{sender_name}: {truncated[:60]}",
            "node_type": "moment",
            "type": "message",
            "energy": round(msg_energy, 3),
            "weight": 0.2,
            "valence": round(msg_valence, 3),
            "synthesis": f"[{chat_title}] {sender_name}: {truncated}",
            "content": json.dumps({
                "platform": "telegram",
                "chat_id": str(chat_id),
                "chat_title": chat_title,
                "chat_type": chat_type,
                "message_id": str(msg_id),
                "sender": sender_name,
                "sender_username": sender_username,
                "text": truncated,
                "timestamp": date,
                "topic_id": str(topic_id) if topic_id else None,
            }),
            "status": None,
            "subtype": "message",
            "blocked_by": None,
            "assigned_to": None,
        })

        node_ids = {n["id"] for n in ws["nodes"]}

        # 2b. Temporal thread: link to previous moment in same space
        prev_moments = [
            n for n in ws["nodes"]
            if n["id"] != moment_id
            and n["node_type"] == "moment"
            and n.get("type") == "message"
            and f"telegram:{chat_id}_" in n["id"]
        ]
        if prev_moments:
            # Sort by message_id (last segment of ID) to find the most recent
            prev_moments.sort(key=lambda n: n["id"], reverse=True)
            prev = prev_moments[0]
            ws["links"].append({
                "source_id": prev["id"],
                "target_id": moment_id,
                "weight": 0.2,
                "energy": 0.1,
                "hierarchy": 0.0,
                "stability": 0.1,
                "permanence": 0.3,
                "trust": 1.0,
                "polarity": [1.0, 0.5],  # directional: prev → next
            })

        # 3. Link moment to space (containment)
        ws["links"].append({
            "source_id": space_id,
            "target_id": moment_id,
            "weight": 0.3,
            "energy": 0.1,
            "hierarchy": -1.0,
            "stability": 0.0,
            "permanence": 0.2,
            "trust": 1.0,
            "polarity": [1.0, 1.0],
        })

        # 4. Link sender actor → moment (resolved by TG handle)
        if sender_username:
            sender_actor = f"actor:mp:{sender_username}"
            if sender_actor in node_ids:
                ws["links"].append({
                    "source_id": sender_actor,
                    "target_id": moment_id,
                    "weight": 0.3,
                    "energy": 0.1,
                    "hierarchy": -1.0,
                    "stability": 0.0,
                    "permanence": 0.2,
                    "trust": 0.5,
                    "polarity": [1.0, 0.5],
                })

        # 5. Presence: move sender to this space (one space at a time)
        #    Remove old presence links, create new one with low stability (decays fast)
        if sender_username:
            sender_actor = f"actor:mp:{sender_username}"
            if sender_actor in node_ids:
                # Remove all existing presence links (actor → any space:telegram:*)
                ws["links"] = [
                    l for l in ws["links"]
                    if not (
                        l.get("source_id") == sender_actor
                        and l.get("target_id", "").startswith("space:telegram:")
                        and l.get("hierarchy", 0) == 0.0
                        and l.get("stability", 1.0) < 0.2
                    )
                ]
                # Create new presence link
                ws["links"].append({
                    "source_id": sender_actor,
                    "target_id": space_id,
                    "weight": 0.1,
                    "energy": 0.5,
                    "hierarchy": 0.0,
                    "stability": 0.05,  # very low — decays fast
                    "permanence": 0.1,  # ephemeral
                    "trust": 0.5,
                    "polarity": [1.0, 1.0],
                })
                logger.info(f"[webhook] Presence: {sender_username} → {space_id}")

        # 6. Link @mentioned actors as receivers
        mentions = _extract_mentions(text)
        for mention in mentions:
            receiver_actor = f"actor:mp:{mention}"
            if receiver_actor in node_ids:
                ws["links"].append({
                    "source_id": moment_id,
                    "target_id": receiver_actor,
                    "weight": 0.2,
                    "energy": 0.1,
                    "hierarchy": 0.0,
                    "stability": 0.0,
                    "permanence": 0.2,
                    "trust": 0.3,
                    "polarity": [0.5, 1.0],
                })

        # 7. Semantic discovery: embed, find cluster, inherit physics from neighbors
        auto_linked_to = None
        try:
            moment_node = next(n for n in ws["nodes"] if n["id"] == moment_id)
            emb = get_embedding(moment_node.get("synthesis", truncated))
            if emb:
                moment_node["embedding"] = emb

                # Find top-K nearest nodes by embedding
                scored = []
                for n in ws["nodes"]:
                    if n["id"] == moment_id:
                        continue
                    n_emb = n.get("embedding")
                    if not n_emb:
                        continue
                    sim = cosine_similarity(emb, n_emb)
                    if sim > 0.3:
                        scored.append((sim, n))

                scored.sort(key=lambda x: -x[0])
                cluster = scored[:5]  # top 5 neighbors = local cluster

                if cluster:
                    # Inherit physics from cluster: weighted average by cosine similarity
                    total_w = sum(sim for sim, _ in cluster)
                    if total_w > 0:
                        avg_energy = sum(sim * n.get("energy", 0.2) for sim, n in cluster) / total_w
                        avg_weight = sum(sim * n.get("weight", 0.2) for sim, n in cluster) / total_w
                        avg_valence = sum(sim * n.get("valence", 0.0) for sim, n in cluster) / total_w
                        avg_stability = sum(sim * n.get("stability", 0.0) for sim, n in cluster) / total_w

                        # Blend: 30% structural signal + 70% inherited from cluster
                        moment_node["energy"] = round(moment_node["energy"] * 0.3 + avg_energy * 0.7, 3)
                        moment_node["weight"] = round(moment_node["weight"] * 0.3 + avg_weight * 0.7, 3)
                        moment_node["valence"] = round(avg_valence, 3)
                        moment_node["stability"] = round(avg_stability * 0.5, 3)

                    # Link to best match
                    best_sim, best_node = cluster[0]
                    ws["links"].append({
                        "source_id": moment_id,
                        "target_id": best_node["id"],
                        "weight": round(best_sim * 0.4, 3),
                        "energy": round(moment_node["energy"] * 0.5, 3),
                        "hierarchy": 0.0,
                        "stability": 0.0,
                        "permanence": 0.2,
                        "trust": 0.0,
                        "affinity": round(best_sim * 0.3, 3),
                        "polarity": [0.5, 0.5],
                    })
                    auto_linked_to = (
                        f"{best_node['id']} (sim={best_sim:.3f}) "
                        f"cluster={len(cluster)} inherited: "
                        f"e={moment_node['energy']:.2f} w={moment_node['weight']:.2f} v={moment_node['valence']:.2f}"
                    )
        except Exception as e:
            logger.debug(f"[webhook] Embedding/auto-link skipped: {e}")

        with open(WORKSPACE_PATH, "w", encoding="utf-8") as f:
            json.dump(ws, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"[webhook] {moment_id} from {sender_name} in {chat_title}" +
                     (f" (topic {topic_id})" if topic_id else "") +
                     (f" mentions: {mentions}" if mentions else "") +
                     (f" linked→{auto_linked_to}" if auto_linked_to else ""))

    except Exception as e:
        logger.warning(f"[webhook] Failed: {e}")

    return "ok", 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return json.dumps({"status": "ok", "tools": len(TOOL_SCHEMAS), "server": "mind-mcp"})


@app.route("/tools", methods=["GET"])
def list_tools():
    """List available tools (convenience endpoint)."""
    return Response(json.dumps({"tools": TOOL_SCHEMAS}, indent=2), mimetype="application/json")


if __name__ == "__main__":
    port = 3005
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--port" and i + 1 < len(sys.argv) - 1:
            port = int(sys.argv[i + 2])

    logger.info(f"Starting HTTP MCP server on port {port}")
    logger.info(f"Endpoint: http://localhost:{port}/mcp")
    logger.info(f"Health: http://localhost:{port}/health")
    app.run(host="0.0.0.0", port=port, debug=False)
