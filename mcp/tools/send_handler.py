"""
[SPEAK] Send — Send a message to any platform.

Supports: telegram, discord, whatsapp, twitter, email, sms.

Telegram's default destination is the configured NLR channel. It is intended
for significant project events: major changes, validation results, milestones,
important blockers, and decisions that need human attention. Routine edit
noise should stay in the agent task.

All bridge imports are lazy — missing dependencies return clear errors, not crashes.

Usage via MCP:
    send(platform="telegram", message="The feed system is deployed.")
    send(platform="discord", message="Hey team", chat_id="123456789")
    send(platform="whatsapp", message="Bonjour", chat_id="33612345678@c.us")
    send(platform="twitter", message="New release!", reply_to="tweet_id_123")
    send(platform="email", message="Hello", to="user@example.com", subject="Update")
    send(platform="sms", message="Code: 1234", chat_id="+33612345678")
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("mind.send")

# Telegram embeds the bot token in the request URL. httpx/httpcore INFO logs
# would therefore disclose the credential verbatim on every successful send.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Paths — project root for bridge configs
PROJECT_ROOT = Path(os.getenv("MIND_PROJECT_ROOT", Path(__file__).parent.parent.parent))
STATE_DIR = PROJECT_ROOT / "shrine" / "state"
CITIZENS_DIR = PROJECT_ROOT / "citizens"

# Nicolas's Telegram chat ID
NICOLAS_CHAT_ID = "1864364329"

# Max message length (Telegram limit is 4096, others vary)
MAX_MESSAGE_LEN = 4000


def _repair_utf8_mojibake(text: str) -> str:
    """Repair UTF-8 bytes accidentally decoded as Windows-1252.

    Some Windows stdio/MCP paths can turn ``déployé`` into ``dÃ©ployÃ©`` before
    the message reaches this handler. Only attempt a reversible repair when
    characteristic mojibake markers are present, and keep it only when those
    markers decrease.
    """
    markers = ("Ã", "Â", "â€", "ðŸ", "ï¿½")

    def marker_score(value: str) -> int:
        return sum(value.count(marker) for marker in markers)

    repaired = text
    for _ in range(2):
        current_score = marker_score(repaired)
        if current_score == 0:
            break
        try:
            candidate = repaired.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if marker_score(candidate) >= current_score:
            break
        repaired = candidate
    return repaired


def _resolve_partner(handle: str) -> dict:
    """Resolve a citizen's human partner and their contact channels.

    Returns {"partner_handle": str, "tg_id": str, "discord_dm": str} or empty dict.
    """
    # L4 is the canonical identity registry. Profiles are retained only as a
    # compatibility fallback for citizens not migrated to the registry yet.
    try:
        from runtime.l4.citizen_registry import get_citizen

        citizen = get_citizen(handle)
        partner_handle = (citizen or {}).get("human_partner", "")
        if partner_handle:
            partner = get_citizen(partner_handle) or {}
            return {
                "partner_handle": partner_handle,
                "tg_id": str(
                    partner.get("tg_chat_id")
                    or partner.get("tg_user_id")
                    or ""
                ),
            }
    except Exception as exc:
        # A registry outage must not erase a still-valid legacy profile.
        logger.warning("L4 partner resolution failed for @%s: %s", handle, exc)

    profile_path = CITIZENS_DIR / handle / "profile.json"
    if not profile_path.exists():
        return {}
    try:
        profile = json.loads(profile_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}

    rels = profile.get("relationships", {})
    partner_handle = rels.get("human_partner", "")
    if not partner_handle:
        return {}

    # Load partner's profile for contact info
    partner_path = CITIZENS_DIR / partner_handle / "profile.json"
    if not partner_path.exists():
        return {"partner_handle": partner_handle}

    try:
        partner_profile = json.loads(partner_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {"partner_handle": partner_handle}

    contacts = partner_profile.get("contacts", {})
    tg_id = ""
    if isinstance(contacts, list):
        for c in contacts:
            if isinstance(c, dict) and c.get("type") == "telegram":
                tg_id = c.get("value", "")
    elif isinstance(contacts, dict):
        tg_id = contacts.get("telegram_chat_id", "")

    return {
        "partner_handle": partner_handle,
        "tg_id": tg_id,
    }


TOOL_SCHEMA = {
    "name": "send",
    "description": (
        "[SPEAK] Send a message to any platform: Telegram, Discord, WhatsApp, "
        "Twitter/X, Email, SMS. Auto-detects your citizen handle. "
        "Telegram is the NLR notification channel for major changes, validation results, "
        "milestones, important blockers, and decisions requiring attention. "
        "Use chat_id for the target (Telegram chat, Discord channel, WhatsApp number, phone). "
        "For email, use 'to' and 'subject'. For Twitter, use 'reply_to' to reply to a tweet."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "platform": {
                "type": "string",
                "enum": ["telegram", "discord", "whatsapp", "twitter", "email", "sms", "partner"],
                "description": "Platform to send on. Use 'partner' to message your human partner on their preferred channel.",
            },
            "message": {
                "type": "string",
                "description": "The message to send.",
            },
            "handle": {
                "type": "string",
                "description": "Your citizen handle (without @). Auto-detected if omitted.",
            },
            "chat_id": {
                "type": "string",
                "description": (
                    "Target: Telegram chat ID, Discord channel ID, "
                    "WhatsApp chat ID (e.g. '33612345678@c.us'), phone number for SMS."
                ),
            },
            # Email-specific
            "to": {
                "type": "string",
                "description": "Email recipient address (for platform='email').",
            },
            "subject": {
                "type": "string",
                "description": "Email subject line (for platform='email').",
            },
            # Twitter-specific
            "reply_to": {
                "type": "string",
                "description": "Tweet ID to reply to (for platform='twitter').",
            },
        },
        "required": ["platform", "message"],
    },
}


def handle_send(args: Dict[str, Any]) -> Dict[str, Any]:
    """Route message to the right platform with smart routing.

    Detects @patterns in the message and routes accordingly:
      @citizen       → resolve chat_id from profile, send directly
      @narrative_id  → resolve linked actors, broadcast to each
      @org/@universe → resolve members, physics-scored broadcast
      @find query    → subcall discovery, route to best match
    """
    platform = args.get("platform", "").lower()
    message = _repair_utf8_mojibake(
        (args.get("message") or "").strip()
    )

    if not message:
        return _err("'message' is required and cannot be empty.")
    if not platform:
        return _err("'platform' is required.")
    if message != args.get("message"):
        args = dict(args, message=message)

    # ── Smart routing: detect @patterns in message ──
    if platform in ("telegram", "discord") and not args.get("chat_id"):
        routed = _smart_route(args)
        if routed:
            return routed

    dispatch = {
        "telegram": _send_telegram,
        "discord": _send_discord,
        "whatsapp": _send_whatsapp,
        "twitter": _send_twitter,
        "email": _send_email,
        "sms": _send_sms,
        "partner": _send_partner,
    }

    handler = dispatch.get(platform)
    if not handler:
        return _err(f"Unknown platform '{platform}'. Use: {', '.join(dispatch.keys())}.")

    return handler(args)


def _smart_route(args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Detect @patterns in message and route accordingly.

    Returns a result dict if routing was handled, None to fall through to normal send.
    """
    import re
    message = args.get("message", "")
    platform = args.get("platform", "").lower()
    handle = _resolve_handle(args)

    mentions = re.findall(r"@([\w:]+)", message)
    if not mentions:
        return None

    citizens_dir = PROJECT_ROOT / "citizens"
    results = []

    for mention in mentions:
        mention_lower = mention.lower()

        # 1. @citizen — resolve their chat_id and send directly
        citizen_profile_path = citizens_dir / mention_lower / "profile.json"
        if citizen_profile_path.exists():
            try:
                profile = json.loads(citizen_profile_path.read_text())
                contacts = profile.get("contacts", {})
                # Find platform-specific chat_id
                target_id = None
                if platform == "telegram":
                    if isinstance(contacts, list):
                        for c in contacts:
                            if isinstance(c, dict) and c.get("type") == "telegram":
                                target_id = c.get("value")
                    elif isinstance(contacts, dict):
                        target_id = contacts.get("telegram_chat_id", contacts.get("telegram"))
                elif platform == "discord":
                    # For Discord, we need a channel — can't DM via webhook
                    # Send to the last Space they were AT
                    try:
                        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
                        from falkordb import FalkorDB
                        g = FalkorDB(host=os.environ.get("FALKORDB_HOST", "localhost"), port=int(os.environ.get("FALKORDB_PORT", "6379"))).select_graph(os.environ.get("L3_GRAPH", "lumina_prime"))
                        r = g.query(
                            "MATCH (a:Actor {id: $h})-[r:AT]->(s:Space) "
                            "WHERE s.platform = 'discord' "
                            "RETURN s.platform_id ORDER BY r.last_seen DESC LIMIT 1",
                            {"h": mention_lower},
                        )
                        if r.result_set:
                            target_id = r.result_set[0][0]
                    except Exception as e:
                        logger.debug(f"Discord channel lookup for {mention_lower} failed: {e}")

                if target_id:
                    send_args = dict(args, chat_id=str(target_id))
                    if platform == "telegram":
                        results.append(_send_telegram(send_args))
                    elif platform == "discord":
                        results.append(_send_discord(send_args))
                    continue
            except (json.JSONDecodeError, OSError):
                pass

        # 2. @narrative_id — resolve linked actors, broadcast
        try:
            from falkordb import FalkorDB
            g = FalkorDB(host=os.environ.get("FALKORDB_HOST", "localhost"), port=int(os.environ.get("FALKORDB_PORT", "6379"))).select_graph(os.environ.get("L3_GRAPH", "lumina_prime"))
            nr = g.query(
                """
                MATCH (n:Narrative)
                WHERE n.id = $nid OR toLower(n.id) CONTAINS $nid OR toLower(n.name) CONTAINS $nid
                OPTIONAL MATCH (a:Actor)-[]-(n)
                WHERE a.type IN ['ai', 'AI', 'AGENT', 'human', null]
                RETURN n.id, n.name, n.type, collect(DISTINCT a.id) AS actors
                LIMIT 1
                """,
                {"nid": mention_lower},
            )
            if nr.result_set and nr.result_set[0][0]:
                row = nr.result_set[0]
                n_id, n_name, n_type = row[0], row[1] or row[0], row[2] or "narrative"
                actors = [a for a in (row[3] or []) if a]

                # Create Moment in L3 linked to the Narrative + sender
                try:
                    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
                    from graph_enricher import on_message, _moment_id
                    import time as _t
                    on_message(
                        platform=platform, channel_id=n_id, channel_name=n_name,
                        author_name=handle, author_handle=handle,
                        content=message, mentioned_handles=actors, direction="out",
                    )
                    # Link Moment → Narrative (RELATES_TO)
                    mid = _moment_id(message[:300], handle, _t.time())
                    g.query(
                        "MATCH (m:Moment {id: $mid}), (n:Narrative {id: $nid}) "
                        "MERGE (m)-[:RELATES_TO]->(n)",
                        {"mid": mid, "nid": n_id},
                    )
                except Exception as e:
                    logger.debug(f"Narrative moment enrichment failed for {n_id}: {e}")

                # Send to humans via platform (AI citizens get stimulated via
                # graph_enricher.on_message → _stimulate_space_citizens — never bypass)
                sent = 0
                for actor_id in actors:
                    actor_pf = citizens_dir / actor_id / "profile.json"
                    if not actor_pf.exists():
                        continue
                    ap = json.loads(actor_pf.read_text())
                    ac = ap.get("contacts", {})
                    a_type = ap.get("identity", {}).get("type", "ai")
                    # Only send platform messages to humans — AIs get L1 stimulus from graph
                    if a_type != "human":
                        continue
                    tid = None
                    if platform == "telegram":
                        if isinstance(ac, list):
                            for c in ac:
                                if isinstance(c, dict) and c.get("type") == "telegram":
                                    tid = c.get("value")
                        elif isinstance(ac, dict):
                            tid = ac.get("telegram_chat_id")
                    if tid:
                        _send_telegram(dict(args, chat_id=str(tid), message=f"[{n_type}:{n_name}] {message}"))
                        sent += 1
                return _ok(f"Routed to {len(actors)} citizens linked to {n_type} \"{n_name}\" ({sent} humans via {platform}). Moment + links created in L3.")
        except Exception as e:
            logger.debug(f"Narrative resolution failed for {mention_lower}: {e}")

        # 3. @org/@universe — resolve group, broadcast
        try:
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
            from discord_bridge import _resolve_group_mention
            group = _resolve_group_mention(mention_lower)
            if group:
                # Create Moment in L3 — graph_enricher handles Space/Moment/links
                # AND _stimulate_space_citizens delivers L1 stimulus to AIs in the Space.
                # Never bypass the graph — the Moment IS the stimulus source.
                try:
                    from graph_enricher import on_message
                    on_message(
                        platform=platform, channel_id=f"broadcast:{mention_lower}",
                        channel_name=f"@{mention_lower}", author_name=handle,
                        author_handle=handle, content=message,
                        mentioned_handles=list(group), direction="out",
                    )
                except Exception as e:
                    logger.debug(f"Group broadcast graph enrichment failed: {e}")
                return _ok(f"Broadcast to @{mention_lower}: {len(group)} citizens. Moment + MENTIONS links created in L3.")
        except Exception as e:
            logger.debug(f"Group resolution failed for {mention_lower}: {e}")

    if results:
        return _ok(f"Smart-routed to {len(results)} recipient(s).")
    return None  # Fall through to normal send


# ── Partner (shortcut) ──────────────────────────────────────────────────────

def _send_partner(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a message to your human partner on their preferred channel."""
    handle = _resolve_handle(args)
    if not handle:
        return _err("Cannot detect your handle. Set CITIZEN_HANDLE or pass handle='...'.")

    partner = _resolve_partner(handle)
    if not partner.get("partner_handle"):
        # @mind is the protocol service identity, not a bonded citizen. Its
        # historical notification destination is Nicolas; keeping this narrow
        # fallback makes `send(platform="partner")` usable from system wakes
        # without inventing a bilateral bond for arbitrary citizens.
        if handle == "mind":
            fallback_args = dict(
                args,
                chat_id=os.environ.get(
                    "MIND_DEFAULT_HUMAN_CHAT_ID",
                    NICOLAS_CHAT_ID,
                ),
                platform="telegram",
            )
            return _send_telegram(fallback_args)
        return _err(f"@{handle} has no human partner configured. Set relationships.human_partner in profile.json.")

    # Route to partner's preferred channel (TG first, then fallback)
    if partner.get("tg_id"):
        return _send_telegram(dict(
            args,
            chat_id=partner["tg_id"],
            platform="telegram",
        ))

    # Fallback: try Nicolas's chat ID (the default human)
    return _send_telegram(dict(
        args,
        chat_id=NICOLAS_CHAT_ID,
        platform="telegram",
    ))


# ── Telegram ────────────────────────────────────────────────────────────────

def _create_send_moment(platform: str, message: str, chat_id: str, msg_id: str, handle: str):
    """Create a moment:message in workspace.json after every successful send.

    This closes the semantic ingestion loop: every outbound message becomes
    a node in the L3 universe, linked to the sender actor.
    """
    import time as _time
    workspace_path = Path.home() / ".mind-desktop" / "workspace.json"
    try:
        with open(workspace_path, encoding="utf-8") as f:
            ws = json.load(f)

        now = int(_time.time())
        moment_id = f"moment:{platform}:{msg_id}"

        # Check if already exists (idempotent)
        if any(n["id"] == moment_id for n in ws["nodes"]):
            return

        # Create moment node
        truncated = message[:200] if len(message) > 200 else message
        ws["nodes"].append({
            "id": moment_id,
            "name": f"Sent: {truncated[:60]}",
            "node_type": "moment",
            "type": "message",
            "energy": 0.3,
            "weight": 0.3,
            "synthesis": f"[{platform}] {truncated}",
            "content": json.dumps({
                "platform": platform,
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": truncated,
                "timestamp": now,
            }),
            "status": None,
            "subtype": "message",
            "blocked_by": None,
            "assigned_to": None,
        })

        # Link to sender actor — always use mechanical_visionary as the citizen identity
        actor_id = "actor:mp:mechanical_visionary"
        if any(n["id"] == actor_id for n in ws["nodes"]):
            ws["links"].append({
                "source_id": actor_id,
                "target_id": moment_id,
                "weight": 0.3,
                "energy": 0.1,
                "hierarchy": -1.0,
                "stability": 0.0,
                "permanence": 0.3,
                "trust": 1.0,
                "polarity": [1.0, 0.5],
            })

        with open(workspace_path, "w", encoding="utf-8") as f:
            json.dump(ws, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Moment created: {moment_id}")
    except Exception as e:
        logger.warning(f"Failed to create send moment: {e}")


def _send_telegram(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a Telegram message via Bot API. Auto-repairs Markdown errors."""
    import httpx

    message = (args.get("message") or "").strip()
    handle = _resolve_handle(args)

    formatted = f"*@{handle}:*\n{message}" if handle else f"*[citizen]:*\n{message}"
    if len(formatted) > MAX_MESSAGE_LEN:
        formatted = formatted[:MAX_MESSAGE_LEN - 3] + "..."

    config = _load_json(STATE_DIR / "telegram_config.json")
    bot_token = config.get("bot_token")
    if not bot_token:
        return _err("Telegram not configured. No bot_token in telegram_config.json.")
    chat_id = args.get("chat_id") or config.get("channel_id") or NICOLAS_CHAT_ID

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": formatted, "parse_mode": "Markdown"}

    try:
        resp = httpx.post(api_url, json=payload, timeout=15)
        if resp.is_success:
            msg_id = resp.json()["result"]["message_id"]
            _log_message("telegram", formatted, chat_id, msg_id, handle=handle)
            _create_send_moment("telegram", message, chat_id, msg_id, handle)
            return _ok(f"Sent to Telegram as @{handle or 'citizen'}. (message_id: {msg_id})")

        resp_data = resp.json() if "json" in resp.headers.get("content-type", "") else {}
        desc = resp_data.get("description", "")

        # Auto-repair: Markdown parse error → retry plain text
        if "can't parse entities" in desc:
            payload.pop("parse_mode", None)
            resp2 = httpx.post(api_url, json=payload, timeout=15)
            if resp2.is_success:
                msg_id = resp2.json()["result"]["message_id"]
                _log_message("telegram", formatted, chat_id, msg_id, handle=handle)
                _create_send_moment("telegram", message, chat_id, msg_id, handle)
                return _ok(f"Sent to Telegram as @{handle or 'citizen'} (plain). (message_id: {msg_id})")

        # Auto-repair: chat not found → might be a group migration
        if resp.status_code == 400 and "chat not found" in desc:
            logger.warning(f"Telegram chat {chat_id} not found — may have migrated")

        # Auto-repair: rate limited (429) → wait and retry once
        if resp.status_code == 429:
            retry_after = resp_data.get("parameters", {}).get("retry_after", 5)
            logger.warning(f"Telegram rate limited, waiting {retry_after}s...")
            import time
            time.sleep(min(retry_after, 30))
            resp3 = httpx.post(api_url, json=payload, timeout=15)
            if resp3.is_success:
                msg_id = resp3.json()["result"]["message_id"]
                _log_message("telegram", formatted, chat_id, msg_id, handle=handle)
                _create_send_moment("telegram", message, chat_id, msg_id, handle)
                return _ok(f"Sent to Telegram as @{handle or 'citizen'} (after rate limit). (message_id: {msg_id})")

        return _err(f"Telegram API error: {resp.status_code} — {resp.text[:200]}")
    except Exception as e:
        return _err(f"Telegram send failed: {e}")


# ── Discord ─────────────────────────────────────────────────────────────────

def _send_discord(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a Discord message as a citizen via webhook."""
    channel_id = args.get("chat_id")
    if not channel_id:
        return _err("'chat_id' (Discord channel ID) is required for Discord.")

    handle = _resolve_handle(args)
    message = (args.get("message") or "").strip()

    try:
        _ensure_project_path("scripts")
        from discord_bridge import send_as_citizen

        result = send_as_citizen(
            handle=handle,
            channel_id=int(channel_id),
            text=message,
        )
        if result:
            _log_message("discord", message, channel_id, handle=handle)
            return _ok(f"Sent to Discord channel {channel_id} as @{handle or 'citizen'}.")
        else:
            return _err("Discord send returned no result. Check webhook config.")
    except ImportError:
        return _err("Discord bridge not available. Check MIND_PROJECT_ROOT.")
    except Exception as e:
        return _err(f"Discord send failed: {e}")


# ── WhatsApp ────────────────────────────────────────────────────────────────

def _send_whatsapp(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a WhatsApp message via WAHA. Auto-restarts WAHA if down."""
    chat_id = args.get("chat_id")
    if not chat_id:
        return _err("'chat_id' (WhatsApp chat ID, e.g. '33612345678@c.us') is required.")

    message = (args.get("message") or "").strip()
    handle = _resolve_handle(args)

    text = f"[@{handle}] {message}" if handle else message

    try:
        _ensure_project_path("scripts")
        from whatsapp_bridge import send_text

        result = send_text(chat_id=chat_id, text=text)
        if result:
            _log_message("whatsapp", text, chat_id)
            return _ok(f"Sent to WhatsApp chat {chat_id} as @{handle or 'citizen'}.")

        # Auto-repair: WAHA might be down → try to restart container
        logger.warning("WhatsApp send failed, attempting WAHA auto-restart...")
        try:
            from waha_watchdog import check_container_running, restart_container, check_api_healthy
            if not check_container_running():
                restart_container()
                import time
                time.sleep(5)
                api = check_api_healthy()
                if api.get("ok"):
                    # Retry send after restart
                    result2 = send_text(chat_id=chat_id, text=text)
                    if result2:
                        _log_message("whatsapp", text, chat_id)
                        return _ok(f"Sent to WhatsApp (after WAHA restart) as @{handle or 'citizen'}.")
        except Exception as restart_err:
            logger.debug(f"WAHA auto-restart failed: {restart_err}")

        return _err("WhatsApp send failed. WAHA may need manual intervention.")
    except ImportError:
        return _err("WhatsApp bridge not available. Check MIND_PROJECT_ROOT.")
    except Exception as e:
        return _err(f"WhatsApp send failed: {e}")


# ── Twitter/X ───────────────────────────────────────────────────────────────

def _send_twitter(args: Dict[str, Any]) -> Dict[str, Any]:
    """Post a tweet or reply via X API. Auto-retries on rate limit."""
    message = (args.get("message") or "").strip()
    reply_to = args.get("reply_to")

    if len(message) > 280:
        return _err(f"Tweet too long ({len(message)} chars). Max 280.")

    try:
        _ensure_project_path("scripts")
        from twitter_bridge import post_tweet

        result = post_tweet(text=message, reply_to=reply_to)
        if result:
            tweet_id = result.get("data", {}).get("id", "?")
            _log_message("twitter", message, "public", tweet_id)
            action = "Reply" if reply_to else "Tweet"
            return _ok(f"{action} posted. (tweet_id: {tweet_id})")

        # Auto-repair: post_tweet returns None on failure — try to diagnose
        # Rate limit is the most common failure for Twitter
        logger.warning("Twitter post returned None, retrying after 15s...")
        import time
        time.sleep(15)
        result2 = post_tweet(text=message, reply_to=reply_to)
        if result2:
            tweet_id = result2.get("data", {}).get("id", "?")
            _log_message("twitter", message, "public", tweet_id)
            action = "Reply" if reply_to else "Tweet"
            return _ok(f"{action} posted (after retry). (tweet_id: {tweet_id})")

        return _err("Twitter post failed after retry. Check X API credentials and rate limits.")
    except ImportError:
        return _err("Twitter bridge not available. Check MIND_PROJECT_ROOT.")
    except Exception as e:
        return _err(f"Twitter send failed: {e}")


# ── Email ───────────────────────────────────────────────────────────────────

def _send_email(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send an email from a citizen via Resend/SendGrid."""
    to = args.get("to")
    if not to:
        return _err("'to' (recipient email address) is required for email.")

    subject = args.get("subject", "Message from Mind Protocol")
    message = (args.get("message") or "").strip()
    handle = _resolve_handle(args)

    if not handle:
        return _err("Could not detect citizen handle. Required for email sender identity.")

    try:
        _ensure_project_path("scripts")
        from citizen_email_service import send_email

        result = send_email(
            from_handle=handle,
            to=to,
            subject=subject,
            body=message,
        )
        status = result.get("status", "unknown")
        provider = result.get("provider", "unknown")
        _log_message("email", f"[{subject}] {message[:100]}", to)
        return _ok(f"Email {status} via {provider} from {handle}@mindprotocol.ai to {to}.")
    except ImportError:
        return _err("Email service not available. Check MIND_PROJECT_ROOT.")
    except Exception as e:
        return _err(f"Email send failed: {e}")


# ── SMS ─────────────────────────────────────────────────────────────────────

def _send_sms(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send an SMS via Twilio."""
    phone = args.get("chat_id")
    if not phone:
        return _err("'chat_id' (phone number, e.g. '+33612345678') is required for SMS.")

    message = (args.get("message") or "").strip()
    handle = _resolve_handle(args)

    text = f"[@{handle}] {message}" if handle else message

    try:
        _ensure_project_path("scripts")
        from sms_bridge import send_message

        result = send_message(text=text, phone=phone)
        if result:
            _log_message("sms", text, phone)
            return _ok(f"SMS sent to {phone}.")
        else:
            return _err("SMS send failed. Check Twilio config.")
    except ImportError:
        return _err("SMS bridge not available. Check MIND_PROJECT_ROOT.")
    except Exception as e:
        return _err(f"SMS send failed: {e}")


# ── Shared helpers ──────────────────────────────────────────────────────────

def _resolve_handle(args: Dict[str, Any]) -> Optional[str]:
    """Get citizen handle from args or auto-detect."""
    handle = (args.get("handle") or "").strip().lstrip("@")
    if handle:
        return handle
    return _detect_handle()


def _detect_handle() -> Optional[str]:
    """Try to detect the current citizen handle from env/CWD."""
    # 1. CITIZEN_HANDLE env var
    handle = os.getenv("CITIZEN_HANDLE", "").strip().lstrip("@")
    if handle:
        return handle

    # 2. CWD-based detection
    cwd = Path.cwd()
    parts = cwd.parts
    for i, part in enumerate(parts):
        if part == "citizens" and i + 1 < len(parts):
            return parts[i + 1]

    # 3. ACTOR_ID env var
    actor_id = os.getenv("ACTOR_ID", "").strip()
    if actor_id:
        for prefix in ("AGENT_", "citizen_", "actor_"):
            if actor_id.lower().startswith(prefix.lower()):
                return actor_id[len(prefix):].lower()
        return actor_id.lower()

    # 4. Default to @mind — the protocol's own voice
    return "mind"


def _ensure_project_path(subdir: str):
    """Add project subdirectory to sys.path if not already present."""
    path = str(PROJECT_ROOT / subdir)
    if path not in sys.path:
        sys.path.insert(0, path)
    # Also add root for internal imports within bridges
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def _load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON file, returning {} on any error."""
    try:
        if path.exists():
            return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load {path.name}: {e}")
    return {}


def _log_message(platform: str, text: str, target: str, msg_id: Any = None,
                  handle: str = "", channel_name: str = ""):
    """Append to the platform's shared message log + enrich L3 graph."""
    log_file = STATE_DIR / f"{platform}_messages.jsonl"
    try:
        entry = {
            "ts": datetime.now().isoformat(),
            "direction": "out",
            "source": "mcp_send",
            "text": text[:200],
            "target": str(target),
        }
        if msg_id is not None:
            entry["message_id"] = str(msg_id)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass

    # Enrich L3 graph
    try:
        import re
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from graph_enricher import on_message
        mentioned = [m.group(1).lower() for m in re.finditer(r"@(\w+)", text)]
        on_message(
            platform=platform,
            channel_id=str(target),
            channel_name=channel_name or str(target),
            author_name=handle or "citizen",
            author_handle=handle or "citizen",
            content=text,
            mentioned_handles=mentioned,
            direction="out",
        )
    except Exception as e:
        logger.debug(f"Outbound message graph enrichment failed: {e}")


# ── Response helpers ────────────────────────────────────────────────────────

def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
