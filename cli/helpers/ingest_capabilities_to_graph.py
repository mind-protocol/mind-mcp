"""Ingest capabilities into the graph during init.

Wrapper around runtime/ingest/capabilities.py for CLI use.
"""

from pathlib import Path


def ingest_capabilities(target_dir: Path, graph_name: str) -> None:
    """
    Ingest capabilities into the graph.

    Uses the runtime ingest module which handles:
    - Synthesis generation for embedding
    - Change detection (only updates if synthesis differs)
    - Proper graph structure with IMPLEMENTS links
    """
    try:
        from runtime.ingest import ingest_capabilities as _ingest

        stats = _ingest(target_dir, graph_name=graph_name)

        caps = stats.get("capabilities", 0)
        changed = stats.get("nodes_changed", 0)
        unchanged = stats.get("nodes_unchanged", 0)
        links = stats.get("links_created", 0)

        if changed > 0:
            print(f"✓ Capabilities: {caps} caps, {changed} changed, {unchanged} unchanged, {links} links")
        elif unchanged > 0:
            print(f"○ Capabilities: {caps} caps, {unchanged} unchanged (no re-embedding needed)")
        else:
            print("○ No capability nodes found")

    except Exception as e:
        print(f"⚠ Capability ingest skipped: {e}")
