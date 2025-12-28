#!/usr/bin/env python3
"""
mind-mcp CLI — Minimal entry point

Usage:
    python -m cli init [--force] [--dir PATH]
    python -m cli status
"""

import argparse
import shutil
import sys
from pathlib import Path

def get_templates_path() -> Path:
    """Get path to templates directory."""
    # Check relative to this file: cli/__main__.py -> templates/
    repo_root = Path(__file__).parent.parent
    templates = repo_root / "templates"
    if templates.exists() and (templates / "mind").exists():
        return templates
    raise FileNotFoundError(f"Templates not found at {templates}")


def init_command(target_dir: Path, force: bool = True) -> bool:
    """Initialize .mind/ in target directory."""
    templates = get_templates_path()
    mind_templates = templates / "mind"

    target_mind = target_dir / ".mind"

    # Check if exists
    if target_mind.exists():
        if force:
            print(f"Removing existing {target_mind}")
            shutil.rmtree(target_mind)
        else:
            print(f".mind/ already exists. Use --force to overwrite.")
            return False

    # Copy templates
    print(f"Copying {mind_templates} -> {target_mind}")
    shutil.copytree(mind_templates, target_mind)

    # Create/update CLAUDE.md
    claude_md = target_dir / "CLAUDE.md"
    claude_content = f"""# {target_dir.name}

@.mind/PRINCIPLES.md

---

@.mind/FRAMEWORK.md

---

## Before Any Task

Check project state:
```
.mind/state/SYNC_Project_State.md
```

## After Any Change

Update `.mind/state/SYNC_Project_State.md` with what you did.
"""

    print(f"Creating {claude_md}")
    claude_md.write_text(claude_content)

    print(f"\n✓ mind initialized in {target_dir}")
    print(f"  .mind/ created with protocol files")
    print(f"  CLAUDE.md created with @ references")

    return True


def status_command(target_dir: Path) -> int:
    """Show mind status."""
    mind_dir = target_dir / ".mind"

    if not mind_dir.exists():
        print(f"No .mind/ found in {target_dir}")
        print("Run: python -m cli init")
        return 1

    print(f"mind status: {target_dir.name}")
    print(f"  .mind/ exists: ✓")

    # Check key files
    for fname in ["PRINCIPLES.md", "FRAMEWORK.md", "config.yaml"]:
        fpath = mind_dir / fname
        status = "✓" if fpath.exists() else "✗"
        print(f"  {fname}: {status}")

    # Check state
    state_dir = mind_dir / "state"
    if state_dir.exists():
        sync_files = list(state_dir.glob("SYNC_*.md"))
        print(f"  state/ files: {len(sync_files)}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="mind",
        description="mind-mcp CLI"
    )

    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize .mind/")
    init_parser.add_argument("--force", "-f", action="store_true", default=True)
    init_parser.add_argument("--no-force", action="store_false", dest="force")
    init_parser.add_argument("--dir", "-d", type=Path, default=Path.cwd())

    # status
    status_parser = subparsers.add_parser("status", help="Show status")
    status_parser.add_argument("--dir", "-d", type=Path, default=Path.cwd())

    args = parser.parse_args()

    if args.command == "init":
        success = init_command(args.dir, args.force)
        sys.exit(0 if success else 1)
    elif args.command == "status":
        sys.exit(status_command(args.dir))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
