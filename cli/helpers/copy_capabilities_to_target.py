"""Copy capabilities to .mind/capabilities/ directory."""

import shutil
from pathlib import Path

from .get_paths_for_templates_and_runtime import get_capabilities_path


def copy_capabilities(target_dir: Path) -> None:
    """Copy capabilities from source to .mind/capabilities/.

    Capabilities include:
    - Docs (OBJECTIVES, PATTERNS, etc.)
    - Runtime checks (runtime/checks.py)
    - Procedures and skills
    - Tasks definitions

    The runtime/ folder in each capability contains health check
    functions that the MCP server discovers and runs.
    """
    src = get_capabilities_path()
    dst = target_dir / ".mind" / "capabilities"

    if not src.exists():
        print("! Capabilities source not found, skipping")
        return

    if not dst.exists():
        print(f"Creating {dst}")
        shutil.copytree(src, dst)

        # Count capabilities
        caps = [d for d in dst.iterdir() if d.is_dir() and not d.name.startswith('.')]
        print(f"✓ Capabilities: {len(caps)} installed")
    else:
        print(f"Updating {dst}")
        created = updated = 0

        for f in src.rglob("*"):
            if f.is_dir():
                continue

            # Skip cache marker files
            if f.name == ".cache_time":
                continue

            rel = f.relative_to(src)
            df = dst / rel
            df.parent.mkdir(parents=True, exist_ok=True)

            if not df.exists():
                shutil.copy2(f, df)
                created += 1
            else:
                # Always update capability files (they're not user state)
                shutil.copy2(f, df)
                updated += 1

        print(f"✓ Capabilities: {created} new, {updated} updated")
