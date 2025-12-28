# DOCS: docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md
"""
GitHub integration for mind.

Creates issues from doctor findings, commits with references,
and tracks issue state in SYNC files.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

from .doctor import DoctorIssue


@dataclass
class GitHubIssue:
    """Represents a GitHub issue."""
    number: int
    url: str
    title: str
    issue_type: str
    path: str


def is_gh_available() -> bool:
    """Check if gh CLI is available and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def is_git_repo(path: Path) -> bool:
    """Check if path is inside a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_repo_info(path: Path) -> Optional[Dict[str, str]]:
    """Get GitHub repo owner and name."""
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "owner,name"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                "owner": data["owner"]["login"],
                "name": data["name"],
            }
    except Exception:
        pass
    return None


def create_issue_title(issue: DoctorIssue) -> str:
    """Generate a concise issue title."""
    type_labels = {
        "MONOLITH": "Refactor",
        "UNDOCUMENTED": "Document",
        "STALE_SYNC": "Update",
        "PLACEHOLDER": "Complete",
        "INCOMPLETE_CHAIN": "Add docs",
        "NO_DOCS_REF": "Add link",
        "BROKEN_IMPL_LINK": "Fix link",
        "STUB_IMPL": "Implement",
        "INCOMPLETE_IMPL": "Complete",
        "UNDOC_IMPL": "Document",
        "LARGE_DOC_MODULE": "Reduce",
        "YAML_DRIFT": "Fix",
    }
    prefix = type_labels.get(issue.issue_type, issue.issue_type)
    # Truncate path if too long
    path = issue.path
    if len(path) > 50:
        path = "..." + path[-47:]
    return f"[{issue.issue_type}] {prefix}: {path}"


def create_issue_body(issue: DoctorIssue) -> str:
    """Generate issue body with details."""
    from .doctor import get_issue_explanation, get_issue_guidance

    explanation = get_issue_explanation(issue.issue_type)
    guidance = get_issue_guidance(issue.issue_type)

    lines = []
    lines.append(f"## {issue.issue_type}")
    lines.append("")
    lines.append(f"**File:** `{issue.path}`")
    lines.append(f"**Severity:** {issue.severity}")
    lines.append("")
    lines.append("### Problem")
    lines.append(issue.message)
    lines.append("")
    lines.append("### Risk")
    lines.append(explanation.get("risk", ""))
    lines.append("")
    lines.append("### Suggested Fix")
    lines.append(explanation.get("action", ""))
    if issue.suggestion:
        lines.append("")
        lines.append(f"**Hint:** {issue.suggestion}")
    lines.append("")
    lines.append("### Protocol")
    lines.append(f"Load `{guidance.get('view', 'VIEW_Implement_Write_Or_Modify_Code.md')}` before fixing.")
    lines.append("")
    lines.append("---")
    lines.append("*Created by `mind doctor --github`*")

    return "\n".join(lines)


def create_github_issue(
    issue: DoctorIssue,
    target_dir: Path,
    labels: Optional[List[str]] = None,
) -> Optional[GitHubIssue]:
    """Create a GitHub issue for a doctor finding."""
    title = create_issue_title(issue)
    body = create_issue_body(issue)

    cmd = [
        "gh", "issue", "create",
        "--title", title,
        "--body", body,
    ]

    # Add labels
    default_labels = ["mind", issue.severity]
    all_labels = (labels or []) + default_labels
    for label in all_labels:
        cmd.extend(["--label", label])

    try:
        result = subprocess.run(
            cmd,
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            # Parse issue URL from output
            url = result.stdout.strip()
            # Extract issue number from URL
            number = int(url.split("/")[-1])
            return GitHubIssue(
                number=number,
                url=url,
                title=title,
                issue_type=issue.issue_type,
                path=issue.path,
            )
    except Exception as e:
        print(f"    Failed to create issue: {e}")

    return None


def create_issues_for_findings(
    issues: List[DoctorIssue],
    target_dir: Path,
    max_issues: Optional[int] = None,
    labels: Optional[List[str]] = None,
) -> List[GitHubIssue]:
    """Create GitHub issues for doctor findings."""
    if not is_gh_available():
        print("  Error: gh CLI not available or not authenticated")
        print("  Run: gh auth login")
        return []

    if not is_git_repo(target_dir):
        print("  Error: Not a git repository")
        return []

    created = []
    issues_to_create = issues[:max_issues] if max_issues else issues

    for i, issue in enumerate(issues_to_create, 1):
        print(f"  [{i}/{len(issues_to_create)}] Creating issue for {issue.issue_type}: {issue.path[:40]}...")
        gh_issue = create_github_issue(issue, target_dir, labels)
        if gh_issue:
            created.append(gh_issue)
            print(f"    Created #{gh_issue.number}")

    return created


def close_github_issue(issue_number: int, target_dir: Path, comment: Optional[str] = None) -> bool:
    """Close a GitHub issue."""
    cmd = ["gh", "issue", "close", str(issue_number)]
    if comment:
        cmd.extend(["--comment", comment])

    try:
        result = subprocess.run(
            cmd,
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


def commit_with_issue_ref(
    message: str,
    issue_number: int,
    target_dir: Path,
    close_issue: bool = True,
) -> bool:
    """Create a commit that references (and optionally closes) an issue."""
    # Build commit message
    if close_issue:
        full_message = f"{message}\n\nCloses #{issue_number}"
    else:
        full_message = f"{message}\n\nRef #{issue_number}"

    try:
        # Stage all changes
        subprocess.run(["git", "add", "-A"], cwd=target_dir, check=True, timeout=30)

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", full_message],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


def find_existing_issues(
    target_dir: Path,
    label: str = "mind",
) -> List[Dict[str, Any]]:
    """Find existing mind issues in the repo."""
    try:
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--label", label,
                "--state", "open",
                "--json", "number,title,labels",
            ],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return []


def generate_issues_mapping(created_issues: List[GitHubIssue]) -> Dict[str, int]:
    """Generate a mapping of file paths to issue numbers."""
    return {issue.path: issue.number for issue in created_issues}
