"""Validate that current embedding config matches stored config."""

import os
from pathlib import Path
from typing import Optional, Tuple
import yaml


def validate_embedding_config(target_dir: Path) -> Tuple[bool, Optional[str]]:
    """
    Check if current embedding config matches stored config.

    Returns:
        (is_valid, error_message)
        - (True, None) if config matches or no stored config
        - (False, message) if mismatch detected
    """
    config_path = target_dir / ".mind" / "database_config.yaml"

    if not config_path.exists():
        return True, None

    try:
        config = yaml.safe_load(config_path.read_text())
    except Exception:
        return True, None  # Can't read, skip validation

    stored = config.get("embedding")
    if not stored:
        return True, None  # No stored embedding config

    # Get current config from environment
    current_provider = os.getenv("EMBEDDING_PROVIDER", "local")
    if current_provider == "openai":
        current_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        current_dim = {"text-embedding-3-small": 1536, "text-embedding-3-large": 3072}.get(current_model, 3072)
    else:
        current_model = "all-mpnet-base-v2"
        current_dim = 768

    stored_provider = stored.get("provider", "local")
    stored_dim = stored.get("dimension", 768)

    # Check for dimension mismatch (the critical issue)
    if current_dim != stored_dim:
        return False, (
            f"Embedding dimension mismatch!\n"
            f"  Stored: {stored_provider} ({stored_dim}d)\n"
            f"  Current: {current_provider} ({current_dim}d)\n"
            f"\n"
            f"Vector indexes were created with {stored_dim}d. Options:\n"
            f"  1. Keep using {stored_provider} (revert EMBEDDING_PROVIDER)\n"
            f"  2. Recreate graph: delete and run 'mind init' again\n"
            f"  3. Re-embed all nodes with new provider"
        )

    return True, None


def check_embedding_config(target_dir: Path) -> bool:
    """
    Check embedding config and print warning if mismatch.

    Returns True if OK, False if mismatch.
    """
    is_valid, error = validate_embedding_config(target_dir)

    if not is_valid:
        print(f"\n⚠️  WARNING: {error}\n")
        return False

    return True
