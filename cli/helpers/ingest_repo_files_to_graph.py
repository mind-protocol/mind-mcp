"""Ingest repository files into the graph during init."""

from pathlib import Path


def ingest_repo_files(target_dir: Path, graph_name: str) -> None:
    """Ingest repository files as Thing nodes."""
    try:
        from mind.ingest import scan_and_ingest_files

        stats = scan_and_ingest_files(target_dir, graph_name=graph_name, embed=False)

        print(f"✓ Files: {stats['files_scanned']} scanned, "
              f"{stats['things_created']} created, "
              f"{stats['things_updated']} updated")

        if stats.get('errors'):
            print(f"  Warnings: {len(stats['errors'])}")

    except Exception as e:
        print(f"⚠ File ingest skipped: {e}")
