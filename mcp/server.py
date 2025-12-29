#!/usr/bin/env python3
"""
Mind MCP Server

Exposes the mind graph system as MCP tools for AI agents.

Tools:
  - procedure_start: Start a structured dialogue session
  - procedure_continue: Continue with an answer
  - procedure_abort: Abort a session
  - procedure_list: List available procedures
  - doctor_check: Run health checks
  - agent_list: List work agents
  - agent_spawn: Spawn a work agent
  - agent_status: Get/set agent status
  - task_list: List available tasks
  - graph_query: Query the graph in natural language

Usage:
  Run as MCP server (stdio):
    python tools/mcp/mind_server.py

  Configure in Claude Code settings:
    {
      "mcpServers": {
        "mind": {
          "command": "python",
          "args": ["tools/mcp/mind_server.py"],
          "cwd": "/path/to/mind"
        }
      }
    }
"""

import asyncio
import sys
import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from runtime.connectome import ConnectomeRunner
from runtime.agents import (
    AgentGraph,
    PROBLEM_TO_POSTURE,
    POSTURE_TO_AGENT_ID,
    spawn_work_agent,
    spawn_for_task,
    AGENT_SYSTEM_PROMPT,
    build_agent_prompt,
    get_learnings_content,
)
from runtime.doctor import run_doctor, DoctorIssue
from runtime.doctor_types import DoctorConfig
from runtime.work_core import spawn_work_agent_with_verification_async
from runtime.work_instructions import get_issue_instructions
from runtime.capability_integration import (
    init_capability_manager,
    get_capability_manager,
    CapabilityManager,
    CAPABILITY_RUNTIME_AVAILABLE,
    get_throttler,
    get_agent_registry,
    claim_task,
    complete_task,
    fail_task,
    update_actor_heartbeat,
    set_actor_working,
    set_actor_idle,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("mind")

# =============================================================================
# MCP PROTOCOL IMPLEMENTATION
# =============================================================================

class MindServer:
    """MCP Server for mind graph tools."""

    def __init__(self, connectomes_dir: Optional[Path] = None):
        """Initialize server with optional connectomes directory."""
        self.connectomes_dir = connectomes_dir or (project_root / "procedures")
        self.target_dir = project_root

        # Try to get graph connections if available
        try:
            from runtime.physics.graph import GraphOps, GraphQueries
            # Don't pass graph_name - let the adapter use config
            self.graph_ops = GraphOps()
            self.graph_queries = GraphQueries()
            logger.info("Connected to graph database")
        except Exception as e:
            logger.warning(f"No graph connection: {e}")
            self.graph_ops = None
            self.graph_queries = None

        # Try to connect to membrane graph
        try:
            from runtime.membrane import get_membrane_queries
            self.membrane_queries = get_membrane_queries()
            if self.membrane_queries:
                logger.info("Connected to membrane graph")
        except Exception as e:
            logger.warning(f"No membrane connection: {e}")
            self.membrane_queries = None

        # Initialize agent graph for work agent management
        try:
            self.agent_graph = AgentGraph()
            self.agent_graph.ensure_agents_exist()
            logger.info("Agent graph initialized")
        except Exception as e:
            logger.warning(f"No agent graph: {e}")
            self.agent_graph = AgentGraph()  # Fallback mode

        # Initialize capability manager
        self.capability_manager: Optional[CapabilityManager] = None
        if CAPABILITY_RUNTIME_AVAILABLE:
            try:
                self.capability_manager = init_capability_manager(
                    target_dir=self.target_dir,
                    graph=self.graph_ops,
                )
                cap_summary = self.capability_manager.initialize()
                logger.info(f"Capabilities: {cap_summary}")

                # Start cron scheduler
                self.capability_manager.start_cron_scheduler()

                # Fire startup trigger
                startup_result = self.capability_manager.fire_trigger(
                    "init.startup", {}, create_tasks=True
                )
                logger.info(f"Startup trigger: {startup_result}")
            except Exception as e:
                logger.warning(f"Capability system failed: {e}")
                self.capability_manager = None

        self.runner = ConnectomeRunner(
            graph_ops=self.graph_ops,
            graph_queries=self.graph_queries,
            connectomes_dir=self.connectomes_dir
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
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "mind",
                "version": "0.1.0"
            }
        }

    def _handle_list_tools(self) -> Dict[str, Any]:
        """Return list of available tools."""
        return {
            "tools": [
                {
                    "name": "procedure_start",
                    "description": "Start a new procedure dialogue session. Returns the first step.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "procedure": {
                                "type": "string",
                                "description": "Name of the procedure to run (e.g., 'create_validation', 'document_progress')"
                            },
                            "context": {
                                "type": "object",
                                "description": "Optional initial context values (e.g., {\"actor_id\": \"actor_claude\"})"
                            }
                        },
                        "required": ["procedure"]
                    }
                },
                {
                    "name": "procedure_continue",
                    "description": "Continue a procedure session with an answer to the current step.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID from procedure_start"
                            },
                            "answer": {
                                "description": "Answer for the current step. Type depends on what the step expects."
                            }
                        },
                        "required": ["session_id", "answer"]
                    }
                },
                {
                    "name": "procedure_abort",
                    "description": "Abort a procedure session. No changes will be committed.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID to abort"
                            }
                        },
                        "required": ["session_id"]
                    }
                },
                {
                    "name": "procedure_list",
                    "description": "List available procedure definitions.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "doctor_check",
                    "description": "Run doctor health checks and return issues with assigned agents.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "depth": {
                                "type": "string",
                                "enum": ["links", "docs", "full"],
                                "description": "Check depth: links (fastest), docs, or full"
                            },
                            "path": {
                                "type": "string",
                                "description": "Optional path filter"
                            }
                        }
                    }
                },
                {
                    "name": "agent_list",
                    "description": "List all work agents and their status (ready/running).",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "task_list",
                    "description": "List available tasks grouped by objective. Shows pending tasks agents can work on.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "module": {
                                "type": "string",
                                "description": "Filter by module name"
                            },
                            "objective": {
                                "type": "string",
                                "description": "Filter by objective type (documented, synced, maintainable, etc.)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max tasks to return (default: 20)"
                            }
                        }
                    }
                },
                {
                    "name": "agent_spawn",
                    "description": "Spawn a work agent to fix an issue OR work on a task (narrative node).",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Narrative node ID for the task (e.g., 'task_fix_physics_sync'). If provided, issue_type/path are ignored."
                            },
                            "issue_type": {
                                "type": "string",
                                "description": "Issue type (e.g., STALE_SYNC, UNDOCUMENTED). Used if task_id not provided."
                            },
                            "path": {
                                "type": "string",
                                "description": "Path of the issue to fix. Used if task_id not provided."
                            },
                            "agent_id": {
                                "type": "string",
                                "description": "Optional: specific agent to use (e.g., agent_witness). Auto-selected if not provided."
                            },
                            "provider": {
                                "type": "string",
                                "enum": ["claude", "gemini", "codex"],
                                "description": "LLM provider to use (default: claude)"
                            }
                        }
                    }
                },
                {
                    "name": "agent_status",
                    "description": "Get or set the status of a specific agent.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "agent_id": {
                                "type": "string",
                                "description": "Agent ID (e.g., agent_witness)"
                            },
                            "set_status": {
                                "type": "string",
                                "enum": ["ready", "running"],
                                "description": "Optional: set the agent status"
                            }
                        },
                        "required": ["agent_id"]
                    }
                },
                {
                    "name": "graph_query",
                    "description": "Query the graph using natural language. Supports multiple queries at once. Uses SubEntity traversal to find relevant nodes and their connections.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "queries": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "One or more natural language queries (e.g., ['Who is Edmund?', 'What oaths exist?'])"
                            },
                            "intent": {
                                "type": "string",
                                "description": "WHY you're searching - affects traversal strategy (e.g., 'find contradictions', 'summarize events', 'verify claims')"
                            },
                            "actor_id": {
                                "type": "string",
                                "description": "Actor performing the query (for context, default: actor_claude)"
                            },
                            "debug": {
                                "type": "boolean",
                                "description": "Enable debug mode with traversal logs (default: false)"
                            },
                            "timeout": {
                                "type": "number",
                                "description": "Query timeout in seconds (default: 30)"
                            }
                        },
                        "required": ["queries"]
                    }
                },
                {
                    "name": "capability_status",
                    "description": "Get status of the capability system: loaded capabilities, registered triggers, throttler state.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "capability_trigger",
                    "description": "Fire a trigger manually. Used for testing or manual health checks.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "trigger_type": {
                                "type": "string",
                                "description": "Type of trigger (e.g., 'init.startup', 'file.on_modify', 'cron.hourly')"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Optional file path for file triggers"
                            },
                            "create_tasks": {
                                "type": "boolean",
                                "description": "Whether to create task_run nodes for non-healthy signals (default: true)"
                            }
                        },
                        "required": ["trigger_type"]
                    }
                },
                {
                    "name": "capability_list",
                    "description": "List all loaded capabilities with their health checks.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "task_claim",
                    "description": "Atomically claim a pending task for an agent. Returns success/failure.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The task_run node ID to claim"
                            },
                            "actor_id": {
                                "type": "string",
                                "description": "The actor ID claiming the task"
                            }
                        },
                        "required": ["task_id", "actor_id"]
                    }
                },
                {
                    "name": "task_complete",
                    "description": "Mark a task as completed. Updates graph and releases throttler slot.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The task_run node ID to complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                },
                {
                    "name": "task_fail",
                    "description": "Mark a task as failed with a reason. Updates graph and releases throttler slot.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The task_run node ID that failed"
                            },
                            "reason": {
                                "type": "string",
                                "description": "Why the task failed"
                            }
                        },
                        "required": ["task_id", "reason"]
                    }
                },
                {
                    "name": "agent_heartbeat",
                    "description": "Update agent heartbeat. Call every 60s while working on a task.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "actor_id": {
                                "type": "string",
                                "description": "The actor ID sending heartbeat"
                            },
                            "step": {
                                "type": "integer",
                                "description": "Optional: current step number in task"
                            }
                        },
                        "required": ["actor_id"]
                    }
                }
            ]
        }

    def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool call."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "procedure_start":
            return self._tool_start(arguments)
        elif tool_name == "procedure_continue":
            return self._tool_continue(arguments)
        elif tool_name == "procedure_abort":
            return self._tool_abort(arguments)
        elif tool_name == "procedure_list":
            return self._tool_list(arguments)
        elif tool_name == "doctor_check":
            return self._tool_doctor_check(arguments)
        elif tool_name == "agent_list":
            return self._tool_agent_list(arguments)
        elif tool_name == "task_list":
            return self._tool_task_list(arguments)
        elif tool_name == "agent_spawn":
            return self._tool_agent_spawn(arguments)
        elif tool_name == "agent_status":
            return self._tool_agent_status(arguments)
        elif tool_name == "graph_query":
            return self._tool_graph_query(arguments)
        elif tool_name == "capability_status":
            return self._tool_capability_status(arguments)
        elif tool_name == "capability_trigger":
            return self._tool_capability_trigger(arguments)
        elif tool_name == "capability_list":
            return self._tool_capability_list(arguments)
        elif tool_name == "task_claim":
            return self._tool_task_claim(arguments)
        elif tool_name == "task_complete":
            return self._tool_task_complete(arguments)
        elif tool_name == "task_fail":
            return self._tool_task_fail(arguments)
        elif tool_name == "agent_heartbeat":
            return self._tool_agent_heartbeat(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def _tool_start(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Start a procedure session."""
        procedure_name = args.get("procedure")
        context = args.get("context", {})

        if not procedure_name:
            return {"content": [{"type": "text", "text": "Error: 'procedure' is required"}]}

        response = self.runner.start(procedure_name, initial_context=context)
        return self._format_response(response)

    def _tool_continue(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Continue a procedure session."""
        session_id = args.get("session_id")
        answer = args.get("answer")

        if not session_id:
            return {"content": [{"type": "text", "text": "Error: 'session_id' is required"}]}

        response = self.runner.continue_session(session_id, answer)
        return self._format_response(response)

    def _tool_abort(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Abort a procedure session."""
        session_id = args.get("session_id")

        if not session_id:
            return {"content": [{"type": "text", "text": "Error: 'session_id' is required"}]}

        response = self.runner.abort(session_id)
        return self._format_response(response)

    def _tool_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List available procedures."""
        procedures = []
        if self.connectomes_dir and self.connectomes_dir.exists():
            for path in self.connectomes_dir.glob("*.yaml"):
                procedures.append(path.stem)

        text = "Available procedures:\n"
        for p in procedures:
            text += f"  - {p}\n"

        return {"content": [{"type": "text", "text": text}]}

    def _tool_doctor_check(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run doctor checks and return issues with assigned agents."""
        depth = args.get("depth", "docs")
        path_filter = args.get("path")

        try:
            # Graph schema health check
            schema_lines = []
            try:
                from runtime.physics.graph.graph_schema_cleanup import get_schema_health, cleanup_invalid_nodes
                health = get_schema_health()

                if health.get("error"):
                    schema_lines.append(f"Graph: Error - {health['error']}")
                else:
                    invalid = health["null_node_type"] + health["invalid_node_type"] + health["null_id"]
                    if invalid > 0:
                        schema_lines.append(f"Graph: {invalid} invalid nodes (run cleanup)")
                        # Auto-fix if small number
                        if invalid <= 10:
                            report = cleanup_invalid_nodes(dry_run=False)
                            schema_lines.append(f"  Auto-fixed: {report.nodes_deleted} deleted")
                    else:
                        schema_lines.append(f"Graph: OK ({health['total_nodes']} nodes)")
            except Exception as e:
                schema_lines.append(f"Graph: Check failed - {e}")

            config = DoctorConfig()
            result = run_doctor(self.target_dir, config)
            # Extract issues from all categories
            issues = []
            for category_issues in result.get("issues", {}).values():
                issues.extend(category_issues)

            # Filter by path if provided
            if path_filter:
                issues = [i for i in issues if path_filter in i.path]

            # Filter by depth
            from runtime.work_core import get_depth_types
            allowed_types = get_depth_types(depth)
            issues = [i for i in issues if i.issue_type in allowed_types]

            if not issues:
                output = "\n".join(schema_lines) + "\n\nNo doc issues found."
                return {"content": [{"type": "text", "text": output}]}

            # Get available agents
            available_agents = {a.id: a for a in self.agent_graph.get_available_agents()}

            lines = schema_lines + ["", f"Found {len(issues)} doc issues:\n"]
            for idx, issue in enumerate(issues):
                # Determine assigned agent
                posture = PROBLEM_TO_POSTURE.get(issue.issue_type, "fixer")
                agent_id = f"agent_{posture}"
                agent_status = "ready" if agent_id in available_agents else "busy"

                lines.append(f"{idx+1}. [{issue.severity.upper()}] {issue.issue_type}")
                lines.append(f"   Path: {issue.path}")
                lines.append(f"   Agent: {agent_id} ({agent_status})")
                lines.append(f"   Message: {issue.message[:80]}...")
                lines.append("")

            lines.append("\nUse agent_spawn to fix an issue.")
            return {"content": [{"type": "text", "text": "\n".join(lines)}]}

        except Exception as e:
            logger.exception("Doctor check failed")
            return {"content": [{"type": "text", "text": f"Error running doctor: {e}"}]}

    def _tool_agent_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all agents and their status."""
        agents = self.agent_graph.get_all_agents()

        lines = ["Work Agents:\n"]
        for agent in agents:
            status_icon = "🟢" if agent.status == "ready" else "🔴"
            lines.append(f"  {status_icon} {agent.id} ({agent.posture})")
            lines.append(f"     Status: {agent.status}")
            lines.append(f"     Energy: {agent.energy:.2f}")
            lines.append("")

        # Show posture mappings
        lines.append("\nPosture → Problem Types:")
        posture_problems: Dict[str, List[str]] = {}
        for problem_type, posture in PROBLEM_TO_POSTURE.items():
            posture_problems.setdefault(posture, []).append(problem_type)

        for posture, problems in sorted(posture_problems.items()):
            lines.append(f"  {posture}: {', '.join(problems[:3])}{'...' if len(problems) > 3 else ''}")

        return {"content": [{"type": "text", "text": "\n".join(lines)}]}

    def _tool_task_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List available tasks with linked issues."""
        module_filter = args.get("module")
        objective_filter = args.get("objective")
        limit = args.get("limit", 20)

        if not self.graph_queries:
            return {"content": [{"type": "text", "text": "Error: No graph connection"}]}

        try:
            # Query tasks with their linked issues and objectives
            cypher = """
            MATCH (t:Narrative)
            WHERE t.type = 'task' AND (t.status IS NULL OR t.status <> 'completed')
            OPTIONAL MATCH (t)-[r:relates]->(o:Narrative {type: 'objective'})
            RETURN t.id, t.name, t.task_type, t.module, t.skill, t.status,
                   collect(DISTINCT o.name) as objectives, t.created_at_s
            ORDER BY t.created_at_s DESC
            LIMIT $limit
            """
            result = self.graph_queries._query(cypher, {"limit": limit * 2})

            if not result:
                return {"content": [{"type": "text", "text": "No tasks found. Run `doctor` first to create tasks."}]}

            # Filter and format
            lines = ["Available Tasks:\n"]
            count = 0

            for row in result:
                task_id, name, task_type, module, skill, status, objectives, _created = row

                # Apply filters
                if module_filter and module != module_filter:
                    continue
                if objective_filter and objective_filter not in str(objectives):
                    continue

                count += 1
                if count > limit:
                    break

                status_icon = "⏳" if status == "pending" else "🔄" if status == "in_progress" else "⏸️"
                lines.append(f"{status_icon} {name}")
                lines.append(f"   ID: {task_id}")
                lines.append(f"   Module: {module} | Skill: {skill}")
                if objectives:
                    lines.append(f"   Serves: {', '.join(objectives[:2])}")
                lines.append("")

            # Query issue count per task
            lines.append(f"\nTotal: {count} task(s)")
            lines.append("\nTo spawn an agent for a task:")
            lines.append("  agent_spawn(task_id='<task_id>')")

            return {"content": [{"type": "text", "text": "\n".join(lines)}]}

        except Exception as e:
            logger.exception("Task list failed")
            return {"content": [{"type": "text", "text": f"Error listing tasks: {e}"}]}

    def _tool_agent_spawn(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn a work agent to fix an issue or work on a task. Actually executes the agent."""
        task_id = args.get("task_id")
        issue_type = args.get("issue_type")
        path = args.get("path")
        agent_id = args.get("agent_id")
        provider = args.get("provider", "claude")

        task_content = None
        task_type = None
        prompt = None

        # If task_id provided, fetch from graph with full context
        if task_id:
            if self.graph_queries:
                try:
                    # Query task with linked issues and objectives
                    cypher = """
                    MATCH (t:Narrative {id: $task_id})
                    OPTIONAL MATCH (t)-[:relates]->(o:Narrative {type: 'objective'})
                    OPTIONAL MATCH (i:Narrative {type: 'issue'})-[:relates]->(t)
                    RETURN t.id, t.name, t.content, t.type, t.module, t.skill, t.task_type,
                           collect(DISTINCT {id: o.id, name: o.name, type: o.objective_type}) as objectives,
                           collect(DISTINCT {id: i.id, type: i.issue_type, path: i.path, message: i.message, severity: i.severity}) as issues
                    """
                    result = self.graph_queries._query(cypher, {"task_id": task_id})
                    if result and len(result) > 0:
                        row = result[0]
                        task_name = row[1] if len(row) > 1 else task_id
                        task_content = row[2] if len(row) > 2 else None
                        task_type = row[3] if len(row) > 3 else "task"
                        task_module = row[4] if len(row) > 4 else ""
                        task_skill = row[5] if len(row) > 5 else ""
                        task_subtype = row[6] if len(row) > 6 else ""
                        objectives = row[7] if len(row) > 7 else []
                        issues = row[8] if len(row) > 8 else []

                        # Derive issue_type from first issue or task_type
                        if not issue_type and issues:
                            first_issue = issues[0] if isinstance(issues[0], dict) else {}
                            issue_type = first_issue.get("type", "TASK")
                        elif not issue_type:
                            issue_type = task_subtype.upper() if task_subtype else "TASK"

                        # Build rich prompt with full context
                        prompt_lines = [
                            f"# Task: {task_name}",
                            f"Module: {task_module}",
                            f"Skill: {task_skill}",
                            "",
                        ]

                        if objectives:
                            prompt_lines.append("## Objectives this serves:")
                            for obj in objectives[:3]:
                                if isinstance(obj, dict) and obj.get("name"):
                                    prompt_lines.append(f"- {obj.get('name')}")
                            prompt_lines.append("")

                        if issues:
                            prompt_lines.append("## Issues to fix:")
                            for issue in issues[:10]:  # Limit to 10 issues
                                if isinstance(issue, dict) and issue.get("path"):
                                    prompt_lines.append(f"- [{issue.get('severity', 'warning')}] {issue.get('type')}: {issue.get('path')}")
                                    if issue.get("message"):
                                        prompt_lines.append(f"  {issue.get('message')[:200]}")
                            prompt_lines.append("")

                        if task_content:
                            prompt_lines.append("## Task description:")
                            prompt_lines.append(task_content)

                        prompt_lines.append("\n## Instructions:")
                        prompt_lines.append("Fix all the issues listed above. Follow project conventions.")

                        prompt = "\n".join(prompt_lines)
                    else:
                        return {"content": [{"type": "text", "text": f"Error: Task '{task_id}' not found in graph"}]}
                except Exception as e:
                    logger.warning(f"Failed to fetch task {task_id}: {e}")
                    return {"content": [{"type": "text", "text": f"Error fetching task: {e}"}]}
            else:
                return {"content": [{"type": "text", "text": "Error: No graph connection for task lookup"}]}
        elif not issue_type or not path:
            return {"content": [{"type": "text", "text": "Error: Either task_id OR (issue_type + path) required"}]}

        # Select agent if not specified
        if not agent_id:
            posture = PROBLEM_TO_POSTURE.get(issue_type, "fixer") if issue_type else "fixer"
            agent_id = f"agent_{posture}"

        # Check if agent is available
        agents = {a.id: a for a in self.agent_graph.get_all_agents()}
        if agent_id in agents and agents[agent_id].status == "running":
            return {"content": [{"type": "text", "text": f"Error: {agent_id} is already running. Choose another agent or wait."}]}

        posture = agent_id.replace("agent_", "")

        # Upsert issue/task narratives before linking
        issue_ids = None
        if issue_type and path:
            # Create/update issue narrative in graph
            issue_narrative_id = self.agent_graph.upsert_issue_narrative(
                issue_type=issue_type,
                path=path,
                message=f"Doctor issue: {issue_type} at {path}",
                severity="warning",
            )
            if issue_narrative_id:
                issue_ids = [issue_narrative_id]

            # Build prompt for issue-based spawn
            if not prompt:
                prompt = f"""Fix the doctor issue:
Issue Type: {issue_type}
Path: {path}

Please investigate and fix this issue. Follow the project's coding standards and documentation patterns."""

        # Use task_id for assignment, or create from issue
        assignment_task_id = task_id
        if not assignment_task_id and issue_type:
            # Create task narrative for this fix
            assignment_task_id = self.agent_graph.upsert_task_narrative(
                task_type=f"FIX_{issue_type}",
                content=f"Fix {issue_type} at {path}",
                name=f"Fix {issue_type}",
            )

        # Actually spawn and run the agent
        try:
            spawn_result = asyncio.run(
                spawn_work_agent(
                    agent_id=agent_id,
                    prompt=prompt,
                    target_dir=self.target_dir,
                    agent_provider=provider,
                    timeout=300.0,
                    use_continue=True,
                    task_id=assignment_task_id,
                    issue_ids=issue_ids,
                )
            )

            # Build response
            if task_id:
                lines = [
                    f"Agent Execution Complete (Task):",
                    f"  Agent: {agent_id}",
                    f"  Posture: {posture}",
                    f"  Task ID: {task_id}",
                    f"  Provider: {provider}",
                    f"  Success: {spawn_result.success}",
                    f"  Duration: {spawn_result.duration_seconds:.1f}s",
                ]
            else:
                lines = [
                    f"Agent Execution Complete (Issue):",
                    f"  Agent: {agent_id}",
                    f"  Posture: {posture}",
                    f"  Issue: {issue_type}",
                    f"  Path: {path}",
                    f"  Provider: {provider}",
                    f"  Success: {spawn_result.success}",
                    f"  Duration: {spawn_result.duration_seconds:.1f}s",
                ]

            if spawn_result.assignment_moment_id:
                lines.append(f"  Moment: {spawn_result.assignment_moment_id}")

            if spawn_result.retried_without_continue:
                lines.append(f"  Note: Retried without --continue")

            if spawn_result.error:
                lines.append(f"  Error: {spawn_result.error[:200]}")

            if spawn_result.output:
                lines.extend([
                    "",
                    "Agent Output:",
                    spawn_result.output[:1000] + ("..." if len(spawn_result.output) > 1000 else ""),
                ])

            return {"content": [{"type": "text", "text": "\n".join(lines)}]}

        except Exception as e:
            logger.exception("Agent spawn failed")
            return {"content": [{"type": "text", "text": f"Error executing agent: {e}"}]}

    def _tool_agent_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get or set agent status."""
        agent_id = args.get("agent_id")
        set_status = args.get("set_status")

        if not agent_id:
            return {"content": [{"type": "text", "text": "Error: agent_id is required"}]}

        if set_status:
            if set_status == "running":
                self.agent_graph.set_agent_running(agent_id)
            else:
                self.agent_graph.set_agent_ready(agent_id)
            return {"content": [{"type": "text", "text": f"Agent {agent_id} status set to {set_status}"}]}

        # Get current status
        agents = {a.id: a for a in self.agent_graph.get_all_agents()}
        if agent_id not in agents:
            return {"content": [{"type": "text", "text": f"Agent {agent_id} not found"}]}

        agent = agents[agent_id]
        lines = [
            f"Agent: {agent.id}",
            f"Posture: {agent.posture}",
            f"Status: {agent.status}",
            f"Energy: {agent.energy:.2f}",
            f"Weight: {agent.weight:.2f}",
        ]
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}

    def _tool_graph_query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Query the graph using natural language via SubEntity exploration."""
        queries = args.get("queries", [])
        intent = args.get("intent")  # WHY searching - affects traversal
        actor_id = args.get("actor_id", "actor_claude")
        debug = args.get("debug", False)
        timeout = args.get("timeout", 30.0)

        if not queries:
            return {"content": [{"type": "text", "text": "Error: 'queries' array is required"}]}

        if not self.graph_queries:
            return {"content": [{"type": "text", "text": "Error: No graph connection available"}]}

        # Resolve actor: check if exists, otherwise pick randomly
        actor_id = self._resolve_actor(actor_id, debug)

        debug_lines = []
        if debug:
            debug_lines.append("=== DEBUG MODE ===")
            debug_lines.append(f"Actor: {actor_id}")
            debug_lines.append(f"Intent: {intent or '(none)'}")
            debug_lines.append(f"Timeout: {timeout}s")
            debug_lines.append("")

        try:
            # Run queries
            results = asyncio.run(
                self._ask_async(queries, actor_id, intent, timeout, debug, debug_lines)
            )

            # Format output
            output_lines = []

            if debug:
                output_lines.extend(debug_lines)
                output_lines.append("")

            # Markdown output
            for i, item in enumerate(results, 1):
                if len(results) > 1:
                    output_lines.append(f"## Query {i}: {item['query']}\n")
                output_lines.append(item["result"] if isinstance(item["result"], str) else json.dumps(item["result"], indent=2))
                output_lines.append("")

            return {"content": [{"type": "text", "text": "\n".join(output_lines)}]}

        except Exception as e:
            logger.exception("Graph query failed")
            error_msg = f"Error executing query: {e}"
            if debug:
                import traceback
                error_msg += f"\n\nTraceback:\n{traceback.format_exc()}"
            return {"content": [{"type": "text", "text": error_msg}]}

    def _resolve_actor(self, actor_id: str, debug: bool = False) -> str:
        """Resolve actor ID: return existing actor or pick random one."""
        if not self.graph_queries:
            return actor_id

        # Check if actor exists
        result = self.graph_queries._query(
            "MATCH (a:Actor {id: $actor_id}) RETURN a.id",
            {"actor_id": actor_id}
        )
        if result and result[0]:
            return actor_id

        # Actor not found, pick a random one
        actors = self.graph_queries._query(
            "MATCH (a:Actor) RETURN a.id LIMIT 20"
        )
        if actors:
            random_actor = random.choice(actors)[0]
            if debug:
                logger.info(f"Actor {actor_id} not found, using random actor: {random_actor}")
            return random_actor

        # No actors in graph, return original (will fail later with clear error)
        return actor_id

    async def _ask_async(
        self,
        queries: List[str],
        actor_id: str,
        intent: Optional[str],
        timeout: float,
        debug: bool,
        debug_lines: List[str]
    ) -> List[Dict[str, Any]]:
        """Async SubEntity exploration for multiple queries - runs concurrently."""
        valid_queries = [q for q in queries if q and q.strip()]

        if not valid_queries:
            return []

        if debug:
            debug_lines.append(f"Running {len(valid_queries)} queries concurrently...")

        # Create tasks for all queries
        tasks = [
            self._ask_single(query, actor_id, intent, timeout, debug, debug_lines)
            for query in valid_queries
        ]

        # Run all queries concurrently
        results_raw = await asyncio.gather(*tasks, return_exceptions=True)

        # Format results
        results = []
        for query, result in zip(valid_queries, results_raw):
            if isinstance(result, Exception):
                results.append({"query": query, "result": f"Error: {result}"})
            else:
                results.append({"query": query, "result": result})

        return results

    async def _ask_single(self, query: str, actor_id: str, intent: Optional[str], timeout: float, debug: bool, debug_lines: List[str]) -> str:
        """Async SubEntity exploration to answer a single query."""
        import time
        from runtime.infrastructure.embeddings.service import get_embedding_service
        start = time.time()

        try:
            from runtime.explore_cmd import run_exploration

            if debug:
                debug_lines.append(f"Starting SubEntity exploration...")
                debug_lines.append(f"Actor: {actor_id}, Timeout: {timeout}s")

            # Create query moment and link to actor
            embed_service = get_embedding_service()
            moment_id = self.graph_queries._create_query_moment(
                query=query,
                embed_fn=embed_service.embed,
                initial_energy=1.0
            )
            # Link actor to moment
            self.graph_queries._query("""
                MATCH (a {id: $actor_id})
                MATCH (m {id: $moment_id})
                MERGE (a)-[r:link]->(m)
                SET r.weight = 1.0, r.energy = 1.0
            """, {'actor_id': actor_id, 'moment_id': moment_id})

            # Link to previous actor moment
            prev_moment = self.graph_queries._query("""
                MATCH (a {id: $actor_id})-[:link]->(m:Moment)
                WHERE m.id <> $moment_id
                RETURN m.id
                ORDER BY m.created_at_s DESC
                LIMIT 1
            """, {'actor_id': actor_id, 'moment_id': moment_id})
            if prev_moment:
                prev_id = prev_moment[0][0] if prev_moment[0] else None
                if prev_id:
                    self.graph_queries._query("""
                        MATCH (prev {id: $prev_id})
                        MATCH (curr {id: $curr_id})
                        MERGE (prev)-[r:link]->(curr)
                        SET r.weight = 1.0, r.energy = 0.0
                    """, {'prev_id': prev_id, 'curr_id': moment_id})
                    if debug:
                        debug_lines.append(f"Linked to previous: {prev_id}")

            if debug:
                debug_lines.append(f"Created moment: {moment_id}")

            # Run exploration asynchronously
            result, log_path = await run_exploration(
                query=query,
                actor_id=actor_id,
                intention=intent,  # WHY searching - affects traversal strategy
                graph_name=None,  # Use config default
                origin_moment=moment_id,
                timeout=timeout,
                debug=debug,
            )

            elapsed = time.time() - start

            if debug:
                debug_lines.append(f"Exploration completed in {elapsed:.2f}s")
                debug_lines.append(f"State: {result.state.value}")
                debug_lines.append(f"Satisfaction: {result.satisfaction:.2f}")
                debug_lines.append(f"Found narratives: {len(result.found_narratives)}")
                if log_path:
                    debug_lines.append(f"Log: {log_path}.txt")

            # Format result using cluster presentation
            from runtime.physics.cluster_presentation import (
                ClusterNode,
                ClusterLink,
                RawCluster,
                present_cluster,
                IntentionType,  # For presentation filtering (not link scoring)
            )

            if not result.found_narratives:
                return "No relevant narratives found."

            # Parse intention type
            intent_type = IntentionType.EXPLORE
            if intent:
                intent_lower = intent.lower()
                if "summar" in intent_lower:
                    intent_type = IntentionType.SUMMARIZE
                elif "verif" in intent_lower or "check" in intent_lower:
                    intent_type = IntentionType.VERIFY
                elif "find" in intent_lower or "next" in intent_lower:
                    intent_type = IntentionType.FIND_NEXT
                elif "retriev" in intent_lower or "get" in intent_lower:
                    intent_type = IntentionType.RETRIEVE

            # Fetch actual content for each found narrative
            nodes = []
            query_embedding = embed_service.embed(query)

            for narr_id, alignment in result.found_narratives.items():
                narr_data = self.graph_queries._query("""
                    MATCH (n {id: $narr_id})
                    RETURN n.name, n.content, n.synthesis, n.node_type, n.energy, n.weight
                """, {'narr_id': narr_id})

                if narr_data and narr_data[0]:
                    name = narr_data[0][0] or narr_id
                    content = narr_data[0][1] or ""
                    synthesis = narr_data[0][2] or name
                    node_type = narr_data[0][3] or "narrative"
                    energy = narr_data[0][4] or 1.0
                    weight = narr_data[0][5] or alignment

                    # Use content or synthesis for display
                    display_text = synthesis if synthesis else (content[:200] if content else name)

                    nodes.append(ClusterNode(
                        id=narr_id,
                        node_type=node_type,
                        name=name,
                        synthesis=display_text,
                        embedding=query_embedding,
                        weight=weight,
                        energy=energy,
                    ))

            # Add actor node
            nodes.append(ClusterNode(
                id=actor_id,
                node_type='actor',
                name=actor_id,
                synthesis=f"Explorer: {actor_id}",
                embedding=query_embedding,
                weight=1.0,
                energy=1.0,
            ))

            # Create links from actor to narratives
            links = []
            for narr_id, alignment in result.found_narratives.items():
                links.append(ClusterLink(
                    id=f"link_{actor_id}_{narr_id}",
                    source_id=actor_id,
                    target_id=narr_id,
                    synthesis=f"found (alignment: {alignment:.2f})",
                    embedding=query_embedding,
                    weight=alignment,
                    energy=alignment,
                    permanence=0.5,
                    trust_disgust=0.0,
                ))

            # Build and present cluster
            raw_cluster = RawCluster(
                nodes=nodes,
                links=links,
                traversed_link_ids={l.id for l in links},
            )

            presented = present_cluster(
                raw_cluster=raw_cluster,
                query=query,
                intention=intent or query,
                intention_type=intent_type,
                query_embedding=query_embedding,
                intention_embedding=query_embedding,
                start_id=actor_id,
            )

            # Add crystallization info if present
            output = presented.markdown
            if result.crystallized:
                output += f"\n\n*Crystallized: {result.crystallized}*"

            return output

        except Exception as e:
            if debug:
                debug_lines.append(f"Ask failed: {e}")
            return f"Ask failed: {e}"

    def _tool_capability_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get capability system status."""
        if not self.capability_manager:
            return {"content": [{"type": "text", "text": "Capability system not available"}]}

        status = self.capability_manager.get_status()

        lines = ["Capability System Status\n"]
        lines.append(f"Initialized: {status['initialized']}")
        lines.append(f"Capabilities: {status['capabilities']}")
        lines.append(f"Cron Scheduler: {'running' if status['cron_running'] else 'stopped'}")

        if status.get("registry"):
            reg = status["registry"]
            lines.append(f"\nTrigger Registry:")
            lines.append(f"  Trigger types: {reg.get('trigger_types', 0)}")
            lines.append(f"  Total checks: {reg.get('total_checks', 0)}")
            if reg.get("by_type"):
                lines.append("  By type:")
                for trigger_type, count in sorted(reg["by_type"].items())[:10]:
                    lines.append(f"    {trigger_type}: {count}")

        if status.get("throttler"):
            th = status["throttler"]
            lines.append(f"\nThrottler:")
            lines.append(f"  Pending: {th.get('pending_count', 0)}")
            lines.append(f"  Active: {th.get('active_count', 0)}")

        if status.get("controller"):
            ctrl = status["controller"]
            lines.append(f"\nController:")
            lines.append(f"  Mode: {ctrl.get('mode', 'unknown')}")
            lines.append(f"  Can claim: {ctrl.get('can_claim', False)}")

        return {"content": [{"type": "text", "text": "\n".join(lines)}]}

    def _tool_capability_trigger(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Fire a trigger manually."""
        if not self.capability_manager:
            return {"content": [{"type": "text", "text": "Capability system not available"}]}

        trigger_type = args.get("trigger_type")
        if not trigger_type:
            return {"content": [{"type": "text", "text": "Error: trigger_type is required"}]}

        payload = {}
        if args.get("file_path"):
            payload["file_path"] = args["file_path"]

        create_tasks = args.get("create_tasks", True)

        try:
            result = self.capability_manager.fire_trigger(
                trigger_type=trigger_type,
                payload=payload,
                create_tasks=create_tasks,
            )

            lines = [f"Trigger: {trigger_type}\n"]
            lines.append(f"Checks run: {result.get('checks_run', 0)}")
            lines.append(f"  Healthy: {result.get('healthy', 0)}")
            lines.append(f"  Degraded: {result.get('degraded', 0)}")
            lines.append(f"  Critical: {result.get('critical', 0)}")

            task_runs = result.get("task_runs", [])
            if task_runs:
                lines.append(f"\nTask runs created: {len(task_runs)}")
                # Fetch task details from graph
                for task_id in task_runs[:10]:
                    try:
                        task_result = self.graph_ops._query(
                            "MATCH (n {id: $id}) RETURN n.name, n.status",
                            {"id": task_id}
                        )
                        if task_result and task_result[0]:
                            name = task_result[0][0] or "Unknown"
                            status = task_result[0][1] or "pending"
                            lines.append(f"  - [{status}] {name}")
                            lines.append(f"    ID: {task_id}")
                        else:
                            lines.append(f"  - {task_id}")
                    except:
                        lines.append(f"  - {task_id}")

            return {"content": [{"type": "text", "text": "\n".join(lines)}]}

        except Exception as e:
            logger.exception("Trigger failed")
            return {"content": [{"type": "text", "text": f"Error: {e}"}]}

    def _tool_capability_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all loaded capabilities."""
        if not self.capability_manager:
            return {"content": [{"type": "text", "text": "Capability system not available"}]}

        capabilities = self.capability_manager.list_capabilities()

        if not capabilities:
            return {"content": [{"type": "text", "text": "No capabilities loaded"}]}

        lines = [f"Loaded Capabilities: {len(capabilities)}\n"]

        for cap in capabilities:
            lines.append(f"📦 {cap['name']}")
            for check in cap["checks"]:
                triggers_str = ", ".join(check["triggers"][:2])
                if len(check["triggers"]) > 2:
                    triggers_str += "..."
                lines.append(f"   ├─ {check['id']}")
                lines.append(f"   │  Triggers: {triggers_str}")
                lines.append(f"   │  Problem: {check['on_problem']}")
                lines.append(f"   └─ Task: {check['task']}")
            lines.append("")

        return {"content": [{"type": "text", "text": "\n".join(lines)}]}

    def _tool_task_claim(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Atomically claim a task."""
        task_id = args.get("task_id")
        actor_id = args.get("actor_id")

        if not task_id or not actor_id:
            return {"content": [{"type": "text", "text": "Error: task_id and actor_id are required"}]}

        if not self.graph_ops:
            return {"content": [{"type": "text", "text": "Error: No graph connection"}]}

        try:
            # Check throttler allows claiming (if it knows about this task)
            throttler = get_throttler()
            if throttler:
                # Only check throttler if task is registered (from current session)
                # Tasks from previous sessions won't be in throttler
                if task_id in throttler.active and not throttler.can_claim(task_id, actor_id):
                    return {"content": [{"type": "text", "text": f"Throttler blocked claim: max agents reached or paused"}]}

            # Claim in graph - use node-level status field
            # Check task exists and is pending
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            result = self.graph_ops._query(
                "MATCH (n {id: $id}) WHERE n.status = 'pending' "
                "SET n.status = 'claimed', n.claimed_by = $actor, n.claimed_at = $ts "
                "RETURN n.id",
                {"id": task_id, "actor": actor_id, "ts": timestamp}
            )
            if not result or not result[0]:
                return {"content": [{"type": "text", "text": f"Failed to claim: task not found or already claimed"}]}

            # Create claimed_by link
            self.graph_ops._query(
                "MATCH (t {id: $task_id}) MATCH (a {id: $actor_id}) "
                "MERGE (t)-[:LINK {verb: 'claimed_by'}]->(a)",
                {"task_id": task_id, "actor_id": actor_id}
            )

            # Register with throttler
            if throttler:
                throttler.register_claim(task_id, actor_id)

            return {"content": [{"type": "text", "text": f"Task {task_id} claimed by {actor_id}"}]}

        except Exception as e:
            logger.exception("Task claim failed")
            return {"content": [{"type": "text", "text": f"Error: {e}"}]}

    def _tool_task_complete(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mark task as completed."""
        task_id = args.get("task_id")

        if not task_id:
            return {"content": [{"type": "text", "text": "Error: task_id is required"}]}

        if not self.graph_ops:
            return {"content": [{"type": "text", "text": "Error: No graph connection"}]}

        try:
            # Complete in graph using direct query
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            result = self.graph_ops._query(
                "MATCH (n {id: $id}) WHERE n.status = 'claimed' "
                "SET n.status = 'completed', n.completed_at = $ts "
                "RETURN n.id",
                {"id": task_id, "ts": timestamp}
            )
            if not result or not result[0]:
                return {"content": [{"type": "text", "text": f"Failed to complete: task not found or not claimed"}]}

            # Release throttler slot
            throttler = get_throttler()
            if throttler:
                throttler.on_complete(task_id)

            return {"content": [{"type": "text", "text": f"Task {task_id} completed"}]}

        except Exception as e:
            logger.exception("Task complete failed")
            return {"content": [{"type": "text", "text": f"Error: {e}"}]}

    def _tool_task_fail(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mark task as failed."""
        task_id = args.get("task_id")
        reason = args.get("reason", "Unknown reason")

        if not task_id:
            return {"content": [{"type": "text", "text": "Error: task_id is required"}]}

        if not self.graph_ops:
            return {"content": [{"type": "text", "text": "Error: No graph connection"}]}

        try:
            # Fail in graph using direct query
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            result = self.graph_ops._query(
                "MATCH (n {id: $id}) WHERE n.status IN ['pending', 'claimed'] "
                "SET n.status = 'failed', n.failed_at = $ts, n.failure_reason = $reason "
                "RETURN n.id",
                {"id": task_id, "ts": timestamp, "reason": reason}
            )
            if not result or not result[0]:
                return {"content": [{"type": "text", "text": f"Failed to mark failed: task not found or already completed"}]}

            # Release throttler slot
            throttler = get_throttler()
            if throttler:
                throttler.on_abandon(task_id)

            return {"content": [{"type": "text", "text": f"Task {task_id} failed: {reason}"}]}

        except Exception as e:
            logger.exception("Task fail failed")
            return {"content": [{"type": "text", "text": f"Error: {e}"}]}

    def _tool_agent_heartbeat(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent heartbeat."""
        actor_id = args.get("actor_id")
        step = args.get("step")

        if not actor_id:
            return {"content": [{"type": "text", "text": "Error: actor_id is required"}]}

        if not self.graph_ops:
            return {"content": [{"type": "text", "text": "Error: No graph connection"}]}

        try:
            # Update in graph using direct query
            from datetime import datetime
            timestamp = datetime.now().isoformat()

            if step is not None:
                result = self.graph_ops._query(
                    "MATCH (n {id: $id}) "
                    "SET n.last_heartbeat = $ts, n.current_step = $step "
                    "RETURN n.id",
                    {"id": actor_id, "ts": timestamp, "step": step}
                )
            else:
                result = self.graph_ops._query(
                    "MATCH (n {id: $id}) "
                    "SET n.last_heartbeat = $ts "
                    "RETURN n.id",
                    {"id": actor_id, "ts": timestamp}
                )

            success = bool(result and result[0])

            # Also update in-memory registry
            registry = get_agent_registry()
            if registry:
                registry.heartbeat(actor_id, step)

            if success:
                msg = f"Heartbeat: {actor_id}"
                if step is not None:
                    msg += f" (step {step})"
                return {"content": [{"type": "text", "text": msg}]}
            else:
                return {"content": [{"type": "text", "text": f"Heartbeat failed: actor not found"}]}

        except Exception as e:
            logger.exception("Heartbeat failed")
            return {"content": [{"type": "text", "text": f"Error: {e}"}]}

    def _format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format runner response as MCP tool result."""
        status = response.get("status", "unknown")

        lines = [f"Status: {status}"]

        if response.get("error"):
            lines.append(f"Error: {response['error']}")

        if response.get("session_id"):
            lines.append(f"Session: {response['session_id']}")

        step = response.get("step", {})
        if step:
            step_type = step.get("type", "")
            lines.append(f"Step Type: {step_type}")

            # Show context if provided
            if step.get("context"):
                lines.append(f"\n--- Context ---\n{step['context']}")

            if step.get("question"):
                lines.append(f"\n--- Question ---\n{step['question']}")
                if step.get("question_name"):
                    lines.append(f"(Answer will be stored as: {step['question_name']})")

            if step.get("why_it_matters"):
                lines.append(f"\nWhy it matters: {step['why_it_matters']}")

            if step.get("good_answer"):
                lines.append(f"Good answer example: {step['good_answer']}")

            if step.get("bad_answer"):
                lines.append(f"Bad answer example: {step['bad_answer']}")

            if step.get("expects"):
                expects = step["expects"]
                lines.append(f"\nExpects: {expects.get('type', 'string')}")
                if expects.get("options"):
                    lines.append(f"Options: {expects['options']}")
                if expects.get("min_length"):
                    lines.append(f"Min Length: {expects['min_length']}")
                if expects.get("min") is not None:
                    lines.append(f"Min Items: {expects['min']}")

            if step.get("question_count") and step["question_count"] > 1:
                lines.append(f"Question {step.get('question_index', 0) + 1} of {step['question_count']}")

            if step.get("results"):
                lines.append(f"\nQuery Results: {len(step['results'])} items")
                for r in step["results"][:5]:
                    lines.append(f"  - {r}")

        if status == "complete":
            created = response.get("created", {})
            nodes = created.get("nodes", [])
            links = created.get("links", [])

            lines.append(f"\nCreated: {len(nodes)} nodes, {len(links)} links")

            if nodes:
                lines.append("\nNodes:")
                for n in nodes:
                    lines.append(f"  - [{n.get('type')}] {n.get('id')}")

            if links:
                lines.append("\nLinks:")
                for l in links:
                    lines.append(f"  - {l.get('type')}: {l.get('from')} -> {l.get('to')}")

        text = "\n".join(lines)
        return {"content": [{"type": "text", "text": text}]}

    def _success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Build success response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }

    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Build error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }


def main():
    """Run the MCP server on stdio."""
    server = MindServer()
    logger.info("Mind MCP server started")

    # Read JSON-RPC messages from stdin
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
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
