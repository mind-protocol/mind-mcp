"""Generate repository overview maps during init/upgrade."""

from pathlib import Path


def generate_overview(target_dir: Path) -> None:
    """Generate map.md files for the repository."""
    try:
        from runtime.repo_overview import generate_and_save

        output_path = generate_and_save(target_dir, output_format="md")
        print(f"✓ Overview: {output_path.name}")

    except Exception as e:
        print(f"⚠ Overview skipped: {e}")
