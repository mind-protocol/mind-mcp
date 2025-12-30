"""
File and path utilities for the doctor command.

Extracted from doctor.py to reduce monolith file size.
Contains:
- parse_gitignore: Parse .gitignore patterns
- load_doctor_config: Load config from config.yaml and .gitignore
- should_ignore_path: Check if path matches ignore patterns
- is_binary_file: Check if file is binary
- find_source_files: Find all source code files
- find_code_directories: Find leaf directories with code files
- count_lines: Count non-empty lines in a file
- find_long_sections: Find long functions/classes in a file
"""
# DOCS: docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md

import fnmatch
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

from datetime import datetime
from .core_utils import IGNORED_EXTENSIONS, HAS_YAML, find_module_directories
from .doctor_types import DoctorConfig, IgnoreEntry, DoctorIssue

if HAS_YAML:
    import yaml

DOCTOR_FALSE_POSITIVE_PATTERN = re.compile(
    r'^@mind:doctor:([A-Z0-9_]+):false_positive(?:\s+(.+))?$'
)
DOCTOR_TAG_PATTERN = re.compile(
    r'^@mind:doctor:([A-Z0-9_]+):([a-z_-]+)\s*(.*)$'
)
ISO_DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def save_doctor_config(target_dir: Path, config: DoctorConfig) -> None:
    """Save doctor configuration to .mind/config.yaml."""
    config_path = target_dir / ".mind" / "config.yaml"
    if not HAS_YAML:
        return

    try:
        data = {"doctor": {
            "monolith_lines": config.monolith_lines,
            "stale_sync_days": config.stale_sync_days,
            "docs_ref_search_chars": config.docs_ref_search_chars,
            "hook_check_chars": config.hook_check_chars,
            "ignore": config.ignore,
            "disabled_checks": config.disabled_checks,
            "gemini_model_fallback_status": config.gemini_model_fallback_status,
        }}
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    except Exception as e:
        # Log or print error, but don't fail the main process
        print(f"Warning: Failed to save doctor config: {e}", file=sys.stderr)


def parse_gitignore(gitignore_path: Path) -> List[str]:
    """Parse .gitignore file and return list of patterns."""
    patterns = []
    if not gitignore_path.exists():
        return patterns

    try:
        with open(gitignore_path) as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Normalize pattern for our matching
                if line.endswith('/'):
                    # Directory pattern - add /** suffix
                    patterns.append(line.rstrip('/') + "/**")
                else:
                    patterns.append(line)
    except Exception:
        pass

    return patterns


def load_doctor_config(target_dir: Path) -> DoctorConfig:
    """Load doctor configuration from config.yaml, .gitignore, and .mindignore."""
    config_path = target_dir / ".mind" / "config.yaml"
    gitignore_path = target_dir / ".gitignore"
    protocol_ignore_path = target_dir / ".mindignore"

    config = DoctorConfig()
    
    # Use a set to maintain unique ignore patterns
    ignore_patterns = set(config.ignore)

    # Add patterns from .mindignore (primary ignore file)
    ignore_patterns.update(parse_gitignore(protocol_ignore_path))

    # Add patterns from .gitignore (secondary)
    ignore_patterns.update(parse_gitignore(gitignore_path))

    if not config_path.exists():
        config.ignore = sorted(list(ignore_patterns))
        return config

    if not HAS_YAML:
        config.ignore = sorted(list(ignore_patterns))
        return config

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        doctor_config = data.get("doctor", {})

        if "monolith_lines" in doctor_config:
            config.monolith_lines = int(doctor_config["monolith_lines"])
        if "stale_sync_days" in doctor_config:
            config.stale_sync_days = int(doctor_config["stale_sync_days"])
        if "docs_ref_search_chars" in doctor_config:
            config.docs_ref_search_chars = int(doctor_config["docs_ref_search_chars"])
        if "ignore" in doctor_config:
            ignore_patterns.update(doctor_config["ignore"])
        if "disabled_checks" in doctor_config:
            config.disabled_checks = list(doctor_config["disabled_checks"])
        if "gemini_model_fallback_status" in doctor_config:
            config.gemini_model_fallback_status = dict(doctor_config["gemini_model_fallback_status"])

    except Exception:
        pass  # Use defaults on error

    config.ignore = sorted(list(ignore_patterns))
    return config


def load_doctor_ignore(target_dir: Path) -> List[IgnoreEntry]:
    """Load suppressed issues from .mind/doctor-ignore.yaml.

    Returns a list of IgnoreEntry objects that should be filtered from doctor results.
    """
    ignore_path = target_dir / ".mind" / "doctor-ignore.yaml"

    if not ignore_path.exists():
        return []

    if not HAS_YAML:
        return []

    try:
        with open(ignore_path) as f:
            data = yaml.safe_load(f) or {}

        ignores = []
        for entry in data.get("ignores", []):
            if not isinstance(entry, dict):
                continue
            if "task_type" not in entry:
                continue

            path_value = entry.get("path", "*")
            # Handle case where path is a list (convert to first item or skip)
            if isinstance(path_value, list):
                if not path_value:
                    path_value = "*"
                else:
                    # Create separate entries for each path in the list
                    for p in path_value:
                        ignores.append(IgnoreEntry(
                            task_type=entry.get("task_type", ""),
                            path=str(p),
                            reason=entry.get("reason", ""),
                            added_by=entry.get("added_by", ""),
                            added_date=entry.get("added_date", ""),
                        ))
                    continue
            ignores.append(IgnoreEntry(
                task_type=entry.get("task_type", ""),
                path=str(path_value),  # Ensure string
                reason=entry.get("reason", ""),
                added_by=entry.get("added_by", ""),
                added_date=entry.get("added_date", ""),
            ))

        return ignores

    except Exception:
        return []


def is_issue_ignored(issue: DoctorIssue, ignores: List[IgnoreEntry]) -> bool:
    """Check if a DoctorIssue should be suppressed based on ignore rules.

    Matching logic:
    - task_type must match exactly
    - path can be: exact match, glob pattern, or "*" for all
    """
    for ignore in ignores:
        # Issue type must match
        if ignore.task_type != issue.task_type:
            continue

        # Check path matching
        if ignore.path == "*":
            # Wildcard: ignore all issues of this type
            return True

        # Normalize paths (handle case where path might be a list)
        issue_path_raw = issue.path
        if isinstance(issue_path_raw, list):
            issue_path_raw = issue_path_raw[0] if issue_path_raw else ""
        issue_path = str(issue_path_raw).replace("\\", "/")
        ignore_path = str(ignore.path).replace("\\", "/")

        # Exact match
        if issue_path == ignore_path:
            return True

        # Glob pattern match
        if "*" in ignore_path or "?" in ignore_path:
            if fnmatch.fnmatch(issue_path, ignore_path):
                return True

        # Prefix match for directories
        if ignore_path.endswith("/"):
            if issue_path.startswith(ignore_path):
                return True

    return False


def filter_ignored_issues(issues: List[DoctorIssue], ignores: List[IgnoreEntry]) -> tuple:
    """Filter out ignored issues from a list.

    Returns: (filtered_issues, ignored_count)
    """
    if not ignores:
        return issues, 0

    filtered = []
    ignored_count = 0

    for issue in issues:
        if is_issue_ignored(issue, ignores):
            ignored_count += 1
        else:
            filtered.append(issue)

    return filtered, ignored_count


def extract_docs_references_from_file(path: Path, max_lines: int = 20) -> List[Path]:
    """Extract DOCS: references from the top of a source file."""
    doc_paths: List[Path] = []
    try:
        content = path.read_text(errors="ignore")
    except Exception:
        return doc_paths

    for line in content.split("\n")[:max_lines]:
        if "DOCS:" not in line:
            continue
        doc_path = line.split("DOCS:")[-1].strip()
        if doc_path:
            doc_paths.append(Path(doc_path))
    return doc_paths


def _parse_doc_false_positives(doc_path: Path) -> Dict[str, str]:
    """Parse false positive markers from a doc file metadata block."""
    try:
        lines = doc_path.read_text(errors="ignore").splitlines()
    except Exception:
        return {}

    in_metadata_block = False
    updated_seen = False
    results: Dict[str, str] = {}

    for line in lines[:200]:
        stripped = line.strip()
        if stripped == "```":
            in_metadata_block = not in_metadata_block
            if not in_metadata_block:
                updated_seen = False
            continue
        if not in_metadata_block:
            continue
        if stripped.startswith("UPDATED:"):
            updated_seen = True
            continue
        if not updated_seen:
            continue
        match = DOCTOR_FALSE_POSITIVE_PATTERN.match(stripped)
        if match:
            task_type = match.group(1).strip()
            reason = (match.group(2) or "").strip()
            results[task_type] = reason

    return results


def parse_doctor_doc_tags(doc_path: Path) -> Dict[str, List[Dict[str, str]]]:
    """Parse @mind:doctor tags from a doc file metadata block."""
    try:
        lines = doc_path.read_text(errors="ignore").splitlines()
    except Exception:
        return {}

    in_metadata_block = False
    updated_seen = False
    tags: Dict[str, List[Dict[str, str]]] = {}

    for line in lines[:200]:
        stripped = line.strip()
        if stripped == "```":
            in_metadata_block = not in_metadata_block
            if not in_metadata_block:
                updated_seen = False
            continue
        if not in_metadata_block:
            continue
        if stripped.startswith("UPDATED:"):
            updated_seen = True
            continue
        if not updated_seen:
            continue

        match = DOCTOR_TAG_PATTERN.match(stripped)
        if not match:
            continue

        task_type = match.group(1).strip()
        status = match.group(2).strip()
        remainder = match.group(3).strip()

        date_value = ""
        message = remainder
        if status == "postponed" and remainder:
            parts = remainder.split(maxsplit=1)
            if parts and ISO_DATE_PATTERN.match(parts[0]):
                date_value = parts[0]
                message = parts[1] if len(parts) > 1 else ""

        tags.setdefault(task_type, []).append({
            "status": status,
            "date": date_value,
            "message": message,
        })

    return tags


def load_doctor_false_positives(
    target_dir: Path,
    config: DoctorConfig,
) -> Dict[Path, Dict[str, str]]:
    """Load false positive declarations from docs metadata blocks."""
    docs_dir = target_dir / "docs"
    if not docs_dir.exists():
        return {}

    false_positives: Dict[Path, Dict[str, str]] = {}

    for doc_path in docs_dir.rglob("*.md"):
        if should_ignore_path(doc_path, config.ignore, target_dir):
            continue
        entries = _parse_doc_false_positives(doc_path)
        if entries:
            false_positives[doc_path.relative_to(target_dir)] = entries

    return false_positives


def filter_false_positive_issues(
    issues: List[DoctorIssue],
    false_positives: Dict[Path, Dict[str, str]],
    target_dir: Path,
    config: DoctorConfig,
) -> Tuple[List[DoctorIssue], int]:
    """Filter out issues suppressed by doc metadata false-positive entries."""
    if not false_positives:
        return issues, 0

    filtered: List[DoctorIssue] = []
    suppressed = 0

    for issue in issues:
        issue_path = issue.path
        if isinstance(issue_path, list):
            issue_path = issue_path[0] if issue_path else ""
        issue_path = str(issue_path)
        issue_rel = Path(issue_path)
        issue_abs = target_dir / issue_rel

        doc_refs: List[Path] = []
        if issue_rel.suffix == ".md":
            doc_refs = [issue_rel]
        elif issue_abs.is_file() and not should_ignore_path(issue_abs, config.ignore, target_dir):
            doc_refs = extract_docs_references_from_file(issue_abs)

        suppressed_here = False
        for doc_ref in doc_refs:
            doc_rel = doc_ref
            if doc_rel.is_absolute():
                try:
                    doc_rel = doc_rel.relative_to(target_dir)
                except ValueError:
                    continue
            if doc_rel in false_positives and issue.task_type in false_positives[doc_rel]:
                suppressed_here = True
                break

        if suppressed_here:
            suppressed += 1
        else:
            filtered.append(issue)

    return filtered, suppressed


def add_doctor_ignore(
    target_dir: Path,
    task_type: str,
    path: str,
    reason: str,
    added_by: str = "agent"
) -> bool:
    """Add an entry to doctor-ignore.yaml.

    Creates the file if it doesn't exist.
    Returns True if successful.
    """
    ignore_path = target_dir / ".mind" / "doctor-ignore.yaml"

    if not HAS_YAML:
        return False

    try:
        # Load existing or create new
        if ignore_path.exists():
            with open(ignore_path) as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {"ignores": []}

        if "ignores" not in data:
            data["ignores"] = []

        # Check for duplicate
        for entry in data["ignores"]:
            if entry.get("task_type") == task_type and entry.get("path") == path:
                return True  # Already exists

        # Add new entry
        data["ignores"].append({
            "task_type": task_type,
            "path": path,
            "reason": reason,
            "added_by": added_by,
            "added_date": datetime.now().strftime("%Y-%m-%d"),
        })

        # Write back
        ignore_path.parent.mkdir(parents=True, exist_ok=True)
        with open(ignore_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        return True

    except Exception:
        return False


def should_ignore_path(path: Path, ignore_patterns: List[str], target_dir: Path) -> bool:
    """Check if a path should be ignored based on patterns."""
    try:
        rel_path = str(path.relative_to(target_dir))
    except ValueError:
        rel_path = str(path)

    # Normalize path separators
    rel_path = rel_path.replace("\\", "/")

    for pattern in ignore_patterns:
        pattern = pattern.replace("\\", "/")

        # Pattern ending with /** means match this directory anywhere
        if pattern.endswith("/**"):
            dir_name = pattern[:-3]
            # Match if dir_name is a component in the path
            if f"/{dir_name}/" in f"/{rel_path}/" or rel_path.startswith(f"{dir_name}/"):
                return True

        # Pattern starting with **/ means match suffix
        elif pattern.startswith("**/"):
            suffix = pattern[3:]
            if rel_path.endswith(suffix) or f"/{suffix}" in f"/{rel_path}":
                return True

        # Simple wildcard patterns
        elif "*" in pattern:
            # Try matching with fnmatch
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            # Also try matching just the filename
            if fnmatch.fnmatch(Path(rel_path).name, pattern):
                return True

        # Exact match or prefix
        else:
            if rel_path == pattern or rel_path.startswith(pattern + "/"):
                return True
            # Also match if pattern appears as a path component
            if f"/{pattern}/" in f"/{rel_path}/" or rel_path.startswith(f"{pattern}/"):
                return True

    return False


def is_binary_file(file_path: Path) -> bool:
    """Check if a file is binary."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            return b'\x00' in chunk
    except Exception:
        return True


def find_code_directories(target_dir: Path, config: DoctorConfig) -> List[Path]:
    """Find leaf directories that contain source code files directly.

    Only returns directories that have code files DIRECTLY in them,
    not just subdirectories with code. This means:
    - mind/ is returned (has .py files directly)
    - src/ is NOT returned (only has subdirectories)
    """
    skip_dirs = {'.git', '.mind', 'docs', '__pycache__', '.venv', 'venv', 'templates', 'data'}
    found = []

    def has_direct_code_files(directory: Path) -> bool:
        """Check if directory has code files DIRECTLY in it (not in subdirs)."""
        for f in directory.iterdir():  # iterdir, not rglob
            if not f.is_file():
                continue
            if f.suffix.lower() in IGNORED_EXTENSIONS:
                continue
            if should_ignore_path(f, config.ignore, target_dir):
                continue
            # Check if it's a code file (not just any file)
            if f.suffix.lower() in {'.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.rb', '.php'}:
                return True
        return False

    def find_leaf_code_dirs(directory: Path, depth: int = 0) -> List[Path]:
        """Recursively find leaf directories with code files."""
        if depth > 5:  # Prevent infinite recursion
            return []

        results = []
        has_direct_code = has_direct_code_files(directory)

        # Check subdirectories
        subdirs_with_code = []
        for subdir in directory.iterdir():
            if not subdir.is_dir():
                continue
            if subdir.name.startswith('.'):
                continue
            if subdir.name in skip_dirs:
                continue
            if should_ignore_path(subdir, config.ignore, target_dir):
                continue

            # Recursively find code dirs in subdirectory
            sub_results = find_leaf_code_dirs(subdir, depth + 1)
            if sub_results:
                subdirs_with_code.extend(sub_results)

        # If this dir has direct code files AND no subdirs with code, it's a leaf
        # If this dir has direct code AND subdirs with code, include both
        if has_direct_code:
            results.append(directory)

        results.extend(subdirs_with_code)
        return results

    # Check all top-level directories
    for item in target_dir.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith('.'):
            continue
        if item.name in skip_dirs:
            continue
        if should_ignore_path(item, config.ignore, target_dir):
            continue

        found.extend(find_leaf_code_dirs(item))

    return found


def find_source_files(target_dir: Path, config: DoctorConfig) -> List[Path]:
    """Find all source code files in the project."""
    files = set()

    # Check all code directories
    for code_dir in find_code_directories(target_dir, config):
        for file_path in code_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() in IGNORED_EXTENSIONS:
                continue
            if should_ignore_path(file_path, config.ignore, target_dir):
                continue
            if is_binary_file(file_path):
                continue
            files.add(file_path)

    return sorted(files)


def count_lines(file_path: Path) -> int:
    """Count non-empty lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


def find_long_sections(file_path: Path, min_lines: int = 50) -> List[Dict[str, Any]]:
    """Find long functions, classes, or sections in a file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
    except Exception:
        return []

    sections = []
    suffix = file_path.suffix.lower()

    # Language-specific patterns
    if suffix in ['.py']:
        # Python: def, class, async def
        pattern = re.compile(r'^(\s*)(def |async def |class )(\w+)')
    elif suffix in ['.js', '.ts', '.jsx', '.tsx']:
        # JS/TS: function, class, const/let with arrow or function
        pattern = re.compile(r'^(\s*)(function |class |(?:const|let|var)\s+)(\w+)')
    elif suffix in ['.go']:
        # Go: func
        pattern = re.compile(r'^()(func\s+(?:\([^)]+\)\s+)?)(\w+)')
    elif suffix in ['.rs']:
        # Rust: fn, impl, struct
        pattern = re.compile(r'^(\s*)(fn |impl |struct )(\w+)')
    elif suffix in ['.java', '.kt']:
        # Java/Kotlin: class, interface, method patterns
        pattern = re.compile(r'^(\s*)(public |private |protected |class |interface |fun ).*?(\w+)\s*[({]')
    elif suffix in ['.rb']:
        # Ruby: def, class, module
        pattern = re.compile(r'^(\s*)(def |class |module )(\w+)')
    elif suffix in ['.md']:
        # Markdown: ## headers
        pattern = re.compile(r'^()(#{1,3}\s+)(.+)')
    else:
        return []  # Unsupported language

    # Find all section starts
    section_starts = []
    for i, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            indent = len(match.group(1))
            kind = match.group(2).strip()
            name = match.group(3)
            section_starts.append({
                "line": i + 1,
                "indent": indent,
                "kind": kind,
                "name": name,
            })

    # Calculate section lengths (until next section at same or lower indent)
    for i, section in enumerate(section_starts):
        start_line = section["line"]
        end_line = len(lines)

        # Find end: next section at same or lower indent level
        for j in range(i + 1, len(section_starts)):
            next_section = section_starts[j]
            if next_section["indent"] <= section["indent"]:
                end_line = next_section["line"] - 1
                break

        section["length"] = end_line - start_line + 1
        section["end_line"] = end_line

    # Filter to long sections and sort by length
    long_sections = [s for s in section_starts if s["length"] >= min_lines]
    long_sections.sort(key=lambda x: x["length"], reverse=True)

    return long_sections[:5]  # Top 5 longest
