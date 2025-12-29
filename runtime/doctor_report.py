"""
Doctor report generation and output functions.

Extracted from doctor.py to reduce monolith file size.
Contains:
- get_issue_guidance: Returns VIEW and file guidance for each issue type
- get_issue_explanation: Returns natural language explanations for issues
- generate_health_markdown: Generates SYNC-formatted health report
- print_doctor_report: Prints doctor results in text or JSON format
- check_sync_status: Quick check of SYNC file status
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .doctor_types import DoctorIssue


def get_issue_guidance(issue_type: str) -> Dict[str, str]:
    """Get VIEW and file guidance for each issue type."""
    guidance = {
        "MONOLITH": {
            "view": "VIEW_Refactor_Improve_Code_Structure.md",
            "file": "Split into smaller modules",
            "tip": "Extract related functions into separate files"
        },
        "UNDOCUMENTED": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "file": "modules.yaml",
            "tip": "Add module mapping, then create PATTERNS + SYNC docs"
        },
        "STALE_SYNC": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "file": "The SYNC file itself",
            "tip": "Update LAST_UPDATED date and review content"
        },
        "PLACEHOLDER": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "file": "The doc file with placeholders",
            "tip": "Replace {PLACEHOLDER} markers with actual content"
        },
        "INCOMPLETE_CHAIN": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "file": "The module's docs/ folder",
            "tip": "Create missing doc types (PATTERNS, BEHAVIORS, etc.)"
        },
        "NO_DOCS_REF": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "file": "The source file header",
            "tip": "Add: # DOCS: path/to/PATTERNS.md"
        },
        "BROKEN_IMPL_LINK": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "file": "The IMPLEMENTATION doc",
            "tip": "Update file references to match actual paths"
        },
        "STUB_IMPL": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "file": "The stub file",
            "tip": "Implement the placeholder functions"
        },
        "INCOMPLETE_IMPL": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "file": "The incomplete file",
            "tip": "Fill in empty functions"
        },
        "UNDOC_IMPL": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "file": "Relevant IMPLEMENTATION_*.md",
            "tip": "Add file reference to IMPLEMENTATION doc"
        },
        "LARGE_DOC_MODULE": {
            "view": "VIEW_Refactor_Improve_Code_Structure.md",
            "file": "The module's doc folder",
            "tip": "Split large docs or archive old content"
        },
        "YAML_DRIFT": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "file": "modules.yaml",
            "tip": "Update paths to match reality or remove stale modules"
        },
        "DOC_GAPS": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "file": "The SYNC file with GAPS section",
            "tip": "Complete the tasks listed in GAPS, then mark them [x] or remove the section"
        },
        "ESCALATION": {
            "view": "VIEW_Specify_Design_Vision_And_Architecture.md",
            "file": "The SYNC file with CONFLICTS section",
            "tip": "Make a design decision, update conflicting docs/code to be consistent"
        },
        "RESOLVE_ESCALATION": {
            "view": "VIEW_Escalation_How_To_Handle_Vague_Tasks_Missing_Information_And_Complex_Non-Obvious_Problems.md",
            "file": "The file containing @mind:solved-escalations",
            "tip": "Apply the response, update docs/code, then remove the solved marker"
        },
        "LOG_ERROR": {
            "view": "VIEW_Debug_Investigate_And_Fix_Issues.md",
            "file": "Recent .log file",
            "tip": "Inspect the error line and trace the root cause"
        },
        "PROMPT_DOC_REFERENCE": {
            "view": "VIEW_Health_Define_Health_Checks_And_Verify.md",
            "file": "mind/prompt.py",
            "tip": "Make sure PROTOCOL, PRINCIPLES, and SYNC paths stay in the introduction section"
        },
        "PROMPT_VIEW_TABLE": {
            "view": "VIEW_Health_Define_Health_Checks_And_Verify.md",
            "file": "mind/prompt.py",
            "tip": "Keep the PROMPT_VIEW_ENTRIES list aligned with the rendered table"
        },
        "PROMPT_CHECKLIST": {
            "view": "VIEW_Health_Define_Health_Checks_And_Verify.md",
            "file": "mind/prompt.py",
            "tip": "Finish the bootstrap prompt with the checklist that reminds the agent to update SYNC and rerun `mind prompt --dir`"
        },
        "DOC_LINK_INTEGRITY": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "file": "The code file header + referenced docs",
            "tip": "Add missing docs or mention the code file inside the doc's IMPL/CHAIN section"
        },
        "CODE_DOC_DELTA_COUPLING": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "file": "The doc/SYNC pair",
            "tip": "Update the associated docs or SYNC file whenever the code changes"
        },
        "DOCS_NOT_INGESTED": {
            "view": "VIEW_Ingest_Process_Raw_Data_Sources.md",
            "file": "The doc file to ingest",
            "tip": "Ingest into graph following chain order (OBJECTIVES first), then archive to data/archive/docs/"
        },
    }
    return guidance.get(issue_type, {"view": "VIEW_Implement_Write_Or_Modify_Code.md", "file": "", "tip": ""})


def get_issue_explanation(issue_type: str) -> Dict[str, str]:
    """Get natural language explanation for each issue type."""
    explanations = {
        "MONOLITH": {
            "risk": "Large files are hard to navigate, test, and maintain. They slow down agents who need to load context, and changes become risky because side effects are hard to predict.",
            "action": "Extract cohesive functionality into separate modules. Start with the largest functions/classes listed above.",
        },
        "UNDOCUMENTED": {
            "risk": "Code without documentation becomes a black box. Agents will reverse-engineer intent from implementation, make changes that violate invisible design decisions, or duplicate existing patterns.",
            "action": "Add a mapping in modules.yaml (project root), then create at minimum PATTERNS + SYNC docs for the module.",
        },
        "STALE_SYNC": {
            "risk": "Outdated SYNC files mislead agents about current state. They may work from wrong assumptions or miss important context about recent changes.",
            "action": "Review the SYNC file, update LAST_UPDATED, and ensure it reflects what actually exists.",
        },
        "PLACEHOLDER": {
            "risk": "Template placeholders mean the documentation was started but never completed. Agents loading these docs get no useful information.",
            "action": "Fill in the placeholders with actual content, or delete the file if it's not needed yet.",
        },
        "INCOMPLETE_CHAIN": {
            "risk": "Missing doc types mean agents can't answer certain questions about the module. For example, without IMPLEMENTATION, they don't know where code lives or how data flows.",
            "action": "Create the missing doc types using templates from .mind/templates/.",
        },
        "NO_DOCS_REF": {
            "risk": "Without a DOCS: reference, the bidirectional link is broken. Agents reading code can't find the design docs, and `mind context` won't work.",
            "action": "Add a comment like `# DOCS: docs/path/to/PATTERNS_*.md` near the top of the file.",
        },
        "BROKEN_IMPL_LINK": {
            "risk": "IMPLEMENTATION docs reference files that don't exist. Agents following these docs will waste time looking for non-existent code.",
            "action": "Update file paths in the IMPLEMENTATION doc to match actual locations, or remove references to deleted files.",
        },
        "STUB_IMPL": {
            "risk": "Stub implementations (TODO, NotImplementedError, pass) are placeholders that don't actually work. The code looks complete but fails at runtime.",
            "action": "Implement the stub functions with actual logic, or mark the file as incomplete in SYNC.",
        },
        "INCOMPLETE_IMPL": {
            "risk": "Empty functions indicate incomplete implementation. The interface exists but the behavior doesn't.",
            "action": "Fill in the empty functions with actual implementation.",
        },
        "UNDOC_IMPL": {
            "risk": "Implementation files not referenced in IMPLEMENTATION docs become invisible. Agents won't know they exist when trying to understand the codebase.",
            "action": "Add the file to the relevant IMPLEMENTATION_*.md with a brief description of its role.",
        },
        "LARGE_DOC_MODULE": {
            "risk": "Large doc modules consume significant context window when loaded. Agents may not be able to load everything they need.",
            "action": "Archive old sections to dated files, split into sub-modules, or remove redundant content.",
        },
        "YAML_DRIFT": {
            "risk": "modules.yaml references paths that don't exist. Agents trusting this manifest will look for code/docs that aren't there, wasting time and causing confusion.",
            "action": "Update modules.yaml to match current file structure, or create the missing paths, or remove stale module entries.",
        },
        "DOC_GAPS": {
            "risk": "A previous agent couldn't complete all work and left tasks in a GAPS section. These represent incomplete implementations, missing docs, or decisions that needed human input.",
            "action": "Read the GAPS section in the SYNC file, complete the listed tasks, and mark them [x] done or remove the section when finished.",
        },
        "ESCALATION": {
            "risk": "Documentation or code contradicts itself. Agents found conflicts they couldn't resolve - either docs say different things, or docs don't match implementation. This causes confusion and inconsistent behavior.",
            "action": "Review the CONFLICTS section, make a design decision for each ESCALATION item, update all conflicting sources to be consistent, then convert ESCALATION to DECISION (resolved).",
        },
        "RESOLVE_ESCALATION": {
            "risk": "Resolved escalation markers left in place can accumulate and hide real blockers. They should be applied and cleared.",
            "action": "Apply the response to docs/code, then remove the @mind:solved-escalations marker.",
        },
        "LOG_ERROR": {
            "risk": "Recent log errors may indicate runtime failures or misconfigurations that are not captured by code-only checks.",
            "action": "Review the error line in the log, identify the failing component, and address the underlying issue.",
        },
        "PROMPT_DOC_REFERENCE": {
            "risk": "Missing doc references in the bootstrap prompt leaves agents without the protocol anchors they need.",
            "action": "Restore the PROTOCOL/PRINCIPLES/SYNC references before the VIEW table."
        },
        "PROMPT_VIEW_TABLE": {
            "risk": "A truncated VIEW table steers agents to the wrong guidance or hides the task they intended to run.",
            "action": "Render every row defined in PROMPT_VIEW_ENTRIES and confirm each view file appears."
        },
        "PROMPT_CHECKLIST": {
            "risk": "Without the final checklist, agents may skip updating SYNC or forget how to rediscover the bootstrap instructions.",
            "action": "Finish the prompt with the checklist block that references SYNC and `mind prompt --dir`."
        },
        "DOC_LINK_INTEGRITY": {
            "risk": "Code pointing to nonexistent docs or docs that do not mention the code breaks the bidirectional documentation chain.",
            "action": "Add the referenced docs and mention the code file (IMPL/chain entries) so agents can travel both directions."
        },
        "CODE_DOC_DELTA_COUPLING": {
            "risk": "Code changes that are not reflected in docs or SYNC leave the documentation stale and untrustworthy.",
            "action": "Update the doc or SYNC file after modifying the code so the timestamps stay coupled."
        },
        "DOCS_NOT_INGESTED": {
            "risk": "Documentation files not ingested into the graph cannot be queried by agents. Knowledge remains siloed in files instead of being connected in the graph for traversal and context loading.",
            "action": "Ingest docs into graph module-by-module, following chain order (OBJECTIVES first, then BEHAVIORS, PATTERNS, etc.). After ingestion, archive original files to data/archive/docs/."
        },
    }
    return explanations.get(issue_type, {"risk": "This issue may cause problems.", "action": "Review and fix."})


def generate_health_markdown(results: Dict[str, Any], github_issues: List = None) -> str:
    """Generate SYNC-formatted health report with natural language explanations."""
    # Build a mapping of path -> GitHub issue for quick lookup
    gh_issue_map = {}
    if github_issues:
        for gh in github_issues:
            gh_issue_map[gh.path] = gh

    lines = []

    # Header in SYNC format
    lines.append("# SYNC: Project Health")
    lines.append("")
    lines.append("```")
    lines.append(f"LAST_UPDATED: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("UPDATED_BY: mind doctor")
    score = results['score']
    if score >= 80:
        status = "HEALTHY"
    elif score >= 50:
        status = "NEEDS_ATTENTION"
    else:
        status = "CRITICAL"
    lines.append(f"STATUS: {status}")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Current State section
    lines.append("## CURRENT STATE")
    lines.append("")
    lines.append(f"**Health Score:** {score}/100")
    lines.append("")

    if score >= 80:
        lines.append("The project is in good health. Documentation is up to date and code is well-structured.")
    elif score >= 50:
        lines.append("The project needs attention. Some documentation is stale or incomplete, which may slow down agents.")
    else:
        lines.append("The project has critical issues that will significantly impact agent effectiveness. Address these before starting new work.")
    lines.append("")

    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| Critical | {results['summary']['critical']} |")
    lines.append(f"| Warning | {results['summary']['warning']} |")
    lines.append(f"| Info | {results['summary']['info']} |")
    lines.append("")

    # Group issues by type for better organization
    critical = results["issues"]["critical"]
    warnings = results["issues"]["warning"]

    if critical or warnings:
        lines.append("---")
        lines.append("")
        lines.append("## ISSUES")
        lines.append("")

    # Group critical issues by type
    if critical:
        issues_by_type = {}
        for issue in critical:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = []
            issues_by_type[issue.issue_type].append(issue)

        for issue_type, issues in issues_by_type.items():
            guidance = get_issue_guidance(issue_type)
            explanation = get_issue_explanation(issue_type)

            lines.append(f"### {issue_type} ({len(issues)} files)")
            lines.append("")
            lines.append(f"**What's wrong:** {explanation['risk']}")
            lines.append("")
            lines.append(f"**How to fix:** {explanation['action']}")
            lines.append("")
            lines.append(f"**Protocol:** Load `{guidance['view']}` before starting.")
            lines.append("")
            lines.append("**Files:**")
            lines.append("")

            for issue in issues[:10]:  # Limit to 10 per type
                gh = gh_issue_map.get(issue.path)
                gh_link = f" [#{gh.number}]({gh.url})" if gh else ""
                id_ref = f" `{issue.id}`" if issue.id else ""
                if issue.suggestion and issue.suggestion != "Consider splitting into smaller modules":
                    lines.append(f"- `{issue.path}`{gh_link}{id_ref} - {issue.message}")
                    lines.append(f"  - {issue.suggestion}")
                else:
                    lines.append(f"- `{issue.path}`{gh_link}{id_ref} - {issue.message}")

            if len(issues) > 10:
                lines.append(f"- ... and {len(issues) - 10} more")
            lines.append("")

    # Group warnings by type
    if warnings:
        issues_by_type = {}
        for issue in warnings:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = []
            issues_by_type[issue.issue_type].append(issue)

        for issue_type, issues in issues_by_type.items():
            guidance = get_issue_guidance(issue_type)
            explanation = get_issue_explanation(issue_type)

            lines.append(f"### {issue_type} ({len(issues)} files)")
            lines.append("")
            lines.append(f"**What's wrong:** {explanation['risk']}")
            lines.append("")
            lines.append(f"**How to fix:** {explanation['action']}")
            lines.append("")
            lines.append(f"**Protocol:** Load `{guidance['view']}` before starting.")
            lines.append("")
            lines.append("**Files:**")
            lines.append("")

            for issue in issues[:10]:
                gh = gh_issue_map.get(issue.path)
                gh_link = f" [#{gh.number}]({gh.url})" if gh else ""
                id_ref = f" `{issue.id}`" if issue.id else ""
                lines.append(f"- `{issue.path}`{gh_link}{id_ref} - {issue.message}")

            if len(issues) > 10:
                lines.append(f"- ... and {len(issues) - 10} more")
            lines.append("")

    # Info as Later section
    info = results["issues"]["info"]
    if info:
        lines.append("---")
        lines.append("")
        lines.append("## LATER")
        lines.append("")
        lines.append("These are minor issues that don't block work but would improve project health:")
        lines.append("")
        for issue in info[:10]:
            lines.append(f"- [ ] `{issue.path}` - {issue.message}")
        if len(info) > 10:
            lines.append(f"- ... and {len(info) - 10} more")
        lines.append("")

    # Handoff section
    lines.append("---")
    lines.append("")
    lines.append("## HANDOFF")
    lines.append("")

    if critical:
        lines.append("**For the next agent:**")
        lines.append("")
        lines.append("Before starting your task, consider addressing critical issues - especially if your work touches affected files. Monoliths and undocumented code will slow you down.")
        lines.append("")
        lines.append("**Recommended first action:** Pick one MONOLITH file you'll be working in and split its largest function into a separate module.")
    elif warnings:
        lines.append("**For the next agent:**")
        lines.append("")
        lines.append("The project is in reasonable shape. If you have time, update any stale SYNC files related to your work area.")
    else:
        lines.append("**For the next agent:**")
        lines.append("")
        lines.append("Project health is good. Focus on your task.")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by `mind doctor`*")

    return "\n".join(lines)


def print_doctor_report(results: Dict[str, Any], output_format: str = "text"):
    """Print doctor results in specified format."""
    if output_format == "json":
        # Convert DoctorIssue objects to dicts
        json_results = {
            "project": results["project"],
            "score": results["score"],
            "summary": results["summary"],
            "issues": {
                severity: [
                    {
                        "id": issue.id,
                        "type": issue.issue_type,
                        "path": issue.path,
                        "message": issue.message,
                        "details": issue.details,
                        "suggestion": issue.suggestion,
                        "protocol": issue.protocol,
                    }
                    for issue in issues
                ]
                for severity, issues in results["issues"].items()
            }
        }
        print(json.dumps(json_results, indent=2))
        return

    # Text format
    project_name = Path(results["project"]).name
    print(f"Project Health Report: {project_name}")
    print("=" * 50)
    print()

    # Critical issues
    critical = results["issues"]["critical"]
    if critical:
        print(f"## Critical ({len(critical)} issues)")
        print()
        for issue in critical:
            guidance = get_issue_guidance(issue.issue_type)
            id_suffix = f" [{issue.id}]" if issue.id else ""
            print(f"  X {issue.issue_type}: {issue.path}{id_suffix}")
            print(f"    {issue.message}")
            if issue.suggestion:
                print(f"    -> {issue.suggestion}")
            print(f"    View: {guidance['view']}")
            print()

    # Warnings
    warnings = results["issues"]["warning"]
    if warnings:
        print(f"## Warnings ({len(warnings)} issues)")
        print()
        for issue in warnings:
            guidance = get_issue_guidance(issue.issue_type)
            id_suffix = f" [{issue.id}]" if issue.id else ""
            print(f"  ! {issue.issue_type}: {issue.path}{id_suffix}")
            print(f"    {issue.message}")
            if issue.suggestion:
                print(f"    -> {issue.suggestion}")
            print(f"    View: {guidance['view']}")
            print()

    # Info
    info = results["issues"]["info"]
    if info:
        print(f"## Info ({len(info)} issues)")
        print()
        for issue in info[:5]:  # Limit info display
            id_suffix = f" [{issue.id}]" if issue.id else ""
            print(f"  i {issue.issue_type}: {issue.path}{id_suffix}")
            print(f"    {issue.message}")
        if len(info) > 5:
            print(f"  ... and {len(info) - 5} more")
        print()

    # Summary
    print("-" * 50)
    print(f"Health Score: {results['score']}/100")
    ignored_count = results.get('ignored_count', 0)
    false_positive_count = results.get('false_positive_count', 0)
    summary_line = f"Critical: {results['summary']['critical']} | Warnings: {results['summary']['warning']} | Info: {results['summary']['info']}"
    if ignored_count > 0:
        summary_line += f" | Suppressed: {ignored_count}"
    if false_positive_count > 0:
        summary_line += f" | False positives: {false_positive_count}"
    print(summary_line)
    print("-" * 50)

    # Suggested actions
    if critical or warnings:
        print()
        print("## Suggested Actions")
        print()
        action_num = 1
        for issue in critical[:3]:
            print(f"{action_num}. [ ] Fix {issue.issue_type.lower()}: {issue.path}")
            action_num += 1
        for issue in warnings[:2]:
            print(f"{action_num}. [ ] Address {issue.issue_type.lower()}: {issue.path}")
            action_num += 1
        print()


def check_sync_status(target_dir: Path) -> Dict[str, int]:
    """Quick check of SYNC file status for doctor report."""
    stale_count = 0
    large_count = 0
    threshold_days = 14
    max_lines = 200
    now = datetime.now()

    search_paths = [
        target_dir / ".mind" / "state",
        target_dir / "docs",
    ]

    for search_dir in search_paths:
        if not search_dir.exists():
            continue

        for sync_file in search_dir.rglob("SYNC_*.md"):
            try:
                content = sync_file.read_text()
                lines = content.split('\n')

                # Check size
                if len(lines) > max_lines:
                    large_count += 1

                # Check date
                for line in lines[:30]:
                    if 'LAST_UPDATED:' in line:
                        date_str = line.split('LAST_UPDATED:')[1].strip()[:10]
                        try:
                            last_updated = datetime.strptime(date_str, "%Y-%m-%d")
                            if (now - last_updated).days > threshold_days:
                                stale_count += 1
                        except ValueError:
                            pass
                        break
            except Exception:
                continue

    return {"stale": stale_count, "large": large_count}
