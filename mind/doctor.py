"""
Doctor command for mind CLI.

Provides health checks for projects:
- Monolith files (too many lines)
- Undocumented code directories
- Stale SYNC files
- Placeholder documentation
- Missing DOCS: references
- Incomplete doc chains

DOCS: docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any

from .sync import archive_all_syncs
from .doctor_types import DoctorIssue, DoctorConfig
from .doctor_report import (
    generate_health_markdown,
    print_doctor_report,
    check_sync_status,
)
from .doctor_files import (
    load_doctor_config,
    load_doctor_ignore,
    filter_ignored_issues,
    load_doctor_false_positives,
    filter_false_positive_issues,
)
from .doctor_checks import (
    doctor_check_monolith,
    doctor_check_undocumented,
    doctor_check_stale_sync,
    doctor_check_placeholder_docs,
    doctor_check_no_docs_ref,
    doctor_check_broken_impl_links,
    doctor_check_stub_impl,
    doctor_check_incomplete_impl,
    doctor_check_undoc_impl,
    doctor_check_yaml_drift,
    doctor_check_large_doc_module,
    doctor_check_incomplete_chain,
    doctor_check_doc_template_drift,
    doctor_check_validation_behaviors_list,
    doctor_check_nonstandard_doc_type,
    doctor_check_missing_tests,
    doctor_check_orphan_docs,
    doctor_check_stale_impl,
    doctor_check_prompt_doc_reference,
    doctor_check_prompt_view_table,
    doctor_check_prompt_checklist,
    doctor_check_doc_link_integrity,
    doctor_check_code_doc_delta_coupling,
    doctor_check_magic_values,
    doctor_check_hardcoded_secrets,
    doctor_check_docs_not_ingested,
    doctor_check_sections_without_node_id,
)
from .doctor_checks_naming import (
    doctor_check_naming_conventions,
)
from .doctor_checks_sync import (
    doctor_check_conflicts,
    doctor_check_doc_gaps,
    doctor_check_suggestions,
)
from .doctor_checks_content import (
    doctor_check_new_undoc_code,
    doctor_check_doc_duplication,
    doctor_check_long_strings,
    doctor_check_recent_log_errors,
    doctor_check_special_markers,
    doctor_check_legacy_markers,
)
from .doctor_checks_invariants import (
    doctor_check_invariant_coverage,
    doctor_check_test_validates_markers,
    doctor_check_completion_gate,
)
from .doctor_graph import (
    DoctorGraphStore,
    upsert_all_file_things,
    sync_file_things_to_graph,
    upsert_issue,
    IssueNarrative,
    ObjectiveNarrative,
    TaskNarrative,
    ensure_module_objectives,
    create_tasks_from_issues,
    generate_issue_id,
)


def calculate_health_score(issues: Dict[str, List[DoctorIssue]]) -> int:
    """Calculate health score from issues."""
    score = 100

    score -= len(issues.get("critical", [])) * 10
    score -= len(issues.get("warning", [])) * 3
    score -= len(issues.get("info", [])) * 1

    return max(0, score)


def run_doctor(target_dir: Path, config: DoctorConfig, sync_graph: bool = True) -> Dict[str, Any]:
    """Run all doctor checks and return results.

    Args:
        target_dir: Project root directory
        config: Doctor configuration
        sync_graph: Whether to scan files and sync Thing nodes to graph (default: True)

    Returns:
        Dict with issues, score, summary, and optional graph_stats
    """
    all_issues = []
    graph_stats = None
    store = None
    graph_ops = None

    # Scan files and create Thing nodes in graph
    if sync_graph:
        try:
            store = DoctorGraphStore()
            graph_stats = upsert_all_file_things(
                target_dir=target_dir,
                store=store,
                ignore_patterns=config.ignore,
            )

            # Batch embed all pending nodes and links
            embedded_nodes = store.embed_pending()
            embedded_links = store.embed_pending_links()
            graph_stats["embedded_nodes"] = embedded_nodes
            graph_stats["embedded_links"] = embedded_links

            # Try to sync to external graph database
            try:
                from mind.physics.graph import GraphOps
                graph_ops = GraphOps(graph_name="mind")
                sync_stats = sync_file_things_to_graph(
                    target_dir=target_dir,
                    store=store,
                    ignore_patterns=config.ignore,
                    graph_ops=graph_ops,
                )
                graph_stats.update(sync_stats)
            except Exception:
                # No external graph available, that's fine
                graph_ops = None
        except Exception as e:
            # File scan failed, continue with checks
            graph_stats = {"error": str(e)}
            store = None

    # Run checks
    all_issues.extend(doctor_check_monolith(target_dir, config))
    all_issues.extend(doctor_check_undocumented(target_dir, config))
    all_issues.extend(doctor_check_stale_sync(target_dir, config))
    all_issues.extend(doctor_check_placeholder_docs(target_dir, config))
    all_issues.extend(doctor_check_no_docs_ref(target_dir, config))
    all_issues.extend(doctor_check_incomplete_chain(target_dir, config))
    # Implementation checks
    all_issues.extend(doctor_check_broken_impl_links(target_dir, config))
    all_issues.extend(doctor_check_stub_impl(target_dir, config))
    all_issues.extend(doctor_check_incomplete_impl(target_dir, config))
    all_issues.extend(doctor_check_undoc_impl(target_dir, config))
    all_issues.extend(doctor_check_new_undoc_code(target_dir, config))
    all_issues.extend(doctor_check_large_doc_module(target_dir, config))
    all_issues.extend(doctor_check_yaml_drift(target_dir, config))
    # New checks
    all_issues.extend(doctor_check_missing_tests(target_dir, config))
    all_issues.extend(doctor_check_orphan_docs(target_dir, config))
    all_issues.extend(doctor_check_stale_impl(target_dir, config))
    all_issues.extend(doctor_check_doc_template_drift(target_dir, config))
    all_issues.extend(doctor_check_validation_behaviors_list(target_dir, config))
    all_issues.extend(doctor_check_prompt_doc_reference(target_dir, config))
    all_issues.extend(doctor_check_prompt_view_table(target_dir, config))
    all_issues.extend(doctor_check_prompt_checklist(target_dir, config))
    all_issues.extend(doctor_check_doc_link_integrity(target_dir, config))
    all_issues.extend(doctor_check_code_doc_delta_coupling(target_dir, config))
    all_issues.extend(doctor_check_nonstandard_doc_type(target_dir, config))
    all_issues.extend(doctor_check_naming_conventions(target_dir, config))
    all_issues.extend(doctor_check_doc_gaps(target_dir, config))
    all_issues.extend(doctor_check_conflicts(target_dir, config))
    all_issues.extend(doctor_check_suggestions(target_dir, config))
    all_issues.extend(doctor_check_doc_duplication(target_dir, config))
    all_issues.extend(doctor_check_recent_log_errors(target_dir, config))
    all_issues.extend(doctor_check_special_markers(target_dir, config))
    all_issues.extend(doctor_check_legacy_markers(target_dir, config))
    # Code quality checks
    all_issues.extend(doctor_check_magic_values(target_dir, config))
    all_issues.extend(doctor_check_hardcoded_secrets(target_dir, config))
    all_issues.extend(doctor_check_long_strings(target_dir, config))
    # Invariant test coverage checks
    all_issues.extend(doctor_check_invariant_coverage(target_dir, config))
    all_issues.extend(doctor_check_test_validates_markers(target_dir, config))
    all_issues.extend(doctor_check_completion_gate(target_dir, config))
    # Graph ingestion checks
    all_issues.extend(doctor_check_docs_not_ingested(target_dir, config))
    all_issues.extend(doctor_check_sections_without_node_id(target_dir, config))

    # Filter out suppressed issues from doctor-ignore.yaml
    ignores = load_doctor_ignore(target_dir)
    all_issues, ignored_count = filter_ignored_issues(all_issues, ignores)

    # Filter out doc-declared false positives
    false_positives = load_doctor_false_positives(target_dir, config)
    all_issues, false_positive_count = filter_false_positive_issues(
        all_issues,
        false_positives,
        target_dir,
        config,
    )

    # Generate graph node IDs for all issues
    for issue in all_issues:
        if not issue.id:
            # Derive module from path (first directory segment or project name)
            rel_path = Path(issue.path)
            if rel_path.parts:
                module = rel_path.parts[0]
            else:
                module = target_dir.name
            issue.generate_id(module)

    # Upsert issue narratives to graph store
    if sync_graph and store is not None:
        from .doctor_graph import generate_issue_id
        issues_created = 0
        issues_updated = 0

        for issue in all_issues:
            rel_path = Path(issue.path)
            module = rel_path.parts[0] if rel_path.parts else target_dir.name

            # Check if exists
            issue_id = generate_issue_id(issue.issue_type, module, issue.path)
            existing = store.get_node(issue_id)

            # Upsert to local store
            upsert_issue(
                issue_type=issue.issue_type,
                severity=issue.severity,
                path=issue.path,
                message=issue.message,
                module=module,
                store=store,
            )

            if existing:
                issues_updated += 1
            else:
                issues_created += 1

        if graph_stats:
            graph_stats["issues_created"] = issues_created
            graph_stats["issues_updated"] = issues_updated

        # Sync issue narratives to external graph if available
        if graph_ops is not None:
            try:
                from .doctor_graph import IssueNarrative as IssueNarrativeNode
                synced = 0
                for node_id, node in store.nodes.items():
                    if isinstance(node, IssueNarrativeNode):
                        cypher = """
                        MERGE (n:Narrative {id: $id})
                        SET n.node_type = $node_type,
                            n.type = $type,
                            n.name = $name,
                            n.issue_type = $issue_type,
                            n.severity = $severity,
                            n.path = $path,
                            n.message = $message,
                            n.module = $module,
                            n.status = $status,
                            n.energy = $energy,
                            n.created_at_s = $created_at_s,
                            n.updated_at_s = $updated_at_s
                        """
                        graph_ops._query(cypher, {
                            "id": node.id,
                            "node_type": node.node_type,
                            "type": node.type,
                            "name": node.name,
                            "issue_type": node.issue_type,
                            "severity": node.severity,
                            "path": node.path,
                            "message": node.message[:500],
                            "module": node.module,
                            "status": node.status,
                            "energy": node.energy,
                            "created_at_s": node.created_at_s,
                            "updated_at_s": node.updated_at_s,
                        })
                        synced += 1
                if graph_stats:
                    graph_stats["issues_synced"] = synced
            except Exception as e:
                if graph_stats:
                    graph_stats["issues_sync_error"] = str(e)[:100]

        # Create objectives for modules with issues
        modules_with_issues = set()
        for issue in all_issues:
            rel_path = Path(issue.path)
            module = rel_path.parts[0] if rel_path.parts else target_dir.name
            modules_with_issues.add(module)

        objectives_created = 0
        for module in modules_with_issues:
            objs = ensure_module_objectives(module, store)
            objectives_created += len([o for o in objs if o.created_at_s == o.updated_at_s])

        if graph_stats:
            graph_stats["objectives_created"] = objectives_created
            graph_stats["modules_with_issues"] = len(modules_with_issues)

        # Create tasks grouping issues by objective
        issue_narratives = [
            node for node in store.nodes.values()
            if isinstance(node, IssueNarrative) and node.status == "open"
        ]

        tasks = create_tasks_from_issues(
            issues=issue_narratives,
            store=store,
            modules={},
        )

        if graph_stats:
            graph_stats["tasks_created"] = len(tasks)
            graph_stats["task_types"] = {
                "serve": len([t for t in tasks if t.task_type == "serve"]),
                "reconstruct": len([t for t in tasks if t.task_type == "reconstruct"]),
                "triage": len([t for t in tasks if t.task_type == "triage"]),
            }

        # Sync objectives and tasks to external graph
        if graph_ops is not None:
            try:
                obj_synced = 0
                task_synced = 0

                for node in store.nodes.values():
                    if isinstance(node, ObjectiveNarrative):
                        cypher = """
                        MERGE (n:Narrative {id: $id})
                        SET n.node_type = $node_type,
                            n.type = $type,
                            n.name = $name,
                            n.objective_type = $objective_type,
                            n.module = $module,
                            n.status = $status,
                            n.energy = $energy,
                            n.created_at_s = $created_at_s,
                            n.updated_at_s = $updated_at_s
                        """
                        graph_ops._query(cypher, {
                            "id": node.id,
                            "node_type": node.node_type,
                            "type": node.type,
                            "name": node.name,
                            "objective_type": node.objective_type,
                            "module": node.module,
                            "status": node.status,
                            "energy": node.energy,
                            "created_at_s": node.created_at_s,
                            "updated_at_s": node.updated_at_s,
                        })
                        obj_synced += 1

                for node in store.nodes.values():
                    if isinstance(node, TaskNarrative):
                        cypher = """
                        MERGE (n:Narrative {id: $id})
                        SET n.node_type = $node_type,
                            n.type = $type,
                            n.name = $name,
                            n.task_type = $task_type,
                            n.module = $module,
                            n.skill = $skill,
                            n.status = $status,
                            n.energy = $energy,
                            n.created_at_s = $created_at_s,
                            n.updated_at_s = $updated_at_s
                        """
                        graph_ops._query(cypher, {
                            "id": node.id,
                            "node_type": node.node_type,
                            "type": node.type,
                            "name": node.name,
                            "task_type": node.task_type,
                            "module": node.module,
                            "skill": node.skill,
                            "status": node.status,
                            "energy": node.energy,
                            "created_at_s": node.created_at_s,
                            "updated_at_s": node.updated_at_s,
                        })
                        task_synced += 1

                # Sync all links with embeddings (task->issue, task->objective, space->task)
                links_synced = 0

                # Lazy load embedding service
                embed_svc = None
                try:
                    from mind.infrastructure.embeddings.service import get_embedding_service
                    embed_svc = get_embedding_service()
                except ImportError:
                    pass

                for link in store.links:
                    link_type_upper = link.type.upper()

                    # Generate embedding for link
                    embedding = None
                    if embed_svc:
                        from mind.doctor_graph import _link_to_embed_text
                        embed_text = _link_to_embed_text(link, store)
                        if embed_text:
                            embedding = embed_svc.embed(embed_text)

                    cypher = f"""
                    MATCH (a {{id: $from_id}})
                    MATCH (b {{id: $to_id}})
                    MERGE (a)-[r:{link_type_upper}]->(b)
                    SET r.name = $name,
                        r.role = $role,
                        r.direction = $direction,
                        r.description = $description,
                        r.weight = $weight,
                        r.energy = $energy,
                        r.created_at_s = $created_at_s
                    """
                    params = {
                        "from_id": link.node_a,
                        "to_id": link.node_b,
                        "name": link.name or "",
                        "role": link.role or "",
                        "direction": link.direction or "",
                        "description": link.description or "",
                        "weight": link.weight,
                        "energy": link.energy,
                        "created_at_s": link.created_at_s,
                    }
                    if embedding:
                        cypher = cypher.rstrip() + ",\n                        r.embedding = $embedding"
                        params["embedding"] = embedding

                    graph_ops._query(cypher, params)
                    links_synced += 1

                if graph_stats:
                    graph_stats["objectives_synced"] = obj_synced
                    graph_stats["tasks_synced"] = task_synced
                    graph_stats["task_links_synced"] = links_synced

            except Exception as e:
                if graph_stats:
                    graph_stats["task_sync_error"] = str(e)[:100]

    # Group by severity
    grouped = {
        "critical": [i for i in all_issues if i.severity == "critical"],
        "warning": [i for i in all_issues if i.severity == "warning"],
        "info": [i for i in all_issues if i.severity == "info"],
    }

    score = calculate_health_score(grouped)

    result = {
        "project": str(target_dir),
        "score": score,
        "issues": grouped,
        "summary": {
            "critical": len(grouped["critical"]),
            "warning": len(grouped["warning"]),
            "info": len(grouped["info"]),
        },
        "ignored_count": ignored_count,
        "false_positive_count": false_positive_count,
    }

    # Include graph stats if available
    if graph_stats:
        result["graph_stats"] = graph_stats

    return result


def doctor_command(
    target_dir: Path,
    output_format: str = "text",
    level: str = "all",
    no_save: bool = False,
    github: bool = False,
    github_max: int = 10,
) -> int:
    """Run the doctor command and return exit code."""
    # Auto-archive large SYNC files first (silent)
    archived = archive_all_syncs(target_dir, max_lines=200)

    config = load_doctor_config(target_dir)
    results = run_doctor(target_dir, config)

    # Filter by level if specified
    if level == "critical":
        results["issues"]["warning"] = []
        results["issues"]["info"] = []
        results["summary"]["warning"] = 0
        results["summary"]["info"] = 0
    elif level == "warning":
        results["issues"]["info"] = []
        results["summary"]["info"] = 0

    # Randomize issue order within each severity to distribute focus.
    rng = random.SystemRandom()
    for severity in ("critical", "warning", "info"):
        rng.shuffle(results["issues"][severity])

    print_doctor_report(results, output_format)

    # Check SYNC status and recommend if needed (text format only)
    if output_format == "text":
        # Show graph stats if available
        graph_stats = results.get("graph_stats")
        if graph_stats and not graph_stats.get("error"):
            print()
            print("Graph Sync:")
            print(f"  Files scanned: {graph_stats.get('files_scanned', 0)}")
            print(f"  Thing nodes: {graph_stats.get('things_created', 0)} created, {graph_stats.get('things_updated', 0)} updated")
            print(f"  Modules: {graph_stats.get('modules_count', 0)}")
            if graph_stats.get("nodes_synced"):
                print(f"  Synced to graph: {graph_stats.get('nodes_synced', 0)} nodes, {graph_stats.get('links_synced', 0)} links")

        # Show archived files if any
        if archived:
            print()
            print(f"Auto-archived {len(archived)} large SYNC file(s)")

        sync_status = check_sync_status(target_dir)
        if sync_status["stale"] > 0 or sync_status["large"] > 0:
            print()
            print("SYNC Status:")
            if sync_status["stale"] > 0:
                print(f"  {sync_status['stale']} stale SYNC file(s)")
            if sync_status["large"] > 0:
                print(f"  {sync_status['large']} large SYNC file(s) (>200 lines)")
            print()
            print("  Run: mind sync")

    # Create GitHub issues if requested
    github_issues = []
    if github and output_format == "text":
        print()
        print("Creating GitHub issues...")
        try:
            from .github import create_issues_for_findings
            all_issues = results["issues"]["critical"] + results["issues"]["warning"]
            github_issues = create_issues_for_findings(all_issues, target_dir, max_issues=github_max)
            if github_issues:
                print(f"  Created {len(github_issues)} issue(s)")
                # Store mapping for work command
                results["github_issues"] = {
                    issue.path: {"number": issue.number, "url": issue.url}
                    for issue in github_issues
                }
        except Exception as e:
            print(f"  Failed to create issues: {e}")

    # Save GitHub issue mapping for work command
    if github_issues:
        mapping_path = target_dir / ".mind" / "state" / "github_issues.json"
        if mapping_path.parent.exists():
            mapping_data = {
                issue.path: {"number": issue.number, "url": issue.url, "type": issue.issue_type}
                for issue in github_issues
            }
            mapping_path.write_text(json.dumps(mapping_data, indent=2))

    # Save to SYNC_Project_Health.md by default (unless --no-save or json output)
    if not no_save and output_format != "json":
        health_path = target_dir / ".mind" / "state" / "SYNC_Project_Health.md"
        if health_path.parent.exists():
            health_content = generate_health_markdown(results, github_issues)
            health_path.write_text(health_content)
            print()
            print(f"Saved to {health_path.relative_to(target_dir)}")

    # Always exit 0; issues are reported in output and SYNC file
    return 0
