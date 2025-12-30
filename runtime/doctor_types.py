"""
Data types for the doctor command.

Contains shared types used by both doctor.py and doctor_report.py.
Extracted to avoid circular imports.
"""

import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class DoctorIssue:
    """A health issue found by the doctor command.

    Fields:
        task_type: Category (MONOLITH, UNDOCUMENTED, STALE_SYNC, etc.)
        severity: critical, warning, info
        path: Affected file/directory
        message: Human description
        details: Additional context
        suggestion: Human-readable fix
        protocol: Remediation protocol (e.g., "define_space", "add_invariant")
                  If set, membrane can auto-trigger this protocol to fix the issue.
        id: Graph node ID (auto-generated if not provided)
    """
    task_type: str      # MONOLITH, UNDOCUMENTED, STALE_SYNC, etc.
    severity: str        # critical, warning, info
    path: str            # Affected file/directory
    message: str         # Human description
    details: Dict[str, Any] = field(default_factory=dict)
    suggestion: str = ""
    protocol: str = ""   # Protocol to auto-fix (e.g., "define_space", "add_invariant")
    id: str = ""         # Graph node ID (narrative_PROBLEM_*)

    def generate_id(self, module: str) -> str:
        """Generate graph node ID for this issue.

        Format: narrative_PROBLEM_{module}-{task_type}_{hash}
        Example: narrative_PROBLEM_engine-physics-MONOLITH_a7c2
        """
        if self.id:
            return self.id

        # Clean module name
        clean_module = module.lower().replace("_", "-").replace(" ", "-")

        # Create short hash from path for uniqueness (4 chars = 65536 values)
        path_hash = hashlib.sha256(self.path.encode()).hexdigest()[:4]

        # Clean issue type
        clean_type = self.task_type.upper().replace("_", "-")

        self.id = f"narrative_PROBLEM_{clean_module}-{clean_type}_{path_hash}"
        return self.id


@dataclass
class DoctorConfig:
    """Configuration for doctor checks."""
    monolith_lines: int = 800
    stale_sync_days: int = 14
    docs_ref_search_chars: int = 2000  # How many chars to search for DOCS: reference
    hook_check_chars: int = 1000  # How many chars to read when checking hooks for docs
    gemini_model_fallback_status: Dict[str, str] = field(default_factory=dict) # Status of Gemini model fallback per agent
    ignore: List[str] = field(default_factory=lambda: [
        "node_modules/**",
        ".next/**",
        "dist/**",
        "build/**",
        "vendor/**",
        "__pycache__/**",
        ".git/**",
        "*.min.js",
        "*.bundle.js",
        ".venv/**",
        "venv/**",
    ])
    disabled_checks: List[str] = field(default_factory=list)


@dataclass
class IgnoreEntry:
    """A suppressed issue in doctor-ignore.yaml.

    Issues can be ignored by:
    - task_type + path: Exact match (e.g., MONOLITH on src/big_file.py)
    - task_type + path pattern: Glob match (e.g., MAGIC_VALUES on tests/**)
    - task_type only: Suppress all issues of that type (rarely used)
    """
    task_type: str       # MONOLITH, HARDCODED_SECRET, etc.
    path: str             # File/dir path or glob pattern
    reason: str = ""      # Why this is being ignored (required for audit)
    added_by: str = ""    # Who/what added this ignore
    added_date: str = ""  # When added (YYYY-MM-DD)


# =============================================================================
# DEPTH FILTERS
# =============================================================================

DEPTH_LINKS = {
    "NO_DOCS_REF",
    "BROKEN_IMPL_LINK",
    "YAML_DRIFT",
    "UNDOC_IMPL",
    "ORPHAN_DOCS",
}

DEPTH_DOCS = DEPTH_LINKS | {
    "UNDOCUMENTED",
    "STALE_SYNC",
    "PLACEHOLDER",
    "INCOMPLETE_CHAIN",
    "LARGE_DOC_MODULE",
    "STALE_IMPL",
    "DOC_GAPS",
    "ESCALATION",
    "DOC_DUPLICATION",
}

DEPTH_FULL = DEPTH_DOCS | {
    "MONOLITH",
    "STUB_IMPL",
    "INCOMPLETE_IMPL",
    "MISSING_TESTS",
    "HARDCODED_SECRET",
    "HARDCODED_CONFIG",
    "MAGIC_VALUES",
    "LONG_PROMPT",
    "LONG_SQL",
}


def get_depth_types(depth: str) -> set:
    """Get the set of task types for a given depth level."""
    if depth == "links":
        return DEPTH_LINKS
    elif depth == "docs":
        return DEPTH_DOCS
    else:
        return DEPTH_FULL
