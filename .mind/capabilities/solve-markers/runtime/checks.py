"""
Health Checks: solve-markers

Decorator-based health checks for marker freshness monitoring.
Detects stale escalations, propositions, legacy markers, and questions.

DOCS: capabilities/solve-markers/HEALTH.md
"""

import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from runtime.capability import check, Signal, triggers


# =============================================================================
# CONSTANTS
# =============================================================================

# Marker patterns
ESCALATION_PATTERN = re.compile(r"@mind:escalation\b(.*)$", re.MULTILINE)
PROPOSITION_PATTERN = re.compile(r"@mind:proposition\b(.*)$", re.MULTILINE)
QUESTION_PATTERN = re.compile(r"@mind:question\b(.*)$", re.MULTILINE)
LEGACY_PATTERNS = [
    re.compile(r"(?:#|//)\s*(TODO)\b[:\s]*(.*)", re.IGNORECASE),
    re.compile(r"(?:#|//)\s*(FIXME)\b[:\s]*(.*)", re.IGNORECASE),
    re.compile(r"(?:#|//)\s*(HACK)\b[:\s]*(.*)", re.IGNORECASE),
    re.compile(r"(?:#|//)\s*(XXX)\b[:\s]*(.*)", re.IGNORECASE),
]

# Age thresholds
ESCALATION_STALE_HOURS = 48
PROPOSITION_STALE_DAYS = 7
LEGACY_STALE_DAYS = 30
QUESTION_STALE_DAYS = 14

# Code file extensions to scan
SCAN_EXTENSIONS = {".py", ".ts", ".js", ".tsx", ".jsx", ".md", ".yaml", ".yml"}

# Directories to exclude
EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox"}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_line_age(file_path: Path, lineno: int) -> Optional[datetime]:
    """Get the age of a specific line via git blame."""
    try:
        result = subprocess.run(
            ["git", "blame", "-L", f"{lineno},{lineno}", "--porcelain", str(file_path)],
            capture_output=True,
            text=True,
            cwd=file_path.parent,
            timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("author-time "):
                    timestamp = int(line.split(" ", 1)[1])
                    return datetime.fromtimestamp(timestamp)
    except Exception:
        pass

    # Fallback to file mtime
    try:
        return datetime.fromtimestamp(file_path.stat().st_mtime)
    except Exception:
        return None


def scan_files(root: Path) -> list[Path]:
    """Collect scannable files, excluding vendored/test dirs."""
    files = []
    for ext in SCAN_EXTENSIONS:
        for path in root.rglob(f"*{ext}"):
            if any(excluded in path.parts for excluded in EXCLUDE_DIRS):
                continue
            files.append(path)
    return files


def find_markers(files: list[Path], pattern: re.Pattern, stale_threshold: timedelta) -> list[dict]:
    """Find markers matching pattern that exceed the staleness threshold."""
    now = datetime.now()
    stale_markers = []

    for path in files:
        try:
            content = path.read_text()
        except Exception:
            continue

        for match in pattern.finditer(content):
            # Calculate line number
            lineno = content[:match.start()].count("\n") + 1
            context = match.group(1).strip() if match.lastindex else ""

            age = get_line_age(path, lineno)
            if age and (now - age) > stale_threshold:
                stale_markers.append({
                    "file": str(path),
                    "line": lineno,
                    "age_days": (now - age).days,
                    "context": context[:200],
                })

    return stale_markers


# =============================================================================
# HEALTH CHECKS
# =============================================================================

@check(
    id="escalation_freshness",
    triggers=[
        triggers.file.on_modify("**/*.{py,ts,js,md,yaml}"),
        triggers.cron.every(hours=6),
    ],
    on_problem="ESCALATION",
    task="TASK_resolve_escalation",
)
def escalation_freshness(ctx) -> dict:
    """
    H1: Detect @mind:escalation markers older than 48 hours.

    Returns CRITICAL if any stale escalation found (blocks work).
    Returns HEALTHY if no stale escalations.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")
    files = scan_files(root)
    threshold = timedelta(hours=ESCALATION_STALE_HOURS)

    stale = find_markers(files, ESCALATION_PATTERN, threshold)

    if not stale:
        return Signal.healthy()

    return Signal.critical(
        stale_escalations=stale,
        count=len(stale),
    )


@check(
    id="proposition_freshness",
    triggers=[
        triggers.cron.weekly(),
    ],
    on_problem="SUGGESTION",
    task="TASK_evaluate_proposition",
)
def proposition_freshness(ctx) -> dict:
    """
    H2: Detect @mind:proposition markers older than 7 days.

    Returns CRITICAL if >= 5 stale propositions.
    Returns DEGRADED if any stale propositions.
    Returns HEALTHY if none stale.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")
    files = scan_files(root)
    threshold = timedelta(days=PROPOSITION_STALE_DAYS)

    stale = find_markers(files, PROPOSITION_PATTERN, threshold)

    if not stale:
        return Signal.healthy()

    if len(stale) >= 5:
        return Signal.critical(
            stale_propositions=stale,
            count=len(stale),
        )

    return Signal.degraded(
        stale_propositions=stale,
        count=len(stale),
    )


@check(
    id="legacy_marker_freshness",
    triggers=[
        triggers.cron.daily(),
    ],
    on_problem="LEGACY_MARKER",
    task="TASK_fix_legacy_marker",
)
def legacy_marker_freshness(ctx) -> dict:
    """
    H3: Detect TODO/FIXME/HACK/XXX markers older than 30 days.

    Returns CRITICAL if >= 10 stale legacy markers.
    Returns DEGRADED if any stale markers.
    Returns HEALTHY if none stale.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")
    now = datetime.now()
    threshold = timedelta(days=LEGACY_STALE_DAYS)

    # Only scan code files for legacy markers
    code_extensions = {".py", ".ts", ".js", ".tsx", ".jsx"}
    files = []
    for ext in code_extensions:
        for path in root.rglob(f"*{ext}"):
            if any(excluded in path.parts for excluded in EXCLUDE_DIRS):
                continue
            # Exclude test files and vendored code
            if "test" in str(path).lower() or "vendor" in str(path).lower():
                continue
            files.append(path)

    stale_markers = []

    for path in files:
        try:
            content = path.read_text()
        except Exception:
            continue

        for lineno, line in enumerate(content.split("\n"), 1):
            for pattern in LEGACY_PATTERNS:
                match = pattern.search(line)
                if match:
                    age = get_line_age(path, lineno)
                    if age and (now - age) > threshold:
                        stale_markers.append({
                            "file": str(path),
                            "line": lineno,
                            "marker_type": match.group(1).upper(),
                            "context": match.group(2).strip()[:100],
                            "age_days": (now - age).days,
                        })
                    break  # One marker per line

    if not stale_markers:
        return Signal.healthy()

    if len(stale_markers) >= 10:
        return Signal.critical(
            stale_markers=stale_markers,
            count=len(stale_markers),
        )

    return Signal.degraded(
        stale_markers=stale_markers,
        count=len(stale_markers),
    )


@check(
    id="question_freshness",
    triggers=[
        triggers.cron.weekly(),
    ],
    on_problem="UNRESOLVED_QUESTION",
    task="TASK_answer_question",
)
def question_freshness(ctx) -> dict:
    """
    H4: Detect @mind:question markers older than 14 days.

    Returns DEGRADED if any stale questions found.
    Returns HEALTHY if none stale.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")
    files = scan_files(root)
    threshold = timedelta(days=QUESTION_STALE_DAYS)

    stale = find_markers(files, QUESTION_PATTERN, threshold)

    if not stale:
        return Signal.healthy()

    return Signal.degraded(
        stale_questions=stale,
        count=len(stale),
    )


# =============================================================================
# REGISTRY
# =============================================================================

CHECKS = [
    escalation_freshness,
    proposition_freshness,
    legacy_marker_freshness,
    question_freshness,
]
