#!/usr/bin/env python3
"""
Mind MCP Server — Membrane Dispatcher

Exposes the mind graph system as 9 MCP tools organized by THINK / ACT / SPEAK.

THINK (knowledge & reasoning):
  1. graph_query   — semantic search across the knowledge graph
  2. graph_write   — create nodes and links in the graph
  3. procedure     — structured dialogues (list/start/continue/abort)

ACT (work & coordination):
  4. task          — manage tasks (list/claim/complete/fail)
  5. agent         — manage work agents (list/run/status)
  6. think         — consult another LLM (Gemini)

SPEAK (outward communication):
  7. send          — send message to any platform (telegram, ...)

Usage:
  python mcp/server.py
"""

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
from runtime.agents import AgentGraph
from runtime.capability_integration import (
    init_capability_manager,
    CapabilityManager,
    CAPABILITY_RUNTIME_AVAILABLE,
)

# Import tool schemas and handlers
from mcp.tools.context import ServerContext
from mcp.tools.graph_query_handler import TOOL_SCHEMA as GRAPH_QUERY_SCHEMA, handle_graph_query
from mcp.tools.graph_write_handler import TOOL_SCHEMA as GRAPH_WRITE_SCHEMA, handle_graph_write
from mcp.tools.procedure_handler import TOOL_SCHEMA as PROCEDURE_SCHEMA, handle_procedure
from mcp.tools.task_handler import TOOL_SCHEMA as TASK_SCHEMA, handle_task
from mcp.tools.agent_handler import TOOL_SCHEMA as AGENT_SCHEMA, handle_agent
from mcp.tools.think_handler import TOOL_SCHEMA as THINK_SCHEMA, handle_think
from mcp.tools.send_handler import TOOL_SCHEMA as SEND_SCHEMA, handle_send
from mcp.tools.media_handler import TOOL_SCHEMA as MEDIA_SCHEMA, handle_media
from mcp.tools.alarm_handler import TOOL_SCHEMA as ALARM_SCHEMA, handle_alarm

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
    # ACT
    TASK_SCHEMA,
    AGENT_SCHEMA,
    THINK_SCHEMA,
    # SPEAK
    SEND_SCHEMA,
    MEDIA_SCHEMA,
    # ACT (citizen autonomy)
    ALARM_SCHEMA,
]

# Tool name → (handler_fn, needs_ctx)
# handlers that need ServerContext get it; stateless ones (think, send) don't
TOOL_DISPATCH = {
    "graph_query": (handle_graph_query, True),
    "graph_write": (handle_graph_write, True),
    "procedure":   (handle_procedure,   True),
    "task":        (handle_task,        True),
    "agent":       (handle_agent,       True),
    "think":       (handle_think,       False),
    "send":        (handle_send,        False),
    "media":       (handle_media,       False),
    "alarm":       (handle_alarm,       False),
}


class MindServer:
    """MCP Server for mind graph tools."""

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

        # Agent graph
        try:
            self.agent_graph = AgentGraph()
            self.agent_graph.ensure_agents_exist()
            logger.info("Agent graph initialized")
        except Exception as e:
            logger.warning(f"No agent graph: {e}")
            self.agent_graph = AgentGraph()

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

        # Build shared context for handlers
        self.ctx = ServerContext(
            graph_ops=self.graph_ops,
            graph_queries=self.graph_queries,
            agent_graph=self.agent_graph,
            runner=self.runner,
            target_dir=self.target_dir,
            capability_manager=self.capability_manager,
            connectomes_dir=self.connectomes_dir,
        )

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
            "serverInfo": {"name": "mind", "version": "0.2.0"},
        }

    def _handle_list_tools(self) -> Dict[str, Any]:
        return {"tools": TOOL_SCHEMAS}

    def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch tool call to the appropriate handler."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        entry = TOOL_DISPATCH.get(tool_name)
        if not entry:
            raise ValueError(f"Unknown tool: {tool_name}")

        handler_fn, needs_ctx = entry
        if needs_ctx:
            return handler_fn(arguments, self.ctx)
        else:
            return handler_fn(arguments)

    def _success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def main():
    """Run the MCP server on stdio."""
    server = MindServer()
    logger.info("Mind MCP server started (8 tools: THINK/ACT/SPEAK)")

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
