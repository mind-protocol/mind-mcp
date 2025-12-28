"""
Report generation for mind work command.

DOCS: docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md

This module contains:
- LLM-generated report via an agent CLI
- Fallback template-based report
- Report formatting and structure
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent_cli import build_agent_command, normalize_agent
from .work_core import WorkResult


# Prompt template for LLM-generated reports
REPORT_PROMPT = """You are generating a work report for an mind project.

Analyze the work session data and write a detailed, insightful report. Be specific about:
1. What patterns you see in the works (common issue types, areas of the codebase)
2. Why certain works may have failed
3. Concrete next steps for the human or next agent
4. Any systemic issues the works reveal about the project

Write in a direct, professional tone. Use markdown formatting.

## Work Session Data

**Project:** {project_name}
**Date:** {date}

### Health Score
- Before: {score_before}/100
- After: {score_after}/100
- Change: {score_change:+d}

### Issue Summary
- Critical before: {critical_before} → after: {critical_after}
- Warnings before: {warning_before} → after: {warning_after}

### Works Attempted ({total_works})
**Successful ({success_count}):**
{successful_list}

**Failed ({failed_count}):**
{failed_list}

**Total Duration:** {total_duration:.1f} seconds

### Decisions Made by Agents
{decisions_list}

### Remaining Issues
Critical: {remaining_critical}
Warnings: {remaining_warning}

---

Write the report now. Include:
1. Executive Summary (2-3 sentences)
2. What Was Fixed (with insights, not just a list)
3. Decisions Made (highlight key choices agents made and their reasoning)
4. What Failed and Why (analysis)
5. Patterns Observed (what do these issues say about the codebase?)
6. Recommended Next Steps (specific, actionable)
7. For Next Agent (handoff notes)
"""


def generate_llm_report(
    before_results: Dict[str, Any],
    after_results: Dict[str, Any],
    work_results: List[WorkResult],
    target_dir: Path,
    colors: Optional[Any] = None,
    agent_provider: str = "codex",
) -> Optional[str]:
    """Generate a detailed report using an agent.

    Args:
        before_results: Doctor results before works
        after_results: Doctor results after works
        work_results: List of WorkResult from each agent
        target_dir: Project directory
        colors: Optional Colors class for CLI output formatting
        agent_provider: Agent provider name (claude or codex)

    Returns:
        Generated report markdown, or None if generation fails
    """
    successful = [r for r in work_results if r.success]
    failed = [r for r in work_results if not r.success]

    successful_list = "\n".join(
        f"- {r.issue_type}: `{r.target_path}` ({r.duration_seconds:.1f}s)"
        for r in successful
    ) or "None"

    failed_list = "\n".join(
        f"- {r.issue_type}: `{r.target_path}` — {r.error or 'unknown error'}"
        for r in failed
    ) or "None"

    # Collect all decisions made
    all_decisions = []
    for r in work_results:
        if r.decisions_made:
            for d in r.decisions_made:
                all_decisions.append(
                    f"- **{d.get('name', 'Unknown')}**: {d.get('resolution', 'No resolution')} "
                    f"(Reason: {d.get('reasoning', 'Not stated')})"
                )
    decisions_list = "\n".join(all_decisions) or "None"

    prompt = REPORT_PROMPT.format(
        project_name=target_dir.name,
        date=datetime.now().strftime('%Y-%m-%d %H:%M'),
        score_before=before_results["score"],
        score_after=after_results["score"],
        score_change=after_results["score"] - before_results["score"],
        critical_before=before_results["summary"]["critical"],
        critical_after=after_results["summary"]["critical"],
        warning_before=before_results["summary"]["warning"],
        warning_after=after_results["summary"]["warning"],
        total_works=len(work_results),
        success_count=len(successful),
        failed_count=len(failed),
        successful_list=successful_list,
        failed_list=failed_list,
        decisions_list=decisions_list,
        total_duration=sum(r.duration_seconds for r in work_results),
        remaining_critical=after_results["summary"]["critical"],
        remaining_warning=after_results["summary"]["warning"],
    )

    agent_provider = normalize_agent(agent_provider)

    try:
        agent_cmd = build_agent_command(
            agent_provider,
            prompt=prompt,
            stream_json=False,
            continue_session=False,
            use_dangerous=True,
        )

        result = subprocess.run(
            agent_cmd.cmd,
            cwd=target_dir,
            capture_output=True,
            text=True,
            input=(agent_cmd.stdin + "\n") if agent_cmd.stdin else None,
            timeout=60,
        )

        if result.returncode == 0 and result.stdout.strip():
            # Add header
            header = f"""# mind Work Report

```
GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M')}
PROJECT: {target_dir.name}
GENERATED_BY: {agent_provider}
```

---

"""
            return header + result.stdout.strip()
    except Exception as e:
        # Print error if colors provided (CLI context)
        if colors:
            print(f"  {colors.DIM}(LLM report failed: {e}, using fallback){colors.RESET}")

    return None


def generate_final_report(
    before_results: Dict[str, Any],
    after_results: Dict[str, Any],
    work_results: List[WorkResult],
    target_dir: Path,
) -> str:
    """Generate a final report summarizing all works (fallback if LLM fails).

    Args:
        before_results: Doctor results before works
        after_results: Doctor results after works
        work_results: List of WorkResult from each agent
        target_dir: Project directory

    Returns:
        Generated report markdown
    """
    # Calculate improvements
    score_before = before_results["score"]
    score_after = after_results["score"]
    score_change = score_after - score_before

    critical_before = before_results["summary"]["critical"]
    critical_after = after_results["summary"]["critical"]

    successful = [r for r in work_results if r.success]
    failed = [r for r in work_results if not r.success]

    total_duration = sum(r.duration_seconds for r in work_results)

    lines = []
    lines.append("# mind Work Report")
    lines.append("")
    lines.append("```")
    lines.append(f"GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"PROJECT: {target_dir.name}")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Before | After | Change |")
    lines.append("|--------|--------|-------|--------|")
    lines.append(f"| Health Score | {score_before}/100 | {score_after}/100 | {'+' if score_change >= 0 else ''}{score_change} |")
    lines.append(f"| Critical Issues | {critical_before} | {critical_after} | {critical_before - critical_after} fixed |")
    lines.append(f"| Warnings | {before_results['summary']['warning']} | {after_results['summary']['warning']} | - |")
    lines.append("")

    # Works attempted
    lines.append("## Works Attempted")
    lines.append("")
    lines.append(f"**Total:** {len(work_results)} issues")
    lines.append(f"**Successful:** {len(successful)}")
    lines.append(f"**Failed:** {len(failed)}")
    lines.append(f"**Duration:** {total_duration:.1f} seconds")
    lines.append("")

    if successful:
        lines.append("### Successful Works")
        lines.append("")
        for r in successful:
            lines.append(f"- **{r.issue_type}**: `{r.target_path}` ({r.duration_seconds:.1f}s)")
        lines.append("")

    if failed:
        lines.append("### Failed Works")
        lines.append("")
        for r in failed:
            lines.append(f"- **{r.issue_type}**: `{r.target_path}`")
            if r.error:
                lines.append(f"  - Error: {r.error}")
        lines.append("")

    # Decisions made
    all_decisions = []
    for r in work_results:
        if r.decisions_made:
            all_decisions.extend(r.decisions_made)

    if all_decisions:
        lines.append("## Decisions Made")
        lines.append("")
        lines.append("Agents made the following decisions to resolve conflicts:")
        lines.append("")
        for d in all_decisions:
            lines.append(f"### {d.get('name', 'Unknown')}")
            if d.get('conflict'):
                lines.append(f"- **Conflict:** {d['conflict']}")
            if d.get('resolution'):
                lines.append(f"- **Resolution:** {d['resolution']}")
            if d.get('reasoning'):
                lines.append(f"- **Reasoning:** {d['reasoning']}")
            if d.get('updated'):
                lines.append(f"- **Updated:** {d['updated']}")
            lines.append("")

    # Remaining issues
    if after_results["summary"]["critical"] > 0 or after_results["summary"]["warning"] > 0:
        lines.append("## Remaining Issues")
        lines.append("")
        lines.append("Run `mind doctor` for details on remaining issues.")
        lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")

    if score_after >= 80:
        lines.append("Project health is good. Continue with normal development.")
    elif score_after >= 50:
        lines.append("Project health is improving. Consider running work again to address remaining issues.")
    else:
        lines.append("Project still has critical issues. Manual intervention may be needed for complex cases.")
    lines.append("")

    if failed:
        lines.append("### Failed Works Need Attention")
        lines.append("")
        lines.append("The following issues could not be automatically worked:")
        for r in failed:
            lines.append(f"- `{r.target_path}`: {r.error or 'Unknown error'}")
        lines.append("")
        lines.append("Consider fixing these manually using the appropriate VIEW.")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by `mind work`*")

    return "\n".join(lines)
