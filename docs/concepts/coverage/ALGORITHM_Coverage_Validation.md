# ALGORITHM: Coverage Validation System
@mind:id: ALGORITHM.COVERAGE.VALIDATION.SYSTEM

```
STATUS: DESIGNING
PURPOSE: Pseudocode for coverage validation
```

---

## Main Algorithm

```python
def validate_coverage(spec_path: str) -> CoverageResult:
    """
    Main entry point for coverage validation.
    Returns CoverageResult with gaps and coverage percentage.
    """

    # 1. Load specification
    spec = load_yaml(spec_path)
    if not spec:
        return CoverageResult(error="Failed to load spec")

    gaps = []

    # 2. Build indices for lookup
    skills_index = {s.id: s for s in spec.skills}
    protocols_index = {p.name: p for p in spec.protocols}

    # 3. Validate detection → skill mapping
    for detection in spec.doctor_workflow.detections:
        if detection.skill not in skills_index:
            gaps.append(Gap(
                layer="detection",
                id=detection.id,
                missing=detection.skill,
                message=f"Detection {detection.id} references unknown skill {detection.skill}"
            ))

    # 4. Validate skill → protocol mapping
    for skill_id, skill in skills_index.items():
        for protocol_name in skill.protocols:
            if protocol_name not in protocols_index:
                gaps.append(Gap(
                    layer="skill",
                    id=skill_id,
                    missing=protocol_name,
                    message=f"Skill {skill_id} references unknown protocol {protocol_name}"
                ))

    # 5. Validate protocol files exist
    for protocol_name, protocol in protocols_index.items():
        if not file_exists(protocol.file):
            gaps.append(Gap(
                layer="protocol",
                id=protocol_name,
                missing=protocol.file,
                message=f"Protocol {protocol_name} file missing: {protocol.file}"
            ))
        else:
            # 6. Validate protocol completeness
            completeness_gaps = validate_protocol_completeness(protocol)
            gaps.extend(completeness_gaps)

    # 7. Check for circular calls
    circular_gaps = detect_circular_calls(protocols_index)
    gaps.extend(circular_gaps)

    # 8. Calculate coverage
    total_paths = len(spec.doctor_workflow.detections)
    complete_paths = total_paths - count_blocking_gaps(gaps)
    coverage_pct = (complete_paths / total_paths * 100) if total_paths > 0 else 0

    return CoverageResult(
        gaps=gaps,
        coverage_percentage=coverage_pct,
        total_detections=total_paths,
        complete_paths=complete_paths
    )
```

---

## Protocol Completeness Check

```python
def validate_protocol_completeness(protocol: Protocol) -> List[Gap]:
    """
    Check that a protocol has required step types.
    Minimum: at least one 'ask' and one 'create'.
    """
    gaps = []

    # Load and parse protocol file
    protocol_yaml = load_yaml(protocol.file)
    if not protocol_yaml:
        return [Gap(
            layer="protocol",
            id=protocol.name,
            missing="valid YAML",
            message=f"Protocol {protocol.name} has invalid YAML"
        )]

    steps = protocol_yaml.get("steps", {})
    step_types = {step.get("type") for step in steps.values()}

    # Check required step types
    required_types = {"ask", "create"}
    missing_types = required_types - step_types

    for missing_type in missing_types:
        gaps.append(Gap(
            layer="protocol_completeness",
            id=protocol.name,
            missing=missing_type,
            message=f"Protocol {protocol.name} missing required step type: {missing_type}"
        ))

    # Check output section
    output = protocol_yaml.get("output", {})
    if not output.get("cluster", {}).get("nodes"):
        gaps.append(Gap(
            layer="protocol_completeness",
            id=protocol.name,
            missing="output.cluster.nodes",
            message=f"Protocol {protocol.name} missing output node definitions"
        ))

    return gaps
```

---

## Circular Dependency Detection

```python
def detect_circular_calls(protocols: Dict[str, Protocol]) -> List[Gap]:
    """
    Build call graph and detect cycles using DFS.
    """
    gaps = []

    # Build adjacency list
    call_graph = {}
    for name, protocol in protocols.items():
        protocol_yaml = load_yaml(protocol.file)
        if not protocol_yaml:
            continue

        calls = []
        for step in protocol_yaml.get("steps", {}).values():
            if step.get("type") == "call_protocol":
                calls.append(step.get("protocol"))
            # Also check branch actions
            for check in step.get("checks", []):
                action = check.get("action", {})
                if action.get("type") == "call_protocol":
                    calls.append(action.get("protocol"))

        call_graph[name] = calls

    # DFS for cycle detection
    visited = set()
    rec_stack = set()

    def dfs(node, path):
        if node in rec_stack:
            cycle = path[path.index(node):] + [node]
            return cycle
        if node in visited:
            return None

        visited.add(node)
        rec_stack.add(node)

        for neighbor in call_graph.get(node, []):
            cycle = dfs(neighbor, path + [node])
            if cycle:
                return cycle

        rec_stack.remove(node)
        return None

    for protocol_name in call_graph:
        if protocol_name not in visited:
            cycle = dfs(protocol_name, [])
            if cycle:
                gaps.append(Gap(
                    layer="circular_dependency",
                    id=protocol_name,
                    missing="acyclic calls",
                    message=f"Circular dependency: {' → '.join(cycle)}"
                ))

    return gaps
```

---

## Report Generation

```python
def generate_report(result: CoverageResult, output_path: str) -> None:
    """
    Generate markdown coverage report.
    """

    report = f"""# Coverage Validation Report

Generated: {datetime.now().isoformat()}

## Summary

| Metric | Value |
|--------|-------|
| Total Detections | {result.total_detections} |
| Complete Paths | {result.complete_paths} |
| Coverage | {result.coverage_percentage:.1f}% |
| Gaps | {len(result.gaps)} |

## Status

{"✅ **PASS** - All paths complete" if not result.gaps else "❌ **FAIL** - Gaps found"}

"""

    if result.gaps:
        report += "## Gaps\n\n"

        # Group by layer
        by_layer = group_by(result.gaps, key=lambda g: g.layer)

        for layer, layer_gaps in by_layer.items():
            report += f"### {layer.title()}\n\n"
            for gap in layer_gaps:
                report += f"- **{gap.id}**: {gap.message}\n"
            report += "\n"

    report += """## Coverage Matrix

| Detection | Skill | Protocol(s) | Status |
|-----------|-------|-------------|--------|
"""

    # Add matrix rows...

    write_file(output_path, report)
```

---

## Data Structures

```python
@dataclass
class Gap:
    layer: str           # detection | skill | protocol | protocol_completeness | circular_dependency
    id: str              # ID of the item with the gap
    missing: str         # What's missing
    message: str         # Human-readable description

@dataclass
class CoverageResult:
    gaps: List[Gap]
    coverage_percentage: float
    total_detections: int
    complete_paths: int
    error: Optional[str] = None

@dataclass
class Detection:
    id: str              # D-UNDOC-CODE
    trigger: str         # "Undocumented code directory"
    skill: str           # mind.create_module_docs

@dataclass
class Skill:
    id: str              # mind.create_module_docs
    file: str            # SKILL_Create_Module_Documentation_Chain...
    protocols: List[str] # [explore_space, create_doc_chain]

@dataclass
class Protocol:
    name: str            # explore_space
    file: str            # protocols/explore_space.yaml
    required_steps: List[str]
    output_nodes: List[str]
    output_links: List[str]
```

---

## CHAIN

- **Prev:** BEHAVIORS_Coverage_Validation.md
- **Next:** VALIDATION_Coverage_Validation.md
