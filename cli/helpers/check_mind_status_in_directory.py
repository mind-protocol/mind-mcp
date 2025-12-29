"""Check mind status in a directory."""

import os
from pathlib import Path

import yaml

from .get_mcp_version_from_config import get_mcp_version


def check_mind_status(target_dir: Path) -> int:
    """Show mind status. Returns 0 if ok, 1 if not initialized."""
    mind_dir = target_dir / ".mind"

    if not mind_dir.exists():
        print(f"No .mind/ found in {target_dir}")
        print("Run: mind init")
        return 1

    print(f"mind: {target_dir.name} (v{get_mcp_version()})")
    print()

    # Core files
    for f in ["PRINCIPLES.md", "FRAMEWORK.md", "config.yaml", "database_config.yaml"]:
        status = "✓" if (mind_dir / f).exists() else "✗"
        print(f"  {f}: {status}")

    # State
    state = mind_dir / "state"
    if state.exists():
        count = len(list(state.glob("SYNC_*.md")))
        print(f"  state/: {count} SYNC files")

    # Skills
    skills = mind_dir / "skills"
    if skills.exists():
        count = len(list(skills.glob("SKILL_*.md")))
        print(f"  skills/: {count} skills")

    # Runtime
    runtime = mind_dir / "runtime"
    if runtime.exists():
        py_count = sum(1 for _ in runtime.rglob("*.py"))
        print(f"  runtime/: {py_count} Python files")

        modules = ["physics", "graph", "connectome", "infrastructure", "traversal"]
        present = [m for m in modules if (runtime / m).exists()]
        if present:
            print(f"    modules: {', '.join(present)}")
    else:
        print("  runtime/: ✗")

    # Embedding config check
    _check_embedding_config(mind_dir)

    # Graph schema health check
    _check_graph_health(mind_dir)

    return 0


def _check_embedding_config(mind_dir: Path) -> None:
    """Check and display embedding configuration status."""
    config_path = mind_dir / "database_config.yaml"
    if not config_path.exists():
        return

    try:
        config = yaml.safe_load(config_path.read_text())
        stored = config.get("embedding", {})
        if not stored:
            return

        stored_provider = stored.get("provider", "local")
        stored_model = stored.get("model", "unknown")
        stored_dim = stored.get("dimension", 768)

        # Get current config from environment
        current_provider = os.getenv("EMBEDDING_PROVIDER", "local")
        if current_provider == "openai":
            current_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
            current_dim = {"text-embedding-3-small": 1536, "text-embedding-3-large": 3072}.get(current_model, 3072)
        else:
            current_model = "all-mpnet-base-v2"
            current_dim = 768

        print()
        print(f"  embedding (stored): {stored_provider}/{stored_model} ({stored_dim}d)")
        print(f"  embedding (current): {current_provider}/{current_model} ({current_dim}d)")

        if stored_dim != current_dim:
            print()
            print(f"  ⚠️  DIMENSION MISMATCH: stored={stored_dim}d, current={current_dim}d")
            print(f"     Vector indexes won't work. Options:")
            print(f"     1. Revert to {stored_provider} (unset EMBEDDING_PROVIDER)")
            print(f"     2. Delete graph and run 'mind init' again")
            print(f"     3. Re-embed all nodes with new provider")

    except Exception:
        pass  # Silently ignore config read errors


def _check_graph_health(mind_dir: Path) -> None:
    """Check graph schema health."""
    try:
        # Import from runtime
        import sys
        runtime_path = str(mind_dir.parent)
        if runtime_path not in sys.path:
            sys.path.insert(0, runtime_path)

        from runtime.physics.graph.graph_schema_cleanup import get_schema_health

        health = get_schema_health()

        print()
        if health.get("error"):
            print(f"  graph: Error - {health['error']}")
            return

        total = health["total_nodes"]
        invalid = health["null_node_type"] + health["invalid_node_type"] + health["null_id"]

        if invalid == 0:
            print(f"  graph: ✓ {total} nodes (schema compliant)")
        else:
            print(f"  graph: ⚠️  {invalid} invalid nodes of {total} total")
            if health["null_node_type"] > 0:
                print(f"    - {health['null_node_type']} with null node_type")
            if health["invalid_node_type"] > 0:
                print(f"    - {health['invalid_node_type']} with invalid node_type")
            if health["null_id"] > 0:
                print(f"    - {health['null_id']} with null id")
            print("    Run: mind doctor --fix to clean up")

        # Show node type breakdown
        by_type = health.get("by_type", {})
        if by_type:
            parts = [f"{k}: {v}" for k, v in sorted(by_type.items())]
            print(f"    types: {', '.join(parts)}")

    except ImportError:
        pass  # Runtime not available
    except Exception as e:
        print(f"  graph: Check failed - {e}")
