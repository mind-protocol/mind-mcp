"""Inject agent actors into the graph during init."""

from pathlib import Path


def inject_agents(target_dir: Path, graph_name: str) -> None:
    """
    Ensure all work agents exist in the graph.

    Creates 10 agent actors (one per posture) if they don't exist:
    - agent_witness, agent_groundwork, agent_architect
    - agent_fixer, agent_scout, agent_keeper
    - agent_weaver, agent_voice, agent_herald, agent_steward
    """
    try:
        from runtime.agents.graph import AgentGraph

        agent_graph = AgentGraph(graph_name=graph_name)
        success = agent_graph.ensure_agents_exist()

        if success:
            # Count created agents
            agents = agent_graph.get_all_agents()
            print(f"✓ Agents: {len(agents)} agents ready")
        else:
            print("○ Agents: skipped (no graph connection)")

    except ImportError as e:
        print(f"⚠ Agent injection skipped: {e}")
    except Exception as e:
        print(f"⚠ Agent injection failed: {e}")
