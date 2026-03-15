"""mind init — Initialize .mind/ in a project directory.

Delegates to runtime.init_cmd.init_protocol which handles:
- Template selection (project-team / universe / roleplay)
- CLAUDE.md generation with inlined FRAMEWORK + BEHAVIORS
- Graph setup, file ingestion, embeddings
- citizens/ folder creation
- Runtime file locking (read-only)
"""

from pathlib import Path


def run(target_dir: Path, database: str = "falkordb", mode: str = None) -> bool:
    """Initialize .mind/ in target directory."""
    from runtime.init_cmd import init_protocol
    return init_protocol(target_dir, force=True, clear_graph=False, mode=mode)
