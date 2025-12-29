"""Setup database: start container, create graph, apply schema indexes."""

import os
import subprocess
import time
from pathlib import Path

# Embedding dimensions by provider/model
EMBEDDING_DIMENSIONS = {
    "local": 768,  # sentence-transformers/all-mpnet-base-v2
    "openai": {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
    },
}


def _get_embedding_dimension() -> int:
    """Get embedding dimension from environment config."""
    provider = os.getenv("EMBEDDING_PROVIDER", "local")

    if provider == "local":
        return EMBEDDING_DIMENSIONS["local"]
    elif provider == "openai":
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        return EMBEDDING_DIMENSIONS["openai"].get(model, 3072)
    else:
        return 768  # Default fallback


def setup_database(target_dir: Path, backend: str, graph_name: str) -> bool:
    """Setup database with schema. Returns True if successful."""
    if backend == "neo4j":
        print("Neo4j: manual setup required (see .env.mind.example)")
        return True

    # FalkorDB setup
    if not _ensure_docker_available():
        print("Docker not available - skipping database setup")
        return False

    if not _ensure_falkordb_running():
        return False

    if not _create_graph_and_indexes(graph_name):
        return False

    print(f"Database: {backend} ready (graph: {graph_name})")
    return True


def _ensure_docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _ensure_falkordb_running() -> bool:
    """Start FalkorDB container if not running."""
    # Check if already running
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=falkordb", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    if "falkordb" in result.stdout:
        print("FalkorDB: already running")
        return True

    # Check if container exists but stopped
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=falkordb", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    if "falkordb" in result.stdout:
        print("FalkorDB: starting existing container...")
        subprocess.run(["docker", "start", "falkordb"], capture_output=True)
    else:
        print("FalkorDB: creating container...")
        result = subprocess.run([
            "docker", "run", "-d",
            "--name", "falkordb",
            "-p", "6379:6379",
            "falkordb/falkordb:latest"
        ], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to start FalkorDB: {result.stderr}")
            return False

    # Wait for startup
    print("FalkorDB: waiting for startup...")
    for _ in range(10):
        time.sleep(1)
        try:
            from falkordb import FalkorDB
            db = FalkorDB(host="localhost", port=6379)
            db.select_graph("_health_check").query("RETURN 1")
            print("FalkorDB: ready")
            return True
        except Exception:
            pass

    print("FalkorDB: startup timeout")
    return False


def _create_graph_and_indexes(graph_name: str) -> bool:
    """Create graph and apply schema indexes."""
    try:
        from falkordb import FalkorDB

        db = FalkorDB(host="localhost", port=6379)
        graph = db.select_graph(graph_name)

        node_types = ["Actor", "Space", "Thing", "Narrative", "Moment"]
        idx_count = 0
        vec_count = 0

        # Get embedding dimension from config
        dimension = _get_embedding_dimension()

        for node_type in node_types:
            # Property indexes
            for prop in ["id", "name", "type", "status"]:
                try:
                    graph.query(f"CREATE INDEX FOR (n:{node_type}) ON (n.{prop})")
                    idx_count += 1
                except Exception:
                    pass  # Index may already exist

            # Vector index for embeddings (dimension from config, cosine similarity)
            try:
                graph.query(
                    f"CREATE VECTOR INDEX FOR (n:{node_type}) ON (n.embedding) "
                    f"OPTIONS {{dimension: {dimension}, similarityFunction: 'cosine'}}"
                )
                vec_count += 1
            except Exception:
                pass  # Vector index may already exist or not supported

        print(f"Schema: {idx_count} property + {vec_count} vector indexes ({dimension}d)")
        return True

    except ImportError:
        print("falkordb package not installed - skipping schema setup")
        return True
    except Exception as e:
        print(f"Schema setup failed: {e}")
        return False
