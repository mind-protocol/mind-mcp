"""Create or update .mcp.json for Claude Code integration."""

import json
from pathlib import Path


def create_mcp_config(target_dir: Path) -> None:
    """Create or update .mcp.json with mind MCP server config."""
    mcp_json = target_dir / ".mcp.json"

    # Load existing or create new
    if mcp_json.exists():
        with open(mcp_json) as f:
            config = json.load(f)
    else:
        config = {}

    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add/update mind server
    mind_runtime = target_dir / ".mind" / "runtime"
    config["mcpServers"]["mind"] = {
        "command": "python3",
        "args": ["-m", "mcp.server"],
        "cwd": str(mind_runtime)
    }

    # Write back
    with open(mcp_json, "w") as f:
        json.dump(config, f, indent=2)

    print("✓ .mcp.json configured (mind server)")
