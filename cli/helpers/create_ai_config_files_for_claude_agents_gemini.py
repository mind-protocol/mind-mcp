"""Create AI tool config files: CLAUDE.md, AGENTS.md, .gemini/styleguide.md."""

from pathlib import Path


def create_ai_config_files(target_dir: Path) -> None:
    """Create config files for Claude, Codex/Agents, and Gemini."""
    _create_claude_md(target_dir)
    _create_agents_md(target_dir)
    _create_gemini_styleguide(target_dir)


def _create_claude_md(target_dir: Path) -> None:
    """Create/update CLAUDE.md with @references."""
    path = target_dir / "CLAUDE.md"

    section = f"""# {target_dir.name}

@.mind/PRINCIPLES.md

---

@.mind/FRAMEWORK.md

---

## Before Any Task

Check: `.mind/state/SYNC_Project_State.md`

## After Any Change

Update: `.mind/state/SYNC_Project_State.md`
"""

    if not path.exists():
        path.write_text(section)
        print("✓ CLAUDE.md created")
    elif "@.mind/PRINCIPLES.md" not in path.read_text():
        path.write_text(path.read_text().rstrip() + "\n\n" + section)
        print("✓ CLAUDE.md updated")


def _create_agents_md(target_dir: Path) -> None:
    """Create AGENTS.md for Codex/OpenAI agents."""
    path = target_dir / "AGENTS.md"
    principles = target_dir / ".mind" / "PRINCIPLES.md"
    framework = target_dir / ".mind" / "FRAMEWORK.md"

    content = f"# {target_dir.name} - Agent Instructions\n\n"

    if principles.exists():
        content += principles.read_text() + "\n\n---\n\n"

    if framework.exists():
        content += framework.read_text() + "\n\n---\n\n"

    content += """## Before Any Task

Check: `.mind/state/SYNC_Project_State.md`

## After Any Change

Update: `.mind/state/SYNC_Project_State.md`
"""

    if not path.exists():
        path.write_text(content)
        print("✓ AGENTS.md created")


def _create_gemini_styleguide(target_dir: Path) -> None:
    """Create .gemini/styleguide.md."""
    gemini_dir = target_dir / ".gemini"
    gemini_dir.mkdir(exist_ok=True)

    path = gemini_dir / "styleguide.md"
    principles = target_dir / ".mind" / "PRINCIPLES.md"

    content = "# Code Style Guide\n\n"

    if principles.exists():
        content += principles.read_text() + "\n"

    path.write_text(content)
    print("✓ .gemini/styleguide.md created")
