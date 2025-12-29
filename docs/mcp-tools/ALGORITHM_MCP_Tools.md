# ALGORITHM: MCP Tools

```
STATUS: V1 SPEC
PURPOSE: Procedural logic for structured graph dialogues
```

---

## Doctor Algorithm

```
FUNCTION doctor_check():
  gaps = query_graph(find_gaps)  # Call graph for missing specs

  FOR gap IN gaps:
    skill = load_skill(gap.domain)  # Markdown with guidance
    protocol = skill.select_protocol(gap)
    IF protocol:
      doctor_run_protocol(protocol, gap, skill)

FUNCTION doctor_run_protocol(protocol_name, context, skill):
  # Membrane executes the protocol
  result = procedure_start(protocol_name, context)

  WHILE result.status == 'active':
    # Agent answers with skill knowledge in context
    answer = agent_provide_answer(result, skill)
    result = procedure_continue(result.session_id, answer)

  RETURN result
```

---

## Membrane Session Algorithm

```
FUNCTION procedure_start(procedure_name, initial_context):
  procedure = load_procedure(procedure_name)
  session = create_session(procedure, initial_context)

  # Check dependencies
  FOR dep IN procedure.dependencies:
    IF NOT check_dependency(dep):
      IF dep.on_missing.action == 'spawn':
        sub_result = procedure_start(dep.spawn_procedure, session.context)
        WHILE sub_result.status == 'active':
          answer = agent_provide_answer(sub_result)
          sub_result = procedure_continue(sub_result.session_id, answer)
        session.context = merge(session.context, sub_result)
      ELIF dep.on_missing.action == 'prompt':
        session.pending_prompt = dep.prompt_message
      ELIF dep.on_missing.action == 'fail':
        RETURN error("Missing dependency: " + dep.id)

  session.current_step = first_step(procedure)
  RETURN execute_step(session)

FUNCTION procedure_continue(session_id, answer):
  session = load_session(session_id)
  step = session.current_step

  # Validate answer
  IF NOT validate_answer(answer, step.expects):
    RETURN error("Invalid: " + validation_message)

  # Store answer
  session.answers[step.id] = answer

  # Create moment for this answer
  IF step.moment:
    create_moment(session, step.moment, answer)

  # Move to next step
  next_step_id = step.next
  IF next_step_id == '$complete':
    RETURN execute_create(session)

  session.current_step = membrane.steps[next_step_id]
  RETURN execute_step(session)
```

---

## Step Execution Algorithm

```
FUNCTION execute_step(session):
  step = session.current_step

  SWITCH step.type:
    CASE 'ask':
      RETURN {
        status: 'active',
        session_id: session.id,
        step_type: 'ask',
        question: interpolate(step.question, session.context),
        expects: step.expects,
        context_enrichment: step.context_enrichment
      }

    CASE 'query':
      result = execute_query(step.query, session.context)
      session.context[step.store_as] = result
      IF step.moment:
        create_moment(session, step.moment, result)
      session.current_step = protocol.steps[step.next]
      RETURN execute_step(session)

    CASE 'branch':
      condition_result = evaluate(step.condition, session.context)
      IF step.cases:
        # Multi-case branch
        next_step = step.cases[condition_result]
      ELSE:
        # Binary branch
        next_step = step.then IF condition_result ELSE step.else
      session.current_step = protocol.steps[next_step]
      RETURN execute_step(session)

    CASE 'call_protocol':
      # Push current session onto stack
      session.call_stack.push({
        protocol: session.protocol,
        step: step,
        on_complete: step.on_complete
      })
      # Start sub-protocol with merged context
      sub_context = merge(session.context, step.context)
      sub_protocol = load_protocol(step.protocol)
      session.protocol = sub_protocol
      session.current_step = first_step(sub_protocol)
      session.context = sub_context
      RETURN execute_step(session)

    CASE 'create':
      RETURN execute_create(session)

    CASE 'update':
      execute_update(step, session)
      IF step.moment:
        create_moment(session, step.moment, step)
      session.current_step = protocol.steps[step.next]
      RETURN execute_step(session)
```

---

## Protocol Completion Algorithm

```
FUNCTION handle_protocol_complete(session):
  IF session.call_stack.empty():
    # Top-level protocol complete
    RETURN execute_create(session)

  # Pop caller from stack
  caller = session.call_stack.pop()
  session.protocol = caller.protocol
  session.current_step = caller.protocol.steps[caller.on_complete]
  # Context preserved (sub-protocol may have added to it)
  RETURN execute_step(session)
```

---

## Cluster Creation Algorithm

```
FUNCTION execute_create(session):
  membrane = session.membrane
  create_spec = membrane.steps.do_create  # or final create step

  nodes = []
  links = []

  # Create nodes
  FOR node_spec IN create_spec.nodes:
    IF node_spec.condition AND NOT evaluate(node_spec.condition):
      CONTINUE

    IF node_spec.for_each:
      items = session.answers[node_spec.for_each]
      FOR item IN items:
        node = instantiate_node(node_spec, session.context, item)
        nodes.append(node)
    ELSE:
      node = instantiate_node(node_spec, session.context)
      nodes.append(node)

  # Create links
  FOR link_spec IN create_spec.links:
    IF link_spec.condition AND NOT evaluate(link_spec.condition):
      CONTINUE

    IF link_spec.for_each:
      items = session.answers[link_spec.for_each]
      FOR item IN items:
        link = instantiate_link(link_spec, session.context, item, nodes)
        links.append(link)
    ELSE:
      link = instantiate_link(link_spec, session.context, nodes)
      links.append(link)

  # Commit to graph
  graph_create_cluster(nodes, links)

  RETURN {
    status: 'complete',
    session_id: session.id,
    nodes_created: len(nodes),
    links_created: len(links),
    summary: interpolate(membrane.output.summary, session.context)
  }
```

---

## Query Execution Algorithm

```
FUNCTION execute_query(query_spec, context):
  query = interpolate(query_spec, context)

  IF query.find:
    RETURN graph_find(query.find, query.where, query.in_space, query.limit)

  IF query.links_from:
    RETURN graph_links_from(query.links_from, query.type)

  IF query.links_to:
    RETURN graph_links_to(query.links_to, query.type)

  IF query.related_to:
    RETURN graph_related(query.related_to, query.via, query.direction, query.depth)

  IF query.contents_of:
    RETURN graph_contents(query.contents_of, query.node_type, query.depth)

  IF query.or_search:
    RETURN graph_search(query.or_search)
```

---

## Moment Creation Algorithm

```
FUNCTION create_moment(session, moment_spec, data):
  moment = {
    id: generate_id("moment_" + moment_spec.type + "_" + timestamp()),
    node_type: "moment",
    type: moment_spec.type,
    status: "completed",
    prose: "",
    timestamp: now()
  }

  # Agent provides description/reasoning based on moment_spec.agent_provides
  IF "description" IN moment_spec.agent_provides:
    moment.content = agent_describe(data)
  IF "reasoning" IN moment_spec.agent_provides:
    moment.reasoning = agent_reason(data)

  # Create links
  links = [
    {type: "expresses", from: session.context.actor_id, to: moment.id}
  ]

  IF session.current_target:
    links.append({type: "about", from: moment.id, to: session.current_target})

  graph_create_cluster([moment], links)
  session.moments.append(moment.id)
```

---

## Validation Algorithm

```
FUNCTION validate_answer(answer, expects):
  SWITCH expects.type:
    CASE 'string':
      IF NOT is_string(answer):
        RETURN {valid: false, message: "Expected string"}
      IF expects.min_length AND len(answer) < expects.min_length:
        RETURN {valid: false, message: "Minimum length: " + expects.min_length}
      IF expects.pattern AND NOT regex_match(answer, expects.pattern):
        RETURN {valid: false, message: "Must match pattern: " + expects.pattern}
      RETURN {valid: true}

    CASE 'id':
      IF NOT graph_exists(answer):
        RETURN {valid: false, message: "Node not found: " + answer}
      IF expects.node_type AND NOT graph_type_match(answer, expects.node_type):
        RETURN {valid: false, message: "Wrong node type"}
      RETURN {valid: true}

    CASE 'id_list':
      FOR id IN answer:
        IF NOT graph_exists(id):
          RETURN {valid: false, message: "Node not found: " + id}
        IF expects.filter:
          node = graph_get(id)
          IF NOT matches_filter(node, expects.filter):
            RETURN {valid: false, message: "Node doesn't match filter"}
      IF expects.min AND len(answer) < expects.min:
        RETURN {valid: false, message: "Minimum " + expects.min + " required"}
      RETURN {valid: true}

    CASE 'string_list':
      IF NOT is_list(answer):
        RETURN {valid: false, message: "Expected list"}
      IF expects.min AND len(answer) < expects.min:
        RETURN {valid: false, message: "Minimum " + expects.min + " required"}
      RETURN {valid: true}

    CASE 'enum':
      IF answer NOT IN expects.options:
        RETURN {valid: false, message: "Must be one of: " + expects.options}
      RETURN {valid: true}
```

---

## Context Enrichment Algorithm

```
FUNCTION handle_enrichment(session, enrichment_request):
  # Agent can query graph during any ask step
  IF enrichment_request.type == 'exploration':
    RETURN execute_query({contents_of: enrichment_request.target, depth: 2})

  IF enrichment_request.type == 'relationship':
    RETURN execute_query({related_to: enrichment_request.target, direction: 'both'})

  IF enrichment_request.type == 'verification':
    RETURN execute_query({find: 'narrative', where: {type: 'validation'}, in_space: enrichment_request.target})

  IF enrichment_request.type == 'clarification':
    RETURN graph_get(enrichment_request.target)
```

---

## CHAIN

- **Prev:** BEHAVIORS_MCP_Tools.md
- **Next:** VALIDATION_MCP_Tools.md
- **Implements:** IMPLEMENTATION_MCP_Tools.md
