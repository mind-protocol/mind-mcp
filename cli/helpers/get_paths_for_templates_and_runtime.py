"""Get paths to mind-mcp resources."""

from pathlib import Path

# Import from core_utils for shared template/capability fetching logic
from runtime.core_utils import get_templates_path  # noqa: F401
from runtime.core_utils import get_capabilities_path  # noqa: F401


def get_repo_root() -> Path:
    """Get mind-mcp repo root."""
    return Path(__file__).parent.parent.parent


def get_runtime_path() -> Path:
    """Get runtime/ package path (copied to client's .mind/mind/)."""
    path = get_repo_root() / "runtime"
    if path.exists() and (path / "__init__.py").exists():
        return path
    raise FileNotFoundError(f"Runtime not found: {path}")
