"""Get paths to mind-mcp resources."""

from pathlib import Path


def get_repo_root() -> Path:
    """Get mind-mcp repo root."""
    return Path(__file__).parent.parent.parent


def get_templates_path() -> Path:
    """Get templates/ directory path."""
    path = get_repo_root() / "templates"
    if path.exists() and (path / "mind").exists():
        return path
    raise FileNotFoundError(f"Templates not found: {path}")


def get_runtime_path() -> Path:
    """Get runtime/ package path (copied to client's .mind/mind/)."""
    path = get_repo_root() / "runtime"
    if path.exists() and (path / "__init__.py").exists():
        return path
    raise FileNotFoundError(f"Runtime not found: {path}")
