"""
Agent Prompt Construction

Builds system prompts and task prompts for work agents.
Extracts prompt templates and helper functions from work_core.

Contains:
- AGENT_SYSTEM_PROMPT: Base system prompt for work agents
- build_agent_prompt: Constructs full task prompt with context
- get_learnings_content: Loads global learnings for injection
- split_docs_to_read: Separates existing from missing docs
- _detect_recent_issue_number: Finds GitHub issue from git history

DOCS: docs/agents/PATTERNS_Agent_System.md
"""

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# AGENT SYSTEM PROMPT
# =============================================================================

AGENT_SYSTEM_PROMPT = """You are an mind work agent. Your job is to fix ONE specific issue in the project.

CRITICAL RULES:
1. FIRST: Read all documentation listed in "Docs to Read" before making changes
2. Follow the VIEW instructions exactly
3. After fixing, update the relevant SYNC file with what you changed
4. Keep changes minimal and focused on the specific issue
5. Do NOT make unrelated changes or "improvements"
6. Report completion status clearly at the end
7. NEVER create git branches - always work on the current branch
8. NEVER use git stash - other agents are working in parallel

PIPELINE AWARENESS:
You are part of a development pipeline. When making changes, keep docs in sync:
- Code changes → Update ALGORITHM and/or IMPLEMENTATION docs
- Behavior changes → Update BEHAVIORS doc
- Design changes → Update PATTERNS doc
- Test changes → Update TEST doc
- ANY changes → Update SYNC with what changed and why

The doctor checks for drift (STALE_SYNC, NEW_UNDOC_CODE, STALE_IMPL).
The manager monitors your work for doc/code alignment.
Don't leave upstream docs stale when you change downstream artifacts.

CLI COMMANDS (use these!):
- `mind context {file}` - Get full doc chain for any source file
- `mind validate` - Check protocol invariants after changes
- `mind doctor` - Re-check project health

BIDIRECTIONAL LINKS:
- When creating new docs, add CHAIN section linking to related docs
- When modifying code, ensure DOCS: reference points to correct docs
- When creating module docs, add mapping to modules.yaml

AFTER CHANGES:
- Run `mind validate` to verify links are correct
- Update SYNC file with what changed
- Commit with descriptive message using a type prefix (e.g., "fix:", "docs:", "refactor:") and include the issue reference ("Closes #NUMBER" if provided or inferred from recent commits)

IF YOU CAN'T COMPLETE THE FULL FIX:
- Add a "## GAPS" section to the relevant SYNC file listing:
  - What was completed
  - What remains to be done
  - Why you couldn't finish (missing info, too complex, needs human decision, etc.)
Do NOT claim completion without a git commit.

IF YOU FIND CONTRADICTIONS (docs vs code, or doc vs doc):
- Add a "## CONFLICTS" section to the relevant SYNC file
- **BE DECISIVE** - make the call yourself unless you truly cannot

**Before making a DECISION:**
- If <70% confident, RE-READ the relevant docs first
- Check: PATTERNS (why), BEHAVIORS (what), ALGORITHM (how), VALIDATION (constraints)

- For each conflict, categorize as DECISION or ESCALATION:
  - DECISION: You resolve it (this should be 90%+ of conflicts)
  - ESCALATION: Only when you truly cannot decide

- **DECISION format** (preferred - be decisive!):
  ```
  ### DECISION: {conflict name}
  - Conflict: {what contradicted what}
  - Resolution: {what you decided}
  - Reasoning: {why this choice}
  - Updated: {what files you changed}
  ```
"""


# =============================================================================
# LEARNINGS LOADER
# =============================================================================

def get_learnings_content(target_dir: Path) -> str:
    """
    Load learnings from GLOBAL_LEARNINGS.md.

    Args:
        target_dir: Project root directory

    Returns:
        Formatted learnings content to append to system prompt,
        or empty string if no learnings file exists.
    """
    views_dir = target_dir / ".mind" / "views"
    global_learnings = views_dir / "GLOBAL_LEARNINGS.md"

    if global_learnings.exists():
        content = global_learnings.read_text()
        if "## Learnings" in content and content.count("\n") > 10:
            return "\n\n---\n\n# GLOBAL LEARNINGS (apply to ALL tasks)\n" + content
    return ""


# =============================================================================
# DOC SPLITTING HELPER
# =============================================================================

def split_docs_to_read(docs_to_read: List[str], target_dir: Path) -> tuple:
    """
    Split docs into existing and missing paths relative to target_dir.

    Args:
        docs_to_read: List of doc paths to check
        target_dir: Project root directory

    Returns:
        Tuple of (existing_docs, missing_docs) as lists of paths
    """
    existing = []
    missing = []
    for doc in docs_to_read:
        if not doc:
            continue
        doc_path = Path(doc)
        candidate = doc_path if doc_path.is_absolute() else (target_dir / doc_path)
        if candidate.exists():
            existing.append(doc)
        else:
            missing.append(doc)
    return existing, missing


# =============================================================================
# GIT ISSUE DETECTION
# =============================================================================

def _detect_recent_issue_number(target_dir: Path, max_commits: int = 5) -> Optional[int]:
    """
    Detect a recent issue number from the last few commit messages.

    Scans recent git commits for #N patterns to find an associated
    GitHub issue number for commit message references.

    Args:
        target_dir: Project root directory
        max_commits: How many recent commits to scan (default: 5)

    Returns:
        Issue number if found, None otherwise
    """
    try:
        result = subprocess.run(
            ["git", "log", f"-{max_commits}", "--pretty=%s"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        for line in result.stdout.splitlines():
            match = re.search(r"#(\d+)", line)
            if match:
                return int(match.group(1))
    except Exception:
        return None
    return None


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_agent_prompt(
    issue: Any,  # DoctorIssue
    instructions: Dict[str, Any],
    target_dir: Path,
    github_issue_number: Optional[int] = None,
) -> str:
    """
    Build the full prompt for the work agent.

    Combines:
    - Issue metadata (type, severity)
    - View instructions
    - Docs to read (existing and missing)
    - GitHub issue reference (if any)
    - Completion instructions

    Args:
        issue: DoctorIssue with issue_type, severity, path
        instructions: Dict with 'view', 'docs_to_read', 'prompt' keys
        target_dir: Project root directory
        github_issue_number: Optional GitHub issue to reference in commits

    Returns:
        Full prompt string for the work agent
    """
    existing_docs, missing_docs = split_docs_to_read(instructions["docs_to_read"], target_dir)
    docs_list = "\n".join(f"- {d}" for d in existing_docs) or "- (no docs found)"
    missing_section = ""
    if missing_docs:
        missing_list = "\n".join(f"- {d}" for d in missing_docs)
        missing_section = f"""
## Missing Docs at Prompt Time
{missing_list}

If any missing docs should exist, locate the correct paths before proceeding.
"""

    if github_issue_number is None:
        github_issue_number = _detect_recent_issue_number(target_dir)

    github_section = ""
    if github_issue_number:
        github_section = f"""
## GitHub Issue
This fix is tracked by GitHub issue #{github_issue_number}.
When committing, include "Closes #{github_issue_number}" in your commit message.
"""

    return f"""# mind Work Task

## Issue Type: {issue.issue_type}
## Severity: {issue.severity}
{github_section}
## VIEW to Follow
Load and follow: `.mind/views/{instructions['view']}`

## Docs to Read FIRST (before any changes)
{docs_list}
{missing_section}

{instructions['prompt']}

## After Completion
1. Commit your changes with a descriptive message using a type prefix (e.g., "fix:", "docs:", "refactor:"){f' and include "Closes #{github_issue_number}"' if github_issue_number else ''}
2. Update `.mind/state/SYNC_Project_State.md` with:
   - What you fixed
   - Files created/modified
   - Any issues encountered
"""
