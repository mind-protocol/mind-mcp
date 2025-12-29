"""
File and data ingestion for the mind graph.

Provides:
- scan_and_ingest_files: Scan repo and create Thing nodes
- ingest_capabilities: Create capability graph nodes
"""

from .files import scan_and_ingest_files
from .capabilities import ingest_capabilities

__all__ = ["scan_and_ingest_files", "ingest_capabilities"]
