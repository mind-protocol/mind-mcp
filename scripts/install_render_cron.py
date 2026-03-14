#!/usr/bin/env python3
"""
Install Render cron job for log monitoring.

Adds a cron service to render.yaml that runs render_log_monitor.py
every 5 minutes. Called by mind init.

Usage:
    python scripts/install_render_cron.py [--project-root /path/to/org]
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def install_cron(project_root: Path = PROJECT_ROOT):
    """Add log monitor cron job to render.yaml if not already present."""
    render_yaml = project_root / "render.yaml"
    if not render_yaml.exists():
        print("  No render.yaml found — skipping cron install")
        return False

    content = render_yaml.read_text()

    # Check if already installed
    if "render_log_monitor" in content:
        print("  Cron job already installed")
        return True

    # Detect org name from render.yaml
    org_name = project_root.name
    for line in content.split("\n"):
        if "name:" in line and "key" not in line.lower():
            org_name = line.split("name:")[-1].strip().strip('"').strip("'")
            break

    # Add cron job section
    cron_block = f"""
  # ── Mind Protocol Log Monitor (auto-installed by mind init) ──
  - type: cron
    name: {org_name}-log-monitor
    runtime: python
    schedule: "*/5 * * * *"
    buildCommand: pip install pyyaml falkordb
    startCommand: python .mind/runtime/scripts/render_log_monitor.py
    envVars:
      - key: RENDER_API_KEY
        sync: false
      - key: ORG_ID
        value: {org_name}
      - key: UNIVERSE
        sync: false
      - key: FALKORDB_HOST
        sync: false
      - key: FALKORDB_PORT
        sync: false
"""

    # Append to render.yaml
    content = content.rstrip() + "\n" + cron_block
    render_yaml.write_text(content)
    print(f"  Cron job added to render.yaml: {org_name}-log-monitor (every 5 min)")

    # Copy the monitor script to .mind/runtime/scripts/
    scripts_dir = project_root / ".mind" / "runtime" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    src = Path(__file__).parent / "render_log_monitor.py"
    dst = scripts_dir / "render_log_monitor.py"
    if src.exists():
        dst.write_text(src.read_text())
        print(f"  Copied render_log_monitor.py to {dst}")

    return True


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT
    install_cron(root)
