# Prompt-specific and documentation coupling checks.
# DOCS: docs/mcp-design/doctor/IMPLEMENTATION_Project_Health_Doctor.md

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .doctor_files import find_source_files, should_ignore_path
from .doctor_types import DoctorConfig, DoctorIssue
from .prompt import PROMPT_VIEW_ENTRIES, generate_bootstrap_prompt

DOC_REFERENCE_SUBSTRINGS = [
    "/.mind/PROTOCOL.md",
    "/.mind/PRINCIPLES.md",
    "/.mind/state/SYNC_Project_State.md",
]


def _extract_docs_refs_from_code_file(source_file: Path, search_chars: int) -> List[str]:
    try:
        content = source_file.read_text()
    except Exception:
        return []

    pattern = re.compile(r'DOCS:\s*([^\s`"]+\.md)', re.IGNORECASE)
    snippet = content[:search_chars]
    return list(dict.fromkeys(pattern.findall(snippet)))


def _find_associated_sync_file(doc_path: Path, target_dir: Path) -> Optional[Path]:
    project_root = target_dir.resolve()
    current = doc_path.parent

    while current and str(current).startswith(str(project_root)):
        sync_candidates = list(current.glob("SYNC_*.md"))
        if sync_candidates:
            return max(sync_candidates, key=lambda p: p.stat().st_mtime if p.exists() else 0)
        if current == project_root:
            break
        current = current.parent

    fallback = project_root / ".mind" / "state" / "SYNC_Project_State.md"
    return fallback if fallback.exists() else None


def _format_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def doctor_check_prompt_doc_reference(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    if "prompt_doc_reference" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    try:
        prompt = generate_bootstrap_prompt(target_dir)
    except Exception as exc:
        issues.append(DoctorIssue(
            issue_type="PROMPT_DOC_REFERENCE",
            severity="critical",
            path="mind/prompt.py",
            message="Failed to render bootstrap prompt",
            details={"error": str(exc)},
            suggestion="Fix generate_bootstrap_prompt()"
        ))
        return issues

    missing = [s for s in DOC_REFERENCE_SUBSTRINGS if s not in prompt]

    if missing:
        issues.append(DoctorIssue(
            issue_type="PROMPT_DOC_REFERENCE",
            severity="critical",
            path="mind/prompt.py",
            message="Bootstrap prompt missing required doc references",
            details={"missing": missing},
            suggestion="Ensure PROTOCOL, PRINCIPLES, and state SYNC appear before the VIEW guidance"
        ))

    return issues


def doctor_check_prompt_view_table(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    if "prompt_view_table" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    try:
        prompt = generate_bootstrap_prompt(target_dir)
    except Exception:
        return issues

    missing = [view for _, view in PROMPT_VIEW_ENTRIES if view not in prompt]
    if missing:
        issues.append(DoctorIssue(
            issue_type="PROMPT_VIEW_TABLE",
            severity="warning",
            path="mind/prompt.py",
            message="Prompt VIEW table is missing rows",
            details={"missing": missing},
            suggestion="Keep PROMPT_VIEW_ENTRIES and the rendered table aligned"
        ))

    return issues


def doctor_check_prompt_checklist(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    if "prompt_checklist" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    try:
        prompt = generate_bootstrap_prompt(target_dir)
    except Exception:
        return issues

    required_phrases = {
        "checklist_header": "### Checklist",
        "sync_reminder": "Update SYNC files",
        "relaunch_cmd": "mind prompt --dir",
    }

    missing = [desc for desc, phrase in required_phrases.items() if phrase not in prompt]
    if missing:
        issues.append(DoctorIssue(
            issue_type="PROMPT_CHECKLIST",
            severity="warning",
            path="mind/prompt.py",
            message="Checklist block is incomplete or missing",
            details={"missing": missing},
            suggestion="Add the checklist reminding agents to update SYNC and rerun `mind prompt --dir`"
        ))

    return issues


def doctor_check_doc_link_integrity(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    if "doc_link_integrity" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    project_root = target_dir.resolve()

    for source_file in find_source_files(target_dir, config):
        if should_ignore_path(source_file, config.ignore, target_dir):
            continue

        doc_refs = _extract_docs_refs_from_code_file(source_file.resolve(), config.docs_ref_search_chars)
        if not doc_refs:
            continue

        missing_docs = []
        docs_without_ref = []

        for doc_ref in doc_refs:
            doc_path = (target_dir / doc_ref).resolve()
            if not doc_path.exists():
                missing_docs.append(doc_ref)
                continue

            if should_ignore_path(doc_path, config.ignore, target_dir):
                continue

            try:
                content = doc_path.read_text(errors="ignore")
            except Exception:
                continue

            try:
                rel_path = str(source_file.relative_to(target_dir))
            except ValueError:
                rel_path = str(source_file)

            if rel_path not in content and source_file.name not in content:
                try:
                    rel_doc = str(doc_path.relative_to(project_root))
                except ValueError:
                    rel_doc = str(doc_path)
                docs_without_ref.append(rel_doc)

        if missing_docs or docs_without_ref:
            try:
                issue_path = str(source_file.relative_to(project_root))
            except ValueError:
                issue_path = str(source_file)

            issues.append(DoctorIssue(
                issue_type="DOC_LINK_INTEGRITY",
                severity="warning",
                path=issue_path,
                message="Code file references docs but the bidirectional link is broken",
                details={
                    "missing_docs": missing_docs,
                    "docs_without_code_ref": docs_without_ref,
                },
                suggestion="Add the documents and ensure they mention the implementation file"
            ))

    return issues


def doctor_check_code_doc_delta_coupling(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    if "code_doc_delta" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    project_root = target_dir.resolve()

    for source_file in find_source_files(target_dir, config):
        if should_ignore_path(source_file, config.ignore, target_dir):
            continue

        doc_refs = _extract_docs_refs_from_code_file(source_file.resolve(), config.docs_ref_search_chars)
        if not doc_refs:
            continue

        try:
            code_mtime = source_file.stat().st_mtime
        except Exception:
            continue

        stale_entries = []

        for doc_ref in doc_refs:
            doc_path = (target_dir / doc_ref).resolve()
            if not doc_path.exists():
                continue

            if should_ignore_path(doc_path, config.ignore, target_dir):
                continue

            try:
                doc_mtime = doc_path.stat().st_mtime
            except Exception:
                continue

            sync_file = _find_associated_sync_file(doc_path, target_dir)
            sync_mtime = sync_file.stat().st_mtime if sync_file else 0
            latest_ref = max(doc_mtime, sync_mtime)

            if code_mtime > latest_ref + 1:
                try:
                    rel_doc = str(doc_path.relative_to(target_dir))
                except ValueError:
                    rel_doc = str(doc_path)

                stale_entries.append({
                    "doc": rel_doc,
                    "doc_mtime": _format_timestamp(doc_mtime),
                    "sync": str(sync_file.relative_to(project_root)) if sync_file else None,
                    "sync_mtime": _format_timestamp(sync_mtime) if sync_file else None,
                })

        if stale_entries:
            try:
                issue_path = str(source_file.relative_to(project_root))
            except ValueError:
                issue_path = str(source_file)

            issues.append(DoctorIssue(
                issue_type="CODE_DOC_DELTA_COUPLING",
                severity="warning",
                path=issue_path,
                message="Code changed without corresponding doc or SYNC updates",
                details={
                    "code_last_modified": _format_timestamp(code_mtime),
                    "stale_refs": stale_entries,
                },
                suggestion="Refresh referenced docs/SYNC entries"
            ))

    return issues
