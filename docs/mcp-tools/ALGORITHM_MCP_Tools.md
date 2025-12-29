# ALGORITHM: MCP Tools

```
STATUS: V2
PURPOSE: How MCP tools execute queries and procedures
```

---

## graph_query Algorithm

```
FUNCTION graph_query(queries: string[]):
  # Derive context automatically
  actor = get_current_actor()  # From conversation context

  # Process queries in parallel
  results = parallel_map(queries, query =>
    # Create embedding for query
    embedding = embed(query)

    # Search local graph by similarity
    matches = vector_search(
      graph: LOCAL,
      embedding: embedding,
      top_k: top_k,
      threshold: 0.7
    )

    # Expand to connected nodes if requested
    IF expand:
      FOR match IN matches:
        match.connected = get_linked_nodes(match.id)

    RETURN {query: query, matches: matches}
  )

  RETURN format_results(results, format)
```

---

## membrane_query Algorithm

```
FUNCTION membrane_query(queries: string[]):
  # Connect to membrane graph (hardcoded endpoint)
  membrane_graph = connect(MEMBRANE_HOST, MEMBRANE_GRAPH)

  results = parallel_map(queries, query =>
    embedding = embed(query)

    # Search membrane graph (public nodes only)
    matches = vector_search(
      graph: membrane_graph,
      embedding: embedding,
      top_k: top_k,
      filter: {public: true}
    )

    # Each match includes org_id
    FOR match IN matches:
      match.source_org = match.org_id

    RETURN {query: query, matches: matches}
  )

  RETURN format_results(results, format)
```

---

## vector_search Algorithm

```
FUNCTION vector_search(graph, embedding, top_k, threshold, filter):
  # Get all nodes with embeddings
  nodes = graph.nodes_with_embedding()

  # Apply filter if specified
  IF filter:
    nodes = nodes.where(filter)

  # Calculate cosine similarity
  scored = []
  FOR node IN nodes:
    similarity = cosine_similarity(embedding, node.embedding)
    IF similarity >= threshold:
      scored.append({node: node, score: similarity})

  # Sort by score descending
  scored.sort(by: score, order: desc)

  # Return top k
  RETURN scored[:top_k]
```

---

## procedure_start Algorithm

```
FUNCTION procedure_start(procedure_name, context):
  # Load procedure definition
  procedure = load_yaml(procedures/{procedure_name}.yaml)
  IF NOT procedure:
    RETURN error("Procedure not found")

  # Create session
  session = {
    id: generate_uuid(),
    procedure: procedure,
    context: context or {},
    answers: {},
    current_step: 0
  }

  # Return first step
  RETURN {
    session_id: session.id,
    step: procedure.steps[0],
    question: procedure.steps[0].question
  }
```

---

## procedure_continue Algorithm

```
FUNCTION procedure_continue(session_id, answer):
  session = get_session(session_id)
  IF NOT session:
    RETURN error("Session expired or invalid")

  step = session.procedure.steps[session.current_step]

  # Validate answer
  IF step.expects:
    validation = validate(answer, step.expects)
    IF NOT validation.valid:
      RETURN error(validation.message)

  # Store answer
  session.answers[step.id] = answer

  # Advance to next step
  session.current_step += 1

  # Check if complete
  IF session.current_step >= len(session.procedure.steps):
    RETURN execute_completion(session)

  # Return next step
  next_step = session.procedure.steps[session.current_step]
  RETURN {
    session_id: session.id,
    step: next_step,
    question: next_step.question
  }
```

---

## doctor_check Algorithm

```
FUNCTION doctor_check(depth, path):
  issues = []

  # Run health checks based on depth
  IF depth >= "links":
    issues += check_broken_links(path)

  IF depth >= "docs":
    issues += check_missing_docs(path)
    issues += check_stale_sync(path)

  IF depth >= "full":
    issues += check_schema_violations(path)
    issues += check_orphan_nodes(path)

  # Auto-fix small schema issues
  schema_issues = issues.filter(type == "SCHEMA_VIOLATION")
  IF len(schema_issues) <= 10:
    fix_schema_issues(schema_issues)
    issues = issues.filter(type != "SCHEMA_VIOLATION")

  # Assign agents to remaining issues
  FOR issue IN issues:
    issue.agent = posture_mapping[issue.type]
    issue.agent_status = get_agent_status(issue.agent)

  RETURN issues
```

---

## agent_spawn Algorithm

```
FUNCTION agent_spawn(task_id, issue_type, path, agent_id, provider):
  # Determine agent
  IF task_id:
    task = graph_query(["Find task " + task_id])
    IF NOT task:
      RETURN error("Task not found")
    agent = select_agent_for_task(task)
  ELSE:
    IF NOT issue_type OR NOT path:
      RETURN error("Either task_id or (issue_type + path) required")
    agent = agent_id OR posture_mapping[issue_type]

  # Check availability
  IF agent.status == "running":
    RETURN error(agent.id + " is already running")

  # Set running
  set_agent_status(agent.id, "running")

  # Execute
  result = execute_agent(agent, task OR {issue_type, path}, provider)

  # Set ready
  set_agent_status(agent.id, "ready")

  RETURN result
```

---

## Embedding Algorithm

```
FUNCTION embed(text):
  # Use configured embedding service
  # Default: all-mpnet-base-v2, 768 dimensions
  embedding = embedding_service.encode(text)
  RETURN normalize(embedding)

FUNCTION cosine_similarity(a, b):
  dot_product = sum(a[i] * b[i] for i in range(len(a)))
  norm_a = sqrt(sum(x*x for x in a))
  norm_b = sqrt(sum(x*x for x in b))
  RETURN dot_product / (norm_a * norm_b)
```

---

## CHAIN

- **Prev:** BEHAVIORS_MCP_Tools.md
- **Next:** VALIDATION_MCP_Tools.md
- **Implements:** IMPLEMENTATION_MCP_Tools.md
