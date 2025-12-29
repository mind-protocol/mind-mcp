"""Sync skills to AI tool directories: .claude/skills/, etc."""

from pathlib import Path


def sync_skills_to_ai_tools(target_dir: Path) -> None:
    """Sync .mind/skills/ to AI tool skill directories."""
    skills_dir = target_dir / ".mind" / "skills"
    if not skills_dir.exists():
        return

    count = _sync_to_claude(target_dir, skills_dir)
    print(f"✓ Skills: {count} synced to .claude/skills/")


def _sync_to_claude(target_dir: Path, skills_dir: Path) -> int:
    """Sync skills to .claude/skills/*/SKILL.md format."""
    claude_dir = target_dir / ".claude" / "skills"
    claude_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for f in skills_dir.glob("SKILL_*.md"):
        # SKILL_Name_Here.md -> name-here/SKILL.md
        name = f.stem.replace("SKILL_", "").replace("_", "-").lower()
        skill_dir = claude_dir / name
        skill_dir.mkdir(exist_ok=True)

        content = f.read_text()
        if not content.startswith("---"):
            title = f.stem.replace("SKILL_", "").replace("_", " ")
            content = f"---\nname: {title}\n---\n\n" + content

        (skill_dir / "SKILL.md").write_text(content)
        count += 1

    return count
