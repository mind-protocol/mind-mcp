"""Copy L3 ecosystem templates to .mind/ directory."""

import shutil
from pathlib import Path

from .get_paths_for_templates_and_runtime import get_templates_path

# Files that should never be overwritten (user state)
PROTECTED_PATTERNS = [
    "state/SYNC_",      # Project state files
    "database_config",  # Database configuration
]


def _is_protected(rel_path: Path) -> bool:
    """Check if file should not be overwritten."""
    rel_str = str(rel_path)
    return any(pattern in rel_str for pattern in PROTECTED_PATTERNS)


def copy_ecosystem_templates(target_dir: Path) -> None:
    """Copy or update .mind/ from L3 ecosystem templates."""
    src = get_templates_path() / "mind"
    dst = target_dir / ".mind"

    if not dst.exists():
        print(f"Creating {dst}")
        shutil.copytree(src, dst)
        print("✓ .mind/ created")
    else:
        print(f"Updating {dst}")
        created = updated = skipped = 0

        for f in src.rglob("*"):
            if f.is_dir():
                continue
            rel = f.relative_to(src)
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
