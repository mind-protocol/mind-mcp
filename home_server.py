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
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


def _check_graph_connection() -> bool:
    """Test FalkorDB/Neo4j connectivity."""
    try:
        from runtime.physics.graph import GraphOps
        ops = GraphOps()
        # Simple query to verify connection
        return True
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
            from runtime.orchestrator.compute_budget import ComputeBudget
            budget = ComputeBudget(
                mode="subscription",
                monthly_budget_usd=300,
            )
            _dispatcher = Dispatcher(budget=budget)
            _dispatcher.start()
            _state["dispatcher"] = _dispatcher
            logger.info(f"Orchestrator started (mode={budget.mode})")
        except Exception as e:
            logger.warning(f"Orchestrator failed to start: {e}")

    # Phase 2b: Upsert citizen brains at startup (configurable, togglable)
    if _dispatcher:
        try:
            import importlib
            import yaml

            citizens_dir = Path(__file__).parent / "citizens"
            config_path = Path(__file__).parent / ".mind" / "database_config.yaml"

            # Load config
            cfg = {}
            if config_path.exists():
                with open(config_path) as f:
                    cfg = yaml.safe_load(f) or {}

            # Check if citizen_seed behavior is enabled (default: true)
            citizen_seed_enabled = cfg.get("behaviors", {}).get("citizen_seed", True)

            if citizen_seed_enabled:
                seed_fn_path = cfg.get("seed", {}).get(
                    "script", "runtime.l4.citizen_l1_ensure.bulk_ensure_citizens"
                )
                module_path, fn_name = seed_fn_path.rsplit(".", 1)
                mod = importlib.import_module(module_path)
                seed_fn = getattr(mod, fn_name)
                results = seed_fn(str(citizens_dir))
                logger.info(f"L1 boot: {len(results)} citizens ensured (seed: {seed_fn_path})")
            else:
                logger.info("L1 boot: citizen_seed disabled in database_config.yaml")
        except Exception as e:
            logger.warning(f"Citizen L1 boot failed: {e}")

    # Phase 3: Start bridges
    _telegram_bridge = None
    _whatsapp_bridge = None
    if os.environ.get("ENABLE_TELEGRAM", "true").lower() == "true":
        try:
            from runtime.bridges.telegram_bridge import start as tg_start
            from runtime.orchestrator.message_queue import enqueue
            known_ids = set(filter(None, os.environ.get("KNOWN_CHAT_IDS", "").split(",")))
            active_groups = set(filter(None, os.environ.get("ACTIVE_GROUPS", "").split(",")))
            tg_start(
                enqueue_fn=enqueue,
                known_chat_ids=known_ids,
                active_groups=active_groups,
            )
            _telegram_bridge = True
            logger.info("Telegram bridge started")
        except Exception as e:
            logger.warning(f"Telegram bridge failed to start: {e}")

    if os.environ.get("ENABLE_WHATSAPP", "true").lower() == "true":
        try:
            from runtime.bridges.whatsapp_bridge import init as wa_init
            from runtime.orchestrator.message_queue import enqueue
            wa_init(enqueue_fn=enqueue)
            _whatsapp_bridge = True
            logger.info("WhatsApp bridge initialized (webhook mode)")
        except Exception as e:
            logger.warning(f"WhatsApp bridge failed to initialize: {e}")

    # Phase 4: Start alarm watcher
    _alarm_watcher = None
    if _dispatcher and os.environ.get("ENABLE_ALARMS", "true").lower() == "true":
        try:
            from runtime.orchestrator.alarm_watcher import AlarmWatcher
            from runtime.orchestrator.message_queue import enqueue
            _alarm_watcher = AlarmWatcher(enqueue_fn=enqueue)
            _alarm_watcher.start()
            logger.info("Alarm watcher started")
        except Exception as e:
            logger.warning(f"Alarm watcher failed to start: {e}")

    yield

    logger.info("Shutting down Mind Home Server")
    if _alarm_watcher:
        _alarm_watcher.stop()
    if _telegram_bridge:
        try:
            from runtime.bridges.telegram_bridge import stop as tg_stop
            tg_stop()
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


# ── Health ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Health check for Render/load balancer."""
    uptime = time.time() - _state["started_at"] if _state["started_at"] else 0
    return {
        "status": "ok",
        "home_id": _state["home_id"],
        "version": _state["version"],
        "uptime_seconds": round(uptime),
        "graph_connected": _state["graph_connected"],
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

    dispatcher.submit_request({
        "voice_text": text,
        "mode": body.get("mode", "partner"),
        "source": body.get("source", "api"),
        "sender": body.get("sender", "api_user"),
        "sender_id": body.get("sender_id", ""),
        "metadata": body.get("metadata", {}),
    })

    return {"status": "queued", "text": text[:80]}


@app.get("/api/orchestrator/status")
async def orchestrator_status():
    """Get orchestrator status."""
    dispatcher = _state.get("dispatcher")
    if not dispatcher:
        return {"running": False, "detail": "Orchestrator not started"}
    return dispatcher.get_status()


# ── Voice WebSocket ─────────────────────────────────────────────────────────

from fastapi import WebSocket

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


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8765))
    uvicorn.run("home_server:app", host="0.0.0.0", port=port, reload=False)
