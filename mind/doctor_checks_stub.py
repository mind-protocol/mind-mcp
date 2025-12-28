# Placeholder implementation detectors and related checks.
# DOCS: docs/protocol/doctor/IMPLEMENTATION_Project_Health_Doctor.md

import re
from pathlib import Path
from typing import Any, Dict, List

from .doctor_files import count_lines, find_source_files, should_ignore_path
from .doctor_checks_reference import extract_impl_file_refs
from .doctor_types import DoctorConfig, DoctorIssue


def detect_stub_patterns(content: str, suffix: str) -> List[Dict[str, Any]]:
    """Detect stub/placeholder patterns in source files."""
    stubs = []
    if suffix in {".py"}:
        patterns = [
            (r'def \w+\([^)]*\):\s*\n\s+pass\s*$', 'empty function with pass'),
            (r'def \w+\([^)]*\):\s*\n\s+\.\.\.', 'function with ellipsis'),
            (r'raise NotImplementedError', 'NotImplementedError'),
            (r'#\s*TODO[:\s]', 'TODO comment'),
            (r'#\s*FIXME[:\s]', 'FIXME comment'),
            (r'#\s*XXX[:\s]', 'XXX comment'),
            (r'#\s*STUB[:\s]', 'STUB comment'),
            (r'#\s*HACK[:\s]', 'HACK comment'),
        ]
    elif suffix in {".js", ".ts", ".jsx", ".tsx"}:
        patterns = [
            (r'function \w+\([^)]*\)\s*\{\s*\}', 'empty function'),
            (r'=>\s*\{\s*\}', 'empty arrow function'),
            (r'throw new Error\([\'"]not implemented', 'not implemented error'),
            (r'//\s*TODO[:\s]', 'TODO comment'),
            (r'//\s*FIXME[:\s]', 'FIXME comment'),
            (r'//\s*XXX[:\s]', 'XXX comment'),
        ]
    elif suffix == ".go":
        patterns = [
            (r'func \w+\([^)]*\)\s*\{\s*\}', 'empty function'),
            (r'panic\([\'"]not implemented', 'not implemented panic'),
            (r'//\s*TODO[:\s]', 'TODO comment'),
        ]
    else:
        patterns = [
            (r'TODO[:\s]', 'TODO'),
            (r'FIXME[:\s]', 'FIXME'),
            (r'not implemented', 'not implemented'),
        ]

    for pattern, description in patterns:
        count = len(re.findall(pattern, content, re.MULTILINE | re.IGNORECASE))
        if count:
            stubs.append({"pattern": description, "count": count})

    return stubs


def doctor_check_stub_impl(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for implementation files that remain stubs."""
    if "stub_impl" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []

    for source_file in find_source_files(target_dir, config):
        if 'test' in source_file.name.lower():
            continue

        try:
            content = source_file.read_text()
        except Exception:
            continue

        if len(content) < 100:
            continue

        stubs = detect_stub_patterns(content, source_file.suffix.lower())
        total_stubs = sum(s["count"] for s in stubs)
        if total_stubs < 3:
            continue

        try:
            rel_path = str(source_file.relative_to(target_dir))
        except ValueError:
            rel_path = str(source_file)

        stub_summary = ", ".join(f"{s['pattern']} ({s['count']})" for s in stubs[:3])

        issues.append(DoctorIssue(
            issue_type="STUB_IMPL",
            severity="warning",
            path=rel_path,
            message=f"Contains {total_stubs} stub indicators",
            details={"stubs": stubs, "total": total_stubs},
            suggestion=f"Implement: {stub_summary}"
        ))

    return issues


def find_empty_functions(file_path: Path) -> List[Dict[str, Any]]:
    """Find empty or trivial functions inside a file."""
    try:
        content = file_path.read_text()
    except Exception:
        return []

    lines = content.splitlines()
    empty_funcs = []
    suffix = file_path.suffix.lower()

    def record_if_stub() -> None:
        if not func_lines:
            return
        body = "\n".join(func_lines)
        stripped = re.sub(r'""".*?"""', '', body, flags=re.DOTALL)
        stripped = re.sub(r"'''.*?'''", '', stripped, flags=re.DOTALL)
        stripped = re.sub(r'#.*$', '', stripped, flags=re.MULTILINE)
        body_lines = [l for l in stripped.splitlines() if l.strip()]
        body_text = "\n".join(body_lines).strip()
        if not body_text:
            empty_funcs.append({
                "name": func_name,
                "line": func_start,
                "reason": "empty body"
            })
            return
        normalized = [line.strip() for line in body_lines]
        stub_only = all(
            line in {"pass", "..."} or
            line == "return" or
            line.startswith("return None") or
            line.startswith("raise NotImplemented") or
            "TODO" in line or
            "FIXME" in line
            for line in normalized
        )
        if stub_only:
            empty_funcs.append({
                "name": func_name,
                "line": func_start,
                "reason": "stub-only body"
            })

    if suffix == ".py":
        in_func = False
        func_name = ""
        func_start = 0
        func_indent = 0
        func_lines = []

        for i, line in enumerate(lines):
            match = re.match(r'^(\s*)(async\s+)?def\s+(\w+)', line)
            if match:
                if in_func:
                    record_if_stub()

                in_func = True
                func_indent = len(match.group(1))
                func_name = match.group(3)
                func_start = i + 1
                func_lines = []
            elif in_func:
                if line.strip() and not line.startswith(' ' * (func_indent + 1)):
                    record_if_stub()
                    in_func = False
                else:
                    func_lines.append(line)

        if in_func:
            record_if_stub()

    return empty_funcs[:10]


def doctor_check_incomplete_impl(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for incomplete implementation files.""" 
    if "incomplete_impl" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []

    for source_file in find_source_files(target_dir, config):
        if 'test' in source_file.name.lower():
            continue

        empty_funcs = find_empty_functions(source_file)
        if len(empty_funcs) < 2:
            continue

        try:
            rel_path = str(source_file.relative_to(target_dir))
        except ValueError:
            rel_path = str(source_file)

        func_names = [f["name"] for f in empty_funcs[:5]]

        issues.append(DoctorIssue(
            issue_type="INCOMPLETE_IMPL",
            severity="warning",
            path=rel_path,
            message=f"Contains {len(empty_funcs)} empty/incomplete function(s)",
            details={"empty_functions": empty_funcs},
            suggestion=f"Implement: {', '.join(func_names)}"
        ))

    return issues


def doctor_check_undoc_impl(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for files not referenced in IMPLEMENTATION docs."""
    if "undoc_impl" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    docs_dir = target_dir / "docs"

    if not docs_dir.exists():
        return issues

    documented_files = set()
    for impl_file in docs_dir.rglob("IMPLEMENTATION_*.md"):
        for ref in extract_impl_file_refs(impl_file):
            documented_files.add(ref.lower())
            documented_files.add(Path(ref).name.lower())

    for source_file in find_source_files(target_dir, config):
        if 'test' in source_file.name.lower():
            continue
        if count_lines(source_file) < 50:
            continue

        try:
            rel_path = str(source_file.relative_to(target_dir))
        except ValueError:
            rel_path = str(source_file)

        is_documented = (
            rel_path.lower() in documented_files or
            source_file.name.lower() in documented_files
        )

        if is_documented:
            continue

        issues.append(DoctorIssue(
            issue_type="UNDOC_IMPL",
            severity="info",
            path=rel_path,
            message="Not referenced in any IMPLEMENTATION doc",
            suggestion="Add to relevant IMPLEMENTATION_*.md"
        ))

    return issues
