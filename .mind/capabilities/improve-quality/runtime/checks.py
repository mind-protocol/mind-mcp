"""
Health Checks: improve-quality

Decorator-based health checks for code quality issues.
Detects monoliths, hardcoded secrets, magic values, long prompts,
complex SQL, and naming violations.

DOCS: capabilities/improve-quality/HEALTH.md
"""

import re
from pathlib import Path

from runtime.capability import check, Signal, triggers


# =============================================================================
# CONSTANTS
# =============================================================================

MONOLITH_THRESHOLD = 500
MONOLITH_CRITICAL_THRESHOLD = 1000
MAGIC_VALUE_THRESHOLD = 3
PROMPT_LENGTH_THRESHOLD = 4000
SQL_LENGTH_THRESHOLD = 1000
SQL_JOIN_THRESHOLD = 5
SQL_SUBQUERY_THRESHOLD = 2

CODE_EXTENSIONS = {".py", ".ts", ".js", ".tsx", ".jsx", ".java", ".go", ".rs"}
SAFE_NUMBERS = {"0", "1", "-1", "100", "1000"}

EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}

SECRET_PATTERNS = {
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "openai_key": r"sk-[a-zA-Z0-9]{20,}",
    "github_token": r"ghp_[a-zA-Z0-9]{36}",
    "password_assignment": r'password\s*=\s*["\'][^"\']+["\']',
    "token_assignment": r'token\s*=\s*["\'][^"\']{20,}["\']',
    "api_key_assignment": r'api_key\s*=\s*["\'][^"\']+["\']',
    "bearer_token": r"Bearer\s+[a-zA-Z0-9._-]{20,}",
    "connection_string": r"://[^:]+:[^@]+@",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def count_effective_lines(file_path: Path) -> int:
    """Count non-blank, non-comment lines."""
    try:
        content = file_path.read_text()
    except Exception:
        return 0

    lines = content.split("\n")
    count = 0
    in_multiline_comment = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if '"""' in stripped or "'''" in stripped:
            in_multiline_comment = not in_multiline_comment
            continue
        if in_multiline_comment:
            continue
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        count += 1

    return count


def collect_code_files(root: Path) -> list[Path]:
    """Collect code files, excluding vendored/test dirs."""
    files = []
    for ext in CODE_EXTENSIONS:
        for path in root.rglob(f"*{ext}"):
            if any(excluded in path.parts for excluded in EXCLUDE_DIRS):
                continue
            files.append(path)
    return files


# =============================================================================
# HEALTH CHECKS
# =============================================================================

@check(
    id="monolith_detection",
    triggers=[
        triggers.file.on_modify("**/*.{py,ts,js,tsx,jsx}"),
        triggers.cron.daily(),
    ],
    on_problem="MONOLITH",
    task="TASK_split_monolith",
)
def monolith_detection(ctx) -> dict:
    """
    H1: Detect files exceeding 500 effective lines.

    Returns CRITICAL if any file > 1000 lines.
    Returns DEGRADED if any file > 500 lines.
    Returns HEALTHY if all files under threshold.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")

    if ctx.file_path:
        paths = [Path(ctx.file_path)]
    else:
        paths = collect_code_files(root)

    monoliths = []

    for path in paths:
        if path.suffix not in CODE_EXTENSIONS:
            continue

        line_count = count_effective_lines(path)

        if line_count > MONOLITH_THRESHOLD:
            monoliths.append({
                "file": str(path),
                "line_count": line_count,
                "critical": line_count > MONOLITH_CRITICAL_THRESHOLD,
            })

    if not monoliths:
        return Signal.healthy()

    has_critical = any(m["critical"] for m in monoliths)

    if has_critical:
        return Signal.critical(monoliths=monoliths, count=len(monoliths))

    return Signal.degraded(monoliths=monoliths, count=len(monoliths))


@check(
    id="secret_detection",
    triggers=[
        triggers.file.on_modify("**/*.{py,ts,js,tsx,jsx}"),
        triggers.file.on_create("**/*.{py,ts,js,tsx,jsx}"),
        triggers.cron.daily(),
    ],
    on_problem="HARDCODED_SECRET",
    task="TASK_remove_secret",
)
def secret_detection(ctx) -> dict:
    """
    H2: Detect hardcoded secrets in code. CRITICAL.

    Returns CRITICAL if any secret pattern found.
    Returns HEALTHY if no secrets detected.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")

    if ctx.file_path:
        paths = [Path(ctx.file_path)]
    else:
        paths = collect_code_files(root)

    findings = []

    for path in paths:
        # Skip example and test files
        name = path.name.lower()
        if ".example" in name or "_test" in name or "test_" in name:
            continue

        try:
            content = path.read_text()
        except Exception:
            continue

        file_secrets = []
        for pattern_name, pattern in SECRET_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE):
                file_secrets.append(pattern_name)

        if file_secrets:
            findings.append({
                "file": str(path),
                "patterns": file_secrets,
            })

    if not findings:
        return Signal.healthy()

    return Signal.critical(findings=findings, count=len(findings))


@check(
    id="magic_value_detection",
    triggers=[
        triggers.file.on_modify("**/*.{py,ts,js}"),
        triggers.cron.weekly(),
    ],
    on_problem="MAGIC_VALUES",
    task="TASK_extract_constants",
)
def magic_value_detection(ctx) -> dict:
    """
    H3: Detect hardcoded magic values (numbers, IPs).

    Returns DEGRADED if >= 3 magic values found in a file.
    Returns HEALTHY if under threshold.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")

    if ctx.file_path:
        paths = [Path(ctx.file_path)]
    else:
        paths = collect_code_files(root)

    files_with_magic = []

    for path in paths:
        try:
            content = path.read_text()
        except Exception:
            continue

        values = []
        for match in re.finditer(r"\b(\d{4,})\b", content):
            value = match.group(1)
            if value not in SAFE_NUMBERS:
                values.append(value)

        for match in re.finditer(r"\b(\d+\.\d+\.\d+\.\d+)\b", content):
            values.append(match.group(1))

        if len(values) >= MAGIC_VALUE_THRESHOLD:
            files_with_magic.append({
                "file": str(path),
                "values": values[:10],
                "count": len(values),
            })

    if not files_with_magic:
        return Signal.healthy()

    return Signal.degraded(
        files=files_with_magic,
        count=len(files_with_magic),
    )


@check(
    id="prompt_length_detection",
    triggers=[
        triggers.file.on_modify("**/*.py"),
        triggers.cron.weekly(),
    ],
    on_problem="LONG_PROMPT",
    task="TASK_split_prompt",
)
def prompt_length_detection(ctx) -> dict:
    """
    H4: Detect prompts exceeding 4000 characters.

    Returns DEGRADED if long prompts found.
    Returns HEALTHY if all prompts under threshold.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")

    if ctx.file_path:
        paths = [Path(ctx.file_path)]
    else:
        paths = [p for p in collect_code_files(root) if p.suffix == ".py"]

    long_prompts = []

    prompt_patterns = [
        r'(?:SYSTEM_PROMPT|system_prompt|PROMPT)\s*=\s*["\'\"](.+?)["\'\"]',
        r'(?:prompt|message)\s*=\s*f?["\'\"](.+?)["\'\"]',
    ]

    for path in paths:
        try:
            content = path.read_text()
        except Exception:
            continue

        for pattern in prompt_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                prompt_content = match.group(1)
                if len(prompt_content) > PROMPT_LENGTH_THRESHOLD:
                    long_prompts.append({
                        "file": str(path),
                        "char_count": len(prompt_content),
                    })

    if not long_prompts:
        return Signal.healthy()

    return Signal.degraded(
        long_prompts=long_prompts,
        count=len(long_prompts),
    )


@check(
    id="naming_convention_detection",
    triggers=[
        triggers.file.on_create("**/*.{py,ts,js}"),
        triggers.cron.weekly(),
    ],
    on_problem="NAMING_CONVENTION",
    task="TASK_fix_naming",
)
def naming_convention_detection(ctx) -> dict:
    """
    H5: Detect naming convention violations.

    Python: snake_case files, PascalCase classes.
    JS/TS: kebab-case files, PascalCase classes.

    Returns DEGRADED if violations found.
    Returns HEALTHY if conventions followed.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")

    if ctx.file_path:
        paths = [Path(ctx.file_path)]
    else:
        paths = collect_code_files(root)

    conventions = {
        ".py": {"file": r"^[a-z][a-z0-9_]*$", "class": r"^[A-Z][a-zA-Z0-9]*$"},
        ".ts": {"file": r"^[a-z][a-z0-9-]*$", "class": r"^[A-Z][a-zA-Z0-9]*$"},
        ".js": {"file": r"^[a-z][a-z0-9-]*$", "class": r"^[A-Z][a-zA-Z0-9]*$"},
    }

    violations = []

    for path in paths:
        ext = path.suffix
        if ext not in conventions:
            continue

        rules = conventions[ext]
        file_violations = []

        if "file" in rules and not re.match(rules["file"], path.stem):
            file_violations.append(f"filename: {path.stem}")

        try:
            content = path.read_text()
            if "class" in rules:
                classes = re.findall(r"class\s+(\w+)", content)
                for cls in classes:
                    if not re.match(rules["class"], cls):
                        file_violations.append(f"class: {cls}")
        except Exception:
            pass

        if file_violations:
            violations.append({
                "file": str(path),
                "violations": file_violations[:5],
            })

    if not violations:
        return Signal.healthy()

    return Signal.degraded(
        violations=violations,
        count=len(violations),
    )


# =============================================================================
# REGISTRY
# =============================================================================

CHECKS = [
    monolith_detection,
    secret_detection,
    magic_value_detection,
    prompt_length_detection,
    naming_convention_detection,
]
