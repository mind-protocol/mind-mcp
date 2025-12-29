"""Create database_config.yaml in .mind/."""

import os
from pathlib import Path
import yaml

# Embedding dimensions by provider/model
EMBEDDING_DIMENSIONS = {
    "local": 768,
    "openai": {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
    },
}


def _get_embedding_config() -> dict:
    """Get current embedding config from environment."""
    provider = os.getenv("EMBEDDING_PROVIDER", "local")

    if provider == "openai":
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        dimension = EMBEDDING_DIMENSIONS["openai"].get(model, 3072)
    else:
        model = "all-mpnet-base-v2"
        dimension = EMBEDDING_DIMENSIONS["local"]

    return {
        "provider": provider,
        "model": model,
        "dimension": dimension,
    }


def create_database_config(target_dir: Path, backend: str, graph_name: str) -> None:
    """Create .mind/database_config.yaml with database and embedding config."""
    path = target_dir / ".mind" / "database_config.yaml"

    # Get embedding config
    embedding = _get_embedding_config()

    if backend == "neo4j":
        db_config = {
            "backend": "neo4j",
            "neo4j": {
                "uri": "${NEO4J_URI}",
                "user": "${NEO4J_USER}",
                "password": "${NEO4J_PASSWORD}",
                "database": "${NEO4J_DATABASE}",
            }
        }
    else:
        db_config = {
            "backend": "falkordb",
            "falkordb": {
                "host": "localhost",
                "port": 6379,
                "graph_name": graph_name,
            }
        }

    config = {
        "database": db_config,
        "embedding": embedding,
    }

    path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))
    print(f"✓ Database: {backend} (graph: {graph_name})")
