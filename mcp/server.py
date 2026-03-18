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

from runtime.connectome import ConnectomeRunner
from runtime.membrane.endpoint_registrar import auto_register
from runtime.capability_integration import (
    init_capability_manager,
    CapabilityManager,
    CAPABILITY_RUNTIME_AVAILABLE,
)

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
from mcp.tools.call_file_watcher import TOOL_SCHEMA as CALL_SCHEMA, handle_call_file_watcher as handle_call
from mcp.tools.subcall_handler import TOOL_SCHEMA as SUBCALL_SCHEMA, handle_subcall
from mcp.tools.profile_handler import TOOL_SCHEMA as PROFILE_SCHEMA, handle_profile
from mcp.tools.spawn_handler import TOOL_SCHEMA as SPAWN_SCHEMA, handle_spawn
from mcp.tools.debug_handler import TOOL_SCHEMA as DEBUG_SCHEMA, handle_debug
from mcp.tools.bond_handler import TOOL_SCHEMA as BOND_SCHEMA, handle_bond
from mcp.tools.anamnesis_handler import TOOL_SCHEMA as ANAMNESIS_SCHEMA, handle as handle_anamnesis
from mcp.tools.sense_handler import TOOL_SCHEMA as SENSE_SCHEMA, handle_sense

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
    # ACT (living places)
    PLACE_SCHEMA,
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
    "call":        (handle_call,        True),
    "subcall":     (handle_subcall,     True),
    "profile":     (handle_profile,     True),
    "spawn":       (handle_spawn,       True),
    "debug":       (handle_debug,       True),
    "bond":        (handle_bond,        True),
    "anamnesis":   (handle_anamnesis,   True),
    "sense":       (handle_sense,       True),
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

        # Auto-upgrade check on startup
        try:
            from runtime.upgrade import check_and_upgrade
            if check_and_upgrade(self.target_dir):
                logger.info("Runtime upgraded, restart may be needed for full effect")
        except Exception as e:
            logger.debug(f"Upgrade check skipped: {e}")

        # Graph connections
        self.graph_ops = None
        self.graph_queries = None
        try:
            from runtime.physics.graph import GraphOps, GraphQueries
            self.graph_ops = GraphOps()
            self.graph_queries = GraphQueries()
            logger.info("Connected to graph database")
        except Exception as e:
            logger.warning(f"No graph connection: {e}")

        # Membrane graph
        try:
            from runtime.membrane import get_membrane_queries
            self.membrane_queries = get_membrane_queries()
            if self.membrane_queries:
                logger.info("Connected to membrane graph")
        except Exception as e:
            logger.warning(f"No membrane connection: {e}")
            self.membrane_queries = None

        # Capability manager (internal — not exposed as tools)
        self.capability_manager: Optional[CapabilityManager] = None
        if CAPABILITY_RUNTIME_AVAILABLE:
            try:
                self.capability_manager = init_capability_manager(
                    target_dir=self.target_dir,
                    graph=self.graph_ops,
                )
                cap_summary = self.capability_manager.initialize()
                logger.info(f"Capabilities: {cap_summary}")
                self.capability_manager.start_cron_scheduler()
                startup_result = self.capability_manager.fire_trigger(
                    "init.startup", {}, create_tasks=True,
                )
                logger.info(f"Startup trigger: {startup_result}")
            except Exception as e:
                logger.warning(f"Capability system failed: {e}")
                self.capability_manager = None

        # Auto-assign pending tasks
        try:
            from runtime.task_assignment import startup_assign
            assigned, skipped = startup_assign(self.target_dir)
            if assigned > 0:
                logger.info(f"Task assignment: {assigned} assigned, {skipped} skipped")
        except Exception as e:
            logger.debug(f"Task assignment skipped: {e}")

        # Connectome runner (for procedures)
        self.runner = ConnectomeRunner(
            graph_ops=self.graph_ops,
            graph_queries=self.graph_queries,
            connectomes_dir=self.connectomes_dir,
        )

        # Dispatcher — L1 physics tick loop (background thread)
        self.dispatcher = None
        try:
            from runtime.orchestrator.dispatcher import Dispatcher
            self.dispatcher = Dispatcher()
            self.dispatcher.start()
            logger.info("Dispatcher started — L1 physics ticks running")

            # Load L1 engines for all citizens with brains
            self._load_citizen_engines()

            # Start settlement scheduler (6h epochs)
            try:
                from runtime.economy.settlement import start_settlement_scheduler
                start_settlement_scheduler(dispatcher=self.dispatcher)
                logger.info("Settlement scheduler started (6h epochs)")
            except Exception as e:
                logger.warning(f"Settlement scheduler not started: {e}")

            # Wire citizen_wake dispatcher reference
            try:
                import sys
                sys.path.insert(0, str(self.target_dir / "scripts"))
                from citizen_wake import set_dispatcher
                set_dispatcher(self.dispatcher)
                logger.info("Citizen wake dispatcher registered")
            except Exception as e:
                logger.debug(f"Citizen wake dispatcher not registered: {e}")
        except Exception as e:
            logger.warning(f"Dispatcher not started: {e}")

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

    def _load_citizen_engines(self):
        """Load L1 engines for all citizens that have brains."""
        if not self.dispatcher:
            return
        citizens_dir = self.target_dir / "citizens"
        if not citizens_dir.exists():
            return
        handles = []
        for d in sorted(citizens_dir.iterdir()):
            if not d.is_dir():
                continue
            # Citizens with brain files get engines
            if (d / "brain.json").exists() or (d / "brain_full.json").exists():
                handles.append(d.name)
        if handles:
            self.dispatcher.bulk_load_citizen_engines(handles)
            logger.info(f"L1 engines loaded for {len(handles)} citizens")

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC request."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_list_tools()
            elif method == "tools/call":
                result = self._handle_call_tool(params)
            else:
                return self._error_response(request_id, -32601, f"Method not found: {method}")

            return self._success_response(request_id, result)
        except Exception as e:
            logger.exception(f"Error handling {method}")
            return self._error_response(request_id, -32000, str(e))

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "protocolVersion": "2024-11-05",
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
    """Kill any orphaned MCP server processes from previous sessions.

    Each Claude Code session spawns a new MCP server. When sessions die
    (timeout, crash, ctrl+C), the MCP process stays orphaned — eating RAM
    and causing connection instability. This guard kills all other instances
    of this server on startup, keeping exactly one alive (us).
    """
    import subprocess
    my_pid = os.getpid()
    try:
        result = subprocess.run(
            ["pgrep", "-f", "mcp.server"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            pid = int(line.strip())
            if pid != my_pid:
                try:
                    os.kill(pid, 9)
                    logger.info(f"Killed orphaned MCP server (PID {pid})")
                except ProcessLookupError:
                    pass
                except PermissionError:
                    pass
    except Exception as e:
        logger.debug(f"Could not check for orphans: {e}")


def main():
    """Run the MCP server on stdio."""
    _kill_previous_instances()

    server = MindServer()
    logger.info(f"Mind MCP server started ({len(TOOL_SCHEMAS)} tools: THINK/ACT/SPEAK)")

    # Auto-register this instance's endpoint in L4 graph
    auto_register()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = server.handle_request(request)
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
