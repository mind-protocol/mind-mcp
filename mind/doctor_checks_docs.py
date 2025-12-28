"""
Doctor check functions for documentation analysis.

Health checks that analyze documentation quality:
- Placeholder docs with template markers
- Orphan docs not linked from code
- Stale IMPLEMENTATION docs
- Large doc modules
- Incomplete doc chains
- Docs not ingested in graph

DOCS: docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md
"""

import logging
import re
from datetime import date
from pathlib import Path
from typing import List, Set, Optional, Dict

from .core_utils import find_module_directories
from .doctor_types import DoctorIssue, DoctorConfig
from .doctor_files import should_ignore_path, parse_doctor_doc_tags

logger = logging.getLogger(__name__)

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def doctor_check_placeholder_docs(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for docs with template placeholders."""
    if "placeholder" in config.disabled_checks:
        return []

    issues = []
    placeholder_pattern = re.compile(r'\{[A-Z][A-Z_]+\}')

    docs_dir = target_dir / "docs"
    protocol_dir = target_dir / ".mind"

    search_dirs = []
    if docs_dir.exists():
        search_dirs.append(docs_dir)
    if protocol_dir.exists():
        search_dirs.append(protocol_dir)

    for search_dir in search_dirs:
        for md_file in search_dir.rglob("*.md"):
            if should_ignore_path(md_file, config.ignore, target_dir):
                continue

            # Skip template files - they're supposed to have placeholders
            if "template" in md_file.name.lower() or "/templates/" in str(md_file).lower():
                continue

            try:
                content = md_file.read_text()
            except Exception:
                continue

            # Skip code blocks and inline code when searching for placeholders
            lines = content.split('\n')
            in_code_block = False
            placeholders_found = []

            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    continue

                if not in_code_block:
                    # Also skip inline code (text between backticks)
                    line_without_inline_code = re.sub(r'`[^`]+`', '', line)
                    matches = placeholder_pattern.findall(line_without_inline_code)
                    placeholders_found.extend(matches)

            if placeholders_found:
                try:
                    rel_path = str(md_file.relative_to(target_dir))
                except ValueError:
                    rel_path = str(md_file)

                # Filter common false positives
                real_placeholders = [p for p in placeholders_found
                                    if p not in ['{JSON}', '{XML}', '{HTML}', '{CSS}', '{TEMPLATE}', '{PLACEHOLDER}']]

                if real_placeholders:
                    issues.append(DoctorIssue(
                        issue_type="PLACEHOLDER",
                        severity="critical",
                        path=rel_path,
                        message=f"Contains {len(real_placeholders)} template placeholder(s)",
                        details={"placeholders": list(set(real_placeholders))[:5]},
                        suggestion="Fill in actual content"
                    ))

    return issues


def doctor_check_orphan_docs(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for docs not linked from code or modules.yaml."""
    issues = []

    if "ORPHAN_DOCS" in config.disabled_checks:
        return issues

    docs_dir = target_dir / "docs"
    if not docs_dir.exists():
        return issues

    # Get all doc files
    doc_files = set()
    for pattern in ["**/*.md"]:
        for f in docs_dir.glob(pattern):
            if f.is_file():
                doc_files.add(f.relative_to(target_dir))

    # Get docs referenced in modules.yaml
    referenced_docs = set()
    modules_yaml = target_dir / "modules.yaml"
    if modules_yaml.exists() and HAS_YAML:
        try:
            with open(modules_yaml) as f:
                data = yaml.safe_load(f) or {}
            for module_data in data.get("modules", {}).values():
                if isinstance(module_data, dict) and module_data.get("docs"):
                    docs_path = module_data["docs"].rstrip("/*")
                    # Add all files under this docs path
                    docs_subdir = target_dir / docs_path
                    if docs_subdir.exists():
                        for f in docs_subdir.glob("**/*.md"):
                            referenced_docs.add(f.relative_to(target_dir))
        except Exception:
            pass

    # Get docs referenced via DOCS: comments in code
    for code_ext in [".py", ".js", ".ts", ".tsx", ".go", ".rs"]:
        for code_file in target_dir.rglob(f"*{code_ext}"):
            if should_ignore_path(code_file, config.ignore, target_dir):
                continue
            try:
                content = code_file.read_text(errors="ignore")
                for line in content.split("\n")[:20]:  # Check first 20 lines
                    if "DOCS:" in line:
                        # Extract path after DOCS:
                        path_match = line.split("DOCS:")[-1].strip()
                        if path_match:
                            referenced_docs.add(Path(path_match))
            except Exception:
                pass

    # Find orphans
    orphan_docs = doc_files - referenced_docs
    for orphan in sorted(orphan_docs)[:10]:  # Limit to 10
        issues.append(DoctorIssue(
            issue_type="ORPHAN_DOCS",
            severity="info",
            path=str(orphan),
            message="Doc not linked from code or modules.yaml",
            details={},
            suggestion="Link from code, add to modules.yaml, or delete"
        ))

    return issues


def doctor_check_stale_impl(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for IMPLEMENTATION docs that don't match actual files."""
    issues = []

    if "STALE_IMPL" in config.disabled_checks:
        return issues

    # Find all IMPLEMENTATION docs
    docs_dir = target_dir / "docs"
    if not docs_dir.exists():
        return issues

    for impl_doc in docs_dir.rglob("IMPLEMENTATION*.md"):
        if should_ignore_path(impl_doc, config.ignore, target_dir):
            continue

        try:
            content = impl_doc.read_text(errors="ignore")

            # Extract file references from the doc
            referenced_files = set()
            for line in content.split("\n"):
                # Look for file paths in backticks or table cells
                matches = re.findall(r'`([^`]+\.(?:py|js|ts|tsx|go|rs|java))`', line)
                for match in matches:
                    referenced_files.add(match)

            if not referenced_files:
                continue

            # Check which files exist
            missing_files = []
            for ref_file in referenced_files:
                # Try relative to target_dir
                full_path = target_dir / ref_file
                if not full_path.exists():
                    missing_files.append(ref_file)

            if missing_files and len(missing_files) < len(referenced_files):
                # Some files missing but not all (if all missing, doc might be for different project)
                rel_path = str(impl_doc.relative_to(target_dir))
                issues.append(DoctorIssue(
                    issue_type="STALE_IMPL",
                    severity="warning",
                    path=rel_path,
                    message=f"{len(missing_files)} referenced files not found",
                    details={"missing_files": missing_files[:5]},
                    suggestion="Update doc to match actual file structure"
                ))

        except Exception:
            pass

    return issues


def doctor_check_large_doc_module(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for doc modules with too much content (hard to load in context)."""
    if "large_doc_module" in config.disabled_checks:
        return []

    issues = []
    docs_dir = target_dir / "docs"

    if not docs_dir.exists():
        return issues

    # Threshold: 62.5K chars is roughly 15K tokens, which is a lot for one module
    char_threshold = 62500

    modules = find_module_directories(docs_dir)

    for module_dir in modules:
        if should_ignore_path(module_dir, config.ignore, target_dir):
            continue

        total_chars = 0
        file_sizes = []

        for md_file in module_dir.glob("*.md"):
            try:
                content = md_file.read_text()
                size = len(content)
                total_chars += size
                file_sizes.append({"file": md_file.name, "chars": size})
            except Exception:
                continue

        if total_chars > char_threshold:
            try:
                rel_path = str(module_dir.relative_to(target_dir))
            except ValueError:
                rel_path = str(module_dir)

            # Sort by size to show largest files
            file_sizes.sort(key=lambda x: x["chars"], reverse=True)
            largest = [f"{f['file']} ({f['chars']//1000}K)" for f in file_sizes[:3]]

            issues.append(DoctorIssue(
                issue_type="LARGE_DOC_MODULE",
                severity="warning",
                path=rel_path,
                message=f"Total {total_chars//1000}K chars (threshold: {char_threshold//1000}K)",
                details={"total_chars": total_chars, "file_sizes": file_sizes},
                suggestion=f"Consider splitting. Largest: {', '.join(largest)}"
            ))

    return issues


def doctor_check_incomplete_chain(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for modules with incomplete doc chains."""
    if "incomplete_chain" in config.disabled_checks:
        return []

    issues = []
    docs_dir = target_dir / "docs"

    if not docs_dir.exists():
        return issues

    full_chain = [
        "OBJECTIVES_",
        "BEHAVIORS_",
        "PATTERNS_",
        "ALGORITHM_",
        "VALIDATION_",
        "IMPLEMENTATION_",
        "HEALTH_",
        "SYNC_",
    ]
    modules = find_module_directories(docs_dir)

    for module_dir in modules:
        if should_ignore_path(module_dir, config.ignore, target_dir):
            continue

        md_files = list(module_dir.glob("*.md"))

        missing = []
        for doc_type in full_chain:
            if not any(doc_type in f.name for f in md_files):
                missing.append(doc_type.rstrip('_'))

        if missing and len(missing) < 6:  # Not completely empty
            try:
                rel_path = str(module_dir.relative_to(target_dir))
            except ValueError:
                rel_path = str(module_dir)

            issues.append(DoctorIssue(
                issue_type="INCOMPLETE_CHAIN",
                severity="warning",
                path=rel_path,
                message=f"Missing: {', '.join(missing)}",
                details={"missing": missing, "present": [d.rstrip('_') for d in full_chain if d not in missing]},
                suggestion="Complete the doc chain for full coverage",
                protocol="create_doc_chain"
            ))

    return issues


DOC_TYPE_TEMPLATES = {
    "OBJECTIVES": ".mind-mcp/templates/OBJECTIVES_TEMPLATE.md",
    "PATTERNS": ".mind-mcp/templates/PATTERNS_TEMPLATE.md",
    "BEHAVIORS": ".mind-mcp/templates/BEHAVIORS_TEMPLATE.md",
    "ALGORITHM": ".mind-mcp/templates/ALGORITHM_TEMPLATE.md",
    "VALIDATION": ".mind-mcp/templates/VALIDATION_TEMPLATE.md",
    "IMPLEMENTATION": ".mind-mcp/templates/IMPLEMENTATION_TEMPLATE.md",
    "HEALTH": ".mind-mcp/templates/HEALTH_TEMPLATE.md",
    "SYNC": ".mind-mcp/templates/SYNC_TEMPLATE.md",
    "CONCEPT": ".mind-mcp/templates/CONCEPT_TEMPLATE.md",
    "TOUCHES": ".mind-mcp/templates/TOUCHES_TEMPLATE.md",
}

STANDARD_DOC_PREFIXES = tuple(f"{prefix}_" for prefix in DOC_TYPE_TEMPLATES.keys())


def _iter_doc_files(target_dir: Path, config: DoctorConfig) -> List[Path]:
    """Collect doc files from standard documentation roots."""
    doc_files: List[Path] = []
    search_dirs = [target_dir / "docs", target_dir / ".mind" / "state"]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for md_file in search_dir.rglob("*.md"):
            if should_ignore_path(md_file, config.ignore, target_dir):
                continue
            doc_files.append(md_file)

    return doc_files


def _extract_h2_sections(content: str) -> dict:
    """Extract H2 sections and their content."""
    sections = {}
    current = None
    buffer: List[str] = []

    for line in content.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current = line[3:].strip()
            buffer = []
        elif current is not None:
            buffer.append(line)

    if current is not None:
        sections[current] = "\n".join(buffer).strip()

    return sections


def _doc_tag_allows_suppression(
    doc_path: Path,
    issue_type: str,
    allowed_statuses: set,
) -> bool:
    """Check if a doc tag suppresses an issue for now."""
    tags = parse_doctor_doc_tags(doc_path).get(issue_type, [])
    today = date.today()

    for tag in tags:
        status = tag.get("status", "")
        if status not in allowed_statuses:
            continue

        if status == "postponed":
            date_str = tag.get("date", "")
            if not date_str:
                continue
            try:
                postpone_until = date.fromisoformat(date_str)
            except ValueError:
                continue
            if postpone_until >= today:
                return True
            continue

        return True

    return False


def _doc_tag_message(doc_path: Path, issue_type: str, status: str) -> str:
    """Return the first matching tag message for an issue type/status."""
    tags = parse_doctor_doc_tags(doc_path).get(issue_type, [])
    for tag in tags:
        if tag.get("status") == status:
            return tag.get("message", "")
    return ""


def doctor_check_doc_template_drift(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check docs against their templates for missing or too-short sections."""
    if "DOC_TEMPLATE_DRIFT" in config.disabled_checks:
        return []

    issues = []
    template_sections_cache = {}

    for doc_path in _iter_doc_files(target_dir, config):
        prefix = doc_path.name.split("_", 1)[0]
        template_path = DOC_TYPE_TEMPLATES.get(prefix)
        if not template_path:
            continue

        if _doc_tag_allows_suppression(doc_path, "DOC_TEMPLATE_DRIFT", {"postponed", "non-required"}):
            continue

        if prefix not in template_sections_cache:
            template_file = target_dir / template_path
            if not template_file.exists():
                template_sections_cache[prefix] = []
            else:
                template_content = template_file.read_text(errors="ignore")
                template_sections_cache[prefix] = list(_extract_h2_sections(template_content).keys())

        required_sections = template_sections_cache[prefix]
        if not required_sections:
            continue

        doc_content = doc_path.read_text(errors="ignore")
        doc_sections = _extract_h2_sections(doc_content)

        missing = [section for section in required_sections if section not in doc_sections]
        short = [
            section for section in required_sections
            if section in doc_sections and len(doc_sections[section].strip()) < 50
        ]

        escalation_note = ""
        if missing:
            escalation_note = _doc_tag_message(doc_path, "DOC_TEMPLATE_DRIFT", "escalation")

        if missing or short:
            rel_path = str(doc_path.relative_to(target_dir))
            message_parts = []
            if missing:
                message_parts.append(f"Missing: {', '.join(missing)}")
            if short:
                message_parts.append(f"Too short: {', '.join(short)}")
            if escalation_note:
                message_parts.append(f"Escalation: {escalation_note}")

            issues.append(DoctorIssue(
                issue_type="DOC_TEMPLATE_DRIFT",
                severity="warning",
                path=rel_path,
                message="; ".join(message_parts),
                details={"missing": missing, "short": short},
                suggestion="Fill missing sections and expand short ones to 50+ characters",
                protocol="create_doc_chain"
            ))

    return issues


def doctor_check_validation_behaviors_list(
    target_dir: Path,
    config: DoctorConfig
) -> List[DoctorIssue]:
    """Ensure VALIDATION docs list the behaviors they guarantee."""
    if "VALIDATION_BEHAVIORS_MISSING" in config.disabled_checks:
        return []

    issues: List[DoctorIssue] = []
    required_section = "BEHAVIORS GUARANTEED"

    for doc_path in _iter_doc_files(target_dir, config):
        if not doc_path.name.startswith("VALIDATION_"):
            continue

        doc_content = doc_path.read_text(errors="ignore")
        doc_sections = _extract_h2_sections(doc_content)

        if required_section in doc_sections:
            continue

        rel_path = str(doc_path.relative_to(target_dir))
        issues.append(DoctorIssue(
            issue_type="VALIDATION_BEHAVIORS_MISSING",
            severity="info",
            path=rel_path,
            message=f"Missing: {required_section}",
            details={"missing": [required_section]},
            suggestion="Add a BEHAVIORS GUARANTEED section listing covered behaviors"
        ))

    return issues


def doctor_check_nonstandard_doc_type(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """Check for docs that don't use standard doc type prefixes."""
    if "NON_STANDARD_DOC_TYPE" in config.disabled_checks:
        return []

    issues = []
    # Standard exceptions
    EXCEPTIONS = {
        "map.md", "CLAUDE.md", "AGENTS.md", "GEMINI.md", 
        "README.md", "CONTRIBUTING.md", "LICENSE",
        "SYNC_Project_Repository_Map.md", "gitignore", "mindignore"
    }

    for doc_path in _iter_doc_files(target_dir, config):
        if doc_path.name.startswith(STANDARD_DOC_PREFIXES):
            continue
            
        if doc_path.name in EXCEPTIONS or doc_path.name.startswith("."):
            continue

        if _doc_tag_allows_suppression(doc_path, "NON_STANDARD_DOC_TYPE", {"postponed", "exception"}):
            continue

        rel_path = str(doc_path.relative_to(target_dir))
        issues.append(DoctorIssue(
            issue_type="NON_STANDARD_DOC_TYPE",
            severity="warning",
            path=rel_path,
            message="Doc filename does not use a standard prefix",
            details={"prefixes": list(STANDARD_DOC_PREFIXES)},
            suggestion="Rename to OBJECTIVES_/BEHAVIORS_/PATTERNS_/ALGORITHM_/VALIDATION_/IMPLEMENTATION_/HEALTH_/SYNC_"
        ))

    return issues


# =============================================================================
# DOC CHAIN ORDER - Priority for ingestion (top to bottom)
# =============================================================================
DOC_CHAIN_ORDER = [
    "OBJECTIVES",
    "BEHAVIORS",
    "PATTERNS",
    "ALGORITHM",
    "VALIDATION",
    "IMPLEMENTATION",
    "HEALTH",
    "SYNC",
]


def _get_doc_chain_priority(filename: str) -> int:
    """
    Get priority for a doc file based on chain order.
    Lower number = higher priority (ingest first).
    OBJECTIVES = 0, BEHAVIORS = 1, etc.
    Non-chain docs get priority 100.
    """
    for i, prefix in enumerate(DOC_CHAIN_ORDER):
        if filename.startswith(prefix + "_"):
            return i
    return 100  # Non-chain docs are lower priority


def _get_module_from_path(doc_path: Path, target_dir: Path) -> str:
    """
    Extract module name from doc path.
    docs/engine/physics/PATTERNS_*.md -> engine-physics
    docs/frontend/SYNC_*.md -> frontend
    """
    try:
        rel_path = doc_path.relative_to(target_dir / "docs")
        parts = rel_path.parts[:-1]  # Exclude filename
        if parts:
            return "-".join(parts)
        return "root"
    except ValueError:
        return "unknown"


def _query_doc_things_without_narratives(target_dir: Path) -> List[Dict]:
    """
    Query graph for Thing nodes in docs/ that don't have a linked Narrative.

    Returns list of dicts with thing info:
    [{"path": "docs/...", "id": "thing_..."}, ...]
    """
    unlinked_things = []

    try:
        from .agent_graph import AgentGraph
        ag = AgentGraph(graph_name="mind")

        if not ag._connect():
            logger.warning("[doctor] No graph connection, cannot check doc things")
            return unlinked_things

        # Query for Thing nodes in docs/ that do NOT have a linked Narrative of type docs
        # Note: Thing nodes use 'uri' not 'path' for file location
        cypher = """
        MATCH (t:Thing)
        WHERE t.uri STARTS WITH 'docs/'
          AND t.uri ENDS WITH '.md'
        OPTIONAL MATCH (t)<-[:about]-(n:Narrative {type: 'docs'})
        WITH t, n
        WHERE n IS NULL
        RETURN t.id, t.uri
        ORDER BY t.uri
        """
        result = ag._graph_ops._query(cypher)

        for row in result:
            if row and len(row) >= 2:
                unlinked_things.append({
                    "id": row[0],
                    "path": row[1],  # uri value mapped to path key for downstream compatibility
                })

        logger.info(f"[doctor] Found {len(unlinked_things)} doc Things without linked Narratives")

    except Exception as e:
        logger.warning(f"[doctor] Failed to query doc things: {e}")

    return unlinked_things


def doctor_check_docs_not_ingested(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """
    Check for documentation Things in graph that don't have linked Narratives.

    This check:
    1. Queries graph for Thing nodes in docs/
    2. Finds Things without a linked Narrative (type: docs)
    3. Creates issues for docs needing ingestion
    4. Orders by chain priority (OBJECTIVES first, then BEHAVIORS, etc.)
    5. Groups by module for efficient task creation

    Protocol: ingest_docs (auto-fix ingests docs into graph)
    """
    if "DOCS_NOT_INGESTED" in config.disabled_checks:
        return []

    issues = []

    # Get doc Things without linked Narratives from graph
    unlinked_things = _query_doc_things_without_narratives(target_dir)

    if not unlinked_things:
        return []

    # Process each unlinked thing
    doc_files: List[tuple] = []  # (priority, module, path, filename, thing_id)

    for thing in unlinked_things:
        path = thing["path"]
        thing_id = thing["id"]

        # Skip archive directories
        if "/archive/" in path or "\\archive\\" in path:
            continue

        filename = Path(path).name

        # Get priority and module
        priority = _get_doc_chain_priority(filename)
        module = _get_module_from_path(Path(path), target_dir)

        doc_files.append((priority, module, path, filename, thing_id))

    # Sort by module first, then by chain priority within module
    doc_files.sort(key=lambda x: (x[1], x[0]))

    # Group by module for issue creation
    modules_seen: Dict[str, List[tuple]] = {}
    for priority, module, rel_path, filename, thing_id in doc_files:
        if module not in modules_seen:
            modules_seen[module] = []
        modules_seen[module].append((priority, rel_path, filename, thing_id))

    # Create issues - one per file, but with module context
    for module, files in modules_seen.items():
        # Sort files within module by chain priority
        files.sort(key=lambda x: x[0])

        for priority, rel_path, filename, thing_id in files:
            # Determine chain type from filename
            chain_type = "OTHER"
            for prefix in DOC_CHAIN_ORDER:
                if filename.startswith(prefix + "_"):
                    chain_type = prefix
                    break

            issues.append(DoctorIssue(
                issue_type="DOCS_NOT_INGESTED",
                severity="warning",  # High priority but not blocking
                path=rel_path,
                message=f"Doc Thing exists but no linked Narrative (module: {module}, chain: {chain_type})",
                details={
                    "module": module,
                    "chain_type": chain_type,
                    "chain_priority": priority,
                    "thing_id": thing_id,
                    "archive_to": f"data/archive/docs/{module}/{filename}",
                },
                suggestion=f"Ingest into graph (create Narrative linked to Thing), then archive to data/archive/docs/",
                protocol="ingest_docs",
            ))

    # Log summary
    if issues:
        logger.info(f"[doctor] Found {len(issues)} doc Things without Narratives across {len(modules_seen)} modules")

    return issues


def doctor_check_sections_without_node_id(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    """
    Check for markdown sections (## headers) without mind node anchors.

    Sections should have `<!-- mind:node:xxx -->` anchors to link them to
    graph Narrative nodes. Sections without anchors need to be transferred
    to the graph.

    This enables:
    1. Bidirectional sync between markdown and graph
    2. Graph queries to find related documentation
    3. Energy flow through documentation
    """
    if "SECTIONS_WITHOUT_NODE_ID" in config.disabled_checks:
        return []

    issues = []
    docs_dir = target_dir / "docs"

    if not docs_dir.exists():
        return []

    # Pattern to match node anchors
    anchor_pattern = re.compile(r'<!--\s*mind:node:([^\s]+)\s*-->')

    for md_file in docs_dir.rglob("*.md"):
        if should_ignore_path(md_file, config.ignore, target_dir):
            continue

        # Skip templates and archives
        if "template" in md_file.name.lower() or "/archive/" in str(md_file):
            continue

        try:
            content = md_file.read_text()
        except Exception:
            continue

        # Parse sections
        lines = content.split('\n')
        sections_without_anchor = []
        current_section = None
        current_has_anchor = False

        for i, line in enumerate(lines):
            if line.startswith('## '):
                # Save previous section if no anchor
                if current_section and not current_has_anchor:
                    sections_without_anchor.append(current_section)

                current_section = line[3:].strip()
                current_has_anchor = False

                # Check next few lines for anchor
                for j in range(i + 1, min(i + 3, len(lines))):
                    if anchor_pattern.search(lines[j]):
                        current_has_anchor = True
                        break

        # Check last section
        if current_section and not current_has_anchor:
            sections_without_anchor.append(current_section)

        if sections_without_anchor:
            try:
                rel_path = str(md_file.relative_to(target_dir))
            except ValueError:
                rel_path = str(md_file)

            # Get module from path
            module = _get_module_from_path(md_file, target_dir)

            # Determine doc type from filename
            doc_type = "unknown"
            for prefix in DOC_CHAIN_ORDER:
                if md_file.name.startswith(prefix + "_"):
                    doc_type = prefix.lower()
                    break

            issues.append(DoctorIssue(
                issue_type="SECTIONS_WITHOUT_NODE_ID",
                severity="info",
                path=rel_path,
                message=f"{len(sections_without_anchor)} section(s) without graph node anchor",
                details={
                    "module": module,
                    "doc_type": doc_type,
                    "sections": sections_without_anchor[:5],  # First 5
                    "total_sections": len(sections_without_anchor),
                },
                suggestion=f"Transfer sections to graph using ingest_docs protocol",
                protocol="ingest_docs",
            ))

    if issues:
        total_sections = sum(i.details.get("total_sections", 0) for i in issues)
        logger.info(f"[doctor] Found {total_sections} sections without node IDs across {len(issues)} files")

    return issues
