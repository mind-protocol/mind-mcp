"""Create .env.mind.example file."""

from pathlib import Path


def create_env_example(target_dir: Path, backend: str) -> None:
    """Create .env.mind.example with database and embedding config."""
    path = target_dir / ".env.mind.example"

    # Common embedding config
    embedding_config = """
# Embedding Provider
# Options: local (default, no API key), openai (requires OPENAI_API_KEY)
EMBEDDING_PROVIDER=local

# OpenAI Configuration (required if EMBEDDING_PROVIDER=openai)
OPENAI_API_KEY=sk-...
# Model: text-embedding-3-large (3072d, default) or text-embedding-3-small (1536d)
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
"""

    if backend == "neo4j":
        db_config = """# Database
DATABASE_BACKEND=neo4j
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=
NEO4J_DATABASE=neo4j
"""
    else:
        db_config = """# Database
DATABASE_BACKEND=falkordb
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_GRAPH=mind
"""

    content = db_config + embedding_config
    path.write_text(content)
    print("✓ .env.mind.example created")
