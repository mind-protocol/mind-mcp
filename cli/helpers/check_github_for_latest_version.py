"""Check GitHub for latest release version."""

import json

from .get_mcp_version_from_config import get_mcp_version


def check_for_upgrade() -> str | None:
    """Check GitHub for latest version. Returns version if newer, else None."""
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
