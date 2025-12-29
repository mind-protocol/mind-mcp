"""mind status - Show mind status."""

from pathlib import Path

from ..helpers.check_mind_status_in_directory import check_mind_status


def run(target_dir: Path) -> int:
    """Show mind status. Returns exit code."""
    return check_mind_status(target_dir)
