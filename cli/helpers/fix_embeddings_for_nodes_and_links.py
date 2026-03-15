"""Fix embeddings: add missing or re-embed mismatched dimensions."""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

import yaml


def fix_embeddings(target_dir: Path, dry_run: bool = False) -> Tuple[int, int, int]:
    """
    Fix embeddings for nodes and links.

    Finds and re-embeds:
    - Nodes/links without embeddings
    - Nodes/links with wrong dimension

    Args:
        target_dir: Project directory
        dry_run: If True, only report what would be fixed

    Returns:
        (missing_count, mismatch_count, fixed_count)
    """
    config = _load_config(target_dir)
    if not config:
        print("No .mind/database_config.yaml found")
        return 0, 0, 0

    # Get expected dimension from current provider
    expected_dim = _get_current_dimension()
    stored_dim = config.get("embedding", {}).get("dimension", expected_dim)

    print(f"Expected dimension: {expected_dim}d")
    print(f"Stored dimension: {stored_dim}d")

    if expected_dim != stored_dim:
        print(f"\n⚠️  Dimension change: {stored_dim}d → {expected_dim}d")
        print("All existing embeddings will be replaced.\n")

    # Connect to database
    db_config = config.get("database", {})
    backend = db_config.get("backend", "falkordb")

    if backend == "falkordb":
        missing, mismatch, fixed = _fix_falkordb(
            db_config.get("falkordb", {}),
            expected_dim,
            dry_run
        )
    else:
        print(f"Backend {backend} not yet supported for fix-embeddings")
        return 0, 0, 0

    # Update stored config if we fixed anything
    if fixed > 0 and not dry_run:
        _update_stored_config(target_dir, expected_dim)

    return missing, mismatch, fixed


def _load_config(target_dir: Path) -> dict:
    """Load database config."""
    config_path = target_dir / ".mind" / "database_config.yaml"
    if not config_path.exists():
        return {}
    try:
        return yaml.safe_load(config_path.read_text())
    except Exception:
        return {}


def _get_current_dimension() -> int:
    """Get dimension from current embedding provider."""
    provider = os.getenv("EMBEDDING_PROVIDER", "local")
    if provider == "openai":
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        return {"text-embedding-3-small": 1536, "text-embedding-3-large": 3072}.get(model, 3072)
    return 768


def _fix_falkordb(config: dict, expected_dim: int, dry_run: bool) -> Tuple[int, int, int]:
    """Fix embeddings in FalkorDB."""
    try:
        from falkordb import FalkorDB
    except ImportError:
        print("falkordb package not installed")
        return 0, 0, 0

    host = config.get("host", "localhost")
    port = config.get("port", 6379)
    graph_name = config.get("graph_name", "mind")

    try:
        db = FalkorDB(host=host, port=port)
        graph = db.select_graph(graph_name)
    except Exception as e:
        print(f"Cannot connect to FalkorDB: {e}")
        return 0, 0, 0

    # Get embedding service (skip check since we're fixing)
    os.environ["EMBEDDING_SKIP_CHECK"] = "1"
    try:
        from runtime.infrastructure.embeddings import get_embedding_service
        embed_service = get_embedding_service()
    except Exception as e:
        print(f"Cannot load embedding service: {e}")
        return 0, 0, 0
    finally:
        if "EMBEDDING_SKIP_CHECK" in os.environ:
            del os.environ["EMBEDDING_SKIP_CHECK"]

    missing = 0
    mismatch = 0
    fixed = 0
    dimension_changed = False

    node_types = ["Actor", "Space", "Thing", "Narrative", "Moment"]

    # Collect all nodes needing embeddings first
    all_nodes_to_fix = []
    for node_type in node_types:
        nodes = _find_nodes_needing_embeddings(graph, node_type, expected_dim)
        for node in nodes:
            node["node_type"] = node_type
            all_nodes_to_fix.append(node)

    if not all_nodes_to_fix:
        print("All embeddings OK")
        return 0, 0, 0

    # Count missing vs mismatch
    for node in all_nodes_to_fix:
        if node["reason"] == "missing":
            missing += 1
        else:
            mismatch += 1
            dimension_changed = True

    total = len(all_nodes_to_fix)

    if dry_run:
        for node in all_nodes_to_fix:
            print(f"  [dry-run] Would fix {node['node_type']} {node['id']}: {node['reason']}")
        print(f"\nNodes: {missing} missing, {mismatch} mismatched")
    else:
        # Progress bar
        bar_width = 40
        print(f"Fixing {total} embeddings...")

        errors = 0
        for i, node in enumerate(all_nodes_to_fix):
            node_id = node["id"]
            node_type = node["node_type"]

            # Get embeddable text
            text = node.get("synthesis") or node.get("name") or node.get("content") or node_id

            try:
                embedding = embed_service.embed(text)
                _update_node_embedding(graph, node_type, node_id, embedding)
                fixed += 1
            except Exception:
                errors += 1

            # Update progress bar
            progress = (i + 1) / total
            filled = int(bar_width * progress)
            bar = "█" * filled + "░" * (bar_width - filled)
            sys.stdout.write(f"\r[{bar}] {i+1}/{total}")
            sys.stdout.flush()

        # Clear progress bar and show result
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()

        if errors:
            print(f"Nodes: {missing} missing, {mismatch} mismatched, {fixed} fixed ({errors} errors)")
        else:
            print(f"Nodes: {missing} missing, {mismatch} mismatched, {fixed} fixed")

    # Recreate vector indexes if dimension changed
    if dimension_changed and fixed > 0 and not dry_run:
        _recreate_vector_indexes(graph, expected_dim)

    return missing, mismatch, fixed


def _find_nodes_needing_embeddings(graph, node_type: str, expected_dim: int) -> List[Dict[str, Any]]:
    """Find nodes that need embeddings."""
    # Get all nodes of this type
    cypher = f"""
    MATCH (n:{node_type})
    RETURN n.id AS id, n.name AS name, n.synthesis AS synthesis,
           n.content AS content, n.embedding AS embedding
    """

    try:
        result = graph.query(cypher)
        rows = result.result_set if result.result_set else []
    except Exception:
        return []

    nodes_to_fix = []

    for row in rows:
        node_id = row[0]
        name = row[1]
        synthesis = row[2]
        content = row[3]
        embedding = row[4]

        if embedding is None:
            nodes_to_fix.append({
                "id": node_id,
                "name": name,
                "synthesis": synthesis,
                "content": content,
                "reason": "missing"
            })
        elif isinstance(embedding, list) and len(embedding) != expected_dim:
            nodes_to_fix.append({
                "id": node_id,
                "name": name,
                "synthesis": synthesis,
                "content": content,
                "reason": f"dim={len(embedding)}, expected={expected_dim}"
            })

    return nodes_to_fix


def _update_node_embedding(graph, node_type: str, node_id: str, embedding: List[float]) -> None:
    """Update node embedding."""
    cypher = f"""
    MATCH (n:{node_type} {{id: $id}})
    SET n.embedding = $embedding
    """
    graph.query(cypher, {"id": node_id, "embedding": embedding})


def _update_stored_config(target_dir: Path, new_dim: int) -> None:
    """Update stored embedding config after fix."""
    config_path = target_dir / ".mind" / "database_config.yaml"

    try:
        config = yaml.safe_load(config_path.read_text())

        provider = os.getenv("EMBEDDING_PROVIDER", "local")
        if provider == "openai":
            model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        else:
            model = "all-mpnet-base-v2"

        config["embedding"] = {
            "provider": provider,
            "model": model,
            "dimension": new_dim,
        }

        config_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))
        print(f"\nUpdated .mind/database_config.yaml with new embedding config")

    except Exception as e:
        print(f"\nWarning: could not update config: {e}")


def _recreate_vector_indexes(graph, new_dim: int) -> None:
    """Recreate vector indexes with new dimension."""
    node_types = ["Actor", "Space", "Thing", "Narrative", "Moment"]

    print(f"\nRecreating vector indexes ({new_dim}d)...")

    for node_type in node_types:
        # Drop existing vector index
        try:
            graph.query(f"DROP VECTOR INDEX FOR (n:{node_type}) ON (n.embedding)")
        except Exception:
            pass  # Index may not exist

        # Create new vector index
        try:
            graph.query(
                f"CREATE VECTOR INDEX FOR (n:{node_type}) ON (n.embedding) "
                f"OPTIONS {{dimension: {new_dim}, similarityFunction: 'cosine'}}"
            )
            print(f"  ✓ {node_type} vector index")
        except Exception as e:
            print(f"  ✗ {node_type}: {e}")
