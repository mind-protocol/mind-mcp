"""mind upgrade - Check for protocol upgrades."""

from pathlib import Path

from ..helpers.check_github_for_latest_version import check_for_upgrade
from ..helpers.get_mcp_version_from_config import get_mcp_version
from . import init


def run(target_dir: Path) -> bool:
    """Check for upgrades. Returns True if successful."""
    print(f"Checking for upgrades (current: v{get_mcp_version()})...")

    try:
        latest = check_for_upgrade()
        if latest:
            print(f"New version: v{latest}")
            print("Run: pip install --upgrade mind-mcp")
        else:
            print("Already on latest version")
        return True
    except Exception as e:
        print(f"Could not check: {e}")
        print("Running local init...")
        return init.run(target_dir)
