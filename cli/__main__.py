#!/usr/bin/env python3
"""
mind-mcp CLI — Minimal entry point

Usage:
    python -m cli init [--dir PATH]
    python -m cli status
    python -m cli upgrade
"""

import argparse
import json
import shutil
import sys
import time
import yaml
from pathlib import Path

CACHE_DIR = Path.home() / ".mind"
UPGRADE_CHECK_INTERVAL = 86400  # 24 hours


def get_mcp_version() -> str:
    """Get MCP package version from templates/mind/config.yaml."""
    try:
        config_path = get_templates_path() / "mind" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config.get("mcp_version", "0.0.0")
    except Exception:
        return "0.0.0"


def get_protocol_version() -> str:
    """Get L4 protocol/schema version from templates/mind/config.yaml."""
    try:
        config_path = get_templates_path() / "mind" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config.get("protocol_version", "0.0.0")
    except Exception:
        return "0.0.0"


def _check_upgrade_needed() -> str | None:
    """
    Check if upgrade available. Returns latest version if newer, else None.
    Caches result to avoid spamming GitHub API.
    """
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / "upgrade_cache.json"

    # Check cache
    try:
        if cache_file.exists():
            cache = json.loads(cache_file.read_text())
            last_check = cache.get("last_check", 0)
            if time.time() - last_check < UPGRADE_CHECK_INTERVAL:
                # Use cached result
                latest = cache.get("latest_version")
                if latest and latest != get_mcp_version():
                    return latest
                return None
    except Exception:
        pass

    # Fetch from GitHub (quick timeout)
    try:
        import urllib.request
        url = "https://api.github.com/repos/mind-protocol/mind-mcp/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "mind-cli"})

        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            latest = data.get("tag_name", "").lstrip("v")

            # Cache result
            cache_file.write_text(json.dumps({
                "last_check": time.time(),
                "latest_version": latest
            }))

            if latest and latest != get_mcp_version():
                return latest
    except Exception:
        pass

    return None


def maybe_show_upgrade_notice() -> None:
    """Show upgrade notice if new version available."""
    try:
        latest = _check_upgrade_needed()
        if latest:
            print(f"\n💡 New version available: v{latest} (current: v{get_mcp_version()})")
            print(f"   Run: pip install --upgrade mind-mcp")
    except Exception:
        pass  # Never fail on upgrade check


def get_templates_path() -> Path:
    """Get path to templates directory."""
    repo_root = Path(__file__).parent.parent
    templates = repo_root / "templates"
    if templates.exists() and (templates / "mind").exists():
        return templates
    raise FileNotFoundError(f"Templates not found at {templates}")


def init_command(target_dir: Path) -> bool:
    """
    Initialize/update .mind/ in target directory.

    Simple upsert: copy all template files, preserving user files not in template.
    """
    templates = get_templates_path()
    mind_templates = templates / "mind"
    target_mind = target_dir / ".mind"

    if not target_mind.exists():
        # Fresh install
        print(f"Creating {target_mind}")
        shutil.copytree(mind_templates, target_mind)
        print(f"✓ Created .mind/ with protocol files")
    else:
        # Upsert: copy template files, user files untouched
        print(f"Updating {target_mind}")

        created = 0
        updated = 0

        for src_file in mind_templates.rglob("*"):
            if src_file.is_dir():
                continue

            rel_path = src_file.relative_to(mind_templates)
            dst_file = target_mind / rel_path

            dst_file.parent.mkdir(parents=True, exist_ok=True)

            if not dst_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"  + {rel_path}")
                created += 1
            else:
                shutil.copy2(src_file, dst_file)
                print(f"  ~ {rel_path}")
                updated += 1

        print(f"✓ Created: {created}, updated: {updated}")

    # Create/update CLAUDE.md
    _update_claude_md(target_dir)

    print(f"\n✓ mind initialized (v{get_mcp_version()})")
    return True


def _update_claude_md(target_dir: Path) -> None:
    """Create or update root CLAUDE.md with mind section."""
    claude_md = target_dir / "CLAUDE.md"
    mind_section = f"""# {target_dir.name}

@.mind/PRINCIPLES.md

---

@.mind/FRAMEWORK.md

---

## Before Any Task

Check project state:
```
.mind/state/SYNC_Project_State.md
```

What's happening? What changed recently? Any handoffs for you?

## After Any Change

Update `.mind/state/SYNC_Project_State.md` with what you did.
"""

    if not claude_md.exists():
        print(f"Creating {claude_md}")
        claude_md.write_text(mind_section)
    else:
        existing = claude_md.read_text()
        if "@.mind/PRINCIPLES.md" not in existing:
            print(f"Updating {claude_md}")
            claude_md.write_text(existing.rstrip() + "\n\n" + mind_section)
        else:
            print(f"CLAUDE.md already configured")


def upgrade_command(target_dir: Path) -> bool:
    """
    Check for and apply protocol upgrades from GitHub.
    """
    print(f"Checking for upgrades (current: v{get_mcp_version()})...")

    # TODO: Fetch latest version from GitHub
    # For now, just run init which upserts all template files
    try:
        import urllib.request
        import json

        url = "https://api.github.com/repos/mind-protocol/mind-mcp/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "mind-cli"})

        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            latest = data.get("tag_name", "").lstrip("v")

            if latest and latest != get_mcp_version():
                print(f"New version available: v{latest}")
                print(f"Run: pip install --upgrade mind-mcp")
                return True
            else:
                print(f"Already on latest version")
                return True

    except Exception as e:
        print(f"Could not check for updates: {e}")
        print("Running local init instead...")
        return init_command(target_dir)


def status_command(target_dir: Path) -> int:
    """Show mind status."""
    mind_dir = target_dir / ".mind"

    if not mind_dir.exists():
        print(f"No .mind/ found in {target_dir}")
        print("Run: mind init")
        return 1

    print(f"mind status: {target_dir.name} (v{get_mcp_version()})")
    print(f"  .mind/: ✓")

    for fname in ["PRINCIPLES.md", "FRAMEWORK.md", "config.yaml"]:
        fpath = mind_dir / fname
        status = "✓" if fpath.exists() else "✗"
        print(f"  {fname}: {status}")

    state_dir = mind_dir / "state"
    if state_dir.exists():
        sync_files = list(state_dir.glob("SYNC_*.md"))
        print(f"  state/: {len(sync_files)} files")

    skills_dir = mind_dir / "skills"
    if skills_dir.exists():
        skill_files = list(skills_dir.glob("SKILL_*.md"))
        print(f"  skills/: {len(skill_files)} files")

    return 0


def main():
    parser = argparse.ArgumentParser(prog="mind", description="mind-mcp CLI")
    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize/update .mind/")
    init_parser.add_argument("--dir", "-d", type=Path, default=Path.cwd())

    # upgrade
    upgrade_parser = subparsers.add_parser("upgrade", help="Check for protocol updates")
    upgrade_parser.add_argument("--dir", "-d", type=Path, default=Path.cwd())

    # status
    status_parser = subparsers.add_parser("status", help="Show status")
    status_parser.add_argument("--dir", "-d", type=Path, default=Path.cwd())

    args = parser.parse_args()

    if args.command == "init":
        success = init_command(args.dir)
        maybe_show_upgrade_notice()
        sys.exit(0 if success else 1)
    elif args.command == "upgrade":
        success = upgrade_command(args.dir)
        sys.exit(0 if success else 1)
    elif args.command == "status":
        code = status_command(args.dir)
        maybe_show_upgrade_notice()
        sys.exit(code)
    else:
        parser.print_help()
        maybe_show_upgrade_notice()
        sys.exit(1)


if __name__ == "__main__":
    main()
