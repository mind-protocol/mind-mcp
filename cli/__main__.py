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
import yaml
from pathlib import Path



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
    """Check if upgrade available. Returns latest version if newer, else None."""
    try:
        import urllib.request
        url = "https://api.github.com/repos/mind-protocol/mind-mcp/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "mind-cli"})

        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            latest = data.get("tag_name", "").lstrip("v")

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


def get_runtime_path() -> Path:
    """Get path to mind/ runtime package."""
    repo_root = Path(__file__).parent.parent
    runtime = repo_root / "mind"
    if runtime.exists() and (runtime / "__init__.py").exists():
        return runtime
    raise FileNotFoundError(f"Runtime not found at {runtime}")


def _copy_runtime(target_mind: Path) -> None:
    """Copy mind/ runtime package to .mind/mind/ (keeps 'mind' package name for imports)."""
    runtime_src = get_runtime_path()
    runtime_dst = target_mind / "mind"

    # Patterns to skip
    skip_patterns = {"__pycache__", ".pyc", ".pyo", ".git"}

    def should_skip(path: Path) -> bool:
        return any(part in skip_patterns or part.endswith((".pyc", ".pyo"))
                   for part in path.parts)

    if runtime_dst.exists():
        # Update existing runtime
        print(f"Updating runtime...")
        created = 0
        updated = 0

        for src_file in runtime_src.rglob("*"):
            if src_file.is_dir() or should_skip(src_file):
                continue

            rel_path = src_file.relative_to(runtime_src)
            dst_file = runtime_dst / rel_path

            dst_file.parent.mkdir(parents=True, exist_ok=True)

            if not dst_file.exists():
                shutil.copy2(src_file, dst_file)
                created += 1
            else:
                # Only update if content changed
                if src_file.read_bytes() != dst_file.read_bytes():
                    shutil.copy2(src_file, dst_file)
                    updated += 1

        print(f"✓ Runtime: {created} new, {updated} updated")
    else:
        # Fresh copy
        print(f"Copying runtime to {runtime_dst}")

        def ignore_patterns(dir: str, files: list) -> list:
            return [f for f in files if f in skip_patterns or f.endswith((".pyc", ".pyo"))]

        shutil.copytree(runtime_src, runtime_dst, ignore=ignore_patterns)
        file_count = sum(1 for _ in runtime_dst.rglob("*.py"))
        print(f"✓ Runtime: {file_count} Python files")


def init_command(target_dir: Path, database: str = "falkordb") -> bool:
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

    # Copy runtime (physics, graph, traversal, etc.)
    _copy_runtime(target_mind)

    # Create/update CLAUDE.md
    _update_claude_md(target_dir)

    # Sync skills to all AI agent locations
    _sync_skills_to_agents(target_dir, target_mind / "skills")

    # Create database config
    _create_database_config(target_mind, database)

    # Create .env.mind.example
    _create_env_example(target_dir, database)

    # Update .gitignore to exclude runtime
    _update_gitignore(target_dir)

    print(f"\n✓ mind initialized (v{get_mcp_version()}, database: {database})")
    return True


def _create_database_config(mind_dir: Path, database: str) -> None:
    """Create .mind/database_config.yaml."""
    config_path = mind_dir / "database_config.yaml"

    if database == "neo4j":
        config = {
            "database": {
                "backend": "neo4j",
                "neo4j": {
                    "uri": "${NEO4J_URI}",
                    "user": "${NEO4J_USER}",
                    "password": "${NEO4J_PASSWORD}",
                    "database": "${NEO4J_DATABASE}",
                }
            }
        }
    else:
        config = {
            "database": {
                "backend": "falkordb",
                "falkordb": {
                    "host": "localhost",
                    "port": 6379,
                    "graph_name": "mind",
                }
            }
        }

    config_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))
    print(f"✓ Created database config: {config_path} (backend: {database})")


def _create_env_example(target_dir: Path, database: str) -> None:
    """Create .env.mind.example with database-specific template."""
    env_path = target_dir / ".env.mind.example"

    if database == "neo4j":
        content = """# Mind Protocol - Neo4j Configuration
# Copy to .env and fill in your values

DATABASE_BACKEND=neo4j

# Neo4j Aura connection
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j
"""
    else:
        content = """# Mind Protocol - FalkorDB Configuration
# Copy to .env and fill in your values

DATABASE_BACKEND=falkordb

# FalkorDB (local Redis-based graph)
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_GRAPH=mind

# To start FalkorDB:
#   docker run -p 6379:6379 falkordb/falkordb
"""

    env_path.write_text(content)
    print(f"✓ Created: {env_path}")


def _update_gitignore(target_dir: Path) -> None:
    """Add .mind/mind/ (runtime) to .gitignore."""
    gitignore = target_dir / ".gitignore"

    entries_to_add = [
        "# Mind runtime (copied on init, not committed)",
        ".mind/mind/",
        "",
        "# Environment files",
        ".env",
        ".env.local",
    ]

    if gitignore.exists():
        content = gitignore.read_text()
        # Check if already has mind runtime entry
        if ".mind/mind/" in content:
            return
        # Append to existing
        if not content.endswith("\n"):
            content += "\n"
        content += "\n" + "\n".join(entries_to_add) + "\n"
        gitignore.write_text(content)
        print(f"✓ Updated .gitignore (added .mind/mind/)")
    else:
        # Create new
        gitignore.write_text("\n".join(entries_to_add) + "\n")
        print(f"✓ Created .gitignore")


def _sync_skills_to_agents(target_dir: Path, mind_skills: Path) -> None:
    """
    Sync skills to all AI agent locations:
    - .claude/skills/*/SKILL.md (Claude Code)
    - AGENTS.md (Codex/OpenAI)
    - .gemini/styleguide.md (Gemini)
    """
    if not mind_skills.exists():
        return

    # 1. Claude Code: .claude/skills/*/SKILL.md
    claude_skills = target_dir / ".claude" / "skills"
    claude_skills.mkdir(parents=True, exist_ok=True)

    skill_count = 0
    for skill_file in mind_skills.glob("SKILL_*.md"):
        # Convert SKILL_Name_Here.md -> name-here/SKILL.md
        name = skill_file.stem.replace("SKILL_", "").replace("_", "-").lower()
        skill_dir = claude_skills / name
        skill_dir.mkdir(exist_ok=True)

        # Read content and add YAML frontmatter if missing
        content = skill_file.read_text()
        if not content.startswith("---"):
            # Add frontmatter
            title = skill_file.stem.replace("SKILL_", "").replace("_", " ")
            frontmatter = f"---\nname: {title}\ndescription: Mind Protocol skill\n---\n\n"
            content = frontmatter + content

        (skill_dir / "SKILL.md").write_text(content)
        skill_count += 1

    print(f"✓ Claude skills: {skill_count} -> .claude/skills/")

    # 2. Codex/OpenAI: AGENTS.md (already handled by _update_agents_md)
    # Skills are embedded in AGENTS.md content

    # 3. Gemini: .gemini/styleguide.md
    gemini_dir = target_dir / ".gemini"
    gemini_dir.mkdir(exist_ok=True)

    # Build styleguide from PRINCIPLES + key skills
    principles_path = target_dir / ".mind" / "PRINCIPLES.md"
    styleguide_content = "# Code Style Guide\n\n"

    if principles_path.exists():
        styleguide_content += "## Principles\n\n"
        styleguide_content += principles_path.read_text()
        styleguide_content += "\n\n"

    styleguide_content += "## Key Guidelines\n\n"
    styleguide_content += "- Follow existing code patterns\n"
    styleguide_content += "- Update SYNC files after changes\n"
    styleguide_content += "- Test before claiming complete\n"
    styleguide_content += "- One solution per problem - don't duplicate\n"

    (gemini_dir / "styleguide.md").write_text(styleguide_content)
    print(f"✓ Gemini styleguide: .gemini/styleguide.md")


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

    runtime_dir = mind_dir / "mind"
    if runtime_dir.exists():
        py_files = sum(1 for _ in runtime_dir.rglob("*.py"))
        print(f"  mind/ (runtime): {py_files} Python files")

        # Show key modules
        modules = ["physics", "graph", "connectome", "infrastructure", "traversal"]
        present = [m for m in modules if (runtime_dir / m).exists()]
        if present:
            print(f"    modules: {', '.join(present)}")
    else:
        print(f"  mind/ (runtime): ✗ (run: mind init)")

    return 0


def main():
    parser = argparse.ArgumentParser(prog="mind", description="mind-mcp CLI")
    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize/update .mind/")
    init_parser.add_argument("--dir", "-d", type=Path, default=Path.cwd())
    init_parser.add_argument("--database", "-db", choices=["falkordb", "neo4j"], default="falkordb",
                            help="Database backend (default: falkordb)")

    # upgrade
    upgrade_parser = subparsers.add_parser("upgrade", help="Check for protocol updates")
    upgrade_parser.add_argument("--dir", "-d", type=Path, default=Path.cwd())

    # status
    status_parser = subparsers.add_parser("status", help="Show status")
    status_parser.add_argument("--dir", "-d", type=Path, default=Path.cwd())

    args = parser.parse_args()

    if args.command == "init":
        success = init_command(args.dir, database=args.database)
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
