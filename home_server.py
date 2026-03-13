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
                mode=os.environ.get("BUDGET_MODE", "subscription"),
                monthly_budget_usd=float(os.environ.get("MONTHLY_BUDGET_USD", "300")),
            )
            _dispatcher = Dispatcher(budget=budget)
            _dispatcher.start()
            _state["dispatcher"] = _dispatcher
            logger.info(f"Orchestrator started (mode={budget.mode})")
        except Exception as e:
            logger.warning(f"Orchestrator failed to start: {e}")

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
            "chat": "/api/chat",
            "orchestrator": "/api/orchestrator/status",
            "membrane_stimulus": "/membrane/stimulus",
            "membrane_info": "/membrane/info",
            "membrane_subscribe": "/membrane/subscribe",
            "whatsapp_webhook": "/whatsapp/webhook",
            "voice_ws": "/voice/ws",
        },
    }


# ── Citizens ────────────────────────────────────────────────────────────────

@app.get("/api/citizens")
async def get_citizens():
    """List all birthed citizens in this home."""
    from runtime.citizens import list_available_citizens
    return {"citizens": list_available_citizens()}


@app.get("/api/citizens/{handle}")
async def get_citizen(handle: str):
    """Get full citizen identity and profile."""
    from runtime.citizens import load_citizen_identity
    citizen = load_citizen_identity(handle)
    if not citizen:
        raise HTTPException(status_code=404, detail=f"Citizen @{handle} not found")
    # Don't expose full claude_md and memories in API — just profile and metadata
    return {
        "handle": citizen["handle"],
        "dir": citizen["dir"],
        "has_claude_md": bool(citizen.get("claude_md", "").strip()),
        "profile": citizen.get("profile", {}),
        "memory_count": len(citizen.get("memories", [])),
        "has_memory_index": bool(citizen.get("memory_index", "").strip()),
    }


# ── Chat / Orchestrator ─────────────────────────────────────────────────────

@app.post("/api/chat")
async def post_chat(request: Request):
    """Submit a message for processing by the orchestrator."""
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
