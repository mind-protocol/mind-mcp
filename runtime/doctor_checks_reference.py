# Reference-based doctor checks (DOCS pointers, IMPLEMENTATION docs).
# DOCS: docs/mcp-design/doctor/IMPLEMENTATION_Project_Health_Doctor.md

import re
from pathlib import Path
from typing import List

from .doctor_files import find_source_files, should_ignore_path
from .doctor_types import DoctorConfig, DoctorIssue

DOCS_REF_PATTERN = re.compile(r'DOCS:\s*([^\s`"]+\.md)', re.IGNORECASE)


def doctor_check_no_docs_ref(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for source files without DOCS: reference."""
    if "no_docs_ref" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    docs_pattern = re.compile(r'#\s*DOCS:|//\s*DOCS:|/\*\s*DOCS:|^\s*DOCS:', re.MULTILINE)
    doc_extensions = {'.md', '.txt', '.rst', '.html', '.css'}

    for source_file in find_source_files(target_dir, config):
        if source_file.suffix.lower() in doc_extensions:
            continue

        try:
            content = source_file.read_text()
        except Exception:
            continue

        if len(content.splitlines()) < 50:
            continue

        if not docs_pattern.search(content[:config.docs_ref_search_chars]):
            try:
                rel_path = str(source_file.relative_to(target_dir))
            except ValueError:
                rel_path = str(source_file)

            issues.append(DoctorIssue(
                issue_type="NO_DOCS_REF",
                severity="info",
                path=rel_path,
                message="No DOCS: reference in file header",
                suggestion="Document the module itself by pointing to the matching PATTERNS doc.",
                protocol="add_implementation"
            ))

    return issues


def extract_impl_file_refs(impl_path: Path) -> List[str]:
    """Extract file references from an IMPLEMENTATION doc."""
    try:
        content = impl_path.read_text()
    except Exception:
        return []

    refs = []
    patterns = [
        r'`([^`]+\.\w+)`',
        r'- `([^`]+)`',
        r'│\s+[├└]──\s+(\S+\.\w+)',
        r'^\s*(\S+\.(?:py|ts|js|tsx|jsx|go|rs|java|rb))\s*[-—#]',
    ]

    for pattern in patterns:
        refs.extend(re.findall(pattern, content, re.MULTILINE))

    valid_refs = []
    for ref in set(refs):
        ref = ref.strip()
        if '.' in ref and len(ref) < 200 and not ref.startswith('http'):
            valid_refs.append(ref.lstrip('./'))

    return valid_refs


def doctor_check_broken_impl_links(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for IMPLEMENTATION docs pointing to missing files."""
    if "broken_impl_links" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    docs_dir = target_dir / "docs"

    if not docs_dir.exists():
        return issues

    for impl_file in docs_dir.rglob("IMPLEMENTATION_*.md"):
        if should_ignore_path(impl_file, config.ignore, target_dir):
            continue

        missing_files = []
        for ref in extract_impl_file_refs(impl_file):
            ref_path = Path(ref)
            possible_paths = [
                target_dir / ref,
                target_dir / "src" / ref,
                target_dir / "engine" / ref,
                target_dir / "frontend" / ref,
                target_dir / "mind" / ref,
            ]
            if ref_path.parts:
                if ref_path.parts[0] in {"mind", ".mind"}:
                    suffix = Path(*ref_path.parts[1:])
                    if suffix:
                        possible_paths.append(target_dir / ".mind" / suffix)

            if not any(path.exists() for path in possible_paths):
                missing_files.append(ref)

        if not missing_files:
            continue

        try:
            rel_path = str(impl_file.relative_to(target_dir))
        except ValueError:
            rel_path = str(impl_file)

        issues.append(DoctorIssue(
            issue_type="BROKEN_IMPL_LINK",
            severity="critical",
            path=rel_path,
            message=f"References {len(missing_files)} non-existent file(s)",
            details={"missing_files": missing_files[:10]},
            suggestion=f"Update or remove references: {', '.join(missing_files[:3])}"
        ))

    return issues
