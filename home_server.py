#!/usr/bin/env python3
"""
Mind Home Server — Citizen Home Runtime

A deployable FastAPI application that hosts N citizens with their own brains,
keys, and graph. Each deployment is a "citizen home" containing:
  - Physics engine (graph-based consciousness simulation)
  - Orchestrator (budget-driven dispatch of citizen sessions)
  - Bridges (Telegram, WhatsApp, Discord, Voice)
  - Membrane endpoint (universal information bus)
  - MCP server (tools for citizen cognition)

This is the HTTP wrapper around mind-mcp. The MCP server continues to run
on stdio for local Claude Code sessions; this adds HTTP endpoints for
cloud deployment, health monitoring, and cross-home communication.

Usage:
  uvicorn home_server:app --host 0.0.0.0 --port 8765
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("home")

# ── Startup state ───────────────────────────────────────────────────────────

_state = {
    "started_at": None,
    "graph_connected": False,
    "home_id": os.environ.get("HOME_ID", "mind-home-dev"),
    "version": "0.1.0",
}


def _configured_citizen_handles() -> list[str]:
    """Return explicit local citizens that must have a live engine."""
    raw_values = [
        os.environ.get("MIND_HTTP_CITIZEN", ""),
        os.environ.get("MIND_CITIZEN_HANDLE", ""),
        os.environ.get("MIND_CITIZEN_HANDLES", ""),
    ]
    handles = []
    for raw in raw_values:
        for value in raw.split(","):
            handle = value.strip().lstrip("@").lower().replace("-", "_")
            for prefix in ("citizen_", "actor_", "l3_actor_"):
                if handle.startswith(prefix):
                    handle = handle[len(prefix):]
                    break
            handle = handle.strip("_")
            if handle and handle not in handles:
                handles.append(handle)
    return handles


def _check_graph_connection() -> bool:
    """Test FalkorDB/Neo4j connectivity with an actual query."""
    try:
        from runtime.infrastructure.database import get_database_adapter
        adapter = get_database_adapter()
        return adapter.health_check()
    except Exception as e:
        logger.warning(f"Graph connection failed: {e}")
        return False


def _check_claude_cli() -> dict:
    """Test Claude Code CLI availability."""
    import subprocess
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        return {
            "available": result.returncode == 0,
            "version": result.stdout.strip() if result.returncode == 0 else None,
            "error": result.stderr.strip() if result.returncode != 0 else None,
        }
    except FileNotFoundError:
        return {"available": False, "version": None, "error": "claude not found in PATH"}
    except subprocess.TimeoutExpired:
        return {"available": False, "version": None, "error": "timeout"}


# ── Lifespan ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle for background tasks."""
    logger.info(f"Starting Mind Home Server: {_state['home_id']}")
    _state["started_at"] = time.time()
    _state["graph_connected"] = _check_graph_connection()

    if _state["graph_connected"]:
        logger.info("Graph database: connected")
    else:
        logger.warning("Graph database: NOT connected (will retry on requests)")

    claude_status = _check_claude_cli()
    if claude_status["available"]:
        logger.info(f"Claude Code CLI: {claude_status['version']}")
    else:
        logger.warning(f"Claude Code CLI: unavailable ({claude_status['error']})")

    # Phase 2: Start orchestrator dispatch loop
    _dispatcher = None
    if os.environ.get("ENABLE_ORCHESTRATOR", "true").lower() == "true":
        try:
            from runtime.orchestrator.dispatcher import Dispatcher
            _dispatcher = Dispatcher()
            _dispatcher.start()
            _state["dispatcher"] = _dispatcher
            logger.info("Orchestrator started (two-tick engine)")

            # Register dispatcher in citizen_wake for fast L1 stimulus injection
            try:
                from scripts.citizen_wake import set_dispatcher
                set_dispatcher(_dispatcher)
                logger.info("citizen_wake: dispatcher registered (fast stimulus path)")
            except Exception as e:
                logger.warning(f"citizen_wake dispatcher registration failed: {e}")
        except Exception as e:
            import traceback
            logger.error(f"ORCHESTRATOR FAILED TO START: {e}")
            logger.error(traceback.format_exc())
            print(f"[FATAL] Orchestrator failed to start: {e}", flush=True)
            print(traceback.format_exc(), flush=True)

    # Phase 2b: Upsert citizen brains at startup (configurable, togglable)
    if _dispatcher:
        try:
            import importlib
            import yaml

            # Citizens live in universe repos (canonical), world repo is primary
            _mind_mcp = Path(__file__).parent
            citizens_dir = _mind_mcp.parent.parent / "citizens"
            # Auto-discover universe citizen dirs from sibling repos
            # UNIVERSE_REPOS env: explicit comma-separated paths (for prod)
            # Otherwise: scan for sibling repos with world-manifest.json + citizens/
            _env_repos = os.environ.get("UNIVERSE_REPOS", "")
            if _env_repos:
                _universe_dirs = [Path(r.strip()) / "citizens" for r in _env_repos.split(",") if r.strip()]
            else:
                _parent = Path(__file__).parent.parent
                _universe_dirs = sorted(
                    p / "citizens" for p in _parent.iterdir()
                    if p.is_dir()
                    and (p / "citizens").is_dir()
                    and (p / "world-manifest.json").exists()
                    and p.name != "mind-mcp"
                )
            config_path = Path(__file__).parent / ".mind" / "database_config.yaml"

            # Load config
            cfg = {}
            if config_path.exists():
                with open(config_path) as f:
                    cfg = yaml.safe_load(f) or {}

            # Check if citizen_seed behavior is enabled (default: true)
            citizen_seed_enabled = cfg.get("behaviors", {}).get("citizen_seed", True)

            results = {}
            if citizen_seed_enabled:
                seed_fn_path = cfg.get("seed", {}).get(
                    "script", "runtime.l4.citizen_l1_ensure.bulk_ensure_citizens"
                )
                module_path, fn_name = seed_fn_path.rsplit(".", 1)
                mod = importlib.import_module(module_path)
                seed_fn = getattr(mod, fn_name)

                # 1. Seed mind-mcp/citizens first (fallback identities)
                results = seed_fn(str(citizens_dir))
                logger.info(f"L1 boot: {len(results)} citizens from mind-mcp")

                # 2. Seed universe repos — canonical, overwrites mind-mcp for overlapping handles
                for universe_dir in _universe_dirs:
                    if universe_dir.is_dir():
                        universe_results = seed_fn(str(universe_dir))
                        results.update(universe_results)
                        logger.info(f"L1 boot: +{len(universe_results)} from {universe_dir.parent.name} (canonical)")

            else:
                logger.info("L1 boot: citizen_seed disabled in database_config.yaml")

            # Explicitly hosted citizens may exist only in FalkorDB, without a
            # filesystem profile. They still need an in-memory cognitive engine.
            configured_handles = _configured_citizen_handles()
            engine_handles = list(dict.fromkeys([*results.keys(), *configured_handles]))
            if engine_handles:
                _dispatcher.bulk_load_citizen_engines(engine_handles)
                logger.info(
                    "L1 boot: %s total engines loaded (%s explicitly configured)",
                    len(engine_handles),
                    len(configured_handles),
                )
        except Exception as e:
            logger.warning(f"Citizen L1 boot failed: {e}")

    # Phase 3: Start bridges — pass dispatch_fn instead of enqueue
    _dispatch_fn = _dispatcher.dispatch if _dispatcher else None
    _telegram_bridge = None
    _whatsapp_bridge = None
    _twitter_bridge = None
    if os.environ.get("ENABLE_TELEGRAM", "true").lower() == "true":
        try:
            from runtime.bridges.telegram_bridge import start as tg_start
            known_ids = set(filter(None, os.environ.get("KNOWN_CHAT_IDS", "").split(",")))
            active_groups = set(filter(None, os.environ.get("ACTIVE_GROUPS", "").split(",")))
            tg_start(
                enqueue_fn=_dispatch_fn,
                known_chat_ids=known_ids,
                active_groups=active_groups,
            )
            _telegram_bridge = True
            _state["telegram_bridge"] = True
            logger.info("Telegram bridge started")
        except Exception as e:
            logger.warning(f"Telegram bridge failed to start: {e}")

    if os.environ.get("ENABLE_WHATSAPP", "true").lower() == "true":
        try:
            from runtime.bridges.whatsapp_bridge import init as wa_init
            wa_init(enqueue_fn=_dispatch_fn)
            _whatsapp_bridge = True
            _state["whatsapp_bridge"] = True
            logger.info("WhatsApp bridge initialized (webhook mode)")
        except Exception as e:
            logger.warning(f"WhatsApp bridge failed to initialize: {e}")

    # Phase 3b: Auto-repair WAHA webhook URL to match our port
    if _whatsapp_bridge:
        try:
            import requests as _req
            _waha_url = os.environ.get("WAHA_URL", "http://localhost:3002")
            _waha_key = os.environ.get("WAHA_API_KEY", "")
            _waha_session = os.environ.get("WAHA_SESSION", "default")
            _our_port = int(os.environ.get("PORT", "8766"))
            _headers = {"Content-Type": "application/json"}
            if _waha_key:
                _headers["X-Api-Key"] = _waha_key

            _sessions_resp = _req.get(f"{_waha_url}/api/sessions", headers=_headers, timeout=5)
            if _sessions_resp.status_code == 200:
                for _s in _sessions_resp.json():
                    if _s.get("name") == _waha_session:
                        for _wh in _s.get("config", {}).get("webhooks", []):
                            _wh_url = _wh.get("url", "")
                            if f":{_our_port}/" not in _wh_url and _wh_url:
                                # Port mismatch — auto-fix
                                import re
                                _fixed_url = re.sub(r":(\d+)/", f":{_our_port}/", _wh_url)
                                _req.put(
                                    f"{_waha_url}/api/sessions/{_waha_session}",
                                    headers=_headers, timeout=5,
                                    json={"config": {"webhooks": [{"url": _fixed_url, "events": _wh.get("events", ["message", "message.any"])}]}}
                                )
                                logger.info(f"WAHA webhook auto-repaired: {_wh_url} → {_fixed_url}")
                            else:
                                logger.info(f"WAHA webhook OK: {_wh_url}")
        except Exception as e:
            logger.warning(f"WAHA webhook auto-repair failed: {e}")

    if os.environ.get("ENABLE_TWITTER", "true").lower() == "true":
        try:
            from runtime.bridges.twitter_bridge import start as x_start
            x_start(enqueue_fn=_dispatch_fn)
            _twitter_bridge = True
            _state["twitter_bridge"] = True
            logger.info("X/Twitter bridge started")
        except Exception as e:
            logger.warning(f"X/Twitter bridge failed to start: {e}")

    # Phase 4: Start alarm watcher — pass dispatch_fn instead of enqueue
    _alarm_watcher = None
    if _dispatcher and os.environ.get("ENABLE_ALARMS", "true").lower() == "true":
        try:
            from runtime.orchestrator.alarm_watcher import AlarmWatcher
            _alarm_watcher = AlarmWatcher(enqueue_fn=_dispatch_fn)
            _alarm_watcher.start()
            logger.info("Alarm watcher started")
        except Exception as e:
            logger.warning(f"Alarm watcher failed to start: {e}")

    # Phase 5: Start WAHA watchdog (bridge health monitor)
    _waha_watchdog_task = None
    if _whatsapp_bridge:
        try:
            import asyncio
            from scripts.waha_watchdog import check_container_running, check_api_healthy, restart_container, _load_state, _save_state, notify_discord
            from datetime import datetime as _dt

            async def _waha_watchdog_loop():
                """Background task: check WAHA health every 5 min, auto-restart if down."""
                while True:
                    await asyncio.sleep(300)  # 5 minutes
                    try:
                        state = _load_state()
                        state["last_check"] = _dt.now().isoformat()

                        if not check_container_running():
                            logger.warning("WAHA watchdog: container DOWN, restarting...")
                            state["restart_count"] = state.get("restart_count", 0) + 1
                            if restart_container():
                                api = check_api_healthy()
                                if api["ok"] and api["status"] == "WORKING":
                                    state["status"] = "recovered"
                                    notify_discord(f"WAHA auto-recovered (restart #{state['restart_count']})")
                                else:
                                    state["status"] = "needs_qr"
                                    notify_discord(f"WAHA restarted but needs QR scan. @dev check.")
                            else:
                                state["status"] = "restart_failed"
                                notify_discord("WAHA restart FAILED. WhatsApp DOWN. @dev urgent.")
                        else:
                            api = check_api_healthy()
                            if api["ok"] and api["status"] == "WORKING":
                                state["status"] = "healthy"
                            elif api.get("status") == "SCAN_QR_CODE":
                                state["status"] = "needs_qr"
                                notify_discord("WAHA needs QR scan. WhatsApp disconnected.")

                        _save_state(state)
                    except Exception as e:
                        logger.debug(f"WAHA watchdog tick error: {e}")

            _waha_watchdog_task = asyncio.create_task(_waha_watchdog_loop())
            logger.info("WAHA watchdog started (5min interval, in event loop)")
        except Exception as e:
            logger.warning(f"WAHA watchdog failed to start: {e}")

    yield

    logger.info("Shutting down Mind Home Server")
    if _waha_watchdog_task:
        _waha_watchdog_task.cancel()
    if _alarm_watcher:
        _alarm_watcher.stop()
    if _telegram_bridge:
        try:
            from runtime.bridges.telegram_bridge import stop as tg_stop
            tg_stop()
        except Exception:
            pass
    if _twitter_bridge:
        try:
            from runtime.bridges.twitter_bridge import stop as x_stop
            x_stop()
        except Exception:
            pass
    if _dispatcher:
        _dispatcher.stop()


# ── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Mind Home Server",
    version=_state["version"],
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 3: WhatsApp webhook router
try:
    from runtime.bridges.whatsapp_bridge import router as whatsapp_router
    app.include_router(whatsapp_router)
except ImportError:
    pass

# Phase 5: Membrane HTTP endpoint
from runtime.membrane.http_endpoint import router as membrane_router
app.include_router(membrane_router)

# Phase 6: User-facing API routes (auth, chat, citizens, house, feed, DM)
from runtime.api.auth_routes import router as auth_router
from runtime.api.chat_routes import router as chat_router
from runtime.api.house_routes import router as house_router
from runtime.api.citizens_routes import router as citizens_router
from runtime.api.feed_routes import router as feed_router
from runtime.api.dm_routes import router as dm_router
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(house_router)
app.include_router(citizens_router)
app.include_router(feed_router)
app.include_router(dm_router)

# L4: Org confirmation endpoint
from runtime.l4.org_confirmation_endpoint import router as l4_router
app.include_router(l4_router)


# ── Citizen Ping ───────────────────────────────────────────────────────────

@app.get("/ping/{handle}")
async def ping_citizen(handle: str):
    """Ping a citizen hosted on this server.

    Called by L4 or other orgs to verify a citizen is alive.
    Returns: status, brain node count, last tick, orientation.
    """
    import os

    # 1. Check citizen dir exists
    citizens_dir = Path(__file__).resolve().parent / "citizens"
    citizen_dir = citizens_dir / handle
    has_profile = (citizen_dir / "profile.json").exists()

    # 2. Check brain in FalkorDB
    brain_nodes = 0
    brain_links = 0
    try:
        from falkordb import FalkorDB
        host = os.environ.get("FALKORDB_HOST", "localhost")
        port = int(os.environ.get("FALKORDB_PORT", "6379"))
        db = FalkorDB(host=host, port=port)
        graph = db.select_graph(f"brain_{handle}")
        result = graph.query("MATCH (n) RETURN count(n)")
        if result.result_set:
            brain_nodes = result.result_set[0][0]
        result2 = graph.query("MATCH ()-[r]->() RETURN count(r)")
        if result2.result_set:
            brain_links = result2.result_set[0][0]
    except Exception:
        pass

    # 3. Check L1 engine running in dispatcher
    engine_running = False
    orientation = None
    tick_count = 0
    dispatcher = _state.get("dispatcher")
    if dispatcher and hasattr(dispatcher, '_citizen_engines'):
        engine = dispatcher._citizen_engines.get(handle)
        if engine:
            engine_running = True
            orientation = getattr(engine, '_current_orientation', None)
            state = dispatcher._citizen_states.get(handle)
            if state:
                tick_count = state.tick_count

    # 4. Check keys
    keys_dir = Path(__file__).resolve().parent / ".keys" / handle
    has_wallet = (keys_dir / "solana_private_key.json").exists()
    has_rsa = (keys_dir / "rsa_private_key.pem").exists()

    alive = has_profile and brain_nodes > 0

    return {
        "handle": handle,
        "alive": alive,
        "profile": has_profile,
        "brain": {
            "nodes": brain_nodes,
            "links": brain_links,
        },
        "engine": {
            "running": engine_running,
            "orientation": orientation,
            "tick_count": tick_count,
        },
        "keys": {
            "wallet": has_wallet,
            "rsa": has_rsa,
        },
    }


@app.get("/api/sense/{handle}")
async def citizen_sense(handle: str):
    """Expose the citizen's read-only Global Workspace to remote MCP clients."""
    from types import SimpleNamespace
    from mcp.tools.sense_handler import handle_sense

    result = handle_sense(
        {"handle": handle},
        SimpleNamespace(disable_home_bridge=True),
    )
    content = result.get("content", [])
    text = content[0].get("text", "") if content else ""
    return {"handle": handle, "text": text}


@app.post("/api/cognition/stimulus")
async def cognitive_stimulus(request: Request):
    """Persist one MCP stimulus and run the live citizen's two cognitive ticks."""
    client_host = request.client.host if request.client else ""
    if client_host not in {"127.0.0.1", "::1", "localhost", "testclient"}:
        raise HTTPException(status_code=403, detail="Cognitive ingress is local-only")

    payload = await request.json()
    target = str(payload.get("target_handle") or "").strip().lstrip("@").lower()
    caller = str(payload.get("caller_handle") or "unknown").strip().lstrip("@").lower()
    content = str(payload.get("content") or "").strip()
    source = str(payload.get("source") or "mcp").strip()
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    if not target or not content:
        raise HTTPException(
            status_code=422, detail="target_handle and content are required"
        )

    dispatcher = _state.get("dispatcher")
    if dispatcher is None:
        raise HTTPException(status_code=503, detail="Cognitive dispatcher unavailable")

    from runtime.cognition.graph_reader_for_awareness_tick import citizen_actor_ids

    graph = dispatcher._get_shared_graph()
    if graph is None:
        raise HTTPException(status_code=503, detail="Shared L3 graph unavailable")

    moment_id = f"moment:mcp_stimulus:{uuid.uuid4().hex}"
    now = time.time()
    result = graph.query(
        """
        MATCH (a)
        WHERE a.id IN $actor_ids
        WITH a LIMIT 1
        MERGE (m:Moment {id: $moment_id})
        SET m.node_type = 'moment',
            m.type = 'cognitive_stimulus',
            m.content = $content,
            m.synthesis = $content,
            m.energy = 1.0,
            m.weight = 0.8,
            m.stability = 0.0,
            m.timestamp = $timestamp,
            m.source = $source,
            m.author_handle = $caller,
            m.metadata_json = $metadata_json
        MERGE (m)-[r:LINK]->(a)
        SET r.computed_type = 'stimulus_for',
            r.relation_kind = 'stimulus_for',
            r.weight = 0.9,
            r.energy = 1.0,
            r.perception_energy = 1.0
        RETURN a.id, m.id
        """,
        {
            "actor_ids": citizen_actor_ids(target),
            "moment_id": moment_id,
            "content": content,
            "timestamp": now,
            "source": source,
            "caller": caller,
            "metadata_json": json.dumps(metadata, ensure_ascii=False),
        },
    )
    if not result.result_set:
        raise HTTPException(
            status_code=404, detail=f"No L3 Actor found for citizen @{target}"
        )

    ticks = dispatcher.process_stimulus(target, source=source)
    return {
        "status": "processed",
        "target_handle": target,
        "moment_id": moment_id,
        "ticks": ticks,
    }


# ── Health ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Health check for Render/load balancer.

    Covers: graph, orchestrator, bridges, accounts, queue.
    """
    uptime = time.time() - _state["started_at"] if _state["started_at"] else 0

    # Orchestrator status
    dispatcher = _state.get("dispatcher")
    orchestrator = {}
    if dispatcher:
        try:
            orchestrator = dispatcher.get_status()
        except Exception:
            orchestrator = {"running": False, "error": "status unavailable"}

    # Bridge status
    bridges = {
        "telegram": _state.get("telegram_bridge") is not None,
        "whatsapp": _state.get("whatsapp_bridge") is not None,
        "twitter": _state.get("twitter_bridge") is not None,
    }

    # Account health
    accounts = {}
    try:
        from runtime.orchestrator.account_balancer import (
            get_accounts, healthy_account_count, accounts_healthy_line,
        )
        accts = get_accounts()
        accounts = {
            "total": len(accts),
            "healthy": healthy_account_count(),
            "detail": accounts_healthy_line(),
        }
    except Exception:
        accounts = {"total": 0, "healthy": 0, "detail": "unavailable"}

    # Overall status: degraded if graph down or no healthy accounts
    graph_ok = _state["graph_connected"]
    status = "ok"
    if not graph_ok:
        status = "degraded"
    elif accounts.get("healthy", 0) == 0:
        status = "degraded"

    # Activation pressure
    pressure = {}
    try:
        from runtime.orchestrator.activation_pressure import get_status as pressure_status
        pressure = pressure_status()
    except Exception:
        pressure = {"pressure": 0, "error": "unavailable"}

    return {
        "status": status,
        "home_id": _state["home_id"],
        "version": _state["version"],
        "uptime_seconds": round(uptime),
        "graph_connected": graph_ok,
        "orchestrator": orchestrator,
        "bridges": bridges,
        "accounts": accounts,
        "activation_pressure": pressure,
    }


@app.get("/api/info")
async def info():
    """Detailed home information for L4 registry and diagnostics."""
    claude_status = _check_claude_cli()

    from runtime.citizens import list_available_citizens
    citizens = list_available_citizens()

    return {
        "home_id": _state["home_id"],
        "version": _state["version"],
        "graph_connected": _state["graph_connected"],
        "claude_cli": claude_status,
        "citizen_count": len(citizens),
        "citizens": [c["handle"] for c in citizens],
        "endpoints": {
            "health": "/health",
            "info": "/api/info",
            "citizens": "/api/citizens",
            "citizen_search": "/api/citizens/search",
            "brain_scores": "/api/brain-scores",
            "house": "/api/house",
            "house_v2": "/house/state",
            "house_info": "/house/info",
            "house_profile_me": "/house/profile/me",
            "house_profile": "/house/profile/{user_id}",
            "house_citizens": "/house/citizens",
            "auth_register": "/auth/register",
            "auth_login": "/auth/login",
            "chat_send": "/chat/send",
            "chat_messages": "/chat/messages/{thread_id}",
            "feed_get": "/feed/{user_id}",
            "feed_post": "/feed/",
            "feed_me": "/feed/",
            "dm_send": "/dm/send",
            "dm_threads": "/dm/threads",
            "dm_thread": "/dm/thread/{other_user_id}",
            "dm_mark_read": "/dm/thread/{other_user_id}/read",
            "orchestrator": "/api/orchestrator/status",
            "chat_direct": "/api/chat",
            "membrane_stimulus": "/membrane/stimulus",
            "membrane_info": "/membrane/info",
            "membrane_subscribe": "/membrane/subscribe",
            "whatsapp_webhook": "/whatsapp/webhook",
            "voice_ws": "/voice/ws",
        },
    }


# ── Orchestrator status (kept inline — needs _state access) ────────────────

@app.post("/api/chat")
async def post_chat(request: Request):
    """Submit a message for processing by the orchestrator (direct dispatch)."""
    body = await request.json()
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    dispatcher = _state.get("dispatcher")
    if not dispatcher:
        raise HTTPException(status_code=503, detail="Orchestrator not running")

    dispatcher.dispatch({
        "voice_text": text,
        "text": text,
        "mode": body.get("mode", "partner"),
        "source": body.get("source", "api"),
        "sender": body.get("sender", "api_user"),
        "sender_id": body.get("sender_id", ""),
        "metadata": body.get("metadata", {}),
    })

    return {"status": "dispatched", "text": text[:80]}


# ── Citizen Profile Chat (InlineChatWidget) ──────────────────────────────

WEB_CHAT_DIR = Path(__file__).resolve().parent / "shrine" / "state"


@app.post("/api/chat/send")
async def citizen_chat_send(request: Request):
    """Receive a message from the citizen profile InlineChatWidget.

    Stores in shrine/state/web_chat_{citizen_id}.jsonl and returns a message_id.
    v0: store-only, no LLM response yet.
    """
    body = await request.json()
    citizen_id = (body.get("citizen_id") or "").strip()
    message = (body.get("message") or "").strip()
    platform = body.get("platform", "web")

    if not citizen_id:
        raise HTTPException(status_code=400, detail="citizen_id is required")
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    # Sanitize citizen_id for filename safety
    safe_id = "".join(c for c in citizen_id if c.isalnum() or c in "-_")[:64]
    if not safe_id:
        raise HTTPException(status_code=400, detail="Invalid citizen_id")

    message_id = uuid.uuid4().hex
    msg = {
        "id": message_id,
        "sender": "visitor",
        "content": message,
        "platform": platform,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    chat_file = WEB_CHAT_DIR / f"web_chat_{safe_id}.jsonl"
    WEB_CHAT_DIR.mkdir(parents=True, exist_ok=True)
    with open(chat_file, "a") as f:
        f.write(json.dumps(msg) + "\n")

    logger.info(f"web_chat [{safe_id}] visitor: {message[:60]}")

    return {"ok": True, "message_id": message_id}


@app.get("/api/chat/messages/{citizen_id}")
async def citizen_chat_messages(citizen_id: str, platform: str = "web", limit: int = 10):
    """Return recent messages for a citizen's profile chat widget.

    Reads from shrine/state/web_chat_{citizen_id}.jsonl and returns the last N messages.
    """
    safe_id = "".join(c for c in citizen_id if c.isalnum() or c in "-_")[:64]
    if not safe_id:
        raise HTTPException(status_code=400, detail="Invalid citizen_id")

    chat_file = WEB_CHAT_DIR / f"web_chat_{safe_id}.jsonl"
    if not chat_file.exists():
        return {"messages": []}

    messages = []
    for line in chat_file.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            msg = json.loads(line)
            if platform and msg.get("platform") != platform:
                continue
            messages.append(msg)
        except json.JSONDecodeError:
            continue

    # Return last N messages
    limit = max(1, min(limit, 100))
    return {"messages": messages[-limit:]}


@app.get("/api/orchestrator/status")
async def orchestrator_status():
    """Get orchestrator status."""
    dispatcher = _state.get("dispatcher")
    if not dispatcher:
        return {"running": False, "detail": "Orchestrator not started"}
    return dispatcher.get_status()


@app.get("/api/call/health")
async def call_health():
    """Voice call health metrics (H1-H6)."""
    try:
        from runtime.bridges.telegram_bridge import get_call_health
        return get_call_health()
    except Exception as e:
        return {"error": str(e)}


# ── Hot update — git pull + restart without Docker rebuild ──────────────────

@app.post("/api/update")
async def hot_update(request: Request):
    """Pull latest mind-mcp code and restart uvicorn.

    Called by GitHub webhook or manually. Avoids full Docker rebuild.
    Pulls the mind-mcp repo, then restarts the Python process.
    """
    import subprocess
    import signal

    results = {}

    # 1. Pull mind-mcp
    mcp_dir = Path(__file__).parent
    try:
        pull = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=str(mcp_dir),
            capture_output=True, text=True, timeout=30,
        )
        results["mind_mcp"] = {
            "stdout": pull.stdout.strip(),
            "stderr": pull.stderr.strip(),
            "returncode": pull.returncode,
        }
    except Exception as e:
        results["mind_mcp"] = {"error": str(e)}

    # 2. Pull the world repo (parent)
    world_dir = mcp_dir.parent.parent.parent  # /app/.mind/mind-mcp -> /app
    if (world_dir / ".git").exists() or (world_dir / "engine").exists():
        try:
            pull = subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=str(world_dir),
                capture_output=True, text=True, timeout=30,
            )
            results["world"] = {
                "stdout": pull.stdout.strip(),
                "returncode": pull.returncode,
            }
        except Exception as e:
            results["world"] = {"error": str(e)}

    # 3. Restart Python process (uvicorn will be restarted by the parent start.sh)
    restart = request.query_params.get("restart", "false").lower() == "true"
    if restart:
        results["restart"] = "sending SIGTERM to self"
        # Signal ourselves — start.sh will detect exit and can restart
        os.kill(os.getpid(), signal.SIGTERM)

    return {"status": "updated", "results": results}


# ── Voice WebSocket ─────────────────────────────────────────────────────────

@app.websocket("/voice/ws")
async def voice_ws(ws: WebSocket):
    """Real-time voice conversation via WebSocket."""
    try:
        from runtime.bridges.voice_websocket import voice_ws_handler
        await voice_ws_handler(ws)
    except ImportError:
        await ws.accept()
        await ws.send_json({"type": "error", "detail": "Voice bridge not available"})
        await ws.close()


# ── Error handling ──────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)},
    )


# ── Engine Proxy ──────────────────────────────────────────────────────────────
# Forward unmatched requests to the Node.js engine running on ENGINE_PORT.
# This makes the home_server the single exposed port on Render.
# The engine handles: WebSocket, 3D client, static assets, world manifest.

ENGINE_PORT = int(os.environ.get("ENGINE_PORT", 10001))

# Lazy-init a shared httpx client (created on first proxy request)
_httpx_client = None


def _get_httpx_client():
    global _httpx_client
    if _httpx_client is None:
        import httpx
        _httpx_client = httpx.AsyncClient(timeout=30.0)
    return _httpx_client


@app.websocket("/{path:path}")
async def proxy_ws_to_engine(ws: WebSocket, path: str):
    """WebSocket proxy: forward unmatched WS connections to Node.js engine."""
    import asyncio
    try:
        import websockets
    except ImportError:
        await ws.accept()
        await ws.send_json({"error": "websockets not installed for engine WS proxy"})
        await ws.close()
        return

    await ws.accept()
    engine_url = f"ws://localhost:{ENGINE_PORT}/{path}"

    try:
        async with websockets.connect(engine_url) as engine_ws:
            async def client_to_engine():
                try:
                    while True:
                        data = await ws.receive_text()
                        await engine_ws.send(data)
                except WebSocketDisconnect:
                    pass

            async def engine_to_client():
                try:
                    async for message in engine_ws:
                        await ws.send_text(message)
                except Exception:
                    pass

            await asyncio.gather(client_to_engine(), engine_to_client())
    except Exception as e:
        try:
            await ws.send_json({"error": f"engine WS unavailable: {e}"})
            await ws.close()
        except Exception:
            pass


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_to_engine(request: Request, path: str):
    """Reverse proxy: forward unmatched HTTP routes to Node.js engine."""
    try:
        client = _get_httpx_client()
    except ImportError:
        return JSONResponse(status_code=503, content={"error": "httpx not installed for engine proxy"})

    target = f"http://localhost:{ENGINE_PORT}/{path}"
    query = str(request.url.query)
    if query:
        target += f"?{query}"

    try:
        response = await client.request(
            method=request.method,
            url=target,
            headers={k: v for k, v in request.headers.items()
                     if k.lower() not in ("host", "content-length")},
            content=await request.body(),
        )

        # Filter hop-by-hop headers that shouldn't be forwarded
        excluded_headers = {"transfer-encoding", "connection", "content-encoding", "content-length"}
        headers = {k: v for k, v in response.headers.items()
                   if k.lower() not in excluded_headers}

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=headers,
        )
    except Exception as e:
        error_type = type(e).__name__
        if "ConnectError" in error_type or "ConnectionRefused" in str(e):
            return JSONResponse(
                status_code=502,
                content={"error": "engine_not_running", "message": f"Node.js engine not available on port {ENGINE_PORT}"},
            )
        return JSONResponse(status_code=502, content={"error": str(e)})


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8765))

    # Running this file directly is the local-dev path, so auto-reload is on: edit any
    # .py and the server comes back by itself. Set MIND_RELOAD=0 to pin it down.
    # Production does not come through here — docker/entrypoint.sh execs uvicorn directly.
    #
    # Only *.py is watched (uvicorn's default include) and dot-directories are excluded,
    # so .venv/ is skipped. The excludes below matter more: this server writes its own
    # heartbeat every 30s under data/ — watching that would restart it in a loop.
    reload = os.environ.get("MIND_RELOAD", "1").strip().lower() not in {"0", "false", "no", "off"}
    if reload:
        logger.info("Auto-reload enabled — the server restarts on any .py change (MIND_RELOAD=0 to disable)")

    uvicorn.run(
        "home_server:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        reload_excludes=["data/*", "citizens/*", "shrine/*", "logs/*"] if reload else None,
    )
