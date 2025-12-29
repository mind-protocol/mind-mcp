"""Copy runtime package to .mind/mind/ directory."""

import shutil
from pathlib import Path

from .get_paths_for_templates_and_runtime import get_runtime_path

SKIP_PATTERNS = {"__pycache__", ".pyc", ".pyo", ".git"}


def copy_runtime_package(target_dir: Path) -> None:
    """Copy mind/ runtime to .mind/mind/."""
    src = get_runtime_path()
    dst = target_dir / ".mind" / "mind"

    def should_skip(p: Path) -> bool:
        return any(x in SKIP_PATTERNS or x.endswith((".pyc", ".pyo")) for x in p.parts)

    if dst.exists():
        print("Updating runtime...")
        created = updated = 0

        for f in src.rglob("*"):
            if f.is_dir() or should_skip(f):
                continue
            rel = f.relative_to(src)
            df = dst / rel
            df.parent.mkdir(parents=True, exist_ok=True)

            if not df.exists():
                shutil.copy2(f, df)
                created += 1
            elif f.read_bytes() != df.read_bytes():
                shutil.copy2(f, df)
                updated += 1

        print(f"✓ Runtime: {created} new, {updated} updated")
    else:
        print("Copying runtime...")
        shutil.copytree(
            src, dst,
            ignore=lambda d, f: [x for x in f if x in SKIP_PATTERNS or x.endswith((".pyc", ".pyo"))]
        )
        count = sum(1 for _ in dst.rglob("*.py"))
        print(f"✓ Runtime: {count} files")
