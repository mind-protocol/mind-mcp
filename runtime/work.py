"""
Work command for mind CLI.

Automatically fixes project health issues by spawning work agents.
Each agent follows the protocol: read docs, fix issue, update SYNC.
"""
# DOCS: docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md

import asyncio
import json
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import List, Dict, Any, Optional

from .doctor import run_doctor, load_doctor_config, DoctorIssue
from .doctor_types import DoctorConfig
from .work_instructions import get_issue_instructions
from .work_report import generate_llm_report, generate_final_report
from .agent_cli import build_agent_command, normalize_agent
from .work_core import (
    ISSUE_PRIORITY,
    AGENT_SYMBOLS,
    AGENT_SYSTEM_PROMPT,
    WorkResult,
    EscalationDecision,
    get_learnings_content,
    get_issue_symbol,
    get_issue_action_parts,
    get_depth_types,
    build_agent_prompt,
    parse_decisions_from_output,
    spawn_work_agent_async,
    spawn_work_agent_with_verification_async,
)
from .work_escalation_interactive import (
    Colors,
    color,
    print_progress_bar,
    input_listener_thread,
    check_for_manager_input,
    resolve_escalation_interactive,
    reset_manager_state,
    stop_manager_listener,
)


# CLI-specific helper functions (using imported constants from work_core)
# NOTE: These are intentionally simple one-line utility functions.
# They provide semantic meaning to common operations (color lookup, symbol lookup, text wrapping).
# Short body does not mean incomplete - these are complete implementations.

def get_severity_color(severity: str) -> str:
    """Get color code for severity level."""
    return {
        "critical": Colors.FAILURE,
        "warning": Colors.WARNING,
        "info": Colors.DIM,
    }.get(severity, Colors.RESET)


def get_agent_color(agent_id: int) -> str:
    """Get color code for an agent by cycling through available colors."""
    colors = Colors.AGENT_COLORS
    if not colors:
        return Colors.RESET
    return colors[agent_id % len(colors)]


def get_agent_symbol(agent_id: int) -> str:
    """Get visual symbol for an agent by cycling through available symbols."""
    symbols = AGENT_SYMBOLS
    if not symbols:
        return "→"
    return symbols[agent_id % len(symbols)]


def load_github_issue_mapping(target_dir: Path) -> Dict[str, int]:
    """Load GitHub issue mapping from health report or tracking file."""
    mapping = {}

    # Try to load from a tracking file first
    tracking_path = target_dir / ".mind" / "state" / "github_issues.json"
    if tracking_path.exists():
        try:
            import json
            with open(tracking_path) as f:
                data = json.load(f)
                return {k: v["number"] for k, v in data.items()}
        except Exception:
            pass

    return mapping


def save_github_issue_mapping(target_dir: Path, mapping: Dict[str, Dict[str, Any]]) -> None:
    """Save GitHub issue mapping to tracking file."""
    tracking_path = target_dir / ".mind" / "state" / "github_issues.json"
    if tracking_path.parent.exists():
        import json
        with open(tracking_path, "w") as f:
            json.dump(mapping, f, indent=2)


# Core work logic (DEPTH_*, WorkResult, EscalationDecision, AGENT_SYSTEM_PROMPT,
# build_agent_prompt, parse_decisions_from_output, etc.) imported from work_core.py


def spawn_work_agent(
    issue: DoctorIssue,
    target_dir: Path,
    config: DoctorConfig, # New: DoctorConfig to manage fallback status
    dry_run: bool = False,
    github_issue_number: Optional[int] = None,
    escalation_decisions: Optional[List['EscalationDecision']] = None,
    agent_symbol: str = "→",
    agent_provider: str = "codex",
) -> WorkResult:
    """Spawn a work agent to fix a single issue."""
    agent_provider = normalize_agent(agent_provider)

    instructions = get_issue_instructions(issue, target_dir)

    # For ESCALATION issues, inject the human decisions into the prompt
    if issue.issue_type == "ESCALATION" and escalation_decisions:
        decisions_text = "\n".join(
            f"- **{d.conflict_title}**: {d.decision}"
            for d in escalation_decisions if not d.passed
        )
        instructions["prompt"] = instructions["prompt"].replace(
            "{escalation_decisions}",
            decisions_text or "(No decisions provided)"
        )
    elif issue.issue_type == "ESCALATION":
        instructions["prompt"] = instructions["prompt"].replace(
            "{escalation_decisions}",
            "(No decisions provided - skip this issue)"
        )

    prompt = build_agent_prompt(issue, instructions, target_dir, github_issue_number)

    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN: Would spawn agent for {issue.issue_type}")
        print(f"Target: {issue.path}")
        print(f"VIEW: {instructions['view']}")
        if github_issue_number:
            print(f"GitHub Issue: #{github_issue_number}")
        print(f"{'='*60}")
        print(prompt)
        return WorkResult(
            issue_type=issue.issue_type,
            target_path=issue.path,
            success=True,
            agent_output="[DRY RUN]",
            duration_seconds=0,
        )

    # Build system prompt with learnings
    system_prompt = AGENT_SYSTEM_PROMPT + get_learnings_content(target_dir)

    async def _on_output(output: str):
        pass

    # The actual agent spawning is in work_core.py
    # Use verification-enabled version for mandatory checks
    return asyncio.run(spawn_work_agent_with_verification_async(
        issue=issue,
        target_dir=target_dir,
        on_output=_on_output,
        instructions=instructions,
        config=config,
        github_issue_number=github_issue_number,
        escalation_decisions=escalation_decisions,
        agent_symbol=agent_symbol,
        agent_provider=agent_provider,
        max_verification_retries=3,
        membrane_query=None,  # TODO: Connect to membrane MCP
    ))


# print_progress_bar, input_listener_thread, spawn_manager_agent,
# check_for_manager_input, resolve_escalation_interactive imported from work_escalation_interactive.py


def work_command(
    target_dir: Path,
    max_issues: Optional[int] = None,
    issue_types: Optional[List[str]] = None,
    depth: str = "docs",
    dry_run: bool = False,
    parallel: int = 5,
    agent_provider: str = "codex",
) -> int:
    """Run the work command."""
    agent_provider = normalize_agent(agent_provider)

    # Set default parallel to 6 when model is "all"
    if agent_provider == "all" and parallel == 5:
        parallel = 6

    depth_labels = {
        "links": "Links only (refs, mappings)",
        "docs": "Links + Documentation",
        "full": "Full (links + docs + code)",
    }

    print(f"🔧 mind Work")
    print(f"{'='*60}")
    print(f"  Depth: {depth_labels.get(depth, depth)}")
    print(f"  Parallel agents: {parallel}")
    print(f"  Agent provider: {agent_provider}")
    print()

    # Step 1: Run doctor to get issues
    print(f"{Colors.BOLD}📋 Step 1: Analyzing project health...{Colors.RESET}")
    print()
    config = load_doctor_config(target_dir)
    before_results = run_doctor(target_dir, config)

    print(f"  {Colors.HEALTH}Health Score: {before_results['score']}/100{Colors.RESET}")
    print(f"  {Colors.CRITICAL}Critical: {before_results['summary']['critical']}{Colors.RESET}")
    print(f"  {Colors.WARN_COUNT}Warnings: {before_results['summary']['warning']}{Colors.RESET}")
    print()

    # Collect issues to fix
    all_issues: List[DoctorIssue] = []
    all_issues.extend(before_results["issues"]["critical"])
    all_issues.extend(before_results["issues"]["warning"])
    # Include info-level issues for links depth (safe fixes)
    if depth == "links":
        all_issues.extend(before_results["issues"]["info"])

    # Filter by depth level
    allowed_types = get_depth_types(depth)
    all_issues = [i for i in all_issues if i.issue_type in allowed_types]

    # Filter by explicit type if specified
    if issue_types:
        all_issues = [i for i in all_issues if i.issue_type in issue_types]

    # Sort by priority (foundation issues first, then by impact)
    all_issues.sort(key=lambda i: ISSUE_PRIORITY.get(i.issue_type, 99))

    if not all_issues:
        print(f"✅ No issues to work at depth '{depth}'!")
        print()

        # Count total issues at all depths for context
        total_critical = before_results['summary']['critical']
        total_warnings = before_results['summary']['warning']
        has_other_issues = total_critical > 0 or total_warnings > 0

        # Provide guidance based on current depth
        if depth == "links":
            print(f"  {Colors.DIM}All link/reference issues are resolved.{Colors.RESET}")
            if has_other_issues:
                print(f"  {Colors.DIM}There are {total_critical} critical + {total_warnings} warning issues at deeper depths.{Colors.RESET}")
            print(f"  {Colors.DIM}To check documentation issues: {Colors.RESET}{Colors.BOLD}mind work --depth docs{Colors.RESET}")
            print(f"  {Colors.DIM}To check all issues:           {Colors.RESET}{Colors.BOLD}mind work --depth full{Colors.RESET}")
        elif depth == "docs":
            print(f"  {Colors.DIM}All documentation issues are resolved.{Colors.RESET}")
            if has_other_issues:
                print(f"  {Colors.DIM}There are {total_critical} critical + {total_warnings} warning issues at 'full' depth.{Colors.RESET}")
            print(f"  {Colors.DIM}To check implementation issues: {Colors.RESET}{Colors.BOLD}mind work --depth full{Colors.RESET}")
        else:  # full
            print(f"  {Colors.DIM}Project is healthy at all depths!{Colors.RESET}")
            print(f"  {Colors.DIM}Run {Colors.RESET}{Colors.BOLD}mind doctor{Colors.RESET}{Colors.DIM} to see the full health report.{Colors.RESET}")
        print()
        return 0

    # Limit number of issues if specified
    if max_issues is not None:
        issues_to_fix = all_issues[:max_issues]
    else:
        issues_to_fix = all_issues

    # Step 2: Show the work plan
    print(f"{Colors.BOLD}📝 Step 2: Work Plan{Colors.RESET}")
    print()

    print(f"  {color(str(len(issues_to_fix)), Colors.BOLD)} issues to fix:")
    if max_issues is not None and len(all_issues) > max_issues:
        print(f"  {color(f'(showing first {max_issues} of {len(all_issues)})', Colors.DIM)}")
    print()

    # Show each issue with problem description and action
    for i, issue in enumerate(issues_to_fix[:15]):
        agent_sym = get_agent_symbol(i)
        agent_clr = get_agent_color(i)
        prefix, suffix = get_issue_action_parts(issue.issue_type)
        sev_color = get_severity_color(issue.severity)

        # Format: "No documentation mapping (red): 🥷 will add docs for `path`"
        msg = color(issue.message, sev_color)
        action = f"{Colors.GRAY}{Colors.ITALIC}{prefix}{Colors.RESET}"
        path_fmt = f"`{issue.path}`"
        suffix_fmt = f" {Colors.GRAY}{Colors.ITALIC}{suffix}{Colors.RESET}" if suffix else ""

        print(f"    {i+1}. {msg}: {color(agent_sym, agent_clr)} {action} {path_fmt}{suffix_fmt}")

    if len(issues_to_fix) > 15:
        print(f"    {color(f'   ... and {len(issues_to_fix) - 15} more', Colors.DIM)}")
    print()

    if dry_run:
        print("  [DRY RUN] Would spawn work agents for each issue above.")
        print()
        return 0

    print(f"{'='*60}")
    print()

    # Load GitHub issue mapping (if exists)
    github_mapping = load_github_issue_mapping(target_dir)
    if github_mapping:
        print(f"  GitHub issues found: {len(github_mapping)}")
        print()

    # Step 3: Execute works
    print(f"{Colors.BOLD}🔨 Step 3: Executing works...{Colors.RESET}")
    print(f"  {Colors.DIM}(Type anytime to invoke mind manager){Colors.RESET}")
    print(f"  {Colors.DIM}{'─' * 50}{Colors.RESET}")
    print()

    # Start input listener for mind manager
    reset_manager_state()
    recent_logs: List[str] = []

    listener = threading.Thread(target=input_listener_thread, daemon=True)
    listener.start()

    work_results: List[WorkResult] = []
    print_lock = Lock()
    completed_count = [0]  # Use list to allow modification in nested function
    manager_responses: List[str] = []  # Track manager responses for report

    def run_work(issue_tuple, config: DoctorConfig, escalation_decisions=None): # Added config
        """Run a single work in a thread."""
        idx, issue = issue_tuple
        github_issue_num = github_mapping.get(issue.path)

        # Get agent and issue visual identifiers
        agent_clr = get_agent_color(idx - 1)
        agent_sym = get_agent_symbol(idx - 1)
        prefix, suffix = get_issue_action_parts(issue.issue_type)
        sev_color = get_severity_color(issue.severity)

        with print_lock:
            agent_tag = color(agent_sym, agent_clr)
            msg = color(issue.message, sev_color)
            action = f"{Colors.GRAY}{Colors.ITALIC}{prefix}{Colors.RESET}"
            path_fmt = f"`{issue.path}`"
            suffix_fmt = f" {Colors.GRAY}{Colors.ITALIC}{suffix}{Colors.RESET}" if suffix else ""
            print(f"  {msg}: {agent_tag} {action} {path_fmt}{suffix_fmt}")

        result = spawn_work_agent(
            issue,
            target_dir,
            config, # Pass config
            dry_run=False,
            github_issue_number=github_issue_num,
            escalation_decisions=escalation_decisions,
            agent_symbol=agent_sym,
            agent_provider=agent_provider,
        )

        with print_lock:
            completed_count[0] += 1
            agent_tag = color(agent_sym, agent_clr)
            if result.success:
                print(f"  {agent_tag} {color('✓', Colors.SUCCESS)} finished {issue.path} ({result.duration_seconds:.0f}s)")
            else:
                print(f"  {agent_tag} {color('✗', Colors.FAILURE)} failed on {issue.path}: {result.error or 'unknown'}")

        return result

    # Separate special issues (need interactive input) from others
    escalation_issues = [(i, iss) for i, iss in enumerate(issues_to_fix, 1) if iss.issue_type == "ESCALATION"]
    suggestion_issues = [(i, iss) for i, iss in enumerate(issues_to_fix, 1) if iss.issue_type == "SUGGESTION"]
    other_issues = [(i, iss) for i, iss in enumerate(issues_to_fix, 1)
                    if iss.issue_type not in ("ESCALATION", "SUGGESTION")]

    # Handle ESCALATION issues first (interactive, sequential)
    if escalation_issues:
        print(f"  {Colors.BOLD}⚖️ Resolving {len(escalation_issues)} conflict(s) first...{Colors.RESET}")
        print()

        for idx, issue in escalation_issues:
            # Interactive prompt
            decisions = resolve_escalation_interactive(issue)

            # Check if any decisions were made (not all passed)
            has_decisions = any(not d.passed for d in decisions)

            if has_decisions:
                issue_emoji, _ = get_issue_symbol(issue.issue_type)
                github_issue_num = github_mapping.get(issue.path)
                print(f"  {issue_emoji} Spawning agent to implement decisions...")

                result = spawn_work_agent(
                    issue,
                    target_dir,
                    config, # Pass config
                    dry_run=False,
                    github_issue_number=github_issue_num,
                    escalation_decisions=decisions,
                    agent_provider=agent_provider,
                )
                work_results.append(result)

                if result.success:
                    print(f"\n  {color('✓ Complete', Colors.SUCCESS)} ({result.duration_seconds:.1f}s)")
                else:
                    print(f"\n  {color('✗ Failed', Colors.FAILURE)}: {result.error or 'Unknown error'}")
            else:
                print(f"  {Colors.DIM}All conflicts skipped, no agent spawned{Colors.RESET}")
                work_results.append(WorkResult(
                    issue_type=issue.issue_type,
                    target_path=issue.path,
                    success=True,
                    agent_output="User passed all conflicts",
                    duration_seconds=0,
                ))

        print()

    # Handle SUGGESTION issues (interactive, ask user before spawning)
    accepted_suggestions = []
    if suggestion_issues:
        print(f"  {Colors.BOLD}💡 {len(suggestion_issues)} agent suggestion(s) found:{Colors.RESET}")
        print()

        for idx, issue in suggestion_issues:
            suggestion_text = issue.details.get("suggestion", issue.message)
            source_file = issue.details.get("source_file", issue.path)

            print(f"    {Colors.DIM}From: {source_file}{Colors.RESET}")
            print(f"    💡 {suggestion_text}")
            print()

            try:
                response = input(f"    {Colors.BOLD}Implement this? (y/n/q to quit): {Colors.RESET}").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n    Skipping remaining suggestions...")
                break

            if response == 'q':
                print("    Skipping remaining suggestions...")
                break
            elif response in ('y', 'yes'):
                accepted_suggestions.append((idx, issue))
                print(f"    {Colors.SUCCESS}✓ Accepted{Colors.RESET}")
            else:
                print(f"    {Colors.DIM}Skipped{Colors.RESET}")
            print()

        # Spawn agents for accepted suggestions
        if accepted_suggestions:
            print(f"  {Colors.BOLD}Implementing {len(accepted_suggestions)} accepted suggestion(s)...{Colors.RESET}")
            print()

            for idx, issue in accepted_suggestions:
                agent_sym = get_agent_symbol(idx - 1)
                agent_clr = get_agent_color(idx - 1)
                agent_tag = color(agent_sym, agent_clr)

                suggestion_text = issue.details.get("suggestion", issue.message)
                print(f"  {agent_tag} Implementing: {suggestion_text[:50]}...")

                github_issue_num = github_mapping.get(issue.path)
                result = spawn_work_agent(
                    issue,
                    target_dir,
                    config, # Pass config
                    dry_run=False,
                    github_issue_number=github_issue_num,
                    agent_symbol=agent_sym,
                    agent_provider=agent_provider,
                )
                work_results.append(result)

                if result.success:
                    print(f"\n  {agent_tag} {color('✓ Complete', Colors.SUCCESS)} ({result.duration_seconds:.1f}s)")
                else:
                    print(f"\n  {agent_tag} {color('✗ Failed', Colors.FAILURE)}: {result.error or 'Unknown error'}")
                print()
        else:
            print(f"  {Colors.DIM}No suggestions accepted{Colors.RESET}")
            print()

    # Run remaining agents in parallel or sequentially
    if not other_issues:
        pass  # Only had ESCALATION issues
    elif parallel > 1:
        active_workers = min(parallel, len(other_issues))
        print(f"  Running {len(other_issues)} works with {active_workers} parallel agents...")
        print()

        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(run_work, issue_tuple): issue_tuple[1]
                for issue_tuple in other_issues
            }

            for future in as_completed(futures):
                result = future.result()
                work_results.append(result)

                # Log for manager context
                log_entry = f"[{result.issue_type}] {result.target_path}: {'SUCCESS' if result.success else 'FAILED'}"
                recent_logs.append(log_entry)

                # Check for manager input periodically
                manager_response = check_for_manager_input(recent_logs, target_dir, agent_provider)
                if manager_response:
                    manager_responses.append(manager_response)
    else:
        # Sequential execution with more verbose output
        for i, issue in other_issues:
            # Check for manager input between works
            manager_response = check_for_manager_input(recent_logs, target_dir, agent_provider)
            if manager_response:
                manager_responses.append(manager_response)
                if "STOP WORKS" in manager_response:
                    print(f"\n  {Colors.BOLD}Manager requested stop. Halting works.{Colors.RESET}")
                    break

            issue_emoji, issue_sym = get_issue_symbol(issue.issue_type)
            print_progress_bar(i - 1, len(issues_to_fix), status=f"Starting {issue.issue_type}...")
            print()

            github_issue_num = github_mapping.get(issue.path)
            github_info = f" (#{github_issue_num})" if github_issue_num else ""
            prefix, suffix = get_issue_action_parts(issue.issue_type)
            sev_color = get_severity_color(issue.severity)
            msg = color(issue.message, sev_color)
            action = f"{Colors.GRAY}{Colors.ITALIC}{prefix}{Colors.RESET}"
            path_fmt = f"`{issue.path}`"
            suffix_fmt = f" {Colors.GRAY}{Colors.ITALIC}{suffix}{Colors.RESET}" if suffix else ""
            print(f"\n  {issue_emoji} [{i}/{len(issues_to_fix)}] {msg}: {action} {path_fmt}{suffix_fmt}{github_info}")

            result = spawn_work_agent(
                issue,
                target_dir,
                config,
                dry_run=False,
                github_issue_number=github_issue_num,
                agent_provider=agent_provider,
            )
            work_results.append(result)

            # Log for manager context
            log_entry = f"[{issue.issue_type}] {issue.path}: {'SUCCESS' if result.success else 'FAILED'}"
            recent_logs.append(log_entry)

            if result.success:
                print(f"\n  {color('✓ Complete', Colors.SUCCESS)} ({result.duration_seconds:.1f}s)")
            else:
                print(f"\n  {color('✗ Failed', Colors.FAILURE)}: {result.error or 'Unknown error'}")
                if result.agent_output:
                    print(f"  {Colors.DIM}Last few lines of agent output:{Colors.RESET}")
                    for line in result.agent_output.splitlines()[-15:]:
                        print(f"    {Colors.DIM}{line}{Colors.RESET}")

        print_progress_bar(len(issues_to_fix), len(issues_to_fix), status="Done!")

    # Stop the input listener
    stop_manager_listener()

    # Final check for manager input
    manager_response = check_for_manager_input(recent_logs, target_dir, agent_provider)
    if manager_response:
        manager_responses.append(manager_response)

    print("\n")

    # Step 4: Run doctor again
    print(f"{Colors.BOLD}📊 Step 4: Running final health check...{Colors.RESET}")
    after_results = run_doctor(target_dir, config)

    # Calculate and format score change
    score_change = after_results['score'] - before_results['score']
    if score_change > 0:
        change_str = f" {Colors.SUCCESS}(+{score_change}){Colors.RESET}"
    elif score_change < 0:
        change_str = f" {Colors.FAILURE}({score_change}){Colors.RESET}"
    else:
        change_str = f" {Colors.DIM}(±0){Colors.RESET}"

    print(f"  {Colors.HEALTH}Health Score: {after_results['score']}/100{Colors.RESET}{change_str}")
    print(f"  {Colors.CRITICAL}Critical: {after_results['summary']['critical']}{Colors.RESET}")
    print(f"  {Colors.WARN_COUNT}Warnings: {after_results['summary']['warning']}{Colors.RESET}")
    print()

    # Step 5: Generate report
    print(f"{Colors.BOLD}📄 Step 5: Generating report...{Colors.RESET}")

    # Try LLM-generated report first, fall back to template
    report = generate_llm_report(
        before_results,
        after_results,
        work_results,
        target_dir,
        agent_provider=agent_provider,
    )
    if report:
        print(f"  {Colors.DIM}(Generated by {agent_provider}){Colors.RESET}")
    else:
        report = generate_final_report(before_results, after_results, work_results, target_dir)
        print(f"  {Colors.DIM}(Using template report){Colors.RESET}")

    # Save report
    report_path = target_dir / ".mind" / "state" / "WORK_REPORT.md"
    if report_path.parent.exists():
        report_path.write_text(report)
        print(f"  Saved to {report_path.relative_to(target_dir)}")

    print()

    # Display report to CLI
    print(f"{'─'*60}")
    print(report)
    print(f"{'─'*60}")
    print()

    # Summary
    successful = len([r for r in work_results if r.success])
    score_before = before_results['score']
    score_after = after_results['score']
    score_diff = score_after - score_before
    if score_diff > 0:
        score_change_fmt = f"{Colors.SUCCESS}(+{score_diff}){Colors.RESET}"
    elif score_diff < 0:
        score_change_fmt = f"{Colors.FAILURE}({score_diff}){Colors.RESET}"
    else:
        score_change_fmt = f"{Colors.DIM}(±0){Colors.RESET}"

    print(f"{'='*60}")
    print(f"✅ Work Complete: {successful}/{len(work_results)} successful")
    print(f"📈 {Colors.HEALTH}Health Score: {score_before} → {score_after}{Colors.RESET} {score_change_fmt}")
    print(f"{'='*60}")

    # Return exit code
    return 0 if successful == len(work_results) else 1
