"""
[THINK] Procedure — Structured dialogues for common tasks.

Actions: list, start, continue, abort.

Usage via MCP:
    procedure(action="list")
    procedure(action="start", procedure="create_doc_chain")
    procedure(action="continue", session_id="abc123", answer="...")
    procedure(action="abort", session_id="abc123")
"""

from typing import Any, Dict

from mcp.tools.context import ServerContext


TOOL_SCHEMA = {
    "name": "procedure",
    "description": (
        "[THINK] Structured dialogues for documentation, investigation, and workflow tasks. "
        "Use action='list' to see available procedures, 'start' to begin one, "
        "'continue' to answer the current step, 'abort' to cancel."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "start", "continue", "abort"],
                "description": "What to do: list available procedures, start one, continue with an answer, or abort.",
            },
            "procedure": {
                "type": "string",
                "description": "Name of the procedure to start (required for action='start').",
            },
            "session_id": {
                "type": "string",
                "description": "Session ID (required for action='continue' and 'abort').",
            },
            "answer": {
                "description": "Answer for the current step (required for action='continue'). Type depends on what the step expects.",
            },
            "context": {
                "type": "object",
                "description": "Optional initial context values for action='start' (e.g., {\"actor_id\": \"actor_claude\"}).",
            },
        },
        "required": ["action"],
    },
}


def handle_procedure(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Dispatch procedure actions."""
    action = args.get("action")

    if action == "list":
        return _list_procedures(ctx)
    elif action == "start":
        return _start_procedure(args, ctx)
    elif action == "continue":
        return _continue_procedure(args, ctx)
    elif action == "abort":
        return _abort_procedure(args, ctx)
    else:
        return _err(f"Unknown action '{action}'. Use: list, start, continue, abort.")


def _list_procedures(ctx: ServerContext) -> Dict[str, Any]:
    """List available procedures."""
    procedures = []
    if ctx.connectomes_dir and ctx.connectomes_dir.exists():
        for path in ctx.connectomes_dir.glob("*.yaml"):
            procedures.append(path.stem)

    if not procedures:
        return _ok("No procedures found.")

    text = "Available procedures:\n"
    for p in procedures:
        text += f"  - {p}\n"
    return _ok(text)


def _start_procedure(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Start a procedure session."""
    procedure_name = args.get("procedure")
    context = args.get("context", {})

    if not procedure_name:
        return _err("'procedure' is required for action='start'.")

    response = ctx.runner.start(procedure_name, initial_context=context)
    return _format_response(response)


def _continue_procedure(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Continue a procedure session."""
    session_id = args.get("session_id")
    answer = args.get("answer")

    if not session_id:
        return _err("'session_id' is required for action='continue'.")

    response = ctx.runner.continue_session(session_id, answer)
    return _format_response(response)


def _abort_procedure(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Abort a procedure session."""
    session_id = args.get("session_id")

    if not session_id:
        return _err("'session_id' is required for action='abort'.")

    response = ctx.runner.abort(session_id)
    return _format_response(response)


def _format_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Format runner response as MCP tool result."""
    status = response.get("status", "unknown")
    lines = [f"Status: {status}"]

    if response.get("error"):
        lines.append(f"Error: {response['error']}")

    if response.get("session_id"):
        lines.append(f"Session: {response['session_id']}")

    step = response.get("step", {})
    if step:
        step_type = step.get("type", "")
        lines.append(f"Step Type: {step_type}")

        if step.get("context"):
            lines.append(f"\n--- Context ---\n{step['context']}")

        if step.get("question"):
            lines.append(f"\n--- Question ---\n{step['question']}")
            if step.get("question_name"):
                lines.append(f"(Answer will be stored as: {step['question_name']})")

        if step.get("why_it_matters"):
            lines.append(f"\nWhy it matters: {step['why_it_matters']}")

        if step.get("good_answer"):
            lines.append(f"Good answer example: {step['good_answer']}")

        if step.get("bad_answer"):
            lines.append(f"Bad answer example: {step['bad_answer']}")

        if step.get("expects"):
            expects = step["expects"]
            lines.append(f"\nExpects: {expects.get('type', 'string')}")
            if expects.get("options"):
                lines.append(f"Options: {expects['options']}")
            if expects.get("min_length"):
                lines.append(f"Min Length: {expects['min_length']}")
            if expects.get("min") is not None:
                lines.append(f"Min Items: {expects['min']}")

        if step.get("question_count") and step["question_count"] > 1:
            lines.append(f"Question {step.get('question_index', 0) + 1} of {step['question_count']}")

        if step.get("results"):
            lines.append(f"\nQuery Results: {len(step['results'])} items")
            for r in step["results"][:5]:
                lines.append(f"  - {r}")

    if status == "complete":
        created = response.get("created", {})
        nodes = created.get("nodes", [])
        links = created.get("links", [])

        lines.append(f"\nCreated: {len(nodes)} nodes, {len(links)} links")

        if nodes:
            lines.append("\nNodes:")
            for n in nodes:
                lines.append(f"  - [{n.get('type')}] {n.get('id')}")

        if links:
            lines.append("\nLinks:")
            for l in links:
                lines.append(f"  - {l.get('type')}: {l.get('from')} -> {l.get('to')}")

    return _ok("\n".join(lines))


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
