"""Update .gitignore to exclude runtime."""

from pathlib import Path


def update_gitignore(target_dir: Path) -> None:
    """Add .mind/runtime/ to .gitignore."""
    path = target_dir / ".gitignore"
    entry = ".mind/runtime/"

    if path.exists():
        content = path.read_text()
        if entry in content:
            return
        path.write_text(content.rstrip() + f"\n\n# Mind runtime\n{entry}\n.env\n")
    else:
        path.write_text(f"# Mind runtime\n{entry}\n.env\n")

    print("✓ .gitignore updated")
