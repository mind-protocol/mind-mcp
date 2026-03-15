"""Generate embeddings for all graph nodes during init."""

import sys
from pathlib import Path


def generate_embeddings(graph_name: str) -> None:
    """Generate embeddings for all nodes missing them, with progress bar."""
    try:
        from runtime.infrastructure.database import get_database_adapter
        from runtime.infrastructure.embeddings.service import EmbeddingService
    except ImportError as e:
        print(f"⚠ Embeddings skipped: {e}")
        return

    try:
        adapter = get_database_adapter(graph_name=graph_name)
        embed_service = EmbeddingService()
    except Exception as e:
        print(f"⚠ Embeddings skipped: {e}")
        return

    # Find all nodes without embeddings
    result = adapter.query(
        """
        MATCH (n)
        WHERE n.embedding IS NULL AND (n.synthesis IS NOT NULL OR n.description IS NOT NULL)
        RETURN n.id, COALESCE(n.synthesis, n.description) as text
        """
    )

    if not result:
        print("✓ Embeddings: all nodes already embedded")
        return

    total = len(result)
    count = 0
    errors = 0

    # Progress bar
    bar_width = 40
    print(f"Embedding {total} nodes...")

    for i, row in enumerate(result):
        node_id = row[0]
        text = row[1]

        if not text:
            continue

        try:
            embedding = embed_service.embed(text)
            if embedding:
                adapter.execute(
                    "MATCH (n {id: $id}) SET n.embedding = $embedding",
                    {"id": node_id, "embedding": embedding}
                )
                count += 1
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
        print(f"✓ Embeddings: {count} nodes ({errors} errors)")
    else:
        print(f"✓ Embeddings: {count} nodes")
