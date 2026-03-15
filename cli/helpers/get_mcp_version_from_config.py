"""Get version from config.yaml."""

import yaml
from .get_paths_for_templates_and_runtime import get_templates_path


def get_mcp_version() -> str:
    """Get MCP package version."""
    try:
        path = get_templates_path() / "mind" / "config.yaml"
        with open(path) as f:
            return yaml.safe_load(f).get("mcp_version", "0.0.0")
    except Exception:
        return "0.0.0"


def get_protocol_version() -> str:
    """Get L4 protocol version."""
    try:
        path = get_templates_path() / "mind" / "config.yaml"
        with open(path) as f:
            return yaml.safe_load(f).get("protocol_version", "0.0.0")
    except Exception:
        return "0.0.0"
