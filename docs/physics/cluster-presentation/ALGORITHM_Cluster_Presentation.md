# Cluster Presentation Algorithm

```
STATUS: STABLE (v1.9.2)
UPDATED: 2025-12-26
```

## Overview

Transforms a raw cluster (200+ nodes) into a presented cluster (20-30 nodes) with readable formatting.

---

## ALGORITHM: Post-Traversal Selection

### Input

- Raw cluster (all nodes and links traversed)
- Agent intention
- Query
- Start position

### Output

- Presented cluster: 20-30 nodes max
- Metadata about what's not presented

---

### Step 1: Identify Points of Interest

**Direct Response** — Nodes matching the intention:

```python
def find_direct_response(nodes, intention_type, query_embedding):
    if intention_type == IntentionType.FIND_NEXT:
        return [n for n in nodes if n.node_type == 'moment' and n.status == 'possible']

    if intention_type == IntentionType.RETRIEVE:
        return [n for n in nodes if n.node_type == 'narrative' and n.type == 'implementation']

    # Default: highest alignment
    return sorted(nodes, key=lambda n: cosine(n.embedding, query_embedding), reverse=True)[:5]
```

Keep: **1-5 nodes**

**Convergences** — Nodes with 3+ incoming links in cluster:

```python
def find_convergences(nodes, links):
    incoming_count = defaultdict(int)
    for link in links:
        incoming_count[link.target_id] += 1
    return [n for n in nodes if incoming_count[n.id] >= 3]
```

Keep: **all**

**Tensions** — Nodes with contradictory incoming links:

```python
def find_tensions(nodes, links):
    tensions = []
    for node in nodes:
        incoming = [l for l in links if l.target_id == node.id]
        trusts = [l.trust_disgust for l in incoming if hasattr(l, 'trust_disgust')]
        if trusts and max(trusts) > 0.4 and min(trusts) < -0.4:
            tensions.append(node)
    return tensions
```

Keep: **all**

**Divergences** — Nodes with 3+ outgoing links followed:

```python
def find_divergences(nodes, links, traversed_link_ids):
    outgoing_count = defaultdict(int)
    for link in links:
        if link.id in traversed_link_ids:
            outgoing_count[link.source_id] += 1
    return [n for n in nodes if outgoing_count[n.id] >= 3]
```

Keep: **all**

**Gaps** — Relevant incomplete nodes:

```python
def find_gaps(nodes, links, intention_type):
    gaps = []

    # Dead ends (no outgoing links)
    outgoing = {l.source_id for l in links}
    dead_ends = [n for n in nodes if n.id not in outgoing]

    # Weak links (permanence < 0.3)
    weak = [l for l in links if l.permanence < 0.3]

    # Filter by relevance to intention
    if intention_type == IntentionType.VERIFY:
        gaps.extend(dead_ends)  # All gaps relevant
    elif intention_type == IntentionType.FIND_NEXT:
        gaps.extend([n for n in dead_ends if n.status == 'possible'])

    return gaps
```

Keep: **gaps relevant to intention**

---

### Step 2: Build Main Path

From start position to direct response.

```python
def build_main_path(start_id, response_nodes, links, intention_embedding):
    paths = []

    for response in response_nodes:
        path = []
        current = response.id

        while current != start_id:
            incoming = [l for l in links if l.target_id == current]
            if not incoming:
                break

            # Best link by weight × energy × alignment
            best = max(incoming, key=lambda l:
                l.weight * l.energy * cosine(l.embedding, intention_embedding)
            )

            path.insert(0, current)
            path.insert(0, best.id)
            current = best.source_id

        path.insert(0, start_id)
        paths.append(path)

    return paths
```

**If multiple responses:** Find junction point (common ancestor) and present as tree.

---

### Step 3: Add Minimal Context

For points of interest not in main path:

```python
def add_context(point, links, main_path_nodes):
    if point.id in main_path_nodes:
        return []

    incoming = [l for l in links if l.target_id == point.id]
    if not incoming:
        return [point]

    best_link = max(incoming, key=lambda l: l.weight * l.energy)
    return [best_link.source, best_link, point]
```

---

### Step 4: Score and Truncate

If still > 30 nodes:

```python
def score_node(node, response_ids, main_path_ids, convergences, tensions, divergences, intention_embedding):
    score = 0

    if node.id in response_ids:
        score += 10
    if node.id in main_path_ids:
        score += 5
    if node.id in convergences:
        score += 3
    if node.id in tensions:
        score += 3
    if node.id in divergences:
        score += 2

    score += node.weight * 0.5
    score += node.energy * 0.3
    score += cosine(node.embedding, intention_embedding) * 2

    return score

def truncate(nodes, max_nodes=30, main_path_ids=set()):
    scored = sorted(nodes, key=lambda n: score_node(n), reverse=True)
    presented = scored[:max_nodes]

    # Ensure main path intact
    for node_id in main_path_ids:
        node = get_node(node_id)
        if node not in presented:
            presented.append(node)

    return presented
```

---

### Step 5: Reconstruct Links

Keep only links between presented nodes:

```python
def filter_links(links, presented_node_ids):
    return [l for l in links
            if l.source_id in presented_node_ids
            and l.target_id in presented_node_ids]
```

---

## ALGORITHM: Synthesis Unfolding

### Node Synthesis

```python
def unfold_node_synthesis(node):
    """Convert compact synthesis to prose."""
    # Input: "surprising reliable the Revelation, incandescent (ongoing)"

    parts = parse_node_synthesis(node.synthesis)

    # Prefix emotions → adverbs
    adverbs = [to_adverb(p) for p in parts.prefixes]  # "surprisingly reliably"

    # Energy level
    energy_phrase = f"is {parts.energy}"  # "is incandescent"

    # Status
    status_phrase = f"and {parts.status}" if parts.status else ""  # "and ongoing"

    return f"The {node.node_type} **{parts.name}**, {', '.join(adverbs)}, {energy_phrase} {status_phrase}."
```

### Link Synthesis

```python
def unfold_link_synthesis(link, target_node):
    """Convert compact synthesis to prose."""
    # Input: "suddenly definitively establishes, with admiration"

    parts = parse_link_synthesis(link.synthesis)

    # Pre-modifiers → adverbs
    pre = ', '.join(parts.pre_modifiers)  # "suddenly, definitively"

    # Verb → participle
    verb = to_participle(parts.verb)  # "established"

    # Post-modifiers stay same
    post = ', '.join(parts.post_modifiers)  # "with admiration"

    return f"It {pre}, {verb}, {post}, the **{target_node.name}**."
```

### Combined Prose

```python
def node_link_node_prose(source, link, target):
    """Full prose for a traversal step."""
    return f"{source.name} {link.synthesis} {target.name}."
```

---

## ALGORITHM: Presentation Formatting

### Tree Format

**v1.9.1**: Each node includes its content in a ``` block after synthesis.

```python
def format_path_tree(path, response_ids, markers):
    lines = []

    for i, item in enumerate(path):
        if isinstance(item, Node):
            marker = ""
            if item.id in response_ids:
                marker = "  ◆ RESPONSE"
            elif item.id in markers.get('branching', []):
                marker = "  ◆ BRANCHING"

            lines.append(f"{item.synthesis}{marker}")

            # v1.9.1: Add content block if present
            if item.content:
                lines.append("```")
                lines.append(item.content)
                lines.append("```")

        elif isinstance(item, Link):
            lines.append("  │")
            lines.append(f"  └─ {item.synthesis}")
            lines.append("     │")
            lines.append("     ▼")

    return '\n'.join(lines)
```

### Branching Format

**v1.9.1**: Each branch target includes its content block.

```python
def format_branching(node, outgoing_links, targets):
    lines = [f"{node.synthesis}  ◆ BRANCHING"]

    # v1.9.1: Add content block for branching node
    if node.content:
        lines.extend(["```", node.content, "```"])

    lines.append("  │")

    for i, (link, target) in enumerate(zip(outgoing_links, targets)):
        prefix = "├──" if i < len(outgoing_links) - 1 else "└──"
        lines.append(f"  {prefix} {link.synthesis} → {target.synthesis}")

        # v1.9.1: Add content block for target
        if target.content:
            indent = "  │   " if i < len(outgoing_links) - 1 else "      "
            lines.append(f"{indent}```")
            lines.append(f"{indent}{target.content}")
            lines.append(f"{indent}```")

        if i < len(outgoing_links) - 1:
            lines.append("  │")

    return '\n'.join(lines)
```

### Tension Format

```python
def format_tension(node, incoming_links, sources):
    lines = [
        f"⚡ On **{node.name}**:",
        "",
        "| Source | Relation |",
        "|--------|----------|"
    ]

    for link, source in zip(incoming_links, sources):
        lines.append(f"| {source.name} | {link.synthesis} |")

    return '\n'.join(lines)
```

### Convergence Format

```python
def format_convergence(node, incoming_links, sources):
    lines = [
        f"→ {node.synthesis} ({len(sources)} paths)",
        "",
        "Sources:"
    ]

    for link, source in zip(incoming_links, sources):
        lines.append(f"- {source.synthesis} {link.synthesis}")

    return '\n'.join(lines)
```

### Gap Format

```python
def format_gaps(gaps):
    lines = ["### Gap", ""]

    for gap in gaps:
        if gap.type == 'dead_end':
            lines.append(f"○ {gap.node.synthesis} has no outgoing links.")
        elif gap.type == 'missing':
            lines.append(f"○ No narrative covers {gap.subject}.")
        elif gap.type == 'weak':
            lines.append(f"○ Weak link (permanence < 0.3) between {gap.source.name} and {gap.target.name}.")

    return '\n'.join(lines)
```

---

## ALGORITHM: Full Presentation

```python
def present_cluster(raw_cluster, query, intention, intention_type, start_id):
    # Step 1: Identify points of interest
    responses = find_direct_response(raw_cluster.nodes, intention_type, query_embedding)
    convergences = find_convergences(raw_cluster.nodes, raw_cluster.links)
    tensions = find_tensions(raw_cluster.nodes, raw_cluster.links)
    divergences = find_divergences(raw_cluster.nodes, raw_cluster.links, raw_cluster.traversed_ids)
    gaps = find_gaps(raw_cluster.nodes, raw_cluster.links, intention_type)

    # Step 2: Build main path
    main_paths = build_main_path(start_id, responses, raw_cluster.links, intention_embedding)
    main_path_ids = set()
    for path in main_paths:
        main_path_ids.update(path)

    # Step 3: Add context
    all_nodes = set(main_path_ids)
    for poi in convergences + tensions + divergences:
        context = add_context(poi, raw_cluster.links, main_path_ids)
        all_nodes.update([c.id for c in context if hasattr(c, 'id')])

    # Step 4: Score and truncate
    presented_nodes = truncate(list(all_nodes), max_nodes=30, main_path_ids=main_path_ids)

    # Step 5: Filter links
    presented_node_ids = {n.id for n in presented_nodes}
    presented_links = filter_links(raw_cluster.links, presented_node_ids)

    # Format output
    output = format_presentation(
        query=query,
        intention=intention,
        responses=responses,
        main_paths=main_paths,
        convergences=convergences,
        tensions=tensions,
        gaps=gaps,
        stats=ClusterStats(
            traversed_nodes=len(raw_cluster.nodes),
            traversed_links=len(raw_cluster.links),
            presented_nodes=len(presented_nodes),
            presented_links=len(presented_links)
        )
    )

    return PresentedCluster(
        markdown=output,
        nodes=presented_nodes,
        links=presented_links,
        stats=stats
    )
```

---

## Section Filtering by Intention

| Section | summarize | find_next | verify | implement |
|---------|-----------|-----------|--------|-----------|
| Response | Narratives | Possible moment | Tensions | Docs |
| Path | Complete | Minimal | To tensions | To docs |
| Tensions | If found | No | Yes, detailed | If blocking |
| Gaps | No | If blocks moment | Yes | If missing doc |
| Temporal | Yes | Yes | No | No |

```python
def should_include_section(section, intention_type):
    SECTION_MATRIX = {
        IntentionType.SUMMARIZE: {'response', 'path', 'temporal', 'tensions'},
        IntentionType.FIND_NEXT: {'response', 'path', 'temporal', 'gaps'},
        IntentionType.VERIFY: {'response', 'path', 'tensions', 'gaps'},
        IntentionType.RETRIEVE: {'response', 'path', 'gaps'},
        IntentionType.EXPLORE: {'response', 'path', 'tensions', 'convergences', 'gaps'},
    }
    return section in SECTION_MATRIX.get(intention_type, set())
```

---

## ALGORITHM: Render Cluster (v1.9.2)

Unified rendering for response and crystallizing scenarios.

### Modes

| Mode | Purpose | Output Format |
|------|---------|---------------|
| `response` | Present exploration results | Tree with markers and content blocks |
| `crystallize` | Generate narrative content | Prose with unfolded synthesis |
| `compact` | Simple path description | "A → B → C → focus" |

### Response Mode

```python
async def render_cluster(path, focus_node, graph, mode='response'):
    # Build tree from path (start → focus)
    lines = ["### Path", "", "```"]

    for node in ordered_nodes:
        marker = "  ◆ RESPONSE" if is_focus else ""
        lines.append(f"{node.synthesis}{marker}")

        # Content block
        if node.content:
            lines.extend(["```", node.content, "```"])

        # Link to next
        if connecting_link:
            lines.extend(["  │", f"  └─ {link.synthesis}", "     │", "     ▼"])

    lines.append("```")
    return "\n".join(lines)
```

### Crystallize Mode

```python
async def render_cluster(path, focus_node, graph, mode='crystallize', lang='en'):
    lines = []

    for i, node in enumerate(ordered_nodes):
        if i == 0:
            # First node - unfold with full prose
            lines.append(unfold_node_synthesis(node, lang=lang))
        else:
            # Link → target unfolding
            lines.append(unfold_link_synthesis(link, target_name=node.name, lang=lang))

        # Quote content
        if node.content:
            lines.append(f"> {node.content}")

    return "\n".join(lines)
```

### Compact Mode

```python
async def render_cluster(path, focus_node, graph, mode='compact'):
    path_names = [n.name for n in nodes]
    if len(path_names) > 3:
        return f"{path_names[0]} → ... → {path_names[-1]} → {focus_name}"
    return " → ".join(path_names) + f" → {focus_name}"
```

---

## Related Documents

- PATTERNS_Cluster_Presentation.md — Design patterns
- IMPLEMENTATION_Cluster_Presentation.md — Code locations
- runtime/physics/cluster_presentation.py — Implementation
