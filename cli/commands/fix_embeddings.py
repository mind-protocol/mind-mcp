"""mind fix-embeddings - Fix missing or mismatched embeddings."""

from pathlib import Path

from ..helpers.fix_embeddings_for_nodes_and_links import fix_embeddings


def run(target_dir: Path, dry_run: bool = False) -> bool:
    """
    Fix embeddings for all nodes.

    Finds and re-embeds:
    - Nodes without embeddings
    - Nodes with wrong dimension (provider changed)

    Args:
        target_dir: Project directory
        dry_run: If True, only report what would be fixed

    Returns:
        True if successful
    """
    if dry_run:
        print("Dry run mode - no changes will be made\n")

    missing, mismatch, fixed = fix_embeddings(target_dir, dry_run=dry_run)

    if dry_run:
        total = missing + mismatch
        if total > 0:
            print(f"\nWould fix {total} nodes. Run without --dry-run to apply.")
        else:
            print("\nNo nodes need fixing.")
    else:
        if fixed > 0:
            print(f"\n✓ Fixed {fixed} embeddings")
        elif missing == 0 and mismatch == 0:
            print("\n✓ All embeddings OK")

    return True
