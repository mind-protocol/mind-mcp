"""
Shared utilities for mind CLI.

DOCS: docs/core_utils/PATTERNS_Core_Utils_Functions.md
"""

from pathlib import Path
from typing import List

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# File extensions to ignore when counting/checking source files
IGNORED_EXTENSIONS = {
    # Compiled/binary
    '.pyc', '.pyo', '.class', '.o', '.obj', '.exe', '.dll', '.so', '.a',
    # Minified
    '.min.js', '.min.css', '.map',
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp', '.bmp',
    # Fonts
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    # Archives
    '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
    # Data/config
    '.json', '.yaml', '.yml', '.toml', '.xml', '.csv',
    # Misc
    '.lock', '.log', '.env', '.gitignore', '.dockerignore',
    '.d.ts',  # TypeScript declaration files
}


def get_templates_path() -> Path:
    """
    Get path to templates directory.

    Checks two locations:
    1. Inside package (for installed version)
    2. At repo root (for development)
    """
    # Location 1: Inside package
    package_templates = Path(__file__).parent / "templates"
    if package_templates.exists() and (package_templates / "mind").exists():
        return package_templates

    # Location 2: Repo root (development mode)
    # utils.py is in mind/mind/, templates is in mind/templates/
    # So 2 levels up: mind/mind/ -> mind/
    repo_root = Path(__file__).parent.parent
    repo_templates = repo_root / "templates"
    if repo_templates.exists() and (repo_templates / "mind").exists():
        return repo_templates

    # Not found
    raise FileNotFoundError(
        "Templates directory not found.\n"
        f"Checked: {package_templates}\n"
        f"Checked: {repo_templates}\n"
        "If developing, ensure you're running from the repo.\n"
        "If installed, the package may need rebuilding."
    )


def find_module_directories(docs_dir: Path) -> List[Path]:
    """
    Find all module directories in docs/.

    Handles both patterns:
    - docs/{module}/ (1 level)
    - docs/{area}/{module}/ (2 levels)

    A module directory is one that contains .md files with doc type prefixes.
    """
    modules = []
    doc_prefixes = [
        'OBJECTIVES_',
        'PATTERNS_',
        'BEHAVIORS_',
        'ALGORITHM_',
        'VALIDATION_',
        'IMPLEMENTATION_',
        'HEALTH_',
        'TEST_',
        'SYNC_',
    ]

    for item in docs_dir.iterdir():
        if not item.is_dir() or item.name == "concepts":
            continue

        # Check if this directory itself is a module (has doc files)
        md_files = list(item.glob("*.md"))
        has_doc_files = any(
            any(prefix in f.name for prefix in doc_prefixes)
            for f in md_files
        )

        if has_doc_files:
            modules.append(item)
        else:
            # Check subdirectories (area/module pattern)
            for subdir in item.iterdir():
                if not subdir.is_dir():
                    continue
                sub_md_files = list(subdir.glob("*.md"))
                has_sub_doc_files = any(
                    any(prefix in f.name for prefix in doc_prefixes)
                    for f in sub_md_files
                )
                if has_sub_doc_files:
                    modules.append(subdir)

    return modules
