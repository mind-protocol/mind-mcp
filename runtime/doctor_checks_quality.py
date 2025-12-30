"""
Doctor check functions for code quality analysis.

Health checks that analyze code for quality issues:
- Magic numbers and hardcoded values
- Hardcoded secrets and credentials

DOCS: docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md
"""

import re
from pathlib import Path
from typing import List, Dict, Any

from .doctor_types import DoctorIssue, DoctorConfig
from .doctor_files import should_ignore_path


def doctor_check_magic_values(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for magic numbers and hardcoded values that should be in constants.

    Detects:
    - Magic numbers (unexplained numeric literals)
    - Hardcoded strings that look like configuration
    - Values that should be in a constants file
    """
    if "magic_values" in config.disabled_checks:
        return []

    issues = []

    # Patterns for magic values
    # Magic numbers: numeric literals that aren't 0, 1, -1, 2, 100, etc.
    magic_number_pattern = re.compile(r'(?<![a-zA-Z_])(\d{3,}|\d+\.\d+)(?![a-zA-Z_\d])')
    # Hardcoded URLs, IPs, ports
    hardcoded_patterns = [
        (re.compile(r'https?://[^\s"\']+(?<![\.,])'), "hardcoded URL"),
        (re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'), "hardcoded IP address"),
        (re.compile(r':\d{4,5}(?![0-9])'), "hardcoded port"),
    ]

    # Files to check
    code_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"}

    for ext in code_extensions:
        for code_file in target_dir.rglob(f"*{ext}"):
            if should_ignore_path(code_file, config.ignore, target_dir):
                continue

            # Skip constants/config files
            if any(x in code_file.name.lower() for x in ["const", "config", "settings", "env"]):
                continue

            try:
                content = code_file.read_text(errors="ignore")
                lines = content.split("\n")
                rel_path = str(code_file.relative_to(target_dir))

                magic_numbers = []
                hardcoded_values = []

                for i, line in enumerate(lines, 1):
                    # Skip comments and strings in some cases
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith("//"):
                        continue

                    # Check for magic numbers (not in obvious constant definitions)
                    if not any(x in line.upper() for x in ["CONST", "THRESHOLD", "MAX", "MIN", "DEFAULT", "LIMIT"]):
                        for match in magic_number_pattern.finditer(line):
                            num = match.group(1)
                            # Exclude common acceptable values
                            if num not in {"100", "1000", "0.0", "1.0", "0.5"}:
                                magic_numbers.append((i, num))

                    # Check for hardcoded patterns
                    for pattern, desc in hardcoded_patterns:
                        if pattern.search(line):
                            # Exclude test files and doc comments
                            if "test" not in rel_path.lower():
                                hardcoded_values.append((i, desc))

                # Report if significant magic values found
                if len(magic_numbers) > 5:
                    issues.append(DoctorIssue(
                        task_type="MAGIC_VALUES",
                        severity="info",
                        path=rel_path,
                        message=f"Contains {len(magic_numbers)} potential magic numbers",
                        details={"examples": magic_numbers[:3]},
                        suggestion="Consider extracting to constants file"
                    ))

                if hardcoded_values:
                    issues.append(DoctorIssue(
                        task_type="HARDCODED_CONFIG",
                        severity="warning",
                        path=rel_path,
                        message=f"Contains hardcoded configuration values",
                        details={"values": hardcoded_values[:3]},
                        suggestion="Move to config file or environment variables"
                    ))

            except Exception:
                pass

    return issues


def doctor_check_hardcoded_secrets(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for hardcoded secrets, API keys, and credentials.

    Detects:
    - Private keys (PEM format)
    - API keys and tokens
    - Passwords in code
    - AWS credentials
    - Database connection strings with passwords
    """
    if "hardcoded_secrets" in config.disabled_checks:
        return []

    issues = []

    # Patterns for secrets (high confidence)
    secret_patterns = [
        (re.compile(r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----'), "Private key in code", "critical"),
        (re.compile(r'-----BEGIN CERTIFICATE-----'), "Certificate in code", "warning"),
        (re.compile(r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\'][a-zA-Z0-9]{20,}["\']'), "API key", "critical"),
        (re.compile(r'(?i)(secret|token)\s*[=:]\s*["\'][a-zA-Z0-9_\-]{20,}["\']'), "Secret/token", "critical"),
        (re.compile(r'(?i)password\s*[=:]\s*["\'][^"\']{8,}["\']'), "Hardcoded password", "critical"),
        (re.compile(r'AKIA[0-9A-Z]{16}'), "AWS Access Key", "critical"),
        (re.compile(r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\'][^"\']+["\']'), "AWS Secret Key", "critical"),
        (re.compile(r'mongodb(\+srv)?://[^:]+:[^@]+@'), "MongoDB connection with password", "critical"),
        (re.compile(r'postgres(ql)?://[^:]+:[^@]+@'), "PostgreSQL connection with password", "critical"),
        (re.compile(r'mysql://[^:]+:[^@]+@'), "MySQL connection with password", "critical"),
    ]

    # Files to check (skip binary, skip .env files which are expected to have secrets)
    code_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".php", ".yml", ".yaml", ".json"}

    for ext in code_extensions:
        for code_file in target_dir.rglob(f"*{ext}"):
            if should_ignore_path(code_file, config.ignore, target_dir):
                continue

            # Skip files that are expected to have secrets (but should be in .gitignore)
            if code_file.name.startswith(".env") or code_file.name == "credentials.json":
                continue

            try:
                content = code_file.read_text(errors="ignore")
                rel_path = str(code_file.relative_to(target_dir))

                for pattern, desc, severity in secret_patterns:
                    if pattern.search(content):
                        # Check if it's a placeholder or example
                        if not any(x in content.lower() for x in ["example", "placeholder", "xxx", "your_", "changeme"]):
                            issues.append(DoctorIssue(
                                task_type="HARDCODED_SECRET",
                                severity=severity,
                                path=rel_path,
                                message=f"{desc} detected",
                                details={"pattern": desc},
                                suggestion="Move to environment variable or secrets manager"
                            ))
                            break  # One issue per file is enough

            except Exception:
                pass

    return issues
