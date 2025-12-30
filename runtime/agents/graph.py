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
from typing import Dict, List, Optional, Any

from .postures import POSTURE_TO_AGENT_ID, DEFAULT_POSTURE

logger = logging.getLogger(__name__)


def _get_link_physics(nature: str) -> Dict[str, Any]:
    """
    Get physics properties for a link from nature string.
    Uses canonical implementation from runtime/inject.py
    """
    from runtime.inject import _nature_to_physics
    return _nature_to_physics(nature)


def _build_link_props(nature: str, timestamp: int) -> Dict[str, Any]:
    """Build link properties from nature string."""
    physics = _get_link_physics(nature)

    props = {"nature": nature, "updated_at_s": timestamp}

    # Copy physics floats
    for key in ["hierarchy", "permanence", "trust", "surprise", "energy", "weight"]:
        if key in physics and physics[key] is not None:
            props[key] = physics[key]

    # Handle polarity array
    if "polarity" in physics and physics["polarity"]:
        props["polarity_source"] = physics["polarity"][0]
        props["polarity_target"] = physics["polarity"][1]

    return props


def _link_set_clause(props: Dict[str, Any]) -> str:
    """Build SET clause for link properties."""
    return ", ".join(f"r.{k} = ${k}" for k in props.keys())


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

    def set_agent_space(self, agent_id: str, space_id: str) -> bool:
        """Set the agent's current active space and link them."""
        if not self._connect():
            return False

        try:
            timestamp = int(time.time())
            link_props = _build_link_props("occupies", timestamp)
            link_props["created_at_s"] = timestamp
            link_set = _link_set_clause(link_props)

            # Update agent's current_space and link to space
            cypher = f"""
            MATCH (a:Actor {{id: $agent_id}})
            MERGE (s:Space {{id: $space_id}})
            SET s.node_type = 'space',
                s.name = $space_name,
                s.updated_at_s = $timestamp,
                s.created_at_s = coalesce(s.created_at_s, $timestamp)
            SET a.current_space = $space_id, a.updated_at_s = $timestamp
            MERGE (a)-[r:link]->(s)
            SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                {link_set}
            RETURN a.id
            """
            params = {
                "agent_id": agent_id,
                "space_id": space_id,
                "space_name": space_id.replace("space_", "").replace("_", "/"),
                "timestamp": timestamp,
                **link_props,
            }
            self._graph_ops._query(cypher, params)
            logger.info(f"[AgentGraph] Set {agent_id} active in {space_id}")
            return True
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to set agent space: {e}")
            return False

    def link_task_to_space(self, task_id: str, space_id: str) -> bool:
        """Link a task narrative to its space."""
        if not self._connect():
            return False

        try:
            timestamp = int(time.time())
            # Get physics from nature - space includes task
            link_props = _build_link_props("includes", timestamp)
            link_props["created_at_s"] = timestamp

            # Build SET clause for link properties
            link_set = _link_set_clause(link_props)

            cypher = f"""
            MATCH (t:Narrative {{id: $task_id}})
            MERGE (s:Space {{id: $space_id}})
            SET s.node_type = 'space',
                s.name = $space_name,
                s.updated_at_s = $timestamp,
                s.created_at_s = coalesce(s.created_at_s, $timestamp)
            MERGE (s)-[r:link]->(t)
            SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                {link_set}
            RETURN t.id
            """
            params = {
                "task_id": task_id,
                "space_id": space_id,
                "space_name": space_id.replace("space_", "").replace("_", "/"),
                "timestamp": timestamp,
                **link_props,
            }
            self._graph_ops._query(cypher, params)
            logger.info(f"[AgentGraph] Linked task {task_id} to {space_id}")
            return True
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to link task to space: {e}")
            return False

    def get_task_space(self, task_id: str) -> Optional[str]:
        """
        Get the space (module) for a task by following link relations:
        1. task → link (nature: implements) → narrative → link (nature: includes) ← space
        2. task.path or task.module as fallback
        """
        if not self._connect():
            return None

        try:
            # Follow links through narratives to find space
            cypher = """
            MATCH (t:Narrative {id: $task_id})
            OPTIONAL MATCH (t)-[:link {nature: 'implements'}]->(n:Narrative)<-[:link {nature: 'includes'}]-(s:Space)
            OPTIONAL MATCH (t)-[:link {nature: 'implements'}]->(n2:Narrative)
            RETURN s.id as space_id,
                   n2.path as impl_path,
                   t.path as task_path,
                   t.module as task_module
            """
            result = self._graph_ops._query(cypher, {"task_id": task_id})
            if result and result[0]:
                # Priority: direct space link > impl path > task path > module
                space_id = result[0][0]
                if space_id:
                    return space_id

                impl_path = result[0][1]
                task_path = result[0][2]
                task_module = result[0][3]

                # Derive space from best available path
                path = impl_path or task_path or task_module
                if path:
                    from pathlib import Path as P
                    path_parts = P(str(path)).parts[:2]
                    if path_parts:
                        return f"space_{'_'.join(path_parts)}"
            return None
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to get task space: {e}")
            return None

    def get_agent_space(self, agent_id: str) -> Optional[str]:
        """Get the agent's current active space."""
        if not self._connect():
            return None

        try:
            cypher = """
            MATCH (a:Actor {id: $agent_id})
            RETURN a.current_space
            """
            result = self._graph_ops._query(cypher, {"agent_id": agent_id})
            if result and result[0]:
                return result[0][0]
            return None
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to get agent space: {e}")
            return None

    def link_agent_to_task(self, agent_id: str, task_id: str) -> bool:
        """Create claims link between agent and task narrative."""
        if not self._connect():
            return False

        try:
            timestamp = int(time.time())
            # Agent claims task (ownership semantics)
            link_props = _build_link_props("claims", timestamp)
            link_props["created_at_s"] = timestamp
            link_set = _link_set_clause(link_props)

            cypher = f"""
            MATCH (a:Actor {{id: $agent_id}})
            MATCH (t:Narrative {{id: $task_id}})
            MERGE (a)-[r:link]->(t)
            SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                {link_set}
            RETURN type(r)
            """
            result = self._graph_ops._query(cypher, {
                "agent_id": agent_id,
                "task_id": task_id,
                "timestamp": timestamp,
                **link_props,
            })
            if result:
                logger.info(f"[AgentGraph] Linked {agent_id} claims {task_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to link agent to task: {e}")
            return False

    def link_agent_to_problem(self, agent_id: str, problem_id: str) -> bool:
        """Create resolves link between agent and problem narrative."""
        if not self._connect():
            return False

        try:
            timestamp = int(time.time())
            # Agent resolves problem (action semantics)
            link_props = _build_link_props("resolves", timestamp)
            link_props["created_at_s"] = timestamp
            link_set = _link_set_clause(link_props)

            cypher = f"""
            MATCH (a:Actor {{id: $agent_id}})
            MATCH (p:Narrative {{id: $problem_id}})
            MERGE (a)-[r:link]->(p)
            SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                {link_set}
            RETURN type(r)
            """
            result = self._graph_ops._query(cypher, {
                "agent_id": agent_id,
                "problem_id": problem_id,
                "timestamp": timestamp,
                **link_props,
            })
            if result:
                logger.info(f"[AgentGraph] Linked {agent_id} resolves {problem_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to link agent to problem: {e}")
            return False

    def get_task_problem_type(self, task_id: str) -> Optional[str]:
        """Get the problem type associated with a task."""
        if not self._connect():
            return None

        try:
            cypher = """
            MATCH (t:Narrative {id: $task_id})
            RETURN t.problem_type as problem_type
            """
            result = self._graph_ops._query(cypher, {"task_id": task_id})
            if result:
                row = result[0]
                return row.get("problem_type")
            return None
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to get task problem type: {e}")
            return None

    def create_assignment_moment(
        self,
        agent_id: str,
        task_id: str,
        problem_ids: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Create a moment recording agent assignment to task/problems.
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

            # Link: agent expresses moment (with physics)
            expresses_props = _build_link_props("expresses", timestamp)
            expresses_props["created_at_s"] = timestamp
            expresses_set = _link_set_clause(expresses_props)
            self._graph_ops._query(f"""
            MATCH (a:Actor {{id: $agent_id}})
            MATCH (m:Moment {{id: $moment_id}})
            MERGE (a)-[r:link]->(m)
            SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                {expresses_set}
            """, {
                "agent_id": agent_id,
                "moment_id": moment_id,
                "timestamp": timestamp,
                **expresses_props,
            })

            # Link: moment about task (with physics)
            concerns_props = _build_link_props("concerns", timestamp)
            concerns_props["created_at_s"] = timestamp
            concerns_set = _link_set_clause(concerns_props)
            self._graph_ops._query(f"""
            MATCH (m:Moment {{id: $moment_id}})
            MATCH (t:Narrative {{id: $task_id}})
            MERGE (m)-[r:link]->(t)
            SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                {concerns_set}
            """, {
                "moment_id": moment_id,
                "task_id": task_id,
                "timestamp": timestamp,
                **concerns_props,
            })

            # Link: moment about each problem (with physics)
            if problem_ids:
                for problem_id in problem_ids:
                    self._graph_ops._query(f"""
                    MATCH (m:Moment {{id: $moment_id}})
                    MATCH (p:Narrative {{id: $problem_id}})
                    MERGE (m)-[r:link]->(p)
                    SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                        {concerns_set}
                    """, {
                        "moment_id": moment_id,
                        "problem_id": problem_id,
                        "timestamp": timestamp,
                        **concerns_props,
                    })

            logger.info(f"[AgentGraph] Created assignment moment: {moment_id}")
            return moment_id

        except Exception as e:
            logger.error(f"[AgentGraph] Failed to create assignment moment: {e}")
            return None

    def get_actor_last_moment(self, agent_id: str) -> Optional[str]:
        """Get the most recent moment expressed by an actor."""
        if not self._connect():
            return None

        try:
            cypher = """
            MATCH (a:Actor {id: $agent_id})-[:expresses]->(m:Moment)
            RETURN m.id
            ORDER BY m.created_at_s DESC
            LIMIT 1
            """
            result = self._graph_ops._query(cypher, {"agent_id": agent_id})
            if result and result[0]:
                return result[0][0]
            return None
        except Exception as e:
            logger.warning(f"[AgentGraph] Failed to get last moment: {e}")
            return None

    def create_moment(
        self,
        agent_id: str,
        moment_type: str,
        prose: str,
        about_ids: Optional[List[str]] = None,
        space_id: Optional[str] = None,
        extra_props: Optional[Dict] = None,
    ) -> Optional[str]:
        """
        Create a moment node linked to actor, space, and chained to previous moment.

        Args:
            agent_id: Actor creating this moment
            moment_type: Type of moment (e.g., 'task_created', 'problem_detected')
            prose: Human-readable description
            about_ids: Node IDs this moment is about
            space_id: Space (module/project) where this moment occurs
            extra_props: Additional properties for the moment

        Returns:
            Moment ID if created, None on failure
        """
        if not self._connect():
            return None

        try:
            timestamp = int(time.time())
            ts_hash = hashlib.sha256(str(timestamp).encode()).hexdigest()[:4]
            agent_name = agent_id.replace("agent_", "") if agent_id.startswith("agent_") else agent_id
            moment_id = f"moment_{moment_type.upper()}_{agent_name}_{ts_hash}"

            # Get previous moment for chaining
            prev_moment_id = self.get_actor_last_moment(agent_id)

            # Create moment node
            props = {
                "id": moment_id,
                "node_type": "moment",
                "type": moment_type,
                "prose": prose,
                "agent_id": agent_id,
                "created_at_s": timestamp,
                "updated_at_s": timestamp,
            }
            if extra_props:
                props.update(extra_props)

            prop_sets = ", ".join([f"m.{k} = ${k}" for k in props.keys()])
            create_cypher = f"""
            MERGE (m:Moment {{id: $id}})
            SET {prop_sets}
            RETURN m.id
            """
            self._graph_ops._query(create_cypher, props)

            # Link: actor expresses moment (with physics)
            expresses_props = _build_link_props("expresses", timestamp)
            expresses_props["created_at_s"] = timestamp
            expresses_set = _link_set_clause(expresses_props)
            self._graph_ops._query(f"""
            MATCH (a:Actor {{id: $agent_id}})
            MATCH (m:Moment {{id: $moment_id}})
            MERGE (a)-[r:link]->(m)
            SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                {expresses_set}
            """, {"agent_id": agent_id, "moment_id": moment_id, "timestamp": timestamp, **expresses_props})

            # Link: previous moment → this moment (chain with physics)
            if prev_moment_id:
                follows_props = _build_link_props("precedes", timestamp)
                follows_props["created_at_s"] = timestamp
                follows_set = _link_set_clause(follows_props)
                self._graph_ops._query(f"""
                MATCH (prev:Moment {{id: $prev_id}})
                MATCH (curr:Moment {{id: $curr_id}})
                MERGE (prev)-[r:link]->(curr)
                SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                    {follows_set}
                """, {"prev_id": prev_moment_id, "curr_id": moment_id, "timestamp": timestamp, **follows_props})

            # Link: moment about target nodes (with physics)
            if about_ids:
                concerns_props = _build_link_props("concerns", timestamp)
                concerns_props["created_at_s"] = timestamp
                concerns_set = _link_set_clause(concerns_props)
                for about_id in about_ids:
                    self._graph_ops._query(f"""
                    MATCH (m:Moment {{id: $moment_id}})
                    MATCH (n {{id: $about_id}})
                    MERGE (m)-[r:link]->(n)
                    SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                        {concerns_set}
                    """, {"moment_id": moment_id, "about_id": about_id, "timestamp": timestamp, **concerns_props})

            # Link: space includes moment (with physics)
            if space_id:
                includes_props = _build_link_props("includes", timestamp)
                includes_props["created_at_s"] = timestamp
                includes_set = _link_set_clause(includes_props)
                self._graph_ops._query(f"""
                MERGE (s:Space {{id: $space_id}})
                SET s.node_type = 'space',
                    s.name = $space_name,
                    s.updated_at_s = $timestamp,
                    s.created_at_s = coalesce(s.created_at_s, $timestamp)
                WITH s
                MATCH (m:Moment {{id: $moment_id}})
                MERGE (s)-[r:link]->(m)
                SET r.created_at_s = coalesce(r.created_at_s, $timestamp),
                    {includes_set}
                """, {
                    "moment_id": moment_id,
                    "space_id": space_id,
                    "space_name": space_id.replace("space_", "").replace("_", "/"),
                    "timestamp": timestamp,
                    **includes_props,
                })

            logger.info(f"[AgentGraph] Created moment: {moment_id} (follows: {prev_moment_id or 'none'}, space: {space_id or 'none'})")
            return moment_id

        except Exception as e:
            logger.error(f"[AgentGraph] Failed to create moment: {e}")
            return None

    def assign_agent_to_work(
        self,
        agent_id: str,
        task_id: str,
        problem_ids: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Full assignment: link agent to task/problems and create moment.
        """
        if task_id:
            self.link_agent_to_task(agent_id, task_id)

        if problem_ids:
            for problem_id in problem_ids:
                self.link_agent_to_problem(agent_id, problem_id)

        # Use new create_moment with chaining
        about_ids = [task_id] if task_id else []
        if problem_ids:
            about_ids.extend(problem_ids)

        moment_id = self.create_moment(
            agent_id=agent_id,
            moment_type="agent_assignment",
            prose=f"Agent {agent_id} assigned to task {task_id}",
            about_ids=about_ids,
            extra_props={"task_id": task_id, "status": "completed"},
        )
        return moment_id

    def upsert_problem_narrative(
        self,
        problem_type: str,
        path: str,
        message: str,
        severity: str = "warning",
    ) -> Optional[str]:
        """Create or update a problem narrative node."""
        if not self._connect():
            return None

        try:
            timestamp = int(time.time())
            path_hash = hashlib.sha256(path.encode()).hexdigest()[:6]
            narrative_id = f"narrative_issue_{problem_type}_{path_hash}"

            cypher = """
            MERGE (n:Narrative {id: $id})
            SET n.node_type = 'narrative',
                n.type = 'problem',
                n.problem_type = $problem_type,
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
                "problem_type": problem_type,
                "path": path,
                "message": message[:500],
                "severity": severity,
                "timestamp": timestamp,
            })

            if result:
                logger.info(f"[AgentGraph] Upserted problem narrative: {narrative_id}")
                return narrative_id
            return None
        except Exception as e:
            logger.error(f"[AgentGraph] Failed to upsert problem narrative: {e}")
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
