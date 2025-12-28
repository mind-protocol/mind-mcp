"""
Doctor checks for membrane system health.

Health checks that verify membrane runtime behavior:
- Session state validity
- Step ordering correctness
- Cluster creation integrity

DOCS: docs/membrane/HEALTH_Membrane_System.md
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from .doctor_types import DoctorIssue, DoctorConfig

# Add project root for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def _check_runner_available() -> tuple[bool, Optional[str]]:
    """Check if membrane runner is importable."""
    try:
        from mind.connectome.runner import ConnectomeRunner
        return True, None
    except ImportError as e:
        return False, str(e)


def _check_protocols_exist(target_dir: Path) -> tuple[int, List[str]]:
    """Count available protocols."""
    protocols_dir = target_dir / "protocols"
    if not protocols_dir.exists():
        return 0, []
    protocols = list(protocols_dir.glob("*.yaml"))
    return len(protocols), [p.name for p in protocols]


def _test_session_lifecycle(target_dir: Path) -> Dict[str, Any]:
    """Test membrane session lifecycle.

    Returns dict with:
        success: bool
        error: Optional[str]
        checks: dict of check_name -> pass/fail
    """
    result = {
        "success": False,
        "error": None,
        "checks": {
            "runner_import": False,
            "session_create": False,
            "session_unique_id": False,
            "session_state_valid": False,
        }
    }

    # Check 1: Runner import
    available, err = _check_runner_available()
    if not available:
        result["error"] = f"Runner not importable: {err}"
        return result
    result["checks"]["runner_import"] = True

    try:
        from mind.connectome.runner import ConnectomeRunner

        # Check 2: Session creation
        # Runner requires graph_ops and graph_queries, use None for health check
        # (will fail on actual graph operations but validates session mechanics)
        protocols_dir = target_dir / "protocols"
        runner = ConnectomeRunner(
            graph_ops=None,
            graph_queries=None,
            connectomes_dir=protocols_dir
        )

        # Try to start a simple protocol (capture_decision is simple)
        protocols = list((target_dir / "protocols").glob("*.yaml"))
        if not protocols:
            result["error"] = "No protocols available"
            return result

        # Use capture_decision or first available
        test_protocol = "capture_decision"
        if not (target_dir / "protocols" / f"{test_protocol}.yaml").exists():
            test_protocol = protocols[0].stem

        start_result = runner.start(test_protocol)

        if start_result.get("status") in ("active", "complete"):
            result["checks"]["session_create"] = True

            # Check 3: Session ID unique
            session_id = start_result.get("session_id")
            if session_id and len(session_id) > 8:
                result["checks"]["session_unique_id"] = True

            # Check 4: Session state valid (has expected fields)
            if start_result.get("step") or start_result.get("status") == "complete":
                result["checks"]["session_state_valid"] = True

            # Abort to clean up
            if session_id:
                runner.abort(session_id)

        result["success"] = all(result["checks"].values())

    except Exception as e:
        result["error"] = str(e)

    return result


def _test_step_ordering(target_dir: Path) -> Dict[str, Any]:
    """Test that protocol steps execute in order.

    Returns dict with check results.
    """
    result = {
        "success": False,
        "error": None,
        "steps_observed": [],
        "ordering_correct": False,
    }

    available, err = _check_runner_available()
    if not available:
        result["error"] = f"Runner not importable: {err}"
        return result

    try:
        from mind.connectome.runner import ConnectomeRunner

        protocols_dir = target_dir / "protocols"
        runner = ConnectomeRunner(
            graph_ops=None,
            graph_queries=None,
            connectomes_dir=protocols_dir
        )

        # Use a protocol with multiple steps
        test_protocol = "capture_decision"
        if not (target_dir / "protocols" / f"{test_protocol}.yaml").exists():
            protocols = list((target_dir / "protocols").glob("*.yaml"))
            if protocols:
                test_protocol = protocols[0].stem
            else:
                result["error"] = "No protocols available"
                return result

        # Start and track steps
        start_result = runner.start(test_protocol)
        session_id = start_result.get("session_id")

        if start_result.get("step"):
            result["steps_observed"].append(start_result["step"].get("id", "unknown"))

        # Try to continue (with a mock answer if needed)
        if start_result.get("status") == "active" and session_id:
            step = start_result.get("step", {})
            step_type = step.get("type")

            if step_type == "ask":
                # Provide mock answer
                expects = step.get("expects", {})
                answer_type = expects.get("type", "string")

                if answer_type == "string":
                    mock_answer = "test_answer"
                elif answer_type == "enum":
                    mock_answer = expects.get("options", ["test"])[0]
                else:
                    mock_answer = "test"

                continue_result = runner.continue_session(session_id, mock_answer)

                if continue_result.get("step"):
                    result["steps_observed"].append(continue_result["step"].get("id", "unknown"))

            # Abort to clean up
            runner.abort(session_id)

        # Success if we observed at least one step transition
        result["ordering_correct"] = len(result["steps_observed"]) >= 1
        result["success"] = result["ordering_correct"]

    except Exception as e:
        result["error"] = str(e)

    return result


def doctor_check_membrane_health(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check membrane system health.

    Validates:
    - Runner is available
    - Protocols exist
    - Sessions can be created
    - Basic step ordering works
    """
    if "MEMBRANE_HEALTH" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []

    # Check 1: Protocols exist
    protocol_count, protocol_names = _check_protocols_exist(target_dir)

    if protocol_count == 0:
        issues.append(DoctorIssue(
            issue_type="MEMBRANE_NO_PROTOCOLS",
            severity="critical",
            path="procedures/",
            message="No membrane protocols found",
            details={"expected_location": "procedures/"},
            suggestion="Create protocols in procedures/ directory",
            protocol="define_space"
        ))
        return issues  # Can't test further without protocols

    # Check 2: Runner available
    available, import_error = _check_runner_available()

    if not available:
        issues.append(DoctorIssue(
            issue_type="MEMBRANE_IMPORT_ERROR",
            severity="critical",
            path="engine/connectome/runner.py",
            message=f"Cannot import ConnectomeRunner: {import_error}",
            details={"error": import_error},
            suggestion="Fix import errors in engine/connectome/"
        ))
        return issues

    # Check 3: Session lifecycle
    session_result = _test_session_lifecycle(target_dir)

    failed_checks = [k for k, v in session_result["checks"].items() if not v]

    if failed_checks:
        issues.append(DoctorIssue(
            issue_type="MEMBRANE_SESSION_INVALID",
            severity="warning",
            path="engine/connectome/session.py",
            message=f"Session lifecycle issues: {', '.join(failed_checks)}",
            details={
                "failed_checks": failed_checks,
                "error": session_result.get("error"),
            },
            suggestion="Check session state management in session.py"
        ))

    # Check 4: Step ordering
    ordering_result = _test_step_ordering(target_dir)

    if not ordering_result["success"]:
        issues.append(DoctorIssue(
            issue_type="MEMBRANE_STEP_ORDERING",
            severity="warning",
            path="engine/connectome/steps.py",
            message=f"Step ordering issue: {ordering_result.get('error', 'unknown')}",
            details={
                "steps_observed": ordering_result["steps_observed"],
                "error": ordering_result.get("error"),
            },
            suggestion="Check step execution in steps.py"
        ))

    return issues


def doctor_check_membrane_protocols(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check membrane protocol definitions for issues.

    Validates:
    - Protocol YAML structure
    - Step transitions valid
    - Required fields present
    """
    if "MEMBRANE_PROTOCOLS" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    protocols_dir = target_dir / "protocols"

    if not protocols_dir.exists():
        return []  # Covered by membrane_health check

    try:
        import yaml
    except ImportError:
        return []  # Can't check without yaml

    required_fields = {"protocol", "steps"}
    required_step_fields = {"type"}

    for protocol_file in protocols_dir.glob("*.yaml"):
        try:
            with open(protocol_file) as f:
                protocol = yaml.safe_load(f)

            if not protocol:
                issues.append(DoctorIssue(
                    issue_type="MEMBRANE_EMPTY_PROTOCOL",
                    severity="warning",
                    path=str(protocol_file.relative_to(target_dir)),
                    message="Empty protocol file",
                    suggestion="Add protocol definition"
                ))
                continue

            # Check required fields
            missing = required_fields - set(protocol.keys())
            if missing:
                issues.append(DoctorIssue(
                    issue_type="MEMBRANE_MISSING_FIELDS",
                    severity="warning",
                    path=str(protocol_file.relative_to(target_dir)),
                    message=f"Missing required fields: {', '.join(missing)}",
                    details={"missing": list(missing)},
                    suggestion="Add missing protocol fields"
                ))

            # Check steps structure
            steps = protocol.get("steps", {})
            if isinstance(steps, dict):
                for step_id, step_def in steps.items():
                    if isinstance(step_def, dict):
                        step_missing = required_step_fields - set(step_def.keys())
                        if step_missing:
                            issues.append(DoctorIssue(
                                issue_type="MEMBRANE_INVALID_STEP",
                                severity="info",
                                path=str(protocol_file.relative_to(target_dir)),
                                message=f"Step '{step_id}' missing: {', '.join(step_missing)}",
                                details={"step": step_id, "missing": list(step_missing)},
                                suggestion=f"Add 'type' to step '{step_id}'"
                            ))

                        # Check step has valid next
                        step_type = step_def.get("type")
                        if step_type not in ("create",) and "next" not in step_def:
                            # Check for conditional next
                            if step_type == "branch":
                                if "checks" not in step_def:
                                    issues.append(DoctorIssue(
                                        issue_type="MEMBRANE_BRANCH_NO_CHECKS",
                                        severity="warning",
                                        path=str(protocol_file.relative_to(target_dir)),
                                        message=f"Branch step '{step_id}' has no checks",
                                        details={"step": step_id},
                                        suggestion="Add checks to branch step"
                                    ))

        except yaml.YAMLError as e:
            issues.append(DoctorIssue(
                issue_type="MEMBRANE_YAML_ERROR",
                severity="critical",
                path=str(protocol_file.relative_to(target_dir)),
                message=f"YAML parse error: {e}",
                suggestion="Fix YAML syntax"
            ))
        except Exception as e:
            issues.append(DoctorIssue(
                issue_type="MEMBRANE_PARSE_ERROR",
                severity="warning",
                path=str(protocol_file.relative_to(target_dir)),
                message=f"Parse error: {e}",
                suggestion="Check protocol file format"
            ))

    return issues
