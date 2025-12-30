"""
Agent Graph Operations

Query and select work agents from the mind graph.
Agents are Actor nodes with name-based selection.

The 10 agents (by name, not role):
- witness: evidence-first, traces what actually happened
- groundwork: foundation-first, builds scaffolding
- keeper: verification-first, checks before declaring done
- weaver: connection-first, patterns across modules
- voice: naming-first, finds right words for concepts
- scout: exploration-first, navigates and surveys
- architect: structure-first, shapes systems
- fixer: work-first, resolves without breaking
- herald: communication-first, broadcasts changes
- steward: coordination-first, prioritizes and assigns

Status lifecycle:
- ready: Agent available for work
- running: Agent currently executing (only one at a time)

Usage:
    from runtime.agent_graph import AgentGraph

    ag = AgentGraph()

    # Get available agents
    agents = ag.get_available_agents()

    # Select best agent for an issue type
    actor_id = ag.select_agent_for_issue("STALE_SYNC")

    # Mark agent as running (before run)
    ag.set_agent_running(actor_id)

    # Mark agent as ready (after run completes)
    ag.set_agent_ready(actor_id)

DOCS: docs/membrane/PATTERNS_Membrane.md
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# NAME → ISSUE TYPE MAPPING
# =============================================================================
#
# Each issue type maps to a preferred name. The name shapes HOW the
# agent approaches the work, not WHAT it can do.
#
# Key insight: All agents can do all tasks. But matching name to issue
# type leads to better outcomes.

TASK_TO_AGENT: Dict[str, str] = {
    # witness: evidence-first (traces, investigations)
    "STALE_SYNC": "witness",
    "STALE_IMPL": "witness",
    "DOC_DELTA": "witness",
    "NEW_UNDOC_CODE": "witness",

    # groundwork: foundation-first (scaffolding, structure)
    "UNDOCUMENTED": "groundwork",
    "INCOMPLETE_CHAIN": "groundwork",
    "MISSING_TESTS": "groundwork",

    # keeper: verification-first (validation, checks)
    "INVARIANT_COVERAGE": "keeper",
    "TEST_VALIDATES": "keeper",
    "COMPLETION_GATE": "keeper",
    "VALIDATION_BEHAVIORS_LIST": "keeper",

    # weaver: connection-first (patterns, links)
    "BROKEN_IMPL_LINKS": "weaver",
    "DOC_LINK_INTEGRITY": "weaver",
    "ORPHAN_DOCS": "weaver",

    # voice: naming-first (naming, terminology)
    "NAMING_CONVENTION": "voice",
    "NONSTANDARD_DOC_TYPE": "voice",

    # scout: exploration-first (discovery, navigation)
    "MONOLITH": "scout",
    "LARGE_DOC_MODULE": "scout",

    # architect: structure-first (design, patterns)
    "DOC_TEMPLATE_DRIFT": "architect",
    "YAML_DRIFT": "architect",
    "PLACEHOLDER_DOCS": "architect",

    # fixer: work-first (fixes, patches)
    "STUB_IMPL": "fixer",
    "INCOMPLETE_IMPL": "fixer",
    "NO_DOCS_REF": "fixer",
    "UNDOC_IMPL": "fixer",
    "MAGIC_VALUES": "fixer",
    "HARDCODED_SECRETS": "fixer",
    "LONG_STRINGS": "fixer",

    # herald: communication-first (docs, announcements)
    "DOC_GAPS": "herald",
    "DOC_DUPLICATION": "herald",
    "PROMPT_DOC_REFERENCE": "herald",
    "PROMPT_VIEW_TABLE": "herald",
    "PROMPT_CHECKLIST": "herald",

    # steward: coordination-first (conflicts, priorities)
    "ESCALATION": "steward",
    "SUGGESTION": "steward",
    "CONFLICTS": "steward",
}

# Default name when issue type not mapped
DEFAULT_NAME = "fixer"


def get_agent_id(name: str, target_dir: Path = None) -> str:
    """Get agent ID from name, discovering from .mind/actors/."""
    from runtime.agents.mapping import get_agent_id as _get_agent_id
    return _get_agent_id(name, target_dir)


@dataclass
class AgentInfo:
    """Information about an agent from the graph."""
    id: str
    name: str  # The agent's name (e.g., "witness")
    status: str   # ready, running, or paused
    energy: float = 0.0
    weight: float = 1.0


class AgentGraph:
    """
    Query and manage work agents from the mind graph.

    Agents are Actor nodes with:
    - id: AGENT_{Name} (e.g., AGENT_Witness)
    - name: The agent name (e.g., witness)
    - type: AGENT
    - status: ready | running | paused
    """

    def __init__(
        self,
        graph_name: str = None,  # Use config default
        host: str = "localhost",
        port: int = 6379,
    ):
        self.graph_name = graph_name
        self.host = host
        self.port = port
        self._graph_ops = None
        self._graph_queries = None
        self._connected = False

    def _connect(self) -> bool:
        """Lazy connect to graph database."""
        if self._connected:
            return True

        try:
            from runtime.physics.graph.graph_ops import GraphOps
            from runtime.physics.graph.graph_queries import GraphQueries

            # Let factory use config defaults
            self._graph_ops = GraphOps(graph_name=self.graph_name)
            self._graph_queries = GraphQueries(graph_name=self.graph_name)
            self._connected = True
            self.graph_name = self._graph_ops.graph_name  # Update with actual name
            logger.info(f"[AgentGraph] Connected to {self.graph_name}")
            return True
        except Exception as e:
            logger.warning(f"[AgentGraph] No graph connection: {e}")
            return False

    def ensure_agents_exist(self, target_dir: Path = None) -> bool:
        """
        Ensure all discovered agents exist in the graph.
        Creates them if they don't exist.

        Args:
            target_dir: Project root for agent discovery

        Returns:
            True if agents exist or were created, False on failure
        """
        if not self._connect():
            return False

        try:
            import time
            from runtime.agents.mapping import discover_agents
            timestamp = int(time.time())

            agents = discover_agents(target_dir)
            for name, actor_id in agents.items():
                # Check if agent exists
                cypher = f"""
                MATCH (a:Actor {{id: '{actor_id}'}})
                RETURN a.id
                """
                result = self._graph_ops._query(cypher)

                if not result:
                    # Create agent node
                    props = {
                        "id": actor_id,
                        "name": name,
                        "node_type": "actor",
                        "type": "AGENT",
                        "status": "ready",
                        "content": f"Work agent: {name}",
                        "weight": 1.0,
                        "energy": 0.0,
                        "created_at_s": timestamp,
                        "updated_at_s": timestamp,
                    }

                    create_cypher = """
                    MERGE (a:Actor {id: $id})
                    SET a += $props
                    """
                    self._graph_ops._query(create_cypher, {"id": actor_id, "props": props})
                    logger.info(f"[AgentGraph] Created agent: {actor_id}")

            return True
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to ensure agents exist: {e}")
            return False

    def get_all_agents(self) -> List[AgentInfo]:
        """
        Get all agents from the graph.

        Returns:
            List of AgentInfo for all agents
        """
        if not self._connect():
            return self._get_fallback_agents()

        try:
            cypher = """
            MATCH (a:Actor)
            WHERE a.type = 'AGENT'
            RETURN a.id, a.name, a.status, a.energy, a.weight
            ORDER BY a.name
            """
            rows = self._graph_ops._query(cypher)

            agents = []
            for row in rows:
                if len(row) >= 3:
                    actor_id = row[0]
                    name = row[1]
                    status = row[2] or "ready"
                    energy = row[3] if len(row) > 3 else 0.0
                    weight = row[4] if len(row) > 4 else 1.0

                    agents.append(AgentInfo(
                        id=actor_id,
                        name=name,
                        status=status,
                        energy=energy or 0.0,
                        weight=weight or 1.0,
                    ))

            return agents if agents else self._get_fallback_agents()
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to get agents: {e}")
            return self._get_fallback_agents()

    def _get_fallback_agents(self, target_dir: Path = None) -> List[AgentInfo]:
        """Return fallback agent list when graph unavailable."""
        from runtime.agents.mapping import discover_agents
        agents = discover_agents(target_dir)
        return [
            AgentInfo(id=actor_id, name=name, status="ready")
            for name, actor_id in agents.items()
        ]

    def get_available_agents(self) -> List[AgentInfo]:
        """
        Get agents that are available (status=ready).

        Returns:
            List of AgentInfo for available agents
        """
        all_agents = self.get_all_agents()
        return [a for a in all_agents if a.status == "ready"]

    def get_running_agents(self) -> List[AgentInfo]:
        """
        Get agents that are currently running.

        Returns:
            List of AgentInfo for running agents
        """
        all_agents = self.get_all_agents()
        return [a for a in all_agents if a.status == "running"]

    def select_agent_for_issue(self, task_type: str, target_dir: Path = None) -> Optional[str]:
        """
        Select the best agent for an issue type.

        Matches issue type to name, then finds an available agent
        with that name. Falls back to default name if no match.

        Args:
            task_type: The doctor issue type (e.g., "STALE_SYNC")
            target_dir: Project root for agent discovery

        Returns:
            Agent ID (e.g., "AGENT_Witness") or None if all agents busy
        """
        # Get preferred name for this issue type
        name = TASK_TO_AGENT.get(task_type, DEFAULT_NAME)
        preferred_actor_id = get_agent_id(name, target_dir)

        # Get available agents
        available = self.get_available_agents()

        if not available:
            logger.warning("[AgentGraph] All agents are busy")
            return None

        # Check if preferred agent is available
        for agent in available:
            if agent.id == preferred_actor_id:
                return agent.id

        # Fall back to any available agent
        # Prefer higher energy agents (more recently active)
        available.sort(key=lambda a: a.energy, reverse=True)
        return available[0].id

    def get_agent_name(self, actor_id: str) -> str:
        """
        Get the name for an agent ID.

        Args:
            actor_id: e.g., "AGENT_Witness"

        Returns:
            Agent name (e.g., "witness")
        """
        # Extract from ID (AGENT_{Name})
        if actor_id.startswith("AGENT_"):
            return actor_id[6:].lower()  # Remove "AGENT_" prefix and lowercase
        return DEFAULT_NAME

    def set_agent_running(self, actor_id: str) -> bool:
        """
        Mark an agent as running.

        Call this BEFORE running the agent process.

        Args:
            actor_id: The agent to mark as running

        Returns:
            True if successful, False on failure
        """
        if not self._connect():
            logger.warning(f"[AgentGraph] No graph connection, cannot set {actor_id} running")
            return False

        try:
            import time
            cypher = """
            MATCH (a:Actor {id: $id})
            SET a.status = 'running', a.updated_at_s = $timestamp
            RETURN a.id
            """
            result = self._graph_ops._query(cypher, {
                "id": actor_id,
                "timestamp": int(time.time()),
            })

            if result:
                logger.info(f"[AgentGraph] Agent {actor_id} now running")
                return True
            else:
                logger.warning(f"[AgentGraph] Agent {actor_id} not found")
                return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to set {actor_id} running: {e}")
            return False

    def set_agent_ready(self, actor_id: str) -> bool:
        """
        Mark an agent as ready (available).

        Call this AFTER the agent process completes.

        Args:
            actor_id: The agent to mark as ready

        Returns:
            True if successful, False on failure
        """
        if not self._connect():
            logger.warning(f"[AgentGraph] No graph connection, cannot set {actor_id} ready")
            return False

        try:
            import time
            cypher = """
            MATCH (a:Actor {id: $id})
            SET a.status = 'ready', a.updated_at_s = $timestamp
            RETURN a.id
            """
            result = self._graph_ops._query(cypher, {
                "id": actor_id,
                "timestamp": int(time.time()),
            })

            if result:
                logger.info(f"[AgentGraph] Agent {actor_id} now ready")
                return True
            else:
                logger.warning(f"[AgentGraph] Agent {actor_id} not found")
                return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to set {actor_id} ready: {e}")
            return False

    def set_agent_paused(self, actor_id: str) -> bool:
        """
        Mark an agent as paused.

        Paused agents won't have their claimed tasks promoted to running.

        Args:
            actor_id: The agent to pause

        Returns:
            True if successful, False on failure
        """
        if not self._connect():
            logger.warning(f"[AgentGraph] No graph connection, cannot pause {actor_id}")
            return False

        try:
            import time
            cypher = """
            MATCH (a:Actor {id: $id})
            SET a.status = 'paused', a.updated_at_s = $timestamp
            RETURN a.id
            """
            result = self._graph_ops._query(cypher, {
                "id": actor_id,
                "timestamp": int(time.time()),
            })

            if result:
                logger.info(f"[AgentGraph] Agent {actor_id} now paused")
                return True
            else:
                logger.warning(f"[AgentGraph] Agent {actor_id} not found")
                return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to pause {actor_id}: {e}")
            return False

    def boost_agent_energy(self, actor_id: str, amount: float = 0.1) -> bool:
        """
        Boost an agent's energy (used for prioritization).

        More recently active agents have higher energy.

        Args:
            actor_id: The agent to boost
            amount: Energy to add

        Returns:
            True if successful
        """
        if not self._connect():
            return False

        try:
            cypher = """
            MATCH (a:Actor {id: $id})
            SET a.energy = coalesce(a.energy, 0) + $amount
            RETURN a.id
            """
            self._graph_ops._query(cypher, {"id": actor_id, "amount": amount})
            return True
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to boost {actor_id} energy: {e}")
            return False


    def link_agent_to_task(self, actor_id: str, task_id: str) -> bool:
        """
        Create assigned_to link between agent and task narrative.

        Args:
            actor_id: The agent ID (e.g., "ACTOR_witness")
            task_id: The task narrative ID (e.g., "narrative_TASK_engine-SERVE_a7")

        Returns:
            True if link created successfully
        """
        if not self._connect():
            logger.warning(f"[AgentGraph] No graph connection, cannot link {actor_id} to {task_id}")
            return False

        try:
            import time
            cypher = """
            MATCH (a:Actor {id: $actor_id})
            MATCH (t:Narrative {id: $task_id})
            MERGE (a)-[r:assigned_to]->(t)
            SET r.created_at_s = $timestamp
            RETURN type(r)
            """
            result = self._graph_ops._query(cypher, {
                "actor_id": actor_id,
                "task_id": task_id,
                "timestamp": int(time.time()),
            })
            if result:
                logger.info(f"[AgentGraph] Linked {actor_id} assigned_to {task_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to link agent to task: {e}")
            return False

    def link_agent_to_issue(self, actor_id: str, issue_id: str) -> bool:
        """
        Create working_on link between agent and issue narrative.

        Args:
            actor_id: The agent ID (e.g., "ACTOR_witness")
            issue_id: The issue narrative ID (e.g., "narrative_PROBLEM_engine-MONOLITH_a7")

        Returns:
            True if link created successfully
        """
        if not self._connect():
            logger.warning(f"[AgentGraph] No graph connection, cannot link {actor_id} to {issue_id}")
            return False

        try:
            import time
            cypher = """
            MATCH (a:Actor {id: $actor_id})
            MATCH (i:Narrative {id: $issue_id})
            MERGE (a)-[r:working_on]->(i)
            SET r.created_at_s = $timestamp
            RETURN type(r)
            """
            result = self._graph_ops._query(cypher, {
                "actor_id": actor_id,
                "issue_id": issue_id,
                "timestamp": int(time.time()),
            })
            if result:
                logger.info(f"[AgentGraph] Linked {actor_id} working_on {issue_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to link agent to issue: {e}")
            return False

    def create_assignment_moment(
        self,
        actor_id: str,
        task_id: str,
        issue_ids: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Create a moment recording agent assignment to task/issues.

        Format: moment_ASSIGN-AGENT_{agent_name}_{timestamp_short}

        Creates:
        - Moment node with prose "Agent {name} assigned to task {task_id}"
        - expresses link from agent to moment
        - about link from moment to task
        - about links from moment to each issue

        Args:
            actor_id: The agent being assigned
            task_id: The task narrative ID
            issue_ids: Optional list of issue narrative IDs

        Returns:
            The moment ID if created, None on failure
        """
        if not self._connect():
            logger.warning(f"[AgentGraph] No graph connection, cannot create assignment moment")
            return None

        try:
            import time
            import hashlib

            timestamp = int(time.time())
            # Short hash for ID uniqueness
            ts_hash = hashlib.sha256(str(timestamp).encode()).hexdigest()[:4]

            # Extract agent name from ID
            agent_name = actor_id.replace("ACTOR_", "") if actor_id.startswith("ACTOR_") else actor_id

            moment_id = f"moment_ASSIGN-AGENT_{agent_name}_{ts_hash}"

            # Create the moment node
            create_cypher = """
            MERGE (m:Moment {id: $id})
            SET m.node_type = 'moment',
                m.type = 'ACTOR_assignment',
                m.prose = $prose,
                m.status = 'completed',
                m.actor_id = $actor_id,
                m.task_id = $task_id,
                m.created_at_s = $timestamp,
                m.updated_at_s = $timestamp
            RETURN m.id
            """
            self._graph_ops._query(create_cypher, {
                "id": moment_id,
                "prose": f"Agent {agent_name} assigned to task {task_id}",
                "actor_id": actor_id,
                "task_id": task_id,
                "timestamp": timestamp,
            })

            # Link: agent expresses moment
            expresses_cypher = """
            MATCH (a:Actor {id: $actor_id})
            MATCH (m:Moment {id: $moment_id})
            MERGE (a)-[r:expresses]->(m)
            SET r.created_at_s = $timestamp
            """
            self._graph_ops._query(expresses_cypher, {
                "actor_id": actor_id,
                "moment_id": moment_id,
                "timestamp": timestamp,
            })

            # Link: moment about task
            about_task_cypher = """
            MATCH (m:Moment {id: $moment_id})
            MATCH (t:Narrative {id: $task_id})
            MERGE (m)-[r:about]->(t)
            SET r.created_at_s = $timestamp
            """
            self._graph_ops._query(about_task_cypher, {
                "moment_id": moment_id,
                "task_id": task_id,
                "timestamp": timestamp,
            })

            # Link: moment about each issue
            if issue_ids:
                for issue_id in issue_ids:
                    about_issue_cypher = """
                    MATCH (m:Moment {id: $moment_id})
                    MATCH (i:Narrative {id: $issue_id})
                    MERGE (m)-[r:about]->(i)
                    SET r.created_at_s = $timestamp
                    """
                    self._graph_ops._query(about_issue_cypher, {
                        "moment_id": moment_id,
                        "issue_id": issue_id,
                        "timestamp": timestamp,
                    })

            logger.info(f"[AgentGraph] Created assignment moment: {moment_id}")
            return moment_id

        except Exception as e:
            logger.error(f"[AgentGraph] Failed to create assignment moment: {e}")
            return None

    def assign_agent_to_work(
        self,
        actor_id: str,
        task_id: str,
        issue_ids: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Full assignment: link agent to task/issues and create moment.

        This is the main entry point for agent assignment. It:
        1. Creates assigned_to link from agent to task
        2. Creates working_on links from agent to each issue
        3. Creates an assignment moment with all links

        Args:
            actor_id: The agent being assigned
            task_id: The task narrative ID
            issue_ids: Optional list of issue narrative IDs

        Returns:
            The moment ID if created, None on failure
        """
        # Link agent to task
        if task_id:
            self.link_agent_to_task(actor_id, task_id)

        # Link agent to each issue
        if issue_ids:
            for issue_id in issue_ids:
                self.link_agent_to_issue(actor_id, issue_id)

        # Create assignment moment and return its ID
        moment_id = self.create_assignment_moment(actor_id, task_id, issue_ids)
        return moment_id

    def upsert_issue_narrative(
        self,
        task_type: str,
        path: str,
        message: str,
        severity: str = "warning",
    ) -> Optional[str]:
        """
        Create or update an issue narrative node.

        Issue narratives track doctor issues as graph nodes so agents
        can be linked to them via working_on edges.

        ID format: narrative_PROBLEM_{task_type}_{path_hash_6}

        Args:
            task_type: Doctor issue type (e.g., "STALE_SYNC")
            path: File path of the issue
            message: Issue message/description
            severity: Issue severity (warning, error, info)

        Returns:
            The narrative ID if created/updated, None on failure
        """
        if not self._connect():
            logger.warning("[AgentGraph] No graph connection, cannot upsert issue narrative")
            return None

        try:
            import time
            import hashlib

            timestamp = int(time.time())
            # Create deterministic ID from task_type + path
            path_hash = hashlib.sha256(path.encode()).hexdigest()[:6]
            narrative_id = f"narrative_PROBLEM_{task_type}_{path_hash}"

            cypher = """
            MERGE (n:Narrative {id: $id})
            SET n.node_type = 'narrative',
                n.type = 'problem',
                n.task_type = $task_type,
                n.path = $path,
                n.message = $message,
                n.severity = $severity,
                n.status = 'open',
                n.updated_at_s = $timestamp
            ON CREATE SET n.created_at_s = $timestamp
            RETURN n.id
            """
            result = self._graph_ops._query(cypher, {
                "id": narrative_id,
                "task_type": task_type,
                "path": path,
                "message": message[:500],  # Truncate long messages
                "severity": severity,
                "timestamp": timestamp,
            })

            if result:
                logger.info(f"[AgentGraph] Upserted issue narrative: {narrative_id}")
                return narrative_id
            return None
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to upsert issue narrative: {e}")
            return None

    def upsert_task_narrative(
        self,
        task_type: str,
        content: str,
        name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create or update a task narrative node.

        Task narratives track work tasks as graph nodes so agents
        can be assigned to them via assigned_to edges.

        ID format: narrative_TASK_{task_type}_{content_hash_6}

        Args:
            task_type: Task type (e.g., "FIX_ISSUE", "IMPLEMENT")
            content: Task content/description
            name: Optional human-readable name

        Returns:
            The narrative ID if created/updated, None on failure
        """
        if not self._connect():
            logger.warning("[AgentGraph] No graph connection, cannot upsert task narrative")
            return None

        try:
            import time
            import hashlib

            timestamp = int(time.time())
            # Create deterministic ID from task_type + content
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:6]
            narrative_id = f"narrative_TASK_{task_type}_{content_hash}"

            cypher = """
            MERGE (n:Narrative {id: $id})
            SET n.node_type = 'narrative',
                n.type = 'task',
                n.task_type = $task_type,
                n.content = $content,
                n.name = $name,
                n.status = 'pending',
                n.updated_at_s = $timestamp
            ON CREATE SET n.created_at_s = $timestamp
            RETURN n.id
            """
            result = self._graph_ops._query(cypher, {
                "id": narrative_id,
                "task_type": task_type,
                "content": content[:1000],  # Truncate long content
                "name": name or f"{task_type} task",
                "timestamp": timestamp,
            })

            if result:
                logger.info(f"[AgentGraph] Upserted task narrative: {narrative_id}")
                return narrative_id
            return None
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to upsert task narrative: {e}")
            return None


def get_agent_template_path(name: str, target_dir: Path, provider: str = "claude") -> Optional[Path]:
    """
    Get the path to an agent's template file.

    Structure: .mind/actors/{name}/{PROVIDER}.md
    - CLAUDE.md for Claude
    - GEMINI.md for Gemini
    - AGENTS.md as fallback

    Args:
        name: Agent name (e.g., "witness")
        target_dir: Project root directory
        provider: Provider name (claude, gemini)

    Returns:
        Path to template file, or None if not found
    """
    provider_files = {
        "claude": "CLAUDE.md",
        "gemini": "GEMINI.md",
    }

    actor_dir = target_dir / ".mind" / "actors" / name.lower()
    if not actor_dir.exists():
        return None

    # Try provider-specific file first
    provider_file = provider_files.get(provider.lower(), "AGENTS.md")
    actor_path = actor_dir / provider_file
    if actor_path.exists():
        return actor_path

    # Fallback to AGENTS.md
    fallback_path = actor_dir / "AGENTS.md"
    if fallback_path.exists():
        return fallback_path

    return None


def load_agent_prompt(name: str, target_dir: Path, provider: str = "claude") -> Optional[str]:
    """
    Load the agent's base prompt/system prompt from template.

    Args:
        name: Agent name (e.g., "witness")
        target_dir: Project root directory
        provider: Provider name

    Returns:
        Agent prompt content, or None if not found
    """
    template_path = get_agent_template_path(name, target_dir, provider)

    if template_path and template_path.exists():
        return template_path.read_text()

    return None
