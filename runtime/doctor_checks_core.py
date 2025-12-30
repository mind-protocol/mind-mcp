# Doctor check functions that analyze project structure.
# DOCS: docs/mcp-design/doctor/IMPLEMENTATION_Project_Health_Doctor.md

from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from .core_utils import HAS_YAML, IGNORED_EXTENSIONS
from .doctor_files import (
    count_lines,
    find_code_directories,
    find_long_sections,
    find_source_files,
    should_ignore_path,
)
from .doctor_types import DoctorConfig, DoctorIssue


def doctor_check_monolith(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for monolith files (too many lines)."""
    if "monolith" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    threshold = config.monolith_lines
    doc_extensions = {".md", ".txt", ".rst"}

    for source_file in find_source_files(target_dir, config):
        line_count = count_lines(source_file)

        if source_file.suffix.lower() in doc_extensions:
            effective_threshold = threshold * 2
        else:
            effective_threshold = threshold

        if line_count <= effective_threshold:
            continue

        try:
            rel_path = str(source_file.relative_to(target_dir))
        except ValueError:
            rel_path = str(source_file)

        long_sections = find_long_sections(source_file, min_lines=50)

        if long_sections:
            section_strs = [
                f"{s['kind']} {s['name']}() ({s['length']}L, :{s['line']})"
                for s in long_sections[:3]
            ]
            suggestion = "Split: " + ", ".join(section_strs)
        else:
            suggestion = "Consider splitting into smaller modules"

        issues.append(DoctorIssue(
            task_type="MONOLITH",
            severity="critical",
            path=rel_path,
            message=f"{line_count} lines (threshold: {effective_threshold})",
            details={
                "lines": line_count,
                "threshold": effective_threshold,
                "long_sections": long_sections,
            },
            suggestion=suggestion
        ))

    return issues


def doctor_check_undocumented(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for code directories without documentation."""
    if "undocumented" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    manifest_path = target_dir / "modules.yaml"
    mapped_paths = set()

    if manifest_path.exists() and HAS_YAML:
        try:
            import yaml

            with open(manifest_path) as f:
                data = yaml.safe_load(f) or {}
            for module_data in data.get("modules", {}).values():
                if isinstance(module_data, dict) and "code" in module_data:
                    code_val = module_data["code"]
                    if isinstance(code_val, list):
                        code_val = code_val[0] if code_val else ""
                    code_path = str(code_val).replace("/**", "").replace("/*", "")
                    mapped_paths.add(code_path)
        except Exception:
            pass

    for code_dir in find_code_directories(target_dir, config):
        if should_ignore_path(code_dir, config.ignore, target_dir):
            continue

        try:
            rel_path = str(code_dir.relative_to(target_dir))
        except ValueError:
            rel_path = str(code_dir)

        if any(
            rel_path.startswith(mapped) or mapped.startswith(rel_path)
            for mapped in mapped_paths
        ):
            continue

        file_count = sum(
            1 for f in code_dir.rglob("*")
            if f.is_file()
            and f.suffix.lower() not in IGNORED_EXTENSIONS
            and not should_ignore_path(f, config.ignore, target_dir)
        )

        issues.append(DoctorIssue(
            task_type="UNDOCUMENTED",
            severity="critical",
            path=rel_path,
            message=f"No documentation mapping ({file_count} files)",
            details={"file_count": file_count},
            suggestion="Add mapping to modules.yaml",
            protocol="define_space"  # Then call create_doc_chain
        ))

    return issues


def doctor_check_stale_sync(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for stale SYNC files."""
    if "stale_sync" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    threshold_date = datetime.now() - timedelta(days=config.stale_sync_days)
    sync_files = []
    protocol_dir = target_dir / ".mind"
    docs_dir = target_dir / "docs"

    if protocol_dir.exists():
        sync_files.extend(protocol_dir.rglob("SYNC_*.md"))
    if docs_dir.exists():
        sync_files.extend(docs_dir.rglob("SYNC_*.md"))

    for sync_file in sync_files:
        if should_ignore_path(sync_file, config.ignore, target_dir):
            continue

        try:
            content = sync_file.read_text()
        except Exception:
            continue

        last_updated = None
        for line in content.splitlines():
            if "LAST_UPDATED:" in line:
                date_str = line.split("LAST_UPDATED:")[1].strip()
                for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ"):
                    try:
                        last_updated = datetime.strptime(date_str[:10], fmt)
                        break
                    except ValueError:
                        continue
                if last_updated:
                    break

        if not last_updated or last_updated >= threshold_date:
            continue

        days_old = (datetime.now() - last_updated).days

        try:
            rel_path = str(sync_file.relative_to(target_dir))
        except ValueError:
            rel_path = str(sync_file)

        issues.append(DoctorIssue(
            task_type="STALE_SYNC",
            severity="warning",
            path=rel_path,
            message=f"Last updated {days_old} days ago",
            details={"days_old": days_old, "last_updated": str(last_updated.date())},
            suggestion="Review and update SYNC with current state",
            protocol="update_sync"
        ))

    return issues
