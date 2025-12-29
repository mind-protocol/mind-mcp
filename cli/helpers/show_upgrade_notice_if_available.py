"""Show upgrade notice if new version available."""

from .check_github_for_latest_version import check_for_upgrade
from .get_mcp_version_from_config import get_mcp_version


def show_upgrade_notice() -> None:
    """Print upgrade notice if newer version exists."""
    try:
        latest = check_for_upgrade()
        if latest:
            print(f"\n[update] v{latest} available (current: v{get_mcp_version()})")
            print("         pip install --upgrade mind-mcp")
    except Exception:
        pass
