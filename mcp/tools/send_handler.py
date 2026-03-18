"""
[SPEAK] Send — Send a message to any platform.

Supports: telegram, discord, whatsapp, twitter, email, sms.

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

# Paths — project root for bridge configs
PROJECT_ROOT = Path(os.getenv("MIND_PROJECT_ROOT", Path(__file__).parent.parent.parent))
STATE_DIR = PROJECT_ROOT / "shrine" / "state"
CITIZENS_DIR = PROJECT_ROOT / "citizens"

# Nicolas's Telegram chat ID
NICOLAS_CHAT_ID = "1864364329"

# Max message length (Telegram limit is 4096, others vary)
MAX_MESSAGE_LEN = 4000


def _resolve_partner(handle: str) -> dict:
    """Resolve a citizen's human partner and their contact channels.

    Returns {"partner_handle": str, "tg_id": str, "discord_dm": str} or empty dict.
    """
    import json
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
    message = (args.get("message") or "").strip()

    if not message:
        return _err("'message' is required and cannot be empty.")
    if not platform:
        return _err("'platform' is required.")

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
                        g = FalkorDB(host="localhost", port=6379).select_graph("lumina-prime")
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
            g = FalkorDB(host="localhost", port=6379).select_graph("lumina-prime")
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
        return _err(f"@{handle} has no human partner configured. Set relationships.human_partner in profile.json.")

    # Route to partner's preferred channel (TG first, then fallback)
    if partner.get("tg_id"):
        args["chat_id"] = partner["tg_id"]
        args["platform"] = "telegram"
        return _send_telegram(args)

    # Fallback: try Nicolas's chat ID (the default human)
    args["chat_id"] = NICOLAS_CHAT_ID
    args["platform"] = "telegram"
    return _send_telegram(args)


# ── Telegram ────────────────────────────────────────────────────────────────

def _send_telegram(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a Telegram message via Bot API."""
    import requests

    message = (args.get("message") or "").strip()
    chat_id = args.get("chat_id", NICOLAS_CHAT_ID)
    handle = _resolve_handle(args)

    formatted = f"*@{handle}:*\n{message}" if handle else f"*[citizen]:*\n{message}"
    if len(formatted) > MAX_MESSAGE_LEN:
        formatted = formatted[:MAX_MESSAGE_LEN - 3] + "..."

    config = _load_json(STATE_DIR / "telegram_config.json")
    bot_token = config.get("bot_token")
    if not bot_token:
        return _err("Telegram not configured. No bot_token in telegram_config.json.")

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": formatted, "parse_mode": "Markdown"}

    try:
        resp = requests.post(api_url, json=payload, timeout=15)
        if resp.ok:
            msg_id = resp.json()["result"]["message_id"]
            _log_message("telegram", formatted, chat_id, msg_id, handle=handle)
            return _ok(f"Sent to Telegram as @{handle or 'citizen'}. (message_id: {msg_id})")

        # Retry without Markdown on parse error
        resp_data = resp.json() if "json" in resp.headers.get("content-type", "") else {}
        if "can't parse entities" in resp_data.get("description", ""):
            payload.pop("parse_mode", None)
            resp2 = requests.post(api_url, json=payload, timeout=15)
            if resp2.ok:
                msg_id = resp2.json()["result"]["message_id"]
                _log_message("telegram", formatted, chat_id, msg_id, handle=handle)
                return _ok(f"Sent to Telegram as @{handle or 'citizen'} (plain). (message_id: {msg_id})")

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
    """Send a WhatsApp message via WAHA."""
    chat_id = args.get("chat_id")
    if not chat_id:
        return _err("'chat_id' (WhatsApp chat ID, e.g. '33612345678@c.us') is required.")

    message = (args.get("message") or "").strip()
    handle = _resolve_handle(args)

    # Prefix with handle so recipient knows who's talking
    text = f"[@{handle}] {message}" if handle else message

    try:
        _ensure_project_path("scripts")
        from whatsapp_bridge import send_text

        result = send_text(chat_id=chat_id, text=text)
        if result:
            _log_message("whatsapp", text, chat_id)
            return _ok(f"Sent to WhatsApp chat {chat_id} as @{handle or 'citizen'}.")
        else:
            return _err("WhatsApp send failed. Is WAHA running?")
    except ImportError:
        return _err("WhatsApp bridge not available. Check MIND_PROJECT_ROOT.")
    except Exception as e:
        return _err(f"WhatsApp send failed: {e}")


# ── Twitter/X ───────────────────────────────────────────────────────────────

def _send_twitter(args: Dict[str, Any]) -> Dict[str, Any]:
    """Post a tweet or reply via X API."""
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
        else:
            return _err("Twitter post returned no result. Check API config.")
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
