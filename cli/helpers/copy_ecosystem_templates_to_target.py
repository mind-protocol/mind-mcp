"""Copy L3 ecosystem templates to .mind/ directory."""

import shutil
from pathlib import Path

from .get_paths_for_templates_and_runtime import get_templates_path

# Files that should never be overwritten (user state)
PROTECTED_PATTERNS = [
    "state/SYNC_",      # Project state files
    "database_config",  # Database configuration
]

# Folders that should not be copied to .mind/ (used for generation only)
EXCLUDED_FOLDERS = [
    "mcp",  # System prompt templates (used to build CLAUDE.md, not copied)
]

# Actor SYSTEM.md gets copied to multiple provider-specific files
ACTOR_PROVIDER_FILES = ["CLAUDE.md", "GEMINI.md", "AGENTS.md"]


def _is_protected(rel_path: Path) -> bool:
    """Check if file should not be overwritten."""
    rel_str = str(rel_path)
    return any(pattern in rel_str for pattern in PROTECTED_PATTERNS)


def _is_excluded(rel_path: Path) -> bool:
    """Check if file is in an excluded folder."""
    parts = rel_path.parts
    return any(folder in parts for folder in EXCLUDED_FOLDERS)


def _is_actor_system_file(rel_path: Path) -> bool:
    """Check if file is actors/{name}/SYSTEM.md."""
    parts = rel_path.parts
    return (
        len(parts) >= 3 and
        parts[0] == "actors" and
        rel_path.name == "SYSTEM.md"
    )


def _copy_actor_system(src_file: Path, dst_dir: Path) -> int:
    """Copy SYSTEM.md to CLAUDE.md, GEMINI.md, AGENTS.md. Returns count."""
    count = 0
    for provider_file in ACTOR_PROVIDER_FILES:
        dst_file = dst_dir / provider_file
        if not dst_file.exists():
            shutil.copy2(src_file, dst_file)
            count += 1
        else:
            shutil.copy2(src_file, dst_file)
    return count


def copy_ecosystem_templates(target_dir: Path) -> None:
    """Copy or update .mind/ from L3 ecosystem templates."""
    src = get_templates_path()  # templates/ is now the root (no /mind subdirectory)
    dst = target_dir / ".mind"

    def ignore_excluded(directory: str, files: list) -> list:
        """Ignore function for shutil.copytree to skip excluded folders."""
        rel_dir = Path(directory).relative_to(src)
        ignored = []
        for f in files:
            rel_path = rel_dir / f if str(rel_dir) != "." else Path(f)
            if _is_excluded(rel_path):
                ignored.append(f)
        return ignored

    if not dst.exists():
        print(f"Creating {dst}")
        shutil.copytree(src, dst, ignore=ignore_excluded)
        # Convert actor SYSTEM.md to provider-specific files
        actors_dir = dst / "actors"
        if actors_dir.exists():
            for actor_dir in actors_dir.iterdir():
                if actor_dir.is_dir():
                    system_file = actor_dir / "SYSTEM.md"
                    if system_file.exists():
                        _copy_actor_system(system_file, actor_dir)
                        system_file.unlink()  # Remove SYSTEM.md after conversion
        print("✓ .mind/ created")
    else:
        print(f"Updating {dst}")
        created = updated = skipped = 0

        for f in src.rglob("*"):
            if f.is_dir():
                continue
            rel = f.relative_to(src)

            # Skip excluded folders
            if _is_excluded(rel):
                continue

            # Handle actor SYSTEM.md → CLAUDE.md, GEMINI.md, AGENTS.md
            if _is_actor_system_file(rel):
                df_dir = dst / rel.parent
                df_dir.mkdir(parents=True, exist_ok=True)
                created += _copy_actor_system(f, df_dir)
                continue

            df = dst / rel
            df.parent.mkdir(parents=True, exist_ok=True)

            if not df.exists():
                shutil.copy2(f, df)
                created += 1
            elif _is_protected(rel):
                skipped += 1
            else:
                shutil.copy2(f, df)
                updated += 1

        msg = f"✓ Ecosystem: {created} new, {updated} updated"
        if skipped:
            msg += f", {skipped} preserved"
        print(msg)
