"""
Doctor check functions for naming conventions.

Health checks that verify:
- Documentation files use PREFIX_PascalCase_With_Underscores.md
- Code files use snake_case.py
- Directories use snake_case

DOCS: docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md
"""

import re
from pathlib import Path
from typing import List

from .doctor_types import DoctorIssue, DoctorConfig
from .doctor_files import should_ignore_path, find_source_files, find_code_directories

# Standard doc prefixes
STANDARD_DOC_PREFIXES = [
    "OBJECTIVES",
    "PATTERNS",
    "BEHAVIORS",
    "ALGORITHM",
    "VALIDATION",
    "IMPLEMENTATION",
    "TEST",
    "SYNC",
    "HEALTH",
    "CONCEPT",
    "TOUCHES",
]

def is_snake_case(name: str) -> bool:
    """Check if a name is snake_case, allowing for dunder files."""
    if name.startswith('__') and name.endswith('__'):
        inner = name[2:-2]
        return bool(re.match(r'^[a-z0-9]+(_[a-z0-9]+)*$', inner))
    return bool(re.match(r'^[a-z0-9]+(_[a-z0-9]+)*$', name))

def is_pascal_case_with_underscores(name: str) -> bool:
    """Check if a name is PascalCase (allowing acronyms) with underscores."""
    # Each part separated by underscore must start with uppercase
    parts = name.split('_')
    for part in parts:
        if not part:
            return False
        # Part must start with uppercase letter or number (e.g. 2D)
        if not (part[0].isupper() or part[0].isdigit()):
            return False
    return True

def is_descriptive(name: str, min_length: int = 15) -> bool:
    """Check if a name is long enough to be descriptive."""
    return len(name) >= min_length

def doctor_check_naming_conventions(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for files and folders that violate naming conventions."""
    if "naming_conventions" in config.disabled_checks:
        return []

    violations = []
    
    # Vague names to flag as info
    vague_patterns = {
        "utils": "Consider naming by what it actually does (e.g., string_helpers, date_formatters)",
        "helpers": "Consider naming by domain (e.g., auth_helpers, payment_utils)",
        "misc": "Split into specific, named modules",
        "stuff": "Rename to describe actual contents",
        "common": "Consider naming by what's common (e.g., shared_types, base_classes)",
        "lib": "Consider more specific names for subdirectories",
        "core": "Consider what 'core' means in this context",
        "base": "Consider naming by what it's a base for",
        "general": "Split into specific concerns",
        "other": "Categorize contents properly",
    }

    # Check directories
    for code_dir in find_code_directories(target_dir, config):
        if should_ignore_path(code_dir, config.ignore, target_dir):
            continue
            
        if code_dir.name.startswith("."):
            continue

        rel_path = str(code_dir.relative_to(target_dir))
        
        # Check snake_case
        if not is_snake_case(code_dir.name):
            violations.append({"path": rel_path, "type": "directory", "expected": "snake_case", "severity": "warning"})
            
        # Check vague names (info)
        if code_dir.name.lower() in vague_patterns:
            violations.append({
                "path": rel_path, 
                "type": "directory", 
                "expected": vague_patterns[code_dir.name.lower()], 
                "severity": "info",
                "message": f"Directory named '{code_dir.name}' is non-descriptive"
            })

    # Check source files (code)
    for source_file in find_source_files(target_dir, config):
        # Skip doc files (checked separately)
        if source_file.suffix.lower() == '.md':
            continue
            
        if source_file.name.startswith("."):
            continue

        rel_path = str(source_file.relative_to(target_dir))
        
        # Check snake_case
        if not is_snake_case(source_file.stem):
            violations.append({"path": rel_path, "type": "code file", "expected": "snake_case", "severity": "warning"})
            
        # Check for "and" in name (suggests splitting)
        if "_and_" in source_file.stem.lower() or source_file.stem.lower().startswith("and_") or source_file.stem.lower().endswith("_and"):
            violations.append({
                "path": rel_path, 
                "type": "code file", 
                "expected": "single-responsibility name (without 'and')", 
                "severity": "warning",
                "message": f"Code file '{source_file.name}' contains 'and', suggesting it should be split"
            })
            
        # Check vague names (info)
        if source_file.stem.lower() in vague_patterns:
            violations.append({
                "path": rel_path, 
                "type": "code file", 
                "expected": vague_patterns[source_file.stem.lower()], 
                "severity": "info",
                "message": f"File named '{source_file.name}' is non-descriptive"
            })

    # Check documentation files
    docs_dir = target_dir / "docs"
    # Standard exceptions for doc files
    EXCEPTIONS = {
        "map.md", "CLAUDE.md", "AGENTS.md", "GEMINI.md", 
        "README.md", "CONTRIBUTING.md", "LICENSE",
        "SYNC_Project_Repository_Map.md", "gitignore", "mindignore"
    }
    
    if docs_dir.exists():
        for md_file in docs_dir.rglob("*.md"):
            if should_ignore_path(md_file, config.ignore, target_dir):
                continue

            # Skip exceptions and dotfiles
            if md_file.name in EXCEPTIONS or md_file.name.startswith("."):
                continue

            name = md_file.stem
            rel_path = str(md_file.relative_to(target_dir))
            
            if '_' not in name:
                violations.append({"path": rel_path, "type": "doc file", "expected": "PREFIX_Name.md", "severity": "warning"})
                continue

            prefix, rest = name.split('_', 1)
            
            # Check PascalCase
            if not is_pascal_case_with_underscores(rest):
                violations.append({"path": rel_path, "type": "doc file", "expected": f"{prefix}_PascalCase_Name.md", "severity": "warning"})
                
            # Check length/descriptiveness (warning)
            # Threshold: 15 chars for the 'rest' part
            if not is_descriptive(rest, 15):
                violations.append({
                    "path": rel_path, 
                    "type": "doc file", 
                    "expected": "longer, more descriptive name (>15 chars)", 
                    "severity": "warning",
                    "message": f"Doc filename '{md_file.name}' is too short/non-descriptive"
                })

    # Group violations into "tasks"
    issues = []
    
    # Sort violations so warnings come before info
    sorted_violations = sorted(violations, key=lambda x: (x["severity"] == "info", x["path"]))
    
    for i in range(0, len(sorted_violations), 10):
        group = sorted_violations[i:i+10]
        group_paths = [v["path"] for v in group]
        primary_path = group[0]["path"]
        
        # Determine group severity (if any is warning, group is warning)
        group_severity = "warning" if any(v["severity"] == "warning" for v in group) else "info"

        message = group[0].get("message", f"Naming convention violations task ({i//10 + 1}): {len(group)} items")

        issues.append(DoctorIssue(
            issue_type="NAMING_CONVENTION",
            severity=group_severity,
            path=primary_path,
            message=message,
            details={"violations": group},
            suggestion=f"Rename to follow project conventions: {', '.join(group_paths[:3])}"
        ))

    return issues
