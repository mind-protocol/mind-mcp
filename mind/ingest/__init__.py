"""
File and data ingestion for the mind graph.

Provides:
- scan_and_ingest_files: Scan repo and create Thing nodes
"""

from .files import scan_and_ingest_files

__all__ = ["scan_and_ingest_files"]
