"""Inject agent actors into the graph during init.

Wrapper around runtime/ingest/actors.py for CLI use.
"""

from pathlib import Path


def inject_agents(target_dir: Path, graph_name: str) -> None:
    """
    Inject agents from .mind/actors/ into the graph.

    Uses the runtime ingest module which handles:
    - Synthesis generation for embedding
    - Change detection (only updates if synthesis differs)
    - Proper graph structure with Actor nodes
    """
    try:
        from runtime.ingest import ingest_actors

        stats = ingest_actors(target_dir, graph_name=graph_name)

        actors = stats.get("actors", 0)
        created = stats.get("created", 0)
        updated = stats.get("updated", 0)
        unchanged = stats.get("unchanged", 0)

        if created > 0 and updated > 0:
            print(f"✓ Agents: {actors} agents ({created} created, {updated} updated)")
        elif created > 0:
            print(f"✓ Agents: {created} agents created")
        elif updated > 0:
            print(f"✓ Agents: {updated} agents updated")
        elif unchanged > 0:
            print(f"○ Agents: {actors} agents unchanged (no re-embedding needed)")
        else:
            print("○ Agents: no .mind/actors/ found")

    except Exception as e:
        print(f"⚠ Agent injection skipped: {e}")
