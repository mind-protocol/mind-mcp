# Agent System — Algorithm

```
STATUS: CANONICAL
UPDATED: 2025-12-30
```

---

## run_work_agent() Flow

```
INPUT: actor_id, prompt, target_dir, agent_provider, timeout

1. SETUP
   agent_graph = AgentGraph()
   name = extract_name(actor_id)  # "AGENT_Witness" → "witness"
   agent_graph.set_agent_running(actor_id)

2. LOAD PROMPT
   system_prompt = get_agent_system_prompt(name, target_dir)
   # Reads from .mind/actors/{name}/CLAUDE.md

3. EXECUTE
   result = _run_with_retry(prompt, system_prompt, ...)
   # First try with --continue, retry without on failure

4. DETECT CD COMMANDS
   cd_dirs = _detect_cd_commands(result.conversation)
   if cd_dirs:
       new_cwd = resolve_path(cd_dirs[-1], target_dir)
       agent_graph.update_agent_cwd(actor_id, new_cwd)

5. CREATE MOMENTS
   if result.conversation:
       batches = _group_turns_into_batches(result.conversation)
       for batch in batches:
           moment_id = agent_graph.create_moment(
               actor_id, "CONVERSATION", batch.summary
           )
           chain to previous moment

       create final COMPLETION moment

6. CLEANUP (finally)
   agent_graph.set_agent_ready(actor_id)
   delete .mind/actors/{name}/.sessionId

OUTPUT: RunResult(success, output, completion_moment_id, ...)
```

---

## _run_agent() Flow

```
INPUT: prompt, system_prompt, target_dir, agent_provider, agent_name

1. BUILD COMMAND
   cmd = build_agent_command(
       agent=agent_provider,
       prompt=prompt,
       system_prompt=system_prompt,
       stream_json=True,  # --output-format stream-json
       # --verbose added by cli.py for Claude
   )

2. START PROCESS
   process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)

3. PARSE OUTPUT
   for line in stdout:
       data = json.loads(line)

       if data.type == "system":
           session_id = data.session_id
           write to .mind/actors/{name}/.sessionId

       elif data.type == "assistant":
           for content in data.message.content:
               if content.type == "thinking":
                   turns.append(ConversationTurn("thinking", content.thinking))
               elif content.type == "text":
                   turns.append(ConversationTurn("text", content.text))
               elif content.type == "tool_use":
                   turns.append(ConversationTurn("tool_use", content.input, tool_name=content.name))

       elif data.type == "user":
           for content in data.message.content:
               if content.type == "tool_result":
                   turns.append(ConversationTurn("tool_result", content.content[:2000]))

4. RETURN
   success = process.returncode == 0
   return _RunResult(success, output, error, conversation=turns)
```

---

## _group_turns_into_batches() Algorithm

```
INPUT: turns[], batch_size=5, tool_output_max_len=200

batches = []
for i in range(0, len(turns), batch_size):
    batch_turns = turns[i:i+batch_size]
    summary_parts = []
    tools_used = []

    for turn in batch_turns:
        if turn.type == "thinking":
            summary_parts.append(f"💭 {turn.content}")  # full
        elif turn.type == "text":
            summary_parts.append(f"📝 {turn.content}")  # full
        elif turn.type == "tool_use":
            tools_used.append(turn.tool_name)
            summary_parts.append(f"🔧 {turn.tool_name}({turn.content})")  # full
        elif turn.type == "tool_result":
            truncated = turn.content[:tool_output_max_len]
            if len(turn.content) > tool_output_max_len:
                truncated += "..."
            summary_parts.append(f"→ {truncated}")  # truncated

    batches.append(ConversationBatch(
        summary="\n".join(summary_parts),
        turn_count=len(batch_turns),
        tools_used=tools_used
    ))

OUTPUT: batches[]
```

---

## _detect_cd_commands() Algorithm

```
INPUT: turns[]

directories = []
for turn in turns:
    if turn.type == "tool_use" and turn.tool_name == "Bash":
        tool_input = json.loads(turn.content)
        command = tool_input.get("command", "")

        # Regex matches: cd /path, cd path, cd "path"
        # In contexts: cd /tmp, cd /tmp && ls, ls && cd /tmp
        for match in regex.finditer(r'(?:^|&&|;|\|)\s*cd\s+["\']?([^"\'&;|\n]+)["\']?', command):
            path = match.group(1).strip()
            if path:
                directories.append(path)

OUTPUT: directories[]  # Last one is current cwd
```

---

## create_moment() Flow

```
INPUT: actor_id, moment_type, prose, about_ids?, space_id?, extra_props?, tools_used?

1. EXTRACT SALIENT TERMS (embedding-based)
   embedding = get_embedding(prose[:2000])
   candidates = query graph for nodes with embeddings
   for each candidate:
       similarity = cosine_similarity(embedding, candidate.embedding)
   top_terms = sort by similarity, take top 4
   clean_terms = split on separators, capitalize, join

2. INFER ACTION VERB
   if "bug"/"error" in prose → "Debugging"
   if "found"/"discovered" in prose → "Discovering"
   if "refactor" in prose → "Refactoring"
   if Read/Grep heavy → "Exploring"
   if Edit/Write heavy → "Building"
   else → "Working"

3. BUILD MOMENT NAME AND ID
   agent_name = actor_id[6:]  # "AGENT_Witness" → "Witness"
   moment_name = f"{verb}_{term1}_{term2}_{...}"
   moment_id = f"WORK_{agent_name}_{moment_name}_{hash}"
   # Example: WORK_Witness_Exploring_AgentGraph_Patterns_abc1

4. SET CONTEXT
   set_actor(actor_id)

5. INJECT MOMENT
   inject(adapter, {
       id: moment_id,
       label: "Moment",
       name: moment_name,
       type: moment_type,
       synthesis: prose,
       timestamp: now,
       ...extra_props
   }, with_context=True)

6. LINK TO TARGETS
   for about_id in about_ids:
       inject_link(adapter, moment_id, about_id, nature="about")

   if space_id:
       inject_link(adapter, space_id, moment_id, nature="includes")

OUTPUT: moment_id
```
