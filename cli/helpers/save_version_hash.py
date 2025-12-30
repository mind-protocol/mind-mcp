"""Save commit hash to .mind/version.txt during init."""

import subprocess
from pathlib import Path

from .get_paths_for_templates_and_runtime import get_repo_root


def get_current_commit_hash() -> str:
    """Get current commit hash of mind-mcp repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=get_repo_root(),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def get_remote_url() -> str:
    """Get remote origin URL of mind-mcp repo."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=get_repo_root(),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def save_version_hash(target_dir: Path) -> None:
    """Save commit hash and remote URL to .mind/version.txt."""
    version_file = target_dir / ".mind" / "version.txt"
    commit_hash = get_current_commit_hash()
    remote_url = get_remote_url()

    content = f"{commit_hash}\n{remote_url}\n"
    version_file.write_text(content)
    print(f"✓ Version: {commit_hash[:8]}")
