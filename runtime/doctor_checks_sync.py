"""
Doctor check functions for SYNC file analysis.

Health checks that analyze SYNC files for workflow state:
- Conflicts requiring human decision (ESCALATION)
- Incomplete gaps from previous sessions
- Agent suggestions awaiting action

DOCS: docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md
"""

from pathlib import Path
from typing import List, Dict, Any

from .doctor_types import DoctorIssue, DoctorConfig
from .doctor_files import should_ignore_path


def doctor_check_conflicts(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for CONFLICTS sections with ESCALATION items needing human decision."""
    issues = []

    if "ESCALATION" in config.disabled_checks:
        return issues

    # Search SYNC files for ## CONFLICTS sections
    search_paths = [
        target_dir / ".mind" / "state",
        target_dir / "docs",
    ]

    for search_dir in search_paths:
        if not search_dir.exists():
            continue

        for sync_file in search_dir.rglob("SYNC_*.md"):
            if should_ignore_path(sync_file, config.ignore, target_dir):
                continue

            try:
                content = sync_file.read_text()

                # Look for ## CONFLICTS section
                if "## CONFLICTS" not in content and "## Conflicts" not in content:
                    continue

                # Extract ESCALATION items (unresolved conflicts needing human input)
                escalation_items = []
                in_conflicts_section = False
                current_item = None

                for line in content.split("\n"):
                    if line.strip().startswith("## CONFLICTS") or line.strip().startswith("## Conflicts"):
                        in_conflicts_section = True
                        continue
                    elif line.strip().startswith("## ") and in_conflicts_section:
                        # Left CONFLICTS section
                        break
                    elif in_conflicts_section:
                        # Look for ESCALATION headers
                        if "### ESCALATION:" in line or "### Escalation:" in line:
                            if current_item:
                                escalation_items.append(current_item)
                            current_item = {"title": line.split(":", 1)[-1].strip(), "details": []}
                        elif current_item and line.strip().startswith("-"):
                            current_item["details"].append(line.strip().lstrip("- "))
                        elif line.strip().startswith("### DECISION") or line.strip().startswith("### Decision"):
                            # DECISION items are resolved, skip
                            if current_item:
                                escalation_items.append(current_item)
                            current_item = None

                if current_item:
                    escalation_items.append(current_item)

                if escalation_items:
                    rel_path = str(sync_file.relative_to(target_dir))
                    issues.append(DoctorIssue(
                        issue_type="ESCALATION",
                        severity="critical",  # Needs human decision
                        path=rel_path,
                        message=f"{len(escalation_items)} conflict(s) need human decision",
                        details={
                            "conflicts": [item["title"] for item in escalation_items],
                            "items": escalation_items[:5],
                        },
                        suggestion=f"Decide: {escalation_items[0]['title']}" if escalation_items else "",
                        protocol="resolve_blocker"
                    ))

            except Exception:
                pass

    return issues


def doctor_check_doc_gaps(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for GAPS sections left by previous agents in SYNC files."""
    issues = []

    if "DOC_GAPS" in config.disabled_checks:
        return issues

    # Search SYNC files for ## GAPS sections
    search_paths = [
        target_dir / ".mind" / "state",
        target_dir / "docs",
    ]

    for search_dir in search_paths:
        if not search_dir.exists():
            continue

        for sync_file in search_dir.rglob("SYNC_*.md"):
            if should_ignore_path(sync_file, config.ignore, target_dir):
                continue

            try:
                content = sync_file.read_text()

                # Look for ## GAPS section
                if "## GAPS" not in content and "## Gaps" not in content:
                    continue

                # Extract uncompleted items ([ ] not [x])
                uncompleted = []
                in_gaps_section = False

                for line in content.split("\n"):
                    if line.strip().startswith("## GAPS") or line.strip().startswith("## Gaps"):
                        in_gaps_section = True
                        continue
                    elif line.strip().startswith("## ") and in_gaps_section:
                        # Left GAPS section
                        break
                    elif in_gaps_section:
                        # Look for uncompleted checkboxes
                        if "[ ]" in line:
                            # Extract the task text
                            task = line.split("[ ]")[-1].strip().lstrip("- ")
                            if task:
                                uncompleted.append(task)

                if uncompleted:
                    rel_path = str(sync_file.relative_to(target_dir))
                    issues.append(DoctorIssue(
                        issue_type="DOC_GAPS",
                        severity="warning",
                        path=rel_path,
                        message=f"{len(uncompleted)} incomplete task(s) from previous session",
                        details={"gaps": uncompleted[:10], "total": len(uncompleted)},
                        suggestion=f"Complete: {uncompleted[0][:50]}..." if uncompleted else "",
                        protocol="record_work"
                    ))

            except Exception:
                pass

    return issues


def doctor_check_suggestions(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for agent suggestions in SYNC files that user can act on."""
    issues = []

    if "SUGGESTION" in config.disabled_checks:
        return issues

    # Search SYNC files for ### Suggestions sections
    search_paths = [
        target_dir / ".mind" / "state",
        target_dir / "docs",
    ]

    for search_dir in search_paths:
        if not search_dir.exists():
            continue

        for sync_file in search_dir.rglob("SYNC_*.md"):
            if should_ignore_path(sync_file, config.ignore, target_dir):
                continue

            try:
                content = sync_file.read_text()

                # Look for ### Suggestions section
                if "### Suggestions" not in content and "### suggestions" not in content:
                    continue

                # Extract uncompleted suggestions ([ ] not [x])
                suggestions = []
                in_suggestions_section = False

                for line in content.split("\n"):
                    if line.strip().startswith("### Suggestions") or line.strip().startswith("### suggestions"):
                        in_suggestions_section = True
                        continue
                    elif line.strip().startswith("### ") and in_suggestions_section:
                        # Left Suggestions section
                        break
                    elif line.strip().startswith("## ") and in_suggestions_section:
                        # Left to new major section
                        break
                    elif in_suggestions_section:
                        # Look for uncompleted checkboxes
                        if "[ ]" in line:
                            # Extract the suggestion text
                            suggestion_text = line.split("[ ]")[-1].strip().lstrip("- ")
                            # Remove HTML comments
                            if "<!--" in suggestion_text:
                                suggestion_text = suggestion_text.split("<!--")[0].strip()
                            if suggestion_text:
                                suggestions.append(suggestion_text)

                if suggestions:
                    rel_path = str(sync_file.relative_to(target_dir))
                    for suggestion in suggestions:
                        issues.append(DoctorIssue(
                            issue_type="SUGGESTION",
                            severity="info",
                            path=rel_path,
                            message=f"Agent suggestion: {suggestion[:60]}{'...' if len(suggestion) > 60 else ''}",
                            details={"suggestion": suggestion, "source_file": rel_path},
                            suggestion=suggestion
                        ))

            except Exception:
                pass

    return issues
