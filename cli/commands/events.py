"""mind events - Event timeline CLI commands.

DOCS: docs/cli/commands/IMPLEMENTATION_Events_Command.md

Provides:
- mind events: Show recent events timeline
- mind events --last 30m: Filter by time window
- mind events --type error: Filter by event type
- mind errors: Shortcut for error events
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import re

# ANSI colors
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_CYAN = "\033[96m"
    WHITE = "\033[97m"


@dataclass
class EventInfo:
    """Information about an event."""
    event_id: str
    timestamp: datetime
    event_type: str  # error, trigger, task, agent, health, file
    severity: str  # info, warning, error, critical
    source: str  # capability, agent, doctor, file_watch
    message: str
    details: Optional[Dict[str, Any]] = None
    resolved: bool = False


def _parse_time_window(window: str) -> timedelta:
    """Parse time window string like '30m', '2h', '1d'."""
    match = re.match(r'^(\d+)([smhd])$', window.lower())
    if not match:
        return timedelta(hours=1)  # Default

    value = int(match.group(1))
    unit = match.group(2)

    if unit == 's':
        return timedelta(seconds=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)

    return timedelta(hours=1)


def _event_type_color(event_type: str) -> str:
    """Get color for event type."""
    return {
        "error": C.BRIGHT_RED,
        "trigger": C.BRIGHT_CYAN,
        "task": C.BLUE,
        "agent": C.MAGENTA,
        "health": C.YELLOW,
        "file": C.GREEN,
    }.get(event_type.lower(), C.WHITE)


def _severity_indicator(severity: str) -> str:
    """Get indicator for severity."""
    return {
        "critical": f"{C.BRIGHT_RED}!!{C.RESET}",
        "error": f"{C.RED}! {C.RESET}",
        "warning": f"{C.YELLOW}* {C.RESET}",
        "info": f"{C.DIM}  {C.RESET}",
    }.get(severity.lower(), "  ")


def _get_events_from_logs(
    target_dir: Path,
    since: Optional[datetime] = None,
    event_type_filter: Optional[str] = None,
) -> List[EventInfo]:
    """Get events from log files."""
    events = []
    log_dir = target_dir / ".mind" / "logs"

    if not log_dir.exists():
        return events

    # Patterns for different event types
    error_patterns = [
        (re.compile(r'ERROR', re.IGNORECASE), "error", "error"),
        (re.compile(r'CRITICAL', re.IGNORECASE), "error", "critical"),
        (re.compile(r'WARNING', re.IGNORECASE), "health", "warning"),
    ]

    event_patterns = [
        (re.compile(r'trigger\s+fired', re.IGNORECASE), "trigger", "info"),
        (re.compile(r'task\s+(started|completed|failed)', re.IGNORECASE), "task", "info"),
        (re.compile(r'agent\s+(runed|stopped|killed)', re.IGNORECASE), "agent", "info"),
        (re.compile(r'health\s+check', re.IGNORECASE), "health", "info"),
    ]

    for log_file in log_dir.glob("*.log"):
        try:
            with open(log_file) as f:
                for line in f:
                    # Try to extract timestamp
                    timestamp_match = re.match(
                        r'^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})',
                        line
                    )
                    if timestamp_match:
                        try:
                            ts = datetime.fromisoformat(
                                timestamp_match.group(1).replace(' ', 'T')
                            )
                        except ValueError:
                            ts = datetime.now()
                    else:
                        ts = datetime.now()

                    # Skip if before time window
                    if since and ts < since:
                        continue

                    # Match event patterns
                    for pattern, etype, severity in error_patterns + event_patterns:
                        if pattern.search(line):
                            # Filter by type if specified
                            if event_type_filter and etype != event_type_filter:
                                continue

                            events.append(EventInfo(
                                event_id=f"log_{log_file.stem}_{len(events)}",
                                timestamp=ts,
                                event_type=etype,
                                severity=severity,
                                source=log_file.stem,
                                message=line.strip()[:200],
                            ))
                            break

        except Exception:
            continue

    return events


def _get_events_from_graph(
    target_dir: Path,
    since: Optional[datetime] = None,
    event_type_filter: Optional[str] = None,
) -> List[EventInfo]:
    """Get events from the graph (moment nodes)."""
    events = []

    try:
        from runtime.physics.graph.graph_ops import GraphOps

        graph_name = target_dir.name
        graph = GraphOps(graph_name=graph_name)

        # Query for moment nodes (events)
        where_clauses = ["m:Moment"]

        if event_type_filter:
            where_clauses.append(f"m.type = '{event_type_filter}'")

        if since:
            since_str = since.isoformat()
            where_clauses.append(f"m.created >= '{since_str}'")

        where = " AND ".join(where_clauses)

        result = graph.query(f"""
            MATCH ({where})
            RETURN m.id, m.created, m.type, m.severity, m.source,
                   m.synthesis, m.resolved
            ORDER BY m.created DESC
            LIMIT 100
        """)

        for row in result:
            (moment_id, created, mtype, severity, source,
             synthesis, resolved) = row

            # Parse timestamp
            if created:
                try:
                    ts = datetime.fromisoformat(created.replace('Z', '+00:00'))
                except Exception:
                    ts = datetime.now()
            else:
                ts = datetime.now()

            events.append(EventInfo(
                event_id=moment_id or f"moment_{len(events)}",
                timestamp=ts,
                event_type=mtype or "unknown",
                severity=severity or "info",
                source=source or "graph",
                message=synthesis or "",
                resolved=resolved or False,
            ))

    except Exception:
        pass

    return events


def _format_timestamp(ts: datetime) -> str:
    """Format timestamp for display."""
    now = datetime.now()
    delta = now - ts

    if delta.days == 0:
        return ts.strftime("%H:%M:%S")
    elif delta.days == 1:
        return f"Yesterday {ts.strftime('%H:%M')}"
    elif delta.days < 7:
        return ts.strftime("%a %H:%M")
    else:
        return ts.strftime("%Y-%m-%d")


def list_events(
    target_dir: Path,
    time_window: str = "1h",
    event_type_filter: Optional[str] = None,
    format_output: str = "text",
    limit: int = 50,
) -> int:
    """List events within time window.

    Args:
        target_dir: Project directory
        time_window: Time window (e.g., '30m', '2h', '1d')
        event_type_filter: Filter by event type
        format_output: Output format (text or json)
        limit: Maximum events to show

    Returns:
        Exit code
    """
    # Parse time window
    window = _parse_time_window(time_window)
    since = datetime.now() - window

    # Collect events from all sources
    log_events = _get_events_from_logs(target_dir, since, event_type_filter)
    graph_events = _get_events_from_graph(target_dir, since, event_type_filter)

    # Merge and sort by timestamp (most recent first)
    all_events = log_events + graph_events
    all_events.sort(key=lambda e: e.timestamp, reverse=True)
    events = all_events[:limit]

    if format_output == "json":
        output = []
        for e in events:
            output.append({
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat(),
                "event_type": e.event_type,
                "severity": e.severity,
                "source": e.source,
                "message": e.message,
                "resolved": e.resolved,
            })
        print(json.dumps(output, indent=2))
        return 0

    # Text output
    print()
    print(f"{C.BOLD}{'═' * 78}{C.RESET}")
    print(f"{C.BOLD}  EVENTS{C.RESET} {C.DIM}(last {time_window}){C.RESET}")

    if event_type_filter:
        print(f"{C.DIM}  Filter: type={event_type_filter}{C.RESET}")

    print(f"{C.BOLD}{'═' * 78}{C.RESET}")
    print()

    if not events:
        print(f"  {C.DIM}No events found in the last {time_window}.{C.RESET}")
        print()
        return 0

    # Summary by type
    by_type: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    for e in events:
        by_type[e.event_type] = by_type.get(e.event_type, 0) + 1
        by_severity[e.severity] = by_severity.get(e.severity, 0) + 1

    # Summary line
    summary_parts = []
    for etype, count in sorted(by_type.items()):
        color = _event_type_color(etype)
        summary_parts.append(f"{color}{count} {etype}{C.RESET}")
    print(f"  {C.BOLD}Summary:{C.RESET} {', '.join(summary_parts)}")
    print()

    # Timeline
    print(f"  {C.BOLD}{'TIME':<12} {'  ':<2} {'TYPE':<10} {'SOURCE':<15} MESSAGE{C.RESET}")
    print(f"  {C.DIM}{'─' * 74}{C.RESET}")

    current_date = None
    for e in events:
        # Date separator
        event_date = e.timestamp.date()
        if event_date != current_date:
            current_date = event_date
            if current_date == datetime.now().date():
                date_label = "Today"
            elif current_date == (datetime.now() - timedelta(days=1)).date():
                date_label = "Yesterday"
            else:
                date_label = current_date.strftime("%Y-%m-%d")
            print(f"  {C.DIM}── {date_label} ──{C.RESET}")

        time_str = _format_timestamp(e.timestamp)
        sev_ind = _severity_indicator(e.severity)
        type_color = _event_type_color(e.event_type)

        # Truncate message
        msg = e.message
        if len(msg) > 40:
            msg = msg[:37] + "..."

        print(f"  {time_str:<12} {sev_ind} {type_color}{e.event_type:<10}{C.RESET} {e.source:<15} {msg}")

    print(f"  {C.DIM}{'─' * 74}{C.RESET}")
    print()

    return 0


def list_errors(
    target_dir: Path,
    unresolved_only: bool = False,
    error_type: Optional[str] = None,
    time_window: str = "24h",
    format_output: str = "text",
) -> int:
    """List error events.

    Args:
        target_dir: Project directory
        unresolved_only: Only show unresolved errors
        error_type: Filter by specific error type
        time_window: Time window
        format_output: Output format

    Returns:
        Exit code
    """
    # Get all error events
    window = _parse_time_window(time_window)
    since = datetime.now() - window

    log_events = _get_events_from_logs(target_dir, since, "error")
    graph_events = _get_events_from_graph(target_dir, since, "error")

    all_events = log_events + graph_events

    # Filter unresolved
    if unresolved_only:
        all_events = [e for e in all_events if not e.resolved]

    # Filter by error type
    if error_type:
        all_events = [e for e in all_events if error_type.lower() in e.message.lower()]

    all_events.sort(key=lambda e: e.timestamp, reverse=True)
    errors = all_events[:50]

    if format_output == "json":
        output = []
        for e in errors:
            output.append({
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat(),
                "severity": e.severity,
                "source": e.source,
                "message": e.message,
                "resolved": e.resolved,
            })
        print(json.dumps(output, indent=2))
        return 0

    # Text output
    print()
    print(f"{C.BOLD}{'═' * 78}{C.RESET}")
    print(f"{C.BOLD}  ERRORS{C.RESET} {C.DIM}(last {time_window}){C.RESET}")

    filters = []
    if unresolved_only:
        filters.append("unresolved only")
    if error_type:
        filters.append(f"type contains '{error_type}'")
    if filters:
        print(f"{C.DIM}  Filters: {', '.join(filters)}{C.RESET}")

    print(f"{C.BOLD}{'═' * 78}{C.RESET}")
    print()

    if not errors:
        print(f"  {C.BRIGHT_GREEN}No errors found in the last {time_window}.{C.RESET}")
        print()
        return 0

    # Count by severity
    critical = sum(1 for e in errors if e.severity == "critical")
    error_count = sum(1 for e in errors if e.severity == "error")
    unresolved = sum(1 for e in errors if not e.resolved)

    print(f"  {C.BOLD}Summary:{C.RESET} ", end="")
    if critical:
        print(f"{C.BRIGHT_RED}{critical} critical{C.RESET}, ", end="")
    print(f"{C.RED}{error_count} errors{C.RESET}", end="")
    if unresolved:
        print(f" ({C.YELLOW}{unresolved} unresolved{C.RESET})", end="")
    print()
    print()

    # Error list
    for e in errors:
        sev_ind = _severity_indicator(e.severity)
        time_str = _format_timestamp(e.timestamp)
        resolved_mark = f"{C.GREEN}[resolved]{C.RESET}" if e.resolved else ""

        print(f"  {sev_ind} {time_str:<12} {e.source:<15} {resolved_mark}")
        print(f"     {e.message[:70]}")
        if len(e.message) > 70:
            print(f"     {e.message[70:140]}")
        print()

    print(f"  {C.DIM}{'─' * 74}{C.RESET}")
    print(f"  {C.DIM}Use 'mind work' to address errors with agent assistance{C.RESET}")
    print()

    return 0


def events_command(
    target_dir: Path,
    time_window: str = "1h",
    event_type_filter: Optional[str] = None,
    format_output: str = "text",
    limit: int = 50,
) -> int:
    """Main entry point for events command."""
    return list_events(
        target_dir,
        time_window=time_window,
        event_type_filter=event_type_filter,
        format_output=format_output,
        limit=limit,
    )


def errors_command(
    target_dir: Path,
    unresolved_only: bool = False,
    error_type: Optional[str] = None,
    time_window: str = "24h",
    format_output: str = "text",
) -> int:
    """Main entry point for errors command."""
    return list_errors(
        target_dir,
        unresolved_only=unresolved_only,
        error_type=error_type,
        time_window=time_window,
        format_output=format_output,
    )
