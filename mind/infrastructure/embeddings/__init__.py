"""
Embedding Service

Generate and query embeddings for semantic search.

DOCS: docs/infrastructure/embeddings/

Usage:
    from mind.infrastructure.embeddings import EmbeddingService

    embeddings = EmbeddingService()

    # Generate embedding
    vector = embeddings.embed("Aldric swore an oath")

    # Embed a node
    embeddings.embed_node(node_dict)
"""

from .service import EmbeddingService, get_embedding_service

__all__ = ['EmbeddingService', 'get_embedding_service']
