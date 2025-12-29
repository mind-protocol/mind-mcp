"""
Doctor check functions for content analysis.

Health checks that analyze file content for issues:
- Long strings (prompts, SQL, templates)
- Documentation duplication
- New undocumented code (code fresher than docs)
- Recent log errors

DOCS: docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md
"""

import re
import time
from pathlib import Path
from typing import List, Dict, Any

from .core_utils import find_module_directories
from .doctor_types import DoctorIssue, DoctorConfig
from .doctor_files import (
    should_ignore_path,
    find_source_files,
    count_lines,
    is_binary_file,
)
from .solve_escalations import ESCALATION_TAGS, PROPOSITION_TAGS, TODO_TAGS, IGNORED_FILES

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def doctor_check_new_undoc_code(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for code files newer than their documentation.

    Detects:
    - Source files modified after their IMPLEMENTATION doc
    - Frontend components without stories
    - Hooks without documentation
    - New exports not reflected in docs
    """
    if "new_undoc_code" in config.disabled_checks:
        return []

    issues = []
    docs_dir = target_dir / "docs"

    if not docs_dir.exists():
        return issues

    # Build map of module -> IMPLEMENTATION doc mtime
    impl_doc_times = {}
    for impl_file in docs_dir.rglob("IMPLEMENTATION_*.md"):
        try:
            # Extract module path from doc location
            # e.g., docs/backend/auth/IMPLEMENTATION_Auth.md -> backend/auth
            rel_impl = impl_file.relative_to(docs_dir)
            module_path = str(rel_impl.parent)
            impl_mtime = impl_file.stat().st_mtime
            impl_doc_times[module_path] = (impl_file, impl_mtime)
        except Exception:
            pass

    # Frontend file patterns
    fe_extensions = {'.tsx', '.jsx', '.vue', '.svelte'}
    hook_pattern = re.compile(r'^use[A-Z].*\.(ts|tsx|js|jsx)$')
    story_extensions = {'.stories.tsx', '.stories.jsx', '.stories.ts', '.stories.js'}

    # Check source files
    for source_file in find_source_files(target_dir, config):
        if should_ignore_path(source_file, config.ignore, target_dir):
            continue

        try:
            rel_path = str(source_file.relative_to(target_dir))
            source_mtime = source_file.stat().st_mtime
        except Exception:
            continue

        # Skip small files and tests
        line_count = count_lines(source_file)
        if line_count < 30:
            continue
        if 'test' in source_file.name.lower() or '.test.' in source_file.name.lower():
            continue
        if '.spec.' in source_file.name.lower():
            continue
        if '.stories.' in source_file.name.lower():
            continue

        # Check 1: Source file newer than IMPLEMENTATION doc
        for module_path, (impl_file, impl_mtime) in impl_doc_times.items():
            # Check if this source file belongs to this module
            if rel_path.startswith(module_path) or module_path in rel_path:
                if source_mtime > impl_mtime + 86400:  # More than 1 day newer
                    days_newer = int((source_mtime - impl_mtime) / 86400)
                    issues.append(DoctorIssue(
                        issue_type="NEW_UNDOC_CODE",
                        severity="warning",
                        path=rel_path,
                        message=f"Modified {days_newer}d after IMPLEMENTATION doc",
                        details={
                            "impl_doc": str(impl_file.relative_to(target_dir)),
                            "days_newer": days_newer
                        },
                        suggestion=f"Update {impl_file.name} with changes"
                    ))
                break

        # Check 2: Frontend component without stories
        suffix = source_file.suffix.lower()
        if suffix in fe_extensions:
            # Check if it's a component (capitalized name, not index)
            if source_file.stem[0].isupper() and source_file.stem != 'Index':
                # Look for corresponding stories file
                has_stories = False
                for story_ext in story_extensions:
                    story_file = source_file.with_suffix('').with_suffix(story_ext)
                    if story_file.exists():
                        has_stories = True
                        break
                    # Also check in same directory with different naming
                    story_file2 = source_file.parent / f"{source_file.stem}.stories{suffix}"
                    if story_file2.exists():
                        has_stories = True
                        break

                if not has_stories and line_count > 50:
                    issues.append(DoctorIssue(
                        issue_type="COMPONENT_NO_STORIES",
                        severity="info",
                        path=rel_path,
                        message="Component without Storybook stories",
                        details={"line_count": line_count},
                        suggestion=f"Add {source_file.stem}.stories{suffix}"
                    ))

        # Check 3: Hook without documentation
        if hook_pattern.match(source_file.name):
            # Check if hook has JSDoc or is documented
            try:
                content = source_file.read_text()[:config.hook_check_chars]
                has_jsdoc = '/**' in content or '* @' in content
                has_docs_ref = 'DOCS:' in content
                if not has_jsdoc and not has_docs_ref and line_count > 30:
                    issues.append(DoctorIssue(
                        issue_type="HOOK_UNDOC",
                        severity="info",
                        path=rel_path,
                        message="Custom hook without documentation",
                        details={"line_count": line_count},
                        suggestion="Add JSDoc or DOCS: reference"
                    ))
            except Exception:
                pass

    return issues


def doctor_check_doc_duplication(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for duplicated documentation content.

    Detects:
    - Same file referenced in multiple IMPLEMENTATION docs
    - Similar content across different docs (potential copy-paste)
    - Multiple docs for the same module/topic
    """
    if "doc_duplication" in config.disabled_checks:
        return []

    issues = []
    docs_dir = target_dir / "docs"

    if not docs_dir.exists():
        return issues

    # Track file references across IMPLEMENTATION docs
    # Use Set to avoid flagging the same doc that mentions a file multiple times
    file_references: Dict[str, set] = {}  # file -> set of docs that reference it

    # Track doc content fingerprints for similarity detection
    doc_fingerprints: Dict[str, tuple] = {}  # doc path -> (word_set, heading_set)

    # Track docs by module/topic
    docs_by_topic: Dict[str, List[str]] = {}  # topic -> list of doc paths

    for doc_file in docs_dir.rglob("*.md"):
        if should_ignore_path(doc_file, config.ignore, target_dir):
            continue

        try:
            content = doc_file.read_text(errors="ignore")
            rel_path = str(doc_file.relative_to(target_dir))

            # Check 1: Track file references in IMPLEMENTATION docs
            if "IMPLEMENTATION" in doc_file.name:
                # Extract file paths referenced (look for src/, lib/, etc.)
                # NOTE: The capture group must include the full path, not just optional parts,
                # because re.findall() only returns captured group contents when groups exist
                file_patterns = re.findall(
                    r'[`\s](/?(?:src|lib|app|components|hooks|pages|utils)/[\w/.-]+\.\w+)',
                    content
                )
                for file_ref in file_patterns:
                    file_ref = file_ref.strip('`').lstrip('/')
                    if file_ref not in file_references:
                        file_references[file_ref] = set()
                    file_references[file_ref].add(rel_path)

            # Check 2: Build content fingerprint for similarity detection
            # Extract significant words (skip common words)
            words = set(re.findall(r'\b[a-zA-Z]{4,}\b', content.lower()))
            common_words = {'this', 'that', 'with', 'from', 'have', 'will', 'been',
                          'should', 'would', 'could', 'what', 'when', 'where', 'which',
                          'their', 'there', 'these', 'those', 'about', 'into', 'more',
                          'some', 'such', 'than', 'then', 'them', 'only', 'over'}
            words = words - common_words

            # Extract headings
            headings = set(re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE))

            doc_fingerprints[rel_path] = (words, headings)

            # Check 3: Track by doc type and parent folder (topic)
            # Skip archive files - they are intentionally created by auto-archiving
            # and should not be flagged as duplicates of the main doc
            if '_archive_' in doc_file.name:
                continue

            doc_type = None
            for dtype in ['PATTERNS', 'BEHAVIORS', 'ALGORITHM', 'IMPLEMENTATION', 'VALIDATION', 'SYNC']:
                if dtype in doc_file.name:
                    doc_type = dtype
                    break

            if doc_type:
                # Use parent folder as topic identifier
                topic = f"{doc_file.parent.name}:{doc_type}"
                if topic not in docs_by_topic:
                    docs_by_topic[topic] = []
                docs_by_topic[topic].append(rel_path)

        except Exception:
            pass

    # Report: Files referenced in multiple IMPLEMENTATION docs
    for file_ref, docs_set in file_references.items():
        if len(docs_set) > 1:
            docs_list = sorted(docs_set)  # Convert set to sorted list for consistent output
            issues.append(DoctorIssue(
                issue_type="DOC_DUPLICATION",
                severity="warning",
                path=docs_list[0],  # First doc that references it
                message=f"`{file_ref}` documented in {len(docs_list)} places",
                details={
                    "duplicated_file": file_ref,
                    "docs": docs_list,
                },
                suggestion=f"Consolidate into one IMPLEMENTATION doc, remove from others"
            ))

    # Report: Multiple docs of same type in same folder
    for topic, docs in docs_by_topic.items():
        if len(docs) > 1:
            folder, doc_type = topic.split(':')
            issues.append(DoctorIssue(
                issue_type="DOC_DUPLICATION",
                severity="warning",
                path=docs[0],
                message=f"Multiple {doc_type} docs in `{folder}/`",
                details={
                    "doc_type": doc_type,
                    "folder": folder,
                    "docs": docs,
                },
                suggestion=f"Merge into single {doc_type} doc or split into subfolder"
            ))

    # Report: Similar content across docs (compare fingerprints)
    doc_paths = list(doc_fingerprints.keys())
    for i, path1 in enumerate(doc_paths):
        words1, headings1 = doc_fingerprints[path1]
        if len(words1) < 50:  # Skip very short docs
            continue

        for path2 in doc_paths[i+1:]:
            words2, headings2 = doc_fingerprints[path2]
            if len(words2) < 50:
                continue

            # Calculate Jaccard similarity
            word_intersection = len(words1 & words2)
            word_union = len(words1 | words2)
            if word_union == 0:
                continue

            similarity = word_intersection / word_union

            # Also check heading similarity
            heading_match = len(headings1 & headings2)

            # Flag if >60% similar content or >3 matching headings
            if similarity > 0.6 or (heading_match >= 3 and similarity > 0.4):
                issues.append(DoctorIssue(
                    issue_type="DOC_DUPLICATION",
                    severity="info",
                    path=path1,
                    message=f"{int(similarity*100)}% similar to `{path2}`",
                    details={
                        "similar_to": path2,
                        "similarity": round(similarity, 2),
                        "matching_headings": heading_match,
                    },
                    suggestion="Review for duplicate content, consolidate if redundant"
                ))

    return issues


def doctor_check_recent_log_errors(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check recent .log files for error lines within the last hour."""
    if "log_errors" in config.disabled_checks:
        return []

    issues = []
    seen = set()
    per_file_counts: Dict[str, int] = {}
    cutoff = time.time() - 3600
    error_re = re.compile(r"error", re.IGNORECASE)

    for log_file in target_dir.rglob("*.log"):
        if should_ignore_path(log_file, config.ignore, target_dir):
            continue

        try:
            if log_file.stat().st_mtime < cutoff:
                continue
        except Exception:
            continue

        try:
            rel_path = str(log_file.relative_to(target_dir))
            content = log_file.read_text(errors="ignore")
        except Exception:
            continue

        per_file_counts.setdefault(rel_path, 0)
        lines = content.splitlines()
        if len(lines) > 2000:
            start_line = len(lines) - 2000 + 1
            lines = lines[-2000:]
        else:
            start_line = 1

        for idx, line in enumerate(lines, start_line):
            if not error_re.search(line):
                continue
            snippet = line.strip()
            if not snippet:
                continue
            key = (rel_path, snippet)
            if key in seen:
                continue
            seen.add(key)
            per_file_counts[rel_path] += 1
            if per_file_counts[rel_path] > 10:
                continue
            issues.append(DoctorIssue(
                issue_type="LOG_ERROR",
                severity="warning",
                path=rel_path,
                message=f"Log error: {snippet[:200]}",
                details={"line": idx, "error": snippet},
                suggestion="Inspect recent log errors"
            ))

    return issues


def doctor_check_long_strings(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for long strings that should be externalized.

    Detects:
    - Long prompt strings (should go in /prompts directory)
    - Long SQL queries (should be in separate files)
    - Long HTML/template strings
    """
    if "long_strings" in config.disabled_checks:
        return []

    issues = []

    # Threshold for "long" strings (characters)
    long_string_threshold = getattr(config, 'long_string_threshold', 500)

    # Patterns for long strings
    # Triple-quoted strings in Python
    triple_quote_pattern = re.compile(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', re.MULTILINE)
    # Template literals in JS/TS
    template_literal_pattern = re.compile(r'`[^`]{200,}`', re.MULTILINE)

    code_extensions = {".py", ".js", ".ts", ".tsx", ".jsx"}

    for ext in code_extensions:
        for code_file in target_dir.rglob(f"*{ext}"):
            if should_ignore_path(code_file, config.ignore, target_dir):
                continue

            # Skip test files and prompt files (they're supposed to have long strings)
            if "test" in code_file.name.lower() or "prompt" in str(code_file).lower():
                continue

            try:
                content = code_file.read_text(errors="ignore")
                rel_path = str(code_file.relative_to(target_dir))

                long_strings = []

                # Check triple-quoted strings (Python)
                if ext == ".py":
                    for match in triple_quote_pattern.finditer(content):
                        string_content = match.group(1)
                        if len(string_content) > long_string_threshold:
                            # Check if it looks like a prompt or SQL
                            is_prompt = any(x in string_content.lower() for x in [
                                "you are", "your task", "please", "generate", "respond",
                                "instructions", "context", "## task", "## step"
                            ])
                            is_sql = any(x in string_content.upper() for x in [
                                "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE TABLE"
                            ])

                            if is_prompt:
                                long_strings.append(("prompt", len(string_content)))
                            elif is_sql:
                                long_strings.append(("SQL query", len(string_content)))
                            else:
                                long_strings.append(("long string", len(string_content)))

                # Check template literals (JS/TS)
                if ext in {".js", ".ts", ".tsx", ".jsx"}:
                    for match in template_literal_pattern.finditer(content):
                        long_strings.append(("template literal", len(match.group(0))))

                if long_strings:
                    # Group by type
                    prompts = [s for s in long_strings if s[0] == "prompt"]
                    sqls = [s for s in long_strings if s[0] == "SQL query"]

                    if prompts:
                        issues.append(DoctorIssue(
                            issue_type="LONG_PROMPT",
                            severity="info",
                            path=rel_path,
                            message=f"Contains {len(prompts)} long prompt string(s)",
                            details={"count": len(prompts), "chars": sum(p[1] for p in prompts)},
                            suggestion="Move prompts to prompts/ directory for easier editing"
                        ))
                    if sqls:
                        issues.append(DoctorIssue(
                            issue_type="LONG_SQL",
                            severity="info",
                            path=rel_path,
                            message=f"Contains {len(sqls)} long SQL query/queries",
                            details={"count": len(sqls)},
                            suggestion="Move SQL to separate .sql files"
                        ))

            except Exception:
                pass

    return issues


from .solve_escalations import ESCALATION_TAGS, PROPOSITION_TAGS, IGNORED_FILES


def _strip_code_blocks(content: str) -> str:
    """Remove code blocks (```...```) from content to avoid false positives."""
    # Remove fenced code blocks
    return re.sub(r'```[\s\S]*?```', '', content)


def _extract_questions_from_text(text: str, is_code: bool = False) -> List[str]:
    """Extract sentences ending with '?' from text.

    For code files, only looks at comments.
    """
    questions = []

    if is_code:
        # Extract comments from code
        # Python: # comments and """ docstrings
        # JS/TS: // comments and /* */ blocks
        comment_patterns = [
            r'#\s*(.+\?)',  # Python single-line comments
            r'//\s*(.+\?)',  # JS/TS single-line comments
            r'/\*[\s\S]*?\*/',  # Multi-line comments
            r'"""[\s\S]*?"""',  # Python docstrings
            r"'''[\s\S]*?'''",  # Python docstrings
        ]

        for pattern in comment_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Extract question sentences
                q_matches = re.findall(r'[^.!?\n]*\?', match if isinstance(match, str) else match)
                questions.extend(q.strip() for q in q_matches if len(q.strip()) > 10)
    else:
        # For docs, strip code blocks first
        clean_text = _strip_code_blocks(text)
        # Find sentences ending with ?
        q_matches = re.findall(r'[^.!?\n]*\?', clean_text)
        questions.extend(q.strip() for q in q_matches if len(q.strip()) > 10)

    return questions


def doctor_check_legacy_markers(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for legacy marker formats and unresolved questions.

    Detects:
    - Old GAPS / IDEAS / QUESTIONS section headers
    - Legacy `- [ ]` todo items (should be @mind:todo)
    - Legacy `- IDEA:` items (should be @mind:proposition)
    - Legacy `- QUESTION:` items (should be @mind:escalation)
    - Unresolved questions (sentences ending with ?) in docs and code comments
    """
    if "legacy_markers" in config.disabled_checks:
        return []

    issues = []
    docs_dir = target_dir / "docs"

    # Legacy patterns to detect
    legacy_patterns = {
        "GAPS_SECTION": (r'^## GAPS / IDEAS / QUESTIONS', "Legacy GAPS section header"),
        "LEGACY_TODO": (r'^- \[ \] ', "Legacy todo format (use @mind:todo)"),
        "LEGACY_IDEA": (r'^- IDEA:', "Legacy IDEA format (use @mind:proposition)"),
        "LEGACY_QUESTION": (r'^- QUESTION:', "Legacy QUESTION format (use @mind:escalation)"),
    }

    # Check docs for legacy markers and questions
    if docs_dir.exists():
        for doc_file in docs_dir.rglob("*.md"):
            if should_ignore_path(doc_file, config.ignore, target_dir):
                continue
            # Skip templates and archives
            if "TEMPLATE" in doc_file.name or "_archive_" in doc_file.name:
                continue

            try:
                content = doc_file.read_text(errors="ignore")
                rel_path = str(doc_file.relative_to(target_dir))

                # Check for legacy patterns
                for marker_type, (pattern, message) in legacy_patterns.items():
                    if re.search(pattern, content, re.MULTILINE):
                        issues.append(DoctorIssue(
                            issue_type="LEGACY_MARKER",
                            severity="warning",
                            path=rel_path,
                            message=message,
                            details={"marker_type": marker_type},
                            suggestion="Convert to @mind:todo, @mind:proposition, or @mind:escalation format"
                        ))

                # Check for unresolved questions (not in code blocks or MARKERS sections)
                # Remove MARKERS sections and Discussion sections before scanning
                clean_content = _strip_code_blocks(content)
                # Remove ## MARKERS sections (they're intentional placeholders)
                clean_content = re.sub(r'^## MARKERS\n[\s\S]*?(?=^## |\Z)', '', clean_content, flags=re.MULTILINE)
                # Remove Discussion sections (questions there are intentional)
                clean_content = re.sub(r'^#+ Discussion\n[\s\S]*?(?=^#+ |\Z)', '', clean_content, flags=re.MULTILINE | re.IGNORECASE)
                clean_content = re.sub(r'^#+ Open Questions\n[\s\S]*?(?=^#+ |\Z)', '', clean_content, flags=re.MULTILINE | re.IGNORECASE)

                # Find sentences ending with ?
                q_matches = re.findall(r'[^.!?\n]*\?', clean_content)
                questions = [q.strip() for q in q_matches if len(q.strip()) > 10]

                # Filter out rhetorical/documentation questions
                skip_patterns = [
                    r'^what is',  # Definitional
                    r'^how to',   # Tutorial
                    r'^why ',     # Explanatory
                    r'^when ',    # Conditional
                    r'^where ',   # Locational
                    r'example',   # Example questions
                    r'<!--',      # HTML comments (already markers)
                ]

                actionable_questions = []
                for q in questions:
                    q_lower = q.lower()
                    # Skip if it's a documentation/rhetorical question
                    if any(re.search(pat, q_lower) for pat in skip_patterns):
                        continue
                    # Skip if it's already in a marker
                    if '@mind:' in q:
                        continue
                    # Skip very short questions
                    if len(q) < 20:
                        continue
                    actionable_questions.append(q)

                if actionable_questions:
                    issues.append(DoctorIssue(
                        issue_type="UNRESOLVED_QUESTION",
                        severity="info",
                        path=rel_path,
                        message=f"{len(actionable_questions)} unresolved question(s)",
                        details={
                            "questions": actionable_questions[:5],  # Limit to first 5
                            "total_count": len(actionable_questions),
                        },
                        suggestion="Investigate and convert to @mind:escalation or @mind:proposition, or resolve directly"
                    ))

            except Exception:
                pass

    # Check code files for questions in comments
    code_extensions = {".py", ".js", ".ts", ".tsx", ".jsx"}

    for ext in code_extensions:
        for code_file in target_dir.rglob(f"*{ext}"):
            if should_ignore_path(code_file, config.ignore, target_dir):
                continue
            # Skip test files and prompts
            if "test" in code_file.name.lower() or "prompt" in str(code_file).lower():
                continue
            # Skip node_modules, .venv, etc.
            if any(p in str(code_file) for p in ["node_modules", ".venv", "__pycache__", ".git"]):
                continue

            try:
                content = code_file.read_text(errors="ignore")
                rel_path = str(code_file.relative_to(target_dir))

                # Extract questions from comments only
                questions = _extract_questions_from_text(content, is_code=True)

                # Filter out trivial questions
                actionable_questions = [q for q in questions if len(q) > 20 and '@mind:' not in q]

                if actionable_questions:
                    issues.append(DoctorIssue(
                        issue_type="UNRESOLVED_QUESTION",
                        severity="info",
                        path=rel_path,
                        message=f"{len(actionable_questions)} question(s) in comments",
                        details={
                            "questions": actionable_questions[:3],  # Limit to first 3
                            "total_count": len(actionable_questions),
                        },
                        suggestion="Investigate: fix directly if clear, or convert to @mind:escalation"
                    ))

            except Exception:
                pass

    return issues


def _extract_marker_priority(content: str, marker_tags: tuple) -> int:
    """Extract priority from marker YAML. Returns 0-10 (higher = more urgent)."""
    for tag in marker_tags:
        if tag not in content:
            continue
        # Find the marker section
        start = content.find(tag)
        end = min(start + 500, len(content))  # Look at next 500 chars
        section = content[start:end]

        # Try to find priority field
        # Format: priority: 8 or priority: high
        priority_match = re.search(r'priority:\s*(\d+|low|medium|high|critical)', section, re.IGNORECASE)
        if priority_match:
            val = priority_match.group(1).lower()
            if val.isdigit():
                return int(val)
            # Convert text priorities to numeric
            return {"critical": 10, "high": 8, "medium": 5, "low": 2}.get(val, 5)
    return 5  # Default priority


def doctor_check_special_markers(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for special markers that need attention (escalations, propositions, todos).

    Extracts priority from marker YAML to order results.
    """
    issues = []

    all_marker_info = [
        ("ESCALATION", ESCALATION_TAGS, "Escalation marker needs decision"),
        ("PROPOSITION", PROPOSITION_TAGS, "Agent proposition needs review"),
        ("TODO", TODO_TAGS, "Todo marker needs attention"),
    ]
    # Base severity by type - escalations are warnings, others are info
    severity_by_type = {
        "ESCALATION": "warning",
        "PROPOSITION": "info",
        "TODO": "info",
    }

    for issue_type, marker_tags, message_template in all_marker_info:
        for path in target_dir.rglob("*"):
            if not path.is_file():
                continue
            if should_ignore_path(path, config.ignore, target_dir):
                continue
            if str(path.relative_to(target_dir)) in IGNORED_FILES:
                continue
            if path.suffix == ".log":
                continue
            if is_binary_file(path):
                continue
            rel_path = str(path.relative_to(target_dir))
            if rel_path.startswith("templates/") or rel_path.startswith(".mind/views"):
                continue
            try:
                content = path.read_text(errors="ignore")
            except Exception:
                continue
            if not any(tag in content for tag in marker_tags):
                continue

            # Extract priority from marker YAML
            priority = _extract_marker_priority(content, marker_tags)

            # High priority markers (7+) get elevated severity
            severity = severity_by_type.get(issue_type, "info")
            if priority >= 7:
                severity = "warning" if severity == "info" else "critical"

            # Find title if available
            title_match = re.search(r'(?:title|task_name):\s*["\']?([^"\'\n]+)', content)
            title = title_match.group(1).strip() if title_match else ""

            message = f"{message_template} (priority: {priority})"
            if title:
                message = f"{title[:60]} (priority: {priority})"

            issues.append(DoctorIssue(
                issue_type=issue_type,
                severity=severity,
                path=rel_path,
                message=message,
                details={
                    "markers": [tag for tag in marker_tags if tag in content],
                    "priority": priority,
                    "title": title,
                    "content_snippet": content[content.find(next(tag for tag in marker_tags if tag in content)):][:200] + "..." if any(tag in content for tag in marker_tags) else ""
                },
                suggestion=f"Review and resolve {issue_type.lower()} in this file"
            ))

    # Sort by priority (highest first) within each issue type
    issues.sort(key=lambda x: (-x.details.get("priority", 5), x.issue_type))
    return issues
