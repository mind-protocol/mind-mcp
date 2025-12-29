# Module-level checks around modules.yaml metadata.
# DOCS: docs/mcp-design/doctor/IMPLEMENTATION_Project_Health_Doctor.md

from pathlib import Path
from typing import List

from .core_utils import HAS_YAML
from .doctor_types import DoctorConfig, DoctorIssue


def doctor_check_yaml_drift(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    if "yaml_drift" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    manifest_path = target_dir / "modules.yaml"

    if not manifest_path.exists() or not HAS_YAML:
        return issues

    try:
        import yaml

        with open(manifest_path) as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return issues

    modules = data.get("modules") or {}
    module_names = set(modules.keys())

    for module_name, module_data in modules.items():
        if not isinstance(module_data, dict):
            continue

        drift_issues = []
        code_path = module_data.get("code")
        if code_path:
            base_path = str(code_path)
            if isinstance(base_path, list):
                base_path = base_path[0] if base_path else ""
            base_path = base_path.replace("/**", "").replace("/*", "").rstrip("/")
            if base_path and not (target_dir / base_path).exists():
                drift_issues.append(f"code path '{base_path}' not found")

        docs_path = module_data.get("docs")
        if docs_path:
            base_docs = str(docs_path)
            if isinstance(base_docs, list):
                base_docs = base_docs[0] if base_docs else ""
            base_docs = base_docs.rstrip("/")
            if base_docs and not (target_dir / base_docs).exists():
                drift_issues.append(f"docs path '{base_docs}' not found")

        tests_path = module_data.get("tests")
        if tests_path:
            base_tests = str(tests_path)
            if isinstance(base_tests, list):
                base_tests = base_tests[0] if base_tests else ""
            base_tests = base_tests.replace("/**", "").replace("/*", "").rstrip("/")
            if base_tests and not (target_dir / base_tests).exists():
                drift_issues.append(f"tests path '{base_tests}' not found")

        depends_on = module_data.get("depends_on", [])
        if isinstance(depends_on, list):
            for dep in depends_on:
                if dep not in module_names:
                    drift_issues.append(f"dependency '{dep}' not defined")

        if drift_issues:
            issues.append(DoctorIssue(
                issue_type="YAML_DRIFT",
                severity="critical",
                path=f"modules.yaml#{module_name}",
                message=f"Module '{module_name}' has {len(drift_issues)} drift issue(s)",
                details={"module": module_name, "issues": drift_issues},
                suggestion="; ".join(drift_issues[:3])
            ))

    return issues


def doctor_check_missing_tests(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    if "MISSING_TESTS" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    modules_yaml = target_dir / "modules.yaml"

    if not modules_yaml.exists() or not HAS_YAML:
        return issues

    try:
        import yaml

        with open(modules_yaml) as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return issues

    modules = data.get("modules") or {}

    for module_name, module_data in modules.items():
        if not isinstance(module_data, dict):
            continue

        tests_path = module_data.get("tests")
        code_path = module_data.get("code")
        if not code_path:
            continue

        if tests_path:
            test_dir = target_dir / str(tests_path).rstrip("/*")
            if test_dir.exists():
                continue

        issues.append(DoctorIssue(
            issue_type="MISSING_TESTS",
            severity="info",
            path=module_name,
            message="No tests for module",
            details={"module": module_name, "code": code_path},
            suggestion="Add tests and update modules.yaml"
        ))

    return issues
