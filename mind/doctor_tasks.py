"""
Doctor Tasks — Surface Issues and Create Task Narratives

Main entry point for the graph-based doctor system:
1. Surface issues from static analysis, tests, health checks
2. Traverse up from issues to find objectives
3. Group and split into tasks
4. Create task narrative nodes

DOCS: docs/protocol/doctor/ALGORITHM_Project_Health_Doctor.md
"""

import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from .doctor_types import DoctorIssue, DoctorConfig
from .doctor_graph import (
    DoctorGraphStore,
    IssueNarrative,
    TaskNarrative,
    ObjectiveNarrative,
    TraversalOutcome,
    upsert_issue_from_check,
    resolve_issue,
    create_tasks_from_issues,
    fetch_objectives,
    ensure_module_objectives,
    generate_issue_id,
    ISSUE_BLOCKS_OBJECTIVE,
)


# =============================================================================
# MODULE DISCOVERY
# =============================================================================

def load_modules_yaml(target_dir: Path) -> Dict[str, Any]:
    """Load modules.yaml and return module definitions."""
    try:
        from .core_utils import HAS_YAML
        if not HAS_YAML:
            return {}

        import yaml
        modules_path = target_dir / "modules.yaml"
        if not modules_path.exists():
            return {}

        with open(modules_path) as f:
            data = yaml.safe_load(f) or {}

        return data.get("modules", {})
    except Exception:
        return {}


def get_module_for_path(path: str, modules: Dict[str, Any], target_dir: Path) -> str:
    """Find module ID that owns this path."""
    import fnmatch

    path_str = str(path)

    for module_id, module_data in modules.items():
        if not isinstance(module_data, dict):
            continue

        code_pattern = module_data.get("code", "")
        if isinstance(code_pattern, list):
            code_pattern = code_pattern[0] if code_pattern else ""

        # Convert glob to fnmatch pattern
        pattern = str(code_pattern).replace("**", "*")

        if fnmatch.fnmatch(path_str, pattern):
            return module_id

        # Also try relative path
        try:
            rel_path = str(Path(path).relative_to(target_dir))
            if fnmatch.fnmatch(rel_path, pattern):
                return module_id
        except ValueError:
            pass

    return "orphan"


# =============================================================================
# ISSUE SURFACING FROM DOCTOR CHECKS
# =============================================================================

def surface_issues_from_checks(
    doctor_issues: List[DoctorIssue],
    store: DoctorGraphStore,
    modules: Dict[str, Any],
    target_dir: Path
) -> List[IssueNarrative]:
    """
    Convert DoctorIssue objects to IssueNarrative graph nodes.
    Upserts into graph store.
    """
    issue_nodes = []

    for issue in doctor_issues:
        module = get_module_for_path(issue.path, modules, target_dir)

        node = upsert_issue_from_check(
            issue_type=issue.issue_type,
            severity=issue.severity,
            path=issue.path,
            message=issue.message,
            module=module,
            store=store,
            details=issue.details
        )
        issue_nodes.append(node)

    return issue_nodes


# =============================================================================
# ISSUE SURFACING FROM TESTS
# =============================================================================

@dataclass
class TestResult:
    """Result from a test run."""
    name: str
    file: str
    status: str  # passed, failed, error, skipped
    message: str = ""
    duration: float = 0.0


def run_tests(target_dir: Path, test_command: Optional[str] = None) -> List[TestResult]:
    """
    Run tests and return results.
    Default: pytest with JSON output.
    """
    results = []

    if test_command:
        cmd = test_command
    else:
        # Try pytest
        cmd = f"{sys.executable} -m pytest --tb=no -q"

    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=300
        )

        # Parse pytest output (simplified)
        for line in proc.stdout.splitlines():
            if "FAILED" in line:
                # Format: path/test.py::test_name FAILED
                parts = line.split(" ")[0].split("::")
                if len(parts) >= 2:
                    results.append(TestResult(
                        name=parts[-1],
                        file=parts[0],
                        status="failed",
                        message=line
                    ))
            elif "ERROR" in line:
                parts = line.split(" ")[0].split("::")
                if len(parts) >= 2:
                    results.append(TestResult(
                        name=parts[-1] if len(parts) > 1 else "unknown",
                        file=parts[0],
                        status="error",
                        message=line
                    ))

    except subprocess.TimeoutExpired:
        results.append(TestResult(
            name="test_suite",
            file="",
            status="timeout",
            message="Test suite timed out after 300s"
        ))
    except Exception as e:
        results.append(TestResult(
            name="test_runner",
            file="",
            status="error",
            message=str(e)
        ))

    return results


def surface_issues_from_tests(
    target_dir: Path,
    store: DoctorGraphStore,
    modules: Dict[str, Any],
    test_command: Optional[str] = None
) -> List[IssueNarrative]:
    """
    Run tests and surface failures as issue nodes.
    """
    test_results = run_tests(target_dir, test_command)
    issue_nodes = []

    for result in test_results:
        if result.status in ("passed", "skipped"):
            # Check if previously failing - resolve
            issue_id = generate_issue_id(
                f"TEST_{result.status.upper()}",
                get_module_for_path(result.file, modules, target_dir),
                result.file
            )
            resolve_issue(issue_id, store)
            continue

        module = get_module_for_path(result.file, modules, target_dir)

        issue_type = f"TEST_{result.status.upper()}"
        node = upsert_issue_from_check(
            issue_type=issue_type,
            severity="critical" if result.status == "failed" else "warning",
            path=result.file,
            message=f"Test {result.name}: {result.message}",
            module=module,
            store=store,
            details={"test_name": result.name, "status": result.status}
        )
        issue_nodes.append(node)

    return issue_nodes


# =============================================================================
# ISSUE SURFACING FROM HEALTH CHECKS
# =============================================================================

@dataclass
class HealthSignal:
    """A health signal to check."""
    id: str
    name: str
    check_type: str  # invariant, endpoint, config, custom
    check_command: Optional[str] = None
    invariant_id: Optional[str] = None
    module: str = ""


@dataclass
class HealthResult:
    """Result from a health check."""
    signal: HealthSignal
    status: str  # healthy, failed, error
    message: str = ""


def load_health_signals(target_dir: Path, modules: Dict[str, Any]) -> List[HealthSignal]:
    """
    Load health signals from HEALTH_*.md files.
    """
    signals = []

    docs_dir = target_dir / "docs"
    if not docs_dir.exists():
        return signals

    for health_file in docs_dir.rglob("HEALTH_*.md"):
        try:
            content = health_file.read_text()

            # Find module for this health file
            module = "unknown"
            for mod_id, mod_data in modules.items():
                if isinstance(mod_data, dict):
                    docs_path = mod_data.get("docs", "")
                    if docs_path and str(health_file).startswith(str(target_dir / docs_path)):
                        module = mod_id
                        break

            # Parse signals (simplified - look for ## Signal sections)
            import re
            signal_pattern = r"##\s+Signal:\s+(\w+)"
            for match in re.finditer(signal_pattern, content):
                signal_name = match.group(1)
                signals.append(HealthSignal(
                    id=f"health_{module}_{signal_name}",
                    name=signal_name,
                    check_type="custom",
                    module=module
                ))

            # Look for invariant references
            invariant_pattern = r"verifies:\s*(\w+\.\d+)"
            for match in re.finditer(invariant_pattern, content):
                inv_id = match.group(1)
                signals.append(HealthSignal(
                    id=f"invariant_{module}_{inv_id}",
                    name=f"Invariant {inv_id}",
                    check_type="invariant",
                    invariant_id=inv_id,
                    module=module
                ))

        except Exception:
            continue

    return signals


def run_health_checks(signals: List[HealthSignal], target_dir: Path) -> List[HealthResult]:
    """
    Run health checks for signals.
    Currently returns empty - implement per signal type.
    """
    results = []

    for signal in signals:
        if signal.check_type == "invariant":
            # Would run validation check
            pass
        elif signal.check_command:
            # Would run custom command
            pass
        # Default: assume healthy (no check implemented)

    return results


def surface_issues_from_health(
    target_dir: Path,
    store: DoctorGraphStore,
    modules: Dict[str, Any]
) -> List[IssueNarrative]:
    """
    Run health checks and surface failures as issue nodes.
    """
    signals = load_health_signals(target_dir, modules)
    results = run_health_checks(signals, target_dir)
    issue_nodes = []

    for result in results:
        if result.status == "healthy":
            # Resolve any previous failure
            issue_id = generate_issue_id(
                "HEALTH_FAILED",
                result.signal.module,
                result.signal.id
            )
            resolve_issue(issue_id, store)
            continue

        issue_type = "HEALTH_FAILED" if result.status == "failed" else "HEALTH_ERROR"
        if result.signal.check_type == "invariant":
            issue_type = "INVARIANT_VIOLATED"

        node = upsert_issue_from_check(
            issue_type=issue_type,
            severity="critical",
            path=result.signal.id,
            message=result.message or f"Health check failed: {result.signal.name}",
            module=result.signal.module,
            store=store,
            details={
                "signal_id": result.signal.id,
                "check_type": result.signal.check_type
            }
        )
        issue_nodes.append(node)

    return issue_nodes


# =============================================================================
# MAIN TASK SURFACING FLOW
# =============================================================================

@dataclass
class TaskSurfaceResult:
    """Result of the task surfacing process."""
    issues_surfaced: int
    issues_from_checks: int
    issues_from_tests: int
    issues_from_health: int
    tasks_created: int
    tasks_serve: int
    tasks_reconstruct: int
    tasks_triage: int
    tasks: List[TaskNarrative]


def surface_tasks(
    target_dir: Path,
    doctor_issues: List[DoctorIssue],
    config: DoctorConfig,
    run_tests_flag: bool = False,
    run_health_flag: bool = False,
    store: Optional[DoctorGraphStore] = None
) -> TaskSurfaceResult:
    """
    Main entry point: surface issues and create tasks.

    1. Load modules
    2. Ensure objectives exist
    3. Surface issues from checks
    4. Optionally surface from tests
    5. Optionally surface from health
    6. Traverse to objectives
    7. Create task narratives

    Returns TaskSurfaceResult with statistics and tasks.
    """
    if store is None:
        store = DoctorGraphStore()

    modules = load_modules_yaml(target_dir)

    # Ensure objectives exist for all modules
    for module_id in modules.keys():
        ensure_module_objectives(module_id, store)

    # Surface issues from static checks
    check_issues = surface_issues_from_checks(doctor_issues, store, modules, target_dir)

    # Optionally run tests
    test_issues = []
    if run_tests_flag:
        test_issues = surface_issues_from_tests(target_dir, store, modules)

    # Optionally run health checks
    health_issues = []
    if run_health_flag:
        health_issues = surface_issues_from_health(target_dir, store, modules)

    # Combine all issues
    all_issues = check_issues + test_issues + health_issues

    # Filter to open issues only
    open_issues = [i for i in all_issues if i.status == "open"]

    # Create tasks
    tasks = create_tasks_from_issues(open_issues, store, modules)

    # Count by type
    tasks_serve = len([t for t in tasks if t.task_type == "serve"])
    tasks_reconstruct = len([t for t in tasks if t.task_type == "reconstruct"])
    tasks_triage = len([t for t in tasks if t.task_type == "triage"])

    return TaskSurfaceResult(
        issues_surfaced=len(all_issues),
        issues_from_checks=len(check_issues),
        issues_from_tests=len(test_issues),
        issues_from_health=len(health_issues),
        tasks_created=len(tasks),
        tasks_serve=tasks_serve,
        tasks_reconstruct=tasks_reconstruct,
        tasks_triage=tasks_triage,
        tasks=tasks
    )


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def format_tasks_text(result: TaskSurfaceResult) -> str:
    """Format tasks for text output."""
    lines = []

    lines.append("=" * 60)
    lines.append("DOCTOR TASKS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Issues surfaced: {result.issues_surfaced}")
    lines.append(f"  - From static checks: {result.issues_from_checks}")
    lines.append(f"  - From tests: {result.issues_from_tests}")
    lines.append(f"  - From health: {result.issues_from_health}")
    lines.append("")
    lines.append(f"Tasks created: {result.tasks_created}")
    lines.append(f"  - SERVE (normal): {result.tasks_serve}")
    lines.append(f"  - RECONSTRUCT (fix chain): {result.tasks_reconstruct}")
    lines.append(f"  - TRIAGE (evaluate): {result.tasks_triage}")
    lines.append("")
    lines.append("-" * 60)

    for task in result.tasks:
        lines.append("")
        lines.append(f"## {task.id}")
        lines.append(f"   Type: {task.task_type.upper()}")
        lines.append(f"   Module: {task.module}")
        lines.append(f"   Skill: {task.skill}")
        lines.append(f"   Issues: {len(task.issue_ids)}")

        if task.missing_nodes:
            lines.append(f"   Missing: {', '.join(task.missing_nodes)}")

        if task.objective_id:
            lines.append(f"   Serves: {task.objective_id}")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def format_tasks_yaml(result: TaskSurfaceResult) -> str:
    """Format tasks as YAML."""
    try:
        import yaml

        data = {
            "summary": {
                "issues_surfaced": result.issues_surfaced,
                "issues_from_checks": result.issues_from_checks,
                "issues_from_tests": result.issues_from_tests,
                "issues_from_health": result.issues_from_health,
                "tasks_created": result.tasks_created,
                "tasks_serve": result.tasks_serve,
                "tasks_reconstruct": result.tasks_reconstruct,
                "tasks_triage": result.tasks_triage,
            },
            "tasks": [
                {
                    "id": t.id,
                    "type": t.task_type,
                    "module": t.module,
                    "skill": t.skill,
                    "objective": t.objective_id,
                    "issues": t.issue_ids,
                    "missing": t.missing_nodes if t.missing_nodes else None,
                }
                for t in result.tasks
            ]
        }

        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    except ImportError:
        return format_tasks_text(result)


def format_tasks_json(result: TaskSurfaceResult) -> str:
    """Format tasks as JSON."""
    import json

    data = {
        "summary": {
            "issues_surfaced": result.issues_surfaced,
            "issues_from_checks": result.issues_from_checks,
            "issues_from_tests": result.issues_from_tests,
            "issues_from_health": result.issues_from_health,
            "tasks_created": result.tasks_created,
            "tasks_serve": result.tasks_serve,
            "tasks_reconstruct": result.tasks_reconstruct,
            "tasks_triage": result.tasks_triage,
        },
        "tasks": [
            {
                "id": t.id,
                "type": t.task_type,
                "module": t.module,
                "skill": t.skill,
                "objective": t.objective_id,
                "issues": t.issue_ids,
                "missing": t.missing_nodes if t.missing_nodes else None,
                "name": t.name,
                "content": t.content,
            }
            for t in result.tasks
        ]
    }

    return json.dumps(data, indent=2)
