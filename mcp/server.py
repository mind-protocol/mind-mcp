#!/usr/bin/env python3
"""
Mind MCP Server — The Cognitive Membrane

The interface between AI citizens and the Mind Protocol living graph.
15 tools organized by cognitive function: THINK / ACT / SPEAK.

Every tool operates on a shared FalkorDB knowledge graph where nodes are
thoughts, memories, values, and relationships — governed by 21 physics
laws that run energy propagation, decay, crystallization, and limbic
modulation. Citizens don't just store data; they think, feel, and
collaborate through the graph.

THINK — Knowledge & Reasoning:
  graph_query  Query the graph with natural language. Semantic search
               via SubEntity traversal. Returns resonating nodes.
  graph_write  Create nodes (narratives, moments, things) and links.
               MERGE semantics — safe to call multiple times.
  procedure    Structured dialogues for documentation, investigation,
               and workflow. List/start/continue/abort sessions.
  think        Consult Gemini for reasoning, vision analysis, or
               structured output. Maintains conversation sessions.

ACT — Work & Coordination:
  task         Manage tasks: list pending, claim, complete, fail.
               Tasks are Narrative nodes in the graph.
  alarm        Autonomous wake scheduling. Citizens decide when they
               wake — no cron. Alarms fire via the orchestrator.
  place        Living Places: join/speak/listen/leave/create rooms.
               Private spaces with E2E encryption (AES-256-GCM).
  call         Instant citizen-to-citizen call. Creates a temporary
               room, sends message, wakes target (or gets subconscious
               response immediately if no LLM session active).
  subcall      Zero-LLM telepathy. Probe any citizen's graph without
               waking their LLM. 24 scenarios, 6 targeting modes,
               custom Cypher, thermodynamic resonance formula,
               intelligence briefing output. The flagship tool.
  spawn        Birth a new AI citizen: identity → L1 brain → wallet
               → L4 registry. Full lifecycle from name to citizenship.
  profile      Update citizen profile: bio, tags, emoji, profile pic,
               human partner, parents. Persisted to disk + graph.
  debug        Start/stop debug trace sessions. @traceable functions
               emit structured logs for analysis.

SPEAK — Outward Communication:
  send         Send message to any platform: Telegram, Discord,
               WhatsApp, Twitter/X, email, SMS. Unified API.
  read         Read messages/mentions from any platform. History,
               search, pagination.
  media        Generate images (Ideogram/DALL-E), synthesize voice
               (ElevenLabs), send files to platforms.

Architecture:
  FalkorDB     Graph database (Cypher + vector similarity)
  Schema v2.2  5 node types × 14 link kinds × 21 physics laws
  L1 Brain     Per-citizen cognitive graph (7 node types, 8 drives)
  L3 Universe  Shared public graph (all citizens, spaces, moments)
  Membrane     Law 21 — inter-layer coupling (L1 ↔ L3)

Usage:
  python mcp/server.py
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / ".env")


# Import tool schemas and handlers
from runtime.citizens.autonomy_gate import check_tool_permission, GateResult
from mcp.tools.context import ServerContext
from mcp.tools.graph_query_handler import TOOL_SCHEMA as GRAPH_QUERY_SCHEMA, handle_graph_query
from mcp.tools.graph_write_handler import TOOL_SCHEMA as GRAPH_WRITE_SCHEMA, handle_graph_write
from mcp.tools.procedure_handler import TOOL_SCHEMA as PROCEDURE_SCHEMA, handle_procedure
from mcp.tools.task_handler import TOOL_SCHEMA as TASK_SCHEMA, handle_task
from mcp.tools.think_handler import TOOL_SCHEMA as THINK_SCHEMA, handle_think
from mcp.tools.send_handler import TOOL_SCHEMA as SEND_SCHEMA, handle_send
from mcp.tools.read_handler import TOOL_SCHEMA as READ_SCHEMA, handle_read
from mcp.tools.media_handler import TOOL_SCHEMA as MEDIA_SCHEMA, handle_media
from mcp.tools.alarm_handler import TOOL_SCHEMA as ALARM_SCHEMA, handle_alarm
from mcp.tools.place_handler import TOOL_SCHEMA as PLACE_SCHEMA, handle_place
from mcp.tools.move_handler import TOOL_SCHEMA as MOVE_SCHEMA, handle_move
from mcp.tools.call_file_watcher import TOOL_SCHEMA as CALL_SCHEMA, handle_call_file_watcher as handle_call
from mcp.tools.subcall_handler import TOOL_SCHEMA as SUBCALL_SCHEMA, handle_subcall
from mcp.tools.profile_handler import TOOL_SCHEMA as PROFILE_SCHEMA, handle_profile
from mcp.tools.spawn_handler import TOOL_SCHEMA as SPAWN_SCHEMA, handle_spawn
from mcp.tools.debug_handler import TOOL_SCHEMA as DEBUG_SCHEMA, handle_debug
from mcp.tools.bond_handler import TOOL_SCHEMA as BOND_SCHEMA, handle_bond
from mcp.tools.anamnesis_handler import TOOL_SCHEMA as ANAMNESIS_SCHEMA, handle as handle_anamnesis
from mcp.tools.sense_handler import TOOL_SCHEMA as SENSE_SCHEMA, handle_sense
from mcp.tools.inject_cluster_handler import TOOL_SCHEMA as INJECT_CLUSTER_SCHEMA, handle_inject_cluster

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
)
logger = logging.getLogger("mind")

# All tool schemas in presentation order
TOOL_SCHEMAS = [
    # THINK
    GRAPH_QUERY_SCHEMA,
    GRAPH_WRITE_SCHEMA,
    PROCEDURE_SCHEMA,
    THINK_SCHEMA,
    # ACT
    TASK_SCHEMA,
    # SPEAK
    SEND_SCHEMA,
    READ_SCHEMA,
    MEDIA_SCHEMA,
    # ACT (citizen autonomy)
    ALARM_SCHEMA,
    # ACT (living places + spatial)
    PLACE_SCHEMA,
    MOVE_SCHEMA,
    CALL_SCHEMA,
    SUBCALL_SCHEMA,
    # ACT (identity)
    PROFILE_SCHEMA,
    SPAWN_SCHEMA,
    # ACT (observability)
    DEBUG_SCHEMA,
    # ACT (relationships)
    BOND_SCHEMA,
    # ACT (memory)
    ANAMNESIS_SCHEMA,
    # THINK (perception)
    SENSE_SCHEMA,
    # ACT (L3 ingestion)
    INJECT_CLUSTER_SCHEMA,
]

# Tool name → (handler_fn, needs_ctx)
# handlers that need ServerContext get it; stateless ones (think, send) don't
TOOL_DISPATCH = {
    "graph_query": (handle_graph_query, True),
    "graph_write": (handle_graph_write, True),
    "procedure":   (handle_procedure,   True),
    "task":        (handle_task,        True),
    "think":       (handle_think,       False),
    "send":        (handle_send,        False),
    "read":        (handle_read,        False),
    "media":       (handle_media,       False),
    "alarm":       (handle_alarm,       False),
    "place":       (handle_place,       True),
    "move":        (handle_move,        True),
    "call":        (handle_call,        True),
    "subcall":     (handle_subcall,     True),
    "profile":     (handle_profile,     True),
    "spawn":       (handle_spawn,       True),
    "debug":       (handle_debug,       True),
    "bond":        (handle_bond,        True),
    "anamnesis":   (handle_anamnesis,   True),
    "sense":       (handle_sense,       True),
    "inject_cluster": (handle_inject_cluster, False),
}


class MindServer:
    """MCP Server — the cognitive membrane between AI citizens and the living graph.

    Connects to FalkorDB on startup, initializes graph operations (read/write),
    membrane queries, capability manager, and connectome runner.

    All tools are dispatched via TOOL_DISPATCH: handler_fn(args) or handler_fn(args, ctx).
    ServerContext carries graph_ops, graph_queries, target_dir, capability_manager.
    """

    def __init__(self, connectomes_dir: Optional[Path] = None):
        self.connectomes_dir = connectomes_dir or (project_root / "procedures")
        self.target_dir = project_root

        # All connections are lazy — nothing blocks startup
        self.graph_ops = None
        self.graph_queries = None
        self.membrane_queries = None
        self.capability_manager = None

        # No ConnectomeRunner, no Dispatcher.
        # L1 physics lives in the Rust daemon (mind-desktop).
        # This MCP server is a passive tool executor — nothing more.
        self.runner = None
        self.dispatcher = None

        # Build shared context for handlers
        self.ctx = ServerContext(
            graph_ops=self.graph_ops,
            graph_queries=self.graph_queries,
            runner=self.runner,
            target_dir=self.target_dir,
            capability_manager=self.capability_manager,
            connectomes_dir=self.connectomes_dir,
            dispatcher=self.dispatcher,
        )

    def _ensure_graph_connection(self) -> bool:
        """Lazy reconnect: if graph_ops is None, try connecting now.

        Returns True if graph is available (already connected or just reconnected).
        Returns False if connection still unavailable.

        On successful reconnect, propagates new connections to ctx, runner,
        membrane, and capability manager so all handlers see the live graph.
        """
        # If we have a connection, verify it's still alive
        if self.graph_ops is not None:
            try:
                self.graph_ops._adapter.ping()
                return True
            except Exception:
                logger.warning("Graph connection lost, attempting reconnect...")
                self.graph_ops = None
                self.graph_queries = None

        try:
            # Reload .env in case host/port changed since startup
            load_dotenv(project_root / ".env", override=True)
            from runtime.infrastructure.database.factory import _instances
            _instances.clear()  # Clear cached adapters so new config takes effect
            from runtime.physics.graph import GraphOps, GraphQueries
            self.graph_ops = GraphOps()
            self.graph_queries = GraphQueries()
            logger.info("Graph reconnected (lazy)")
        except Exception as e:
            logger.warning(f"Graph reconnect failed: {e}")
            return False

        # Propagate to context so all handlers see the live graph
        self.ctx.graph_ops = self.graph_ops
        self.ctx.graph_queries = self.graph_queries

        return True

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle a JSON-RPC request.

        Returns the JSON-RPC response dict, or ``None`` for notifications
        (requests without an ``id``, e.g. ``notifications/initialized``).
        Notifications MUST NOT receive a response per the JSON-RPC spec —
        strict clients (ChatGPT developer-mode MCP) break the handshake if
        they get one. Callers must skip emitting anything when this is None.
        """
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")
        # JSON-RPC notifications carry no "id" and must be answered with silence.
        is_notification = "id" not in request

        try:
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_list_tools()
            elif method == "tools/call":
                result = self._handle_call_tool(params)
            else:
                if is_notification:
                    return None  # e.g. notifications/initialized — swallow silently
                return self._error_response(request_id, -32601, f"Method not found: {method}")

            if is_notification:
                return None
            return self._success_response(request_id, result)
        except Exception as e:
            logger.exception(f"Error handling {method}")
            if is_notification:
                return None
            return self._error_response(request_id, -32000, str(e))

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Echo the protocol version the client negotiated when present, so
        # clients that speak a newer revision (ChatGPT: 2025-03-26 / 2025-06-18)
        # don't see a downgrade. Fall back to the version we implement.
        client_version = params.get("protocolVersion")
        return {
            "protocolVersion": client_version or "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "mind", "version": "0.3.0"},
        }

    def _handle_list_tools(self) -> Dict[str, Any]:
        return {"tools": TOOL_SCHEMAS}

    def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch tool call to the appropriate handler.

        Every call passes through the autonomy gate BEFORE the handler executes.
        New tools added to TOOL_DISPATCH are automatically gated.
        """
        # V3: No FalkorDB reconnect. graph_query reads workspace.json directly.
        # self._ensure_graph_connection()  # KILLED — Phase 4

        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        entry = TOOL_DISPATCH.get(tool_name)
        if not entry:
            raise ValueError(f"Unknown tool: {tool_name}")

        # ── Autonomy Gate ──
        gate_result, gate_reason = check_tool_permission(tool_name, arguments)

        if gate_result == GateResult.DENY:
            return {
                "content": [{"type": "text", "text": f"DENIED: {gate_reason}"}],
                "isError": True,
            }

        if gate_result == GateResult.QUEUE:
            return {
                "content": [{"type": "text", "text": (
                    f"QUEUED: {gate_reason}\n\n"
                    "This action requires human approval. "
                    "It has been logged and will be reviewed. "
                    "The action was NOT executed."
                )}],
            }

        # ── ALLOW — proceed to handler ──
        handler_fn, needs_ctx = entry
        if needs_ctx:
            return handler_fn(arguments, self.ctx)
        else:
            return handler_fn(arguments)

    def _success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _kill_previous_instances():
    """Kill orphaned MCP server processes — those whose parent is dead (ppid=1).

    Each Claude/Gemini session spawns a new MCP server. When sessions die
    (timeout, crash, ctrl+C), the MCP process stays orphaned — eating RAM
    and causing connection instability. This guard kills only TRUE orphans
    (ppid=1, meaning their parent process is gone), not active instances
    serving live Claude or Gemini sessions.
    """
    import subprocess
    my_pid = os.getpid()
    try:
        # Get PID and PPID for all mcp.server processes
        result = subprocess.run(
            ["pgrep", "-f", "mcp.server", "--list-full"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                pid = int(line.strip().split()[0])
            except (ValueError, IndexError):
                continue
            if pid == my_pid:
                continue
            # Only kill if parent is init (ppid=1) — truly orphaned
            try:
                with open(f"/proc/{pid}/stat") as f:
                    stat = f.read().split()
                    ppid = int(stat[3])
                if ppid <= 1:
                    os.kill(pid, 9)
                    logger.info(f"Killed orphaned MCP server (PID {pid}, ppid={ppid})")
            except (ProcessLookupError, FileNotFoundError, PermissionError):
                pass
    except Exception as e:
        logger.debug(f"Could not check for orphans: {e}")


def main():
    """Run the MCP server on stdio."""
    _kill_previous_instances()

    server = MindServer()
    logger.info(f"Mind MCP server started ({len(TOOL_SCHEMAS)} tools: THINK/ACT/SPEAK)")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = server.handle_request(request)
            if response is not None:  # notifications produce no response
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {e}"},
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
