"""mind export - Export project content for external tools."""

from pathlib import Path

from ..helpers.export_project_to_notebooklm import export_notebooklm


def run(target_dir: Path, target: str = "notebooklm") -> bool:
    """Export project content. Returns True on success."""
    if target == "notebooklm":
        return export_notebooklm(target_dir)
    else:
        print(f"Unknown export target: {target}")
        print("Available targets: notebooklm")
        return False
