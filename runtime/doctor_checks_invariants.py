"""
Doctor checks for invariant test coverage.

Checks:
1. VALIDATION files have verified_by: fields for HIGH priority invariants
2. Test files have @validates: docstrings linking back
3. Completion gate status (run tests, check results)

DOCS: .mind/skills/SKILL_Test_Integrate_And_Gate_Completion.md
"""

import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field

from .doctor_types import DoctorIssue, DoctorConfig


@dataclass
class Invariant:
    """An invariant from a VALIDATION file."""
    id: str
    priority: str  # HIGH, MED, LOW
    file_path: str
    line_number: int
    verified_by_test: Optional[str] = None
    verified_by_health: Optional[str] = None
    confidence: str = "untested"


@dataclass
class TestMapping:
    """A test that validates an invariant."""
    test_file: str
    test_function: str
    validates: List[str]  # List of invariant IDs
    line_number: int


def find_validation_files(target_dir: Path) -> List[Path]:
    """Find all VALIDATION_*.md files in docs/."""
    validation_files = []
    docs_dir = target_dir / "docs"
    if docs_dir.exists():
        validation_files.extend(docs_dir.rglob("VALIDATION_*.md"))
    return validation_files


def parse_invariants(validation_file: Path) -> List[Invariant]:
    """Parse invariants from a VALIDATION file.

    Looks for patterns like:
    - ### @mind:id: V-ENERGY-NON-NEGATIVE
    - ### @mind:physics:energy:invariant:V-ENERGY-NON-NEGATIVE
    - priority: HIGH
    - verified_by:
        test: file::function
        health: file::function
        confidence: high
    """
    invariants = []
    content = validation_file.read_text()
    lines = content.split('\n')

    current_invariant = None
    in_verified_by = False

    for i, line in enumerate(lines, 1):
        # Look for invariant ID patterns
        # Pattern 1: ### @mind:id: V-XXX
        id_match = re.search(r'@mind:id:\s*(V-[\w-]+)', line)
        # Pattern 2: ### @mind:area:module:invariant:V-XXX
        invariant_match = re.search(r'@mind:[\w:]+:invariant:(V-[\w-]+)', line)

        if id_match or invariant_match:
            # Save previous invariant if any
            if current_invariant:
                invariants.append(current_invariant)

            inv_id = id_match.group(1) if id_match else invariant_match.group(1)
            current_invariant = Invariant(
                id=inv_id,
                priority="MED",  # Default, will be updated
                file_path=str(validation_file),
                line_number=i,
            )
            in_verified_by = False
            continue

        if current_invariant:
            # Look for priority
            priority_match = re.search(r'priority:\s*(HIGH|MED|LOW)', line, re.IGNORECASE)
            if priority_match:
                current_invariant.priority = priority_match.group(1).upper()

            # Look for verified_by section
            if 'verified_by:' in line.lower():
                in_verified_by = True
                continue

            if in_verified_by:
                # Look for test:
                test_match = re.search(r'test:\s*(.+)', line)
                if test_match:
                    current_invariant.verified_by_test = test_match.group(1).strip()

                # Look for health:
                health_match = re.search(r'health:\s*(.+)', line)
                if health_match:
                    current_invariant.verified_by_health = health_match.group(1).strip()

                # Look for confidence:
                confidence_match = re.search(r'confidence:\s*(high|partial|needs-health|untested|blocked)', line, re.IGNORECASE)
                if confidence_match:
                    current_invariant.confidence = confidence_match.group(1).lower()

                # Exit verified_by section on blank line or new section
                if line.strip() == '' or (line.startswith('#') and not line.startswith('##')):
                    in_verified_by = False

        # Also look for @mind:...:test: markers that link to invariants
        test_marker = re.search(r'@mind:[\w:]+:test:([\w_]+)', line)
        if test_marker and current_invariant:
            # This links a test to the current invariant
            if not current_invariant.verified_by_test:
                current_invariant.verified_by_test = test_marker.group(1)

    # Don't forget the last invariant
    if current_invariant:
        invariants.append(current_invariant)

    return invariants


def find_test_files(target_dir: Path) -> List[Path]:
    """Find all test files."""
    test_files = []

    # Common test locations
    for pattern in ["tests/**/*.py", "test/**/*.py", "**/test_*.py", "engine/tests/**/*.py"]:
        test_files.extend(target_dir.glob(pattern))

    # Deduplicate
    return list(set(test_files))


def parse_test_mappings(test_file: Path) -> List[TestMapping]:
    """Parse @validates: markers from test files.

    Looks for:
    - @validates: V-ID-1, V-ID-2
    - @mind:area:module:validates:V-ID
    """
    mappings = []
    content = test_file.read_text()
    lines = content.split('\n')

    current_function = None
    current_line = 0

    for i, line in enumerate(lines, 1):
        # Track current function
        func_match = re.match(r'\s*def (test_\w+)', line)
        if func_match:
            current_function = func_match.group(1)
            current_line = i

        # Look for @validates: patterns
        validates_match = re.search(r'@validates:\s*([\w\s,_-]+)', line)
        if validates_match and current_function:
            ids = [v.strip() for v in validates_match.group(1).split(',')]
            ids = [v for v in ids if v.startswith('V-')]
            if ids:
                mappings.append(TestMapping(
                    test_file=str(test_file),
                    test_function=current_function,
                    validates=ids,
                    line_number=current_line,
                ))

        # Look for @mind:...:validates:V-ID patterns
        mind_validates = re.search(r'@mind:[\w:]+:validates:(V-[\w-]+)', line)
        if mind_validates and current_function:
            inv_id = mind_validates.group(1)
            # Check if we already have this mapping
            existing = next((m for m in mappings if m.test_function == current_function), None)
            if existing:
                if inv_id not in existing.validates:
                    existing.validates.append(inv_id)
            else:
                mappings.append(TestMapping(
                    test_file=str(test_file),
                    test_function=current_function,
                    validates=[inv_id],
                    line_number=current_line,
                ))

    return mappings


def run_tests_for_module(target_dir: Path, test_pattern: str = None) -> Dict[str, Any]:
    """Run pytest and return results.

    Returns:
        {
            "passed": [...],
            "failed": [...],
            "error": Optional[str]
        }
    """
    try:
        cmd = ["python3", "-m", "pytest", "-v", "--tb=short", "-q"]
        if test_pattern:
            cmd.append(test_pattern)

        result = subprocess.run(
            cmd,
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        # Parse output for pass/fail
        passed = []
        failed = []

        for line in result.stdout.split('\n'):
            if ' PASSED' in line:
                match = re.search(r'([\w/]+\.py::\w+::\w+)', line)
                if match:
                    passed.append(match.group(1))
            elif ' FAILED' in line:
                match = re.search(r'([\w/]+\.py::\w+::\w+)', line)
                if match:
                    failed.append(match.group(1))

        return {
            "passed": passed,
            "failed": failed,
            "returncode": result.returncode,
            "error": None if result.returncode == 0 else result.stderr[:500]
        }
    except subprocess.TimeoutExpired:
        return {"passed": [], "failed": [], "error": "Test timeout (5 min)"}
    except Exception as e:
        return {"passed": [], "failed": [], "error": str(e)}


def doctor_check_invariant_coverage(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check that HIGH priority invariants have test coverage.

    Reports:
    - INVARIANT_NO_TEST: HIGH priority invariant without verified_by.test
    - INVARIANT_UNTESTED: Invariant marked as untested
    """
    if "INVARIANT_COVERAGE" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []

    # Find and parse all VALIDATION files
    validation_files = find_validation_files(target_dir)
    all_invariants = []

    for vf in validation_files:
        invariants = parse_invariants(vf)
        all_invariants.extend(invariants)

    # Check each HIGH priority invariant
    for inv in all_invariants:
        if inv.priority == "HIGH":
            if not inv.verified_by_test and not inv.verified_by_health:
                issues.append(DoctorIssue(
                    task_type="INVARIANT_NO_TEST",
                    severity="warning",
                    path=inv.file_path,
                    message=f"HIGH priority invariant {inv.id} has no verified_by",
                    details={
                        "invariant_id": inv.id,
                        "line": inv.line_number,
                        "priority": inv.priority,
                    },
                    suggestion=f"Add verified_by: test: or health: for {inv.id}",
                    protocol="add_health_coverage"
                ))

        if inv.confidence == "untested":
            issues.append(DoctorIssue(
                task_type="INVARIANT_UNTESTED",
                severity="info",
                path=inv.file_path,
                message=f"Invariant {inv.id} marked as untested",
                details={
                    "invariant_id": inv.id,
                    "line": inv.line_number,
                    "priority": inv.priority,
                },
                suggestion=f"Write tests for {inv.id} or set confidence to needs-health",
                protocol="add_health_coverage"
            ))

    return issues


def doctor_check_test_validates_markers(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check that test files have @validates: markers.

    Reports:
    - TEST_NO_VALIDATES: Test file with no @validates markers
    """
    if "TEST_VALIDATES_MARKERS" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []

    # Find all test files
    test_files = find_test_files(target_dir)

    for tf in test_files:
        # Skip __pycache__ and other noise
        if '__pycache__' in str(tf) or '.pyc' in str(tf):
            continue

        mappings = parse_test_mappings(tf)

        # Check if file has any test functions
        content = tf.read_text()
        test_funcs = re.findall(r'def (test_\w+)', content)

        if test_funcs and not mappings:
            issues.append(DoctorIssue(
                task_type="TEST_NO_VALIDATES",
                severity="info",
                path=str(tf),
                message=f"Test file has {len(test_funcs)} tests but no @validates markers",
                details={
                    "test_count": len(test_funcs),
                    "tests": test_funcs[:5],  # First 5
                },
                suggestion="Add @validates: V-ID markers to link tests to invariants",
            ))

    return issues


def doctor_check_completion_gate(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check completion gate status.

    Reads .mind/completion/*.yaml and reports incomplete modules.

    Reports:
    - MODULE_INCOMPLETE: Module has failing tests
    - MODULE_BLOCKED: Module has blocked tests
    """
    if "COMPLETION_GATE" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []

    completion_dir = target_dir / ".mind" / "completion"
    if not completion_dir.exists():
        return issues

    try:
        import yaml
        HAS_YAML = True
    except ImportError:
        HAS_YAML = False
        return issues

    for gate_file in completion_dir.glob("*_gate.yaml"):
        try:
            with open(gate_file) as f:
                gate = yaml.safe_load(f) or {}
        except Exception:
            continue

        status = gate.get("status", "unknown")
        module = gate.get("module", gate_file.stem.replace("_gate", ""))

        if status == "incomplete":
            blocking = gate.get("blocking", [])
            issues.append(DoctorIssue(
                task_type="MODULE_INCOMPLETE",
                severity="critical",
                path=str(gate_file),
                message=f"Module {module} has {len(blocking)} failing test(s)",
                details={
                    "module": module,
                    "blocking_tests": blocking[:5],
                    "tests_passed": gate.get("tests", {}).get("passed", 0),
                    "tests_failed": gate.get("tests", {}).get("failed", 0),
                },
                suggestion=f"Fix failing tests to complete {module}",
            ))
        elif status == "blocked":
            issues.append(DoctorIssue(
                task_type="MODULE_BLOCKED",
                severity="warning",
                path=str(gate_file),
                message=f"Module {module} is blocked",
                details={
                    "module": module,
                    "blocking": gate.get("blocking", []),
                },
                suggestion="Resolve blockers or mark invariants as needs-health",
            ))

    return issues


def generate_completion_gate(
    target_dir: Path,
    module: str,
    test_pattern: str = None
) -> Dict[str, Any]:
    """Run tests and generate completion gate YAML.

    Creates .mind/completion/{module}_gate.yaml
    """
    from datetime import datetime

    # Run tests
    test_results = run_tests_for_module(target_dir, test_pattern)

    # Build gate structure
    gate = {
        "module": module,
        "generated_at": datetime.now().isoformat(),
        "status": "complete" if not test_results["failed"] else "incomplete",
        "tests": {
            "total": len(test_results["passed"]) + len(test_results["failed"]),
            "passed": len(test_results["passed"]),
            "failed": len(test_results["failed"]),
        },
        "blocking": [
            {"test": t} for t in test_results["failed"]
        ],
        "passing": [
            {"test": t} for t in test_results["passed"]
        ],
    }

    if test_results.get("error"):
        gate["error"] = test_results["error"]

    # Write to file
    completion_dir = target_dir / ".mind" / "completion"
    completion_dir.mkdir(parents=True, exist_ok=True)

    gate_file = completion_dir / f"{module}_gate.yaml"

    try:
        import yaml
        with open(gate_file, 'w') as f:
            yaml.dump(gate, f, default_flow_style=False, sort_keys=False)
    except ImportError:
        # Fallback to basic format
        with open(gate_file, 'w') as f:
            f.write(f"module: {module}\n")
            f.write(f"status: {gate['status']}\n")
            f.write(f"tests_passed: {gate['tests']['passed']}\n")
            f.write(f"tests_failed: {gate['tests']['failed']}\n")

    return gate
