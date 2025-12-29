"""
Agent Graph Operations

Query and manage work agents in the mind graph.
Agents are Actor nodes with posture-based selection.

The 10 agents (by posture):
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
- running: Agent currently executing

DOCS: docs/agents/PATTERNS_Agent_System.md
"""

import logging
import time
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .postures import POSTURE_TO_AGENT_ID, DEFAULT_POSTURE

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """Information about an agent from the graph."""
    id: str
    name: str
    posture: str
    status: str
    energy: float = 0.0
    weight: float = 1.0


class AgentGraph:
    """
    Query and manage work agents from the mind graph.

    Agents are Actor nodes with:
    - id: agent_{posture} (e.g., agent_witness)
    - name: The posture name (e.g., witness)
    - type: agent
    - status: ready | running
    """

    def __init__(
        self,
        graph_name: str = None,
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

            self._graph_ops = GraphOps(graph_name=self.graph_name)
            self._graph_queries = GraphQueries(graph_name=self.graph_name)
            self._connected = True
            self.graph_name = self._graph_ops.graph_name
            logger.info(f"[AgentGraph] Connected to {self.graph_name}")
            return True
        except Exception as e:
            logger.warning(f"[AgentGraph] No graph connection: {e}")
            return False

    def ensure_agents_exist(self) -> bool:
        """
        Ensure all 10 agents exist in the graph.
        Creates them if they don't exist.
        """
        if not self._connect():
            return False

        try:
            timestamp = int(time.time())

            for posture, agent_id in POSTURE_TO_AGENT_ID.items():
                cypher = f"""
                MATCH (a:Actor {{id: '{agent_id}'}})
                RETURN a.id
                """
                result = self._graph_ops._query(cypher)

                if not result:
                    props = {
                        "id": agent_id,
                        "name": posture,
                        "node_type": "actor",
                        "type": "agent",
                        "status": "ready",
                        "description": f"Work agent with {posture} posture",
                        "weight": 1.0,
                        "energy": 0.0,
                        "created_at_s": timestamp,
                        "updated_at_s": timestamp,
                    }

                    create_cypher = """
                    MERGE (a:Actor {id: $id})
                    SET a += $props
                    """
                    self._graph_ops._query(create_cypher, {"id": agent_id, "props": props})
                    logger.info(f"[AgentGraph] Created agent: {agent_id}")

            return True
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to ensure agents exist: {e}")
            return False

    def get_all_agents(self) -> List[AgentInfo]:
        """Get all agents from the graph."""
        if not self._connect():
            return self._get_fallback_agents()

        try:
            cypher = """
            MATCH (a:Actor)
            WHERE a.type = 'agent'
            RETURN a.id, a.name, a.status, a.energy, a.weight
            ORDER BY a.name
            """
            rows = self._graph_ops._query(cypher)

            agents = []
            for row in rows:
                if len(row) >= 3:
                    agent_id = row[0]
                    name = row[1]
                    status = row[2] or "ready"
                    energy = row[3] if len(row) > 3 else 0.0
                    weight = row[4] if len(row) > 4 else 1.0

                    agents.append(AgentInfo(
                        id=agent_id,
                        name=name,
                        posture=name,
                        status=status,
                        energy=energy or 0.0,
                        weight=weight or 1.0,
                    ))

            return agents if agents else self._get_fallback_agents()
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to get agents: {e}")
            return self._get_fallback_agents()

    def _get_fallback_agents(self) -> List[AgentInfo]:
        """Return fallback agent list when graph unavailable."""
        return [
            AgentInfo(id=agent_id, name=posture, posture=posture, status="ready")
            for posture, agent_id in POSTURE_TO_AGENT_ID.items()
        ]

    def get_available_agents(self) -> List[AgentInfo]:
        """Get agents that are available (status=ready)."""
        all_agents = self.get_all_agents()
        return [a for a in all_agents if a.status == "ready"]

    def get_running_agents(self) -> List[AgentInfo]:
        """Get agents that are currently running."""
        all_agents = self.get_all_agents()
        return [a for a in all_agents if a.status == "running"]

    def select_agent_for_problem(self, problem_type: str) -> Optional[str]:
        """
        Select the best agent for a problem type.
        Matches problem type to posture, then finds an available agent.
        """
        from .postures import PROBLEM_TO_POSTURE

        posture = PROBLEM_TO_POSTURE.get(problem_type, DEFAULT_POSTURE)
        preferred_agent_id = POSTURE_TO_AGENT_ID.get(posture)

        available = self.get_available_agents()

        if not available:
            logger.warning("[AgentGraph] All agents are busy")
            return None

        for agent in available:
            if agent.id == preferred_agent_id:
                return agent.id

        available.sort(key=lambda a: a.energy, reverse=True)
        return available[0].id

    def get_agent_posture(self, agent_id: str) -> str:
        """Get the posture for an agent ID."""
        if agent_id.startswith("agent_"):
            return agent_id[6:]
        return DEFAULT_POSTURE

    def set_agent_running(self, agent_id: str) -> bool:
        """Mark an agent as running."""
        if not self._connect():
            logger.warning(f"[AgentGraph] No graph connection, cannot set {agent_id} running")
            return False

        try:
            cypher = """
            MATCH (a:Actor {id: $id})
            SET a.status = 'running', a.updated_at_s = $timestamp
            RETURN a.id
            """
            result = self._graph_ops._query(cypher, {
                "id": agent_id,
                "timestamp": int(time.time()),
            })

            if result:
                logger.info(f"[AgentGraph] Agent {agent_id} now running")
                return True
            else:
                logger.warning(f"[AgentGraph] Agent {agent_id} not found")
                return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to set {agent_id} running: {e}")
            return False

    def set_agent_ready(self, agent_id: str) -> bool:
        """Mark an agent as ready (available)."""
        if not self._connect():
            logger.warning(f"[AgentGraph] No graph connection, cannot set {agent_id} ready")
            return False

        try:
            cypher = """
            MATCH (a:Actor {id: $id})
            SET a.status = 'ready', a.updated_at_s = $timestamp
            RETURN a.id
            """
            result = self._graph_ops._query(cypher, {
                "id": agent_id,
                "timestamp": int(time.time()),
            })

            if result:
                logger.info(f"[AgentGraph] Agent {agent_id} now ready")
                return True
            else:
                logger.warning(f"[AgentGraph] Agent {agent_id} not found")
                return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to set {agent_id} ready: {e}")
            return False

    def boost_agent_energy(self, agent_id: str, amount: float = 0.1) -> bool:
        """Boost an agent's energy (used for prioritization)."""
        if not self._connect():
            return False

        try:
            cypher = """
            MATCH (a:Actor {id: $id})
            SET a.energy = coalesce(a.energy, 0) + $amount
            RETURN a.id
            """
            self._graph_ops._query(cypher, {"id": agent_id, "amount": amount})
            return True
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to boost {agent_id} energy: {e}")
            return False

    def link_agent_to_task(self, agent_id: str, task_id: str) -> bool:
        """Create assigned_to link between agent and task narrative."""
        if not self._connect():
            return False

        try:
            cypher = """
            MATCH (a:Actor {id: $agent_id})
            MATCH (t:Narrative {id: $task_id})
            MERGE (a)-[r:assigned_to]->(t)
            SET r.created_at_s = $timestamp
            RETURN type(r)
            """
            result = self._graph_ops._query(cypher, {
                "agent_id": agent_id,
                "task_id": task_id,
                "timestamp": int(time.time()),
            })
            if result:
                logger.info(f"[AgentGraph] Linked {agent_id} assigned_to {task_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to link agent to task: {e}")
            return False

    def link_agent_to_issue(self, agent_id: str, issue_id: str) -> bool:
        """Create working_on link between agent and issue narrative."""
        if not self._connect():
            return False

        try:
            cypher = """
            MATCH (a:Actor {id: $agent_id})
            MATCH (i:Narrative {id: $issue_id})
            MERGE (a)-[r:working_on]->(i)
            SET r.created_at_s = $timestamp
            RETURN type(r)
            """
            result = self._graph_ops._query(cypher, {
                "agent_id": agent_id,
                "issue_id": issue_id,
                "timestamp": int(time.time()),
            })
            if result:
                logger.info(f"[AgentGraph] Linked {agent_id} working_on {issue_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to link agent to issue: {e}")
            return False

    def get_task_problem_type(self, task_id: str) -> Optional[str]:
        """Get the problem type associated with a task."""
        if not self._connect():
            return None

        try:
            cypher = """
            MATCH (t:Narrative {id: $task_id})
            RETURN t.problem_type as problem_type, t.issue_type as issue_type
            """
            result = self._graph_ops._query(cypher, {"task_id": task_id})
            if result:
                row = result[0]
                # Try problem_type first, fall back to issue_type (legacy)
                return row.get("problem_type") or row.get("issue_type")
            return None
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to get task problem type: {e}")
            return None

    def create_assignment_moment(
        self,
        agent_id: str,
        task_id: str,
        issue_ids: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Create a moment recording agent assignment to task/issues.
        """
        if not self._connect():
            return None

        try:
            timestamp = int(time.time())
            ts_hash = hashlib.sha256(str(timestamp).encode()).hexdigest()[:4]
            agent_name = agent_id.replace("agent_", "") if agent_id.startswith("agent_") else agent_id
            moment_id = f"moment_ASSIGN-AGENT_{agent_name}_{ts_hash}"

            create_cypher = """
            MERGE (m:Moment {id: $id})
            SET m.node_type = 'moment',
                m.type = 'agent_assignment',
                m.prose = $prose,
                m.status = 'completed',
                m.agent_id = $agent_id,
                m.task_id = $task_id,
                m.created_at_s = $timestamp,
                m.updated_at_s = $timestamp
            RETURN m.id
            """
            self._graph_ops._query(create_cypher, {
                "id": moment_id,
                "prose": f"Agent {agent_name} assigned to task {task_id}",
                "agent_id": agent_id,
                "task_id": task_id,
                "timestamp": timestamp,
            })

            # Link: agent expresses moment
            expresses_cypher = """
            MATCH (a:Actor {id: $agent_id})
            MATCH (m:Moment {id: $moment_id})
            MERGE (a)-[r:expresses]->(m)
            SET r.created_at_s = $timestamp
            """
            self._graph_ops._query(expresses_cypher, {
                "agent_id": agent_id,
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
        agent_id: str,
        task_id: str,
        issue_ids: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Full assignment: link agent to task/issues and create moment.
        """
        if task_id:
            self.link_agent_to_task(agent_id, task_id)

        if issue_ids:
            for issue_id in issue_ids:
                self.link_agent_to_issue(agent_id, issue_id)

        moment_id = self.create_assignment_moment(agent_id, task_id, issue_ids)
        return moment_id

    def upsert_issue_narrative(
        self,
        issue_type: str,
        path: str,
        message: str,
        severity: str = "warning",
    ) -> Optional[str]:
        """Create or update an issue narrative node."""
        if not self._connect():
            return None

        try:
            timestamp = int(time.time())
            path_hash = hashlib.sha256(path.encode()).hexdigest()[:6]
            narrative_id = f"narrative_ISSUE_{issue_type}_{path_hash}"

            cypher = """
            MERGE (n:Narrative {id: $id})
            SET n.node_type = 'narrative',
                n.type = 'issue',
                n.issue_type = $issue_type,
                n.path = $path,
                n.message = $message,
                n.severity = $severity,
                n.status = 'open',
                n.updated_at_s = $timestamp,
                n.created_at_s = coalesce(n.created_at_s, $timestamp)
            RETURN n.id
            """
            result = self._graph_ops._query(cypher, {
                "id": narrative_id,
                "issue_type": issue_type,
                "path": path,
                "message": message[:500],
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
        """Create or update a task narrative node."""
        if not self._connect():
            return None

        try:
            timestamp = int(time.time())
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
                n.updated_at_s = $timestamp,
                n.created_at_s = coalesce(n.created_at_s, $timestamp)
            RETURN n.id
            """
            result = self._graph_ops._query(cypher, {
                "id": narrative_id,
                "task_type": task_type,
                "content": content[:1000],
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


def get_agent_template_path(posture: str, target_dir: Path, provider: str = "claude") -> Optional[Path]:
    """
    Get the path to an agent's template file.
    Checks: .mind/actors/ACTOR_{Posture}.md
    """
    posture_capitalized = posture.capitalize()
    actor_path = target_dir / ".mind" / "actors" / f"ACTOR_{posture_capitalized}.md"
    if actor_path.exists():
        return actor_path

    return None


def load_agent_prompt(posture: str, target_dir: Path, provider: str = "claude") -> Optional[str]:
    """Load the agent's base prompt/system prompt from template."""
    template_path = get_agent_template_path(posture, target_dir, provider)

    if template_path and template_path.exists():
        return template_path.read_text()

    return None
