"""
Doctor Graph Operations — Issue and Task Narrative Node Management

Creates, updates, and traverses issue/task narrative nodes in the graph.
Follows canonical schema v1.8.1:
- Issues, Objectives, Tasks are Narrative nodes with type attribute
- Modules are Space nodes
- Files are Thing nodes
- Links use single 'linked' type with semantic axes (hierarchy, polarity, permanence)

Flow:
1. Surface issues from checks → create Narrative nodes (type: problem)
2. Traverse up from issues → find Narrative nodes (type: objective)
3. Create Narrative nodes (type: task) grouping issues

DOCS: docs/mcp-design/doctor/ALGORITHM_Project_Health_Doctor.md
"""

import hashlib
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple


# =============================================================================
# SCHEMA-ALIGNED ENUMS
# =============================================================================

class NodeType(Enum):
    """Canonical node types from schema v1.2."""
    ACTOR = "actor"
    SPACE = "space"
    THING = "thing"
    NARRATIVE = "narrative"
    MOMENT = "moment"


class NarrativeSubtype(Enum):
    """Narrative type values for doctor system."""
    PROBLEM = "problem"
    OBJECTIVE = "objective"
    TASK = "task"
    PATTERN = "pattern"
    VALIDATION = "validation"


class TraversalOutcome(Enum):
    """Result of traversing from issue up to objective."""
    SERVE = "serve"              # Found objective → normal task
    RECONSTRUCT = "reconstruct"  # Missing nodes in chain → rebuild
    TRIAGE = "triage"            # No objective defined → evaluate usefulness


# =============================================================================
# SCHEMA-ALIGNED NODE STRUCTURES
# =============================================================================

@dataclass
class GraphNode:
    """Base node following schema v1.6 NodeBase."""
    id: str
    name: str
    node_type: str              # actor, space, thing, narrative, moment
    type: str                   # Subtype within node_type (free string)
    description: str = ""

    # Physics
    weight: float = 1.0         # Importance/inertia (unbounded)
    energy: float = 0.0         # Instantaneous activation (unbounded)

    # Semantics
    synthesis: str = ""         # French synthesis phrase
    embedding: Optional[List[float]] = None  # Vector embedding
    content: Optional[str] = None  # Full content (for narratives)

    # Temporal
    created_at_s: int = 0
    updated_at_s: int = 0
    last_traversed_at_s: Optional[int] = None

    # Extended fields (stored in properties for flexibility)
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        now = int(time.time())
        if not self.created_at_s:
            self.created_at_s = now
        if not self.updated_at_s:
            self.updated_at_s = now


@dataclass
class NarrativeNode(GraphNode):
    """Narrative node (issue, objective, task, pattern, etc.)."""

    def __post_init__(self):
        self.node_type = NodeType.NARRATIVE.value
        super().__post_init__()


@dataclass
class SpaceNode(GraphNode):
    """Space node for modules/containers."""

    def __post_init__(self):
        self.node_type = NodeType.SPACE.value
        super().__post_init__()


@dataclass
class ThingNode(GraphNode):
    """Thing node for files/artifacts."""
    uri: str = ""  # File path, URL, etc.

    def __post_init__(self):
        self.node_type = NodeType.THING.value
        super().__post_init__()


@dataclass
class GraphLink:
    """Link following schema v1.8.1 LinkBase.

    Single link type 'linked' — all semantics encoded in properties:
        - hierarchy: -1 (contains) to +1 (elaborates)
        - polarity: [a→b, b→a] directional flow strength
        - permanence: 0 (speculative) to 1 (definitive)
        - 4 Plutchik emotion axes
        - synthesis: natural language description
    """
    id: str
    node_a: str                 # First endpoint
    node_b: str                 # Second endpoint

    # Physics
    weight: float = 1.0
    energy: float = 0.0

    # Semantic Axes
    polarity: List[float] = field(default_factory=lambda: [0.5, 0.5])  # [a→b, b→a]
    hierarchy: float = 0.0      # -1 (contains) to +1 (elaborates)
    permanence: float = 0.5     # 0 (speculative) to 1 (definitive)

    # Emotions (Plutchik pairs, -1 to +1)
    joy_sadness: float = 0.0
    trust_disgust: float = 0.0
    fear_anger: float = 0.0
    surprise_anticipation: float = 0.0

    # Semantics
    synthesis: str = "is linked to"  # Natural language description
    embedding: Optional[List[float]] = None

    # Temporal
    created_at_s: int = 0
    updated_at_s: int = 0
    last_traversed_at_s: Optional[int] = None

    def __post_init__(self):
        now = int(time.time())
        if not self.created_at_s:
            self.created_at_s = now
        if not self.updated_at_s:
            self.updated_at_s = now
        if not self.id:
            self.id = f"link_{self.node_a}_{self.node_b}_{now}"


# =============================================================================
# ISSUE NARRATIVE NODE
# =============================================================================

@dataclass
class IssueNarrative(NarrativeNode):
    """
    Narrative node with type='problem'.

    Represents an atomic problem detected by doctor.
    """
    task_type: str = ""          # MONOLITH, STALE_SYNC, etc.
    severity: str = "warning"     # critical, warning, info
    status: str = "open"          # open, resolved, in_progress
    module: str = ""              # Module ID (Space it belongs to)
    path: str = ""                # File/dir path
    message: str = ""             # Human description
    detected_at: str = ""
    resolved_at: Optional[str] = None

    def __post_init__(self):
        self.type = NarrativeSubtype.PROBLEM.value
        if not self.detected_at:
            self.detected_at = datetime.now().isoformat()
        super().__post_init__()
        # Map severity to energy (higher severity = more energy)
        self.energy = {"critical": 1.0, "warning": 0.5, "info": 0.2}.get(self.severity, 0.3)


@dataclass
class ObjectiveNarrative(NarrativeNode):
    """
    Narrative node with type='objective'.

    Represents a goal for a module.
    """
    objective_type: str = ""      # documented, maintainable, tested, etc.
    module: str = ""              # Module ID (Space it belongs to)
    status: str = "open"          # open, achieved, deferred, deprecated
    criteria: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.type = NarrativeSubtype.OBJECTIVE.value
        super().__post_init__()


@dataclass
class TaskNarrative(NarrativeNode):
    """
    Narrative node with type='task'.

    Groups issues serving an objective.
    """
    task_type: str = "serve"      # serve, reconstruct, triage
    objective_id: Optional[str] = None
    module: str = ""
    skill: str = ""               # Skill to resolve this task
    status: str = "open"          # open, in_progress, completed
    issue_ids: List[str] = field(default_factory=list)
    missing_nodes: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.type = NarrativeSubtype.TASK.value
        super().__post_init__()


@dataclass
class TraversalResult:
    """Result of traversing from issue to objective."""
    outcome: TraversalOutcome
    objective: Optional[ObjectiveNarrative] = None
    space_id: Optional[str] = None
    missing_nodes: List[str] = field(default_factory=list)
    path: List[str] = field(default_factory=list)


# =============================================================================
# ID GENERATION
# =============================================================================
#
# Convention:
#   {node-type}_{SUBTYPE}_{instance-context}_{disambiguator}
#
# - node-type: lowercase (low info, you already know it)
# - SUBTYPE: ALLCAPS (high info, what you scan for)
# - instance-context: lowercase, `-` between words (which one)
# - disambiguator: lowercase 2-char hash or index (collision safety)
#
# Examples:
#   narrative_PROBLEM_monolith-engine-physics-graph-ops_a7
#   narrative_TASK_serve-engine-physics-documented_01
#   narrative_OBJECTIVE_engine-physics-documented
#   space_MODULE_engine-physics
#   thing_FILE_engine-physics-graph-ops-py
#   moment_TICK_1000_a7
#


def _clean_for_id(s: str) -> str:
    """Clean string for use in ID: lowercase, replace _ and / with -."""
    return s.lower().replace("_", "-").replace("/", "-").replace(" ", "-")


def generate_space_id(module: str, space_type: str = "MODULE") -> str:
    """Generate space ID.

    Format: space_{SUBTYPE}_{instance}
    Example: space_MODULE_engine-physics
    """
    clean_module = _clean_for_id(module)
    return f"space_{space_type.upper()}_{clean_module}"


def slugify(text: str) -> str:
    """Convert text to URL-safe slug.

    Matches symbol_extractor.py format for consistent thing IDs.
    """
    # Replace path separators and special chars with hyphens
    slug = re.sub(r'[/\\._]', '-', text)
    # Remove non-alphanumeric except hyphens
    slug = re.sub(r'[^a-zA-Z0-9-]', '', slug)
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    return slug.strip('-').lower()


def generate_thing_id(path: str, thing_type: str = "FILE") -> str:
    """Generate thing ID for a file/artifact.

    Uses same format as symbol_extractor.py for consistent IDs.

    Format: thing_{SUBTYPE}_{slugified_path}
    Example: thing_FILE_engine-physics-graph-ops-py
    """
    file_slug = slugify(path)
    return f"thing_{thing_type.upper()}_{file_slug}"


def generate_actor_id(name: str, actor_type: str = "AGENT") -> str:
    """Generate actor ID.

    Format: actor_{SUBTYPE}_{instance}
    Example: actor_AGENT_claude
    """
    clean_name = _clean_for_id(name)
    return f"actor_{actor_type.upper()}_{clean_name}"


def generate_issue_id(task_type: str, module: str, path: str) -> str:
    """Generate issue narrative ID.

    Format: narrative_PROBLEM_{issue-type}-{module}-{file}_{hash}
    Example: narrative_PROBLEM_monolith-engine-physics-graph-ops_a7
    """
    file_stem = Path(path).stem if path else "root"
    clean_type = _clean_for_id(task_type)
    clean_module = _clean_for_id(module)
    clean_file = _clean_for_id(file_stem)

    # Build context: type-module-file
    context = f"{clean_type}-{clean_module}-{clean_file}"

    hash_input = f"{task_type}:{module}:{path}"
    short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:2]

    return f"narrative_PROBLEM_{context}_{short_hash}"


def generate_objective_id(objective_type: str, module: str) -> str:
    """Generate objective narrative ID.

    Format: narrative_OBJECTIVE_{module}-{type}
    Example: narrative_OBJECTIVE_engine-physics-documented
    """
    clean_module = _clean_for_id(module)
    clean_type = _clean_for_id(objective_type)
    return f"narrative_OBJECTIVE_{clean_module}-{clean_type}"


def generate_task_id(task_type: str, module: str, objective_type: str = "", index: int = 1) -> str:
    """Generate task narrative ID.

    Format: narrative_TASK_{task-type}-{module}-{objective}_{index}
    Example: narrative_TASK_serve-engine-physics-documented_01
    """
    clean_task = _clean_for_id(task_type)
    clean_module = _clean_for_id(module)

    if objective_type:
        clean_obj = _clean_for_id(objective_type)
        context = f"{clean_task}-{clean_module}-{clean_obj}"
    else:
        context = f"{clean_task}-{clean_module}"

    return f"narrative_TASK_{context}_{index:02d}"


def generate_moment_id(moment_type: str, context: str, tick: int = 0) -> str:
    """Generate moment ID.

    Format: moment_{SUBTYPE}_{context}_{hash}
    Example: moment_TICK_1000_a7
             moment_EXPLORATION_physics-state_x8
    """
    if tick > 0:
        return f"moment_{moment_type.upper()}_{tick}_{hashlib.md5(context.encode()).hexdigest()[:2]}"

    clean_context = _clean_for_id(context)
    short_hash = hashlib.md5(f"{moment_type}:{context}".encode()).hexdigest()[:2]
    return f"moment_{moment_type.upper()}_{clean_context}_{short_hash}"


def generate_link_id(link_type: str, from_id: str, to_id: str, semantic_name: str = "") -> str:
    """Generate link ID.

    Format: {link-type}_{SEMANTIC}_{from-short}_TO_{to-short}
    Example: relates_BLOCKS_narrative-issue-a7_TO_narrative-objective-b3
    """
    # Extract short form from node IDs (last two parts)
    from_parts = from_id.split("_")
    to_parts = to_id.split("_")
    from_short = "-".join(from_parts[-2:]) if len(from_parts) >= 2 else from_id
    to_short = "-".join(to_parts[-2:]) if len(to_parts) >= 2 else to_id

    if semantic_name:
        return f"{link_type.lower()}_{semantic_name.upper()}_{from_short}_TO_{to_short}"
    return f"{link_type.lower()}_{from_short}_TO_{to_short}"


# =============================================================================
# SYNTHESIS & EMBEDDING GENERATION
# =============================================================================
#
# Uses proper synthesis from engine/physics/synthesis.py
# Uses proper embeddings from engine/infrastructure/embeddings/service.py
#

def _get_synthesis_module():
    """Lazy load synthesis module."""
    try:
        from runtime.physics import synthesis
        return synthesis
    except ImportError:
        return None


def synthesize_link_physics(link: "GraphLink") -> str:
    """
    Generate synthesis from link physics using engine/physics/synthesis.py.

    Falls back to simple generation if synthesis module unavailable.
    """
    synth = _get_synthesis_module()
    if synth:
        # Use proper synthesis from physics module
        return synth.synthesize_from_dict({
            "polarity": link.polarity,
            "hierarchy": link.hierarchy,
            "permanence": link.permanence,
            "energy": link.energy,
            "weight": link.weight,
            "fear_anger": link.fear_anger,
            "trust_disgust": link.trust_disgust,
            "joy_sadness": link.joy_sadness,
            "surprise_anticipation": link.surprise_anticipation,
        })

    # Fallback: simple generation
    return _simple_link_synthesis(link)


def _simple_link_synthesis(link: "GraphLink") -> str:
    """Simple fallback synthesis for links."""
    # Use synthesis or derive base verb from hierarchy
    base = link.synthesis if link.synthesis else (
        "contains" if link.hierarchy < -0.5 else
        "elaborates" if link.hierarchy > 0.5 else
        "is linked to"
    )

    prefix = "clearly" if link.permanence > 0.6 else "probably" if link.permanence > 0.3 else "perhaps"

    suffix = ""
    if link.trust_disgust < -0.4:
        suffix = ", with distrust"
    elif link.trust_disgust > 0.4:
        suffix = ", with confidence"

    return f"{prefix} {base}{suffix}"


def synthesize_node_content(node: "GraphNode") -> str:
    """
    Generate synthesis text for a node based on its type and content.

    Uses node name, description, and type to create embeddable text.
    """
    parts = [node.name]

    if node.description:
        parts.append(node.description)

    # Add type-specific context
    if node.node_type == NodeType.NARRATIVE.value:
        if hasattr(node, 'task_type'):
            parts.append(f"issue: {node.task_type}")
        elif hasattr(node, 'objective_type'):
            parts.append(f"objective: {node.objective_type}")
        elif hasattr(node, 'task_type'):
            parts.append(f"task: {node.task_type}")
    elif node.node_type == NodeType.SPACE.value:
        parts.append(f"{node.type} container")
    elif node.node_type == NodeType.THING.value:
        if hasattr(node, 'uri'):
            parts.append(f"file: {node.uri}")

    if node.content:
        parts.append(node.content[:200])  # Truncate

    return ". ".join(p for p in parts if p)


# =============================================================================
# NODE SYNTHESIS GENERATORS (English)
# =============================================================================

def generate_issue_synthesis(task_type: str, severity: str) -> str:
    """Generate synthesis for an issue narrative node."""
    severity_prefix = {
        "critical": "critical",
        "warning": "notable",
        "info": "minor",
    }.get(severity, "notable")

    issue_verb = {
        "UNDOCUMENTED": "lacks documentation",
        "INCOMPLETE_CHAIN": "has incomplete doc chain",
        "STALE_SYNC": "needs sync update",
        "MONOLITH": "is too large",
        "STUB_IMPL": "contains stub code",
        "MISSING_TESTS": "lacks tests",
        "HEALTH_FAILED": "has health failure",
        "PLACEHOLDER": "contains placeholders",
        "BROKEN_IMPL_LINK": "has broken link",
    }.get(task_type, f"has {task_type.lower().replace('_', ' ')} issue")

    return f"{severity_prefix} issue: {issue_verb}"


def generate_objective_synthesis(objective_type: str) -> str:
    """Generate synthesis for an objective narrative node."""
    objective_desc = {
        "documented": "aims for complete documentation",
        "synced": "aims for doc-code synchronization",
        "maintainable": "aims for code maintainability",
        "tested": "aims for test coverage",
        "healthy": "aims for passing health checks",
        "secure": "aims for security compliance",
        "resolved": "aims for resolved issues",
    }.get(objective_type, f"aims for {objective_type} status")

    return f"objective: {objective_desc}"


def generate_task_synthesis(task_type: str) -> str:
    """Generate synthesis for a task narrative node."""
    task_desc = {
        "serve": "serves objective by resolving issues",
        "reconstruct": "rebuilds missing documentation chain",
        "triage": "evaluates orphan code for disposition",
    }.get(task_type, f"{task_type} work task")

    return f"task: {task_desc}"


def generate_space_synthesis(space_type: str, module_name: str) -> str:
    """Generate synthesis for a space node."""
    type_desc = {
        "MODULE": "module container",
        "AREA": "area grouping",
        "module": "module container",
        "area": "area grouping",
    }.get(space_type, "space container")

    return f"{module_name}: {type_desc}"


def generate_thing_synthesis(filename: str) -> str:
    """Generate synthesis for a thing node."""
    # Infer file type from extension
    ext = Path(filename).suffix.lower()
    file_desc = {
        ".py": "Python source file",
        ".ts": "TypeScript source file",
        ".tsx": "TypeScript React component",
        ".js": "JavaScript source file",
        ".jsx": "JavaScript React component",
        ".md": "Markdown documentation",
        ".yaml": "YAML configuration",
        ".yml": "YAML configuration",
        ".json": "JSON data file",
        ".css": "CSS stylesheet",
        ".html": "HTML template",
    }.get(ext, "source file")

    return f"{filename}: {file_desc}"


# =============================================================================
# FIELD FILLING (preserve existing, fill missing)
# =============================================================================

# Lazy-loaded embedding service
_embedding_service = None


def _get_embedding_service():
    """Lazy load embedding service from engine/infrastructure/embeddings/service.py."""
    global _embedding_service
    if _embedding_service is None:
        try:
            from runtime.infrastructure.embeddings.service import get_embedding_service
            _embedding_service = get_embedding_service()
        except ImportError:
            _embedding_service = False  # Mark as unavailable
    return _embedding_service if _embedding_service else None


def _generate_node_embedding(node: GraphNode) -> Optional[List[float]]:
    """
    Generate embedding for a node using engine/infrastructure/embeddings/service.py.

    Uses EmbeddingService.embed_node() if available, falls back to embed().
    """
    service = _get_embedding_service()
    if not service:
        return None

    # Try to use embed_node if available (for proper type-based embedding)
    node_dict = {
        "type": node.type,
        "name": node.name,
        "content": node.content or "",
        "description": node.description or "",
    }

    # Add type-specific fields
    if hasattr(node, 'uri'):
        node_dict["uri"] = node.uri
    if hasattr(node, 'task_type'):
        node_dict["task_type"] = node.task_type
    if hasattr(node, 'objective_type'):
        node_dict["objective_type"] = node.objective_type

    try:
        return service.embed_node(node_dict)
    except (AttributeError, TypeError):
        # Fallback: use synthesize_node_content + embed
        embed_text = synthesize_node_content(node)
        if embed_text:
            return service.embed(embed_text)
    return None


def _generate_link_embedding(link: GraphLink, store: "DoctorGraphStore") -> Optional[List[float]]:
    """
    Generate embedding for a link using engine/infrastructure/embeddings/service.py.

    Uses synthesis text for embedding.
    """
    service = _get_embedding_service()
    if not service:
        return None

    # Build embed text from synthesis and node names
    node_a = store.get_node(link.node_a)
    node_b = store.get_node(link.node_b)
    a_name = node_a.name if node_a else link.node_a
    b_name = node_b.name if node_b else link.node_b

    embed_text = f"{a_name} {link.synthesis} {b_name}"
    if embed_text:
        return service.embed(embed_text)
    return None


# Node type -> default physics values
NODE_PHYSICS_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "issue": {"weight": 2.0, "energy": 3.0},
    "objective": {"weight": 3.0, "energy": 2.0},
    "task": {"weight": 2.0, "energy": 4.0},
    "area": {"weight": 3.0, "energy": 1.0},
    "module": {"weight": 2.0, "energy": 1.0},
    "file": {"weight": 1.0, "energy": 0.5},
}


def fill_missing_node_fields(node: GraphNode) -> bool:
    """
    Fill missing fields on a node. Returns True if any field was modified.

    Only sets defaults for fields that are null/0/empty.
    Never overwrites existing values.
    """
    modified = False

    # Get defaults based on node type
    defaults = NODE_PHYSICS_DEFAULTS.get(node.type, {"weight": 1.0, "energy": 1.0})

    # Fill physics if zero (default)
    if node.weight == 1.0 and node.type in NODE_PHYSICS_DEFAULTS:
        node.weight = defaults["weight"]
        modified = True
    if node.energy == 0.0:
        node.energy = defaults["energy"]
        modified = True

    # Fill synthesis if empty
    if not node.synthesis:
        if node.node_type == NodeType.NARRATIVE.value:
            if node.type == NarrativeSubtype.PROBLEM.value and hasattr(node, 'task_type'):
                severity = getattr(node, 'severity', 'warning')
                node.synthesis = generate_issue_synthesis(node.task_type, severity)
            elif node.type == NarrativeSubtype.OBJECTIVE.value and hasattr(node, 'objective_type'):
                node.synthesis = generate_objective_synthesis(node.objective_type)
            elif node.type == NarrativeSubtype.TASK.value and hasattr(node, 'task_type'):
                node.synthesis = generate_task_synthesis(node.task_type)
        elif node.node_type == NodeType.SPACE.value:
            node.synthesis = generate_space_synthesis(node.type, node.name)
        elif node.node_type == NodeType.THING.value:
            node.synthesis = generate_thing_synthesis(node.name)
        if node.synthesis:
            modified = True

    # Note: Embeddings are NOT generated here.
    # They are batched via embed_pending() for performance.

    return modified


# Link semantic name -> default physics values
LINK_PHYSICS_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "contains": {
        "weight": 1.0, "energy": 0.5,
        "polarity": [0.6, 0.4], "hierarchy": -0.7, "permanence": 1.0,
        "joy_sadness": 0.0, "trust_disgust": 0.0, "fear_anger": 0.0, "surprise_anticipation": 0.0,
    },
    "blocks": {
        "weight": 2.0, "energy": 3.0,
        "polarity": [0.9, 0.1], "hierarchy": 0.0, "permanence": 0.7,
        "joy_sadness": -0.3, "trust_disgust": -0.4, "fear_anger": 0.3, "surprise_anticipation": 0.0,
    },
    "serves": {
        "weight": 2.0, "energy": 2.5,
        "polarity": [0.85, 0.15], "hierarchy": 0.5, "permanence": 0.6,
        "joy_sadness": 0.2, "trust_disgust": 0.4, "fear_anger": 0.0, "surprise_anticipation": 0.3,
    },
    "includes": {
        "weight": 1.5, "energy": 2.0,
        "polarity": [0.7, 0.3], "hierarchy": -0.5, "permanence": 0.8,
        "joy_sadness": 0.0, "trust_disgust": 0.0, "fear_anger": 0.0, "surprise_anticipation": 0.0,
    },
    "about": {
        "weight": 1.5, "energy": 2.0,
        "polarity": [0.8, 0.2], "hierarchy": 0.3, "permanence": 0.9,
        "joy_sadness": 0.0, "trust_disgust": -0.3, "fear_anger": 0.0, "surprise_anticipation": 0.0,
    },
}


def fill_missing_link_fields(link: GraphLink, store: "DoctorGraphStore") -> bool:
    """
    Fill missing fields on a link. Returns True if any field was modified.

    Only sets defaults for fields that are null/0/empty.
    Never overwrites existing values.
    """
    modified = False

    # Get defaults based on link synthesis
    defaults = LINK_PHYSICS_DEFAULTS.get(link.synthesis, {
        "weight": 1.0, "energy": 1.0,
        "polarity": [0.5, 0.5], "hierarchy": 0.0, "permanence": 0.5,
        "joy_sadness": 0.0, "trust_disgust": 0.0, "fear_anger": 0.0, "surprise_anticipation": 0.0,
    })

    # Fill physics if at defaults
    if link.weight == 1.0 and defaults.get("weight", 1.0) != 1.0:
        link.weight = defaults["weight"]
        modified = True
    if link.energy == 0.0:
        link.energy = defaults.get("energy", 1.0)
        modified = True

    # Fill semantic axes if at defaults
    if link.polarity == [0.5, 0.5] and defaults.get("polarity") != [0.5, 0.5]:
        link.polarity = defaults.get("polarity", [0.5, 0.5])
        modified = True
    if link.hierarchy == 0.0 and defaults.get("hierarchy", 0.0) != 0.0:
        link.hierarchy = defaults.get("hierarchy", 0.0)
        modified = True
    if link.permanence == 0.5 and defaults.get("permanence", 0.5) != 0.5:
        link.permanence = defaults.get("permanence", 0.5)
        modified = True

    # Fill emotions if at zero
    if link.joy_sadness == 0.0 and defaults.get("joy_sadness", 0.0) != 0.0:
        link.joy_sadness = defaults.get("joy_sadness", 0.0)
        modified = True
    if link.trust_disgust == 0.0 and defaults.get("trust_disgust", 0.0) != 0.0:
        link.trust_disgust = defaults.get("trust_disgust", 0.0)
        modified = True
    if link.fear_anger == 0.0 and defaults.get("fear_anger", 0.0) != 0.0:
        link.fear_anger = defaults.get("fear_anger", 0.0)
        modified = True
    if link.surprise_anticipation == 0.0 and defaults.get("surprise_anticipation", 0.0) != 0.0:
        link.surprise_anticipation = defaults.get("surprise_anticipation", 0.0)
        modified = True

    # Fill synthesis if empty - use proper physics-based synthesis
    if not link.synthesis:
        link.synthesis = synthesize_link_physics(link)
        if link.synthesis:
            modified = True

    # Note: Embeddings are NOT generated here.
    # They are batched via embed_pending() for performance.

    return modified


# =============================================================================
# ISSUE TYPE → OBJECTIVE TYPE MAPPING
# =============================================================================

ISSUE_BLOCKS_OBJECTIVE: Dict[str, List[str]] = {
    # Documentation issues → documented
    "UNDOCUMENTED": ["documented"],
    "INCOMPLETE_CHAIN": ["documented"],
    "PLACEHOLDER": ["documented"],
    "DOC_TEMPLATE_DRIFT": ["documented"],
    "NO_DOCS_REF": ["documented"],
    "BROKEN_IMPL_LINK": ["documented"],
    "ORPHAN_DOCS": ["documented"],
    "NON_STANDARD_DOC_TYPE": ["documented"],
    "DOC_DUPLICATION": ["documented"],
    "UNDOC_IMPL": ["documented"],
    "NEW_UNDOC_CODE": ["documented"],
    "HOOK_UNDOC": ["documented"],
    "DOC_LINK_INTEGRITY": ["documented"],

    # Sync issues → synced
    "STALE_SYNC": ["synced"],
    "STALE_IMPL": ["synced"],
    "CODE_DOC_DELTA_COUPLING": ["synced"],
    "DOC_GAPS": ["synced"],

    # Code quality issues → maintainable
    "MONOLITH": ["maintainable"],
    "STUB_IMPL": ["maintainable"],
    "INCOMPLETE_IMPL": ["maintainable"],
    "NAMING_CONVENTION": ["maintainable"],
    "MAGIC_VALUES": ["maintainable"],
    "HARDCODED_CONFIG": ["maintainable"],
    "LONG_PROMPT": ["maintainable"],
    "LONG_SQL": ["maintainable"],
    "LEGACY_MARKER": ["maintainable"],
    "PROMPT_DOC_REFERENCE": ["maintainable"],
    "PROMPT_VIEW_TABLE": ["maintainable"],
    "PROMPT_CHECKLIST": ["maintainable"],

    # Test issues → tested
    "MISSING_TESTS": ["tested"],
    "TEST_FAILED": ["tested"],
    "TEST_ERROR": ["tested"],
    "TEST_TIMEOUT": ["tested"],
    "INVARIANT_UNTESTED": ["tested"],
    "TEST_NO_VALIDATES": ["tested"],

    # Health issues → healthy
    "HEALTH_FAILED": ["healthy"],
    "INVARIANT_VIOLATED": ["healthy"],
    "INVARIANT_NO_TEST": ["healthy"],
    "VALIDATION_BEHAVIORS_MISSING": ["healthy"],
    "CONFIG_MISSING": ["healthy"],
    "LOG_ERROR": ["healthy"],
    "MEMBRANE_NO_PROTOCOLS": ["healthy"],
    "MEMBRANE_IMPORT_ERROR": ["healthy"],
    "MEMBRANE_SESSION_INVALID": ["healthy"],
    "MEMBRANE_STEP_ORDERING": ["healthy"],
    "MEMBRANE_EMPTY_PROTOCOL": ["healthy"],
    "MEMBRANE_MISSING_FIELDS": ["healthy"],
    "MEMBRANE_INVALID_STEP": ["healthy"],
    "MEMBRANE_BRANCH_NO_CHECKS": ["healthy"],
    "MEMBRANE_YAML_ERROR": ["healthy"],
    "MEMBRANE_PARSE_ERROR": ["healthy"],

    # Review issues → resolved
    "ESCALATION": ["resolved"],
    "SUGGESTION": ["resolved"],
    "UNRESOLVED_QUESTION": ["resolved"],

    # Security issues → secure
    "HARDCODED_SECRET": ["secure"],

    # Module status
    "MODULE_INCOMPLETE": ["documented", "tested"],
    "MODULE_BLOCKED": ["resolved"],
    "YAML_DRIFT": ["documented"],
    "COMPONENT_NO_STORIES": ["documented"],
}


OBJECTIVE_TO_SKILL: Dict[str, str] = {
    "documented": "create_module_documentation",
    "synced": "update_module_sync_state",
    "maintainable": "implement_write_or_modify_code",
    "tested": "test_integrate_and_gate",
    "healthy": "health_define_and_verify",
    "resolved": "review_evaluate_changes",
    "secure": "implement_write_or_modify_code",
}


STANDARD_OBJECTIVE_TYPES = ["documented", "synced", "maintainable", "tested", "healthy", "secure", "resolved"]


# =============================================================================
# GRAPH STORE (Schema-aligned)
# =============================================================================

class DoctorGraphStore:
    """
    Graph store for doctor nodes and links.

    Follows schema v1.6:
    - Nodes have node_type (actor/space/thing/narrative/moment) and type (subtype)
    - Links use canonical types with semantic properties (role, direction)
    - Auto-fills missing physics/synthesis/embedding fields on upsert
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.links: List[GraphLink] = []
        self._links_by_from: Dict[str, List[GraphLink]] = {}
        self._links_by_to: Dict[str, List[GraphLink]] = {}
        self._pending_node_embeddings: List[str] = []  # Node IDs needing embeddings
        self._pending_link_embeddings: List[int] = []  # Link indices needing embeddings

    def upsert_node(self, node: GraphNode, fill_missing: bool = True) -> bool:
        """
        Create or update a node. Returns True if created, False if updated.

        If fill_missing=True (default), fills in missing physics/synthesis
        fields without overwriting existing values. Embeddings are deferred
        and generated in batch via embed_pending().
        """
        is_new = node.id not in self.nodes
        node.updated_at_s = int(time.time())

        # Fill missing fields (embedding handled via embed_pending batch)
        if fill_missing:
            fill_missing_node_fields(node)

        # Track nodes that need embeddings
        if node.embedding is None:
            self._pending_node_embeddings.append(node.id)

        self.nodes[node.id] = node
        return is_new

    def embed_pending(self) -> int:
        """Generate embeddings for all pending nodes in batch. Returns count embedded."""
        if not self._pending_node_embeddings:
            return 0

        service = _get_embedding_service()
        if not service:
            return 0

        # Collect texts to embed
        texts = []
        node_ids = []
        for node_id in self._pending_node_embeddings:
            node = self.nodes.get(node_id)
            if node and node.embedding is None:
                text = _node_to_embed_text(node)
                texts.append(text)
                node_ids.append(node_id)

        if not texts:
            self._pending_node_embeddings = []
            return 0

        # Batch embed
        try:
            embeddings = service.embed_batch(texts)
            for node_id, embedding in zip(node_ids, embeddings):
                if embedding and node_id in self.nodes:
                    self.nodes[node_id].embedding = embedding
            self._pending_node_embeddings = []
            return len(embeddings)
        except Exception as e:
            # Fallback to single embed if batch fails
            count = 0
            for node_id, text in zip(node_ids, texts):
                try:
                    embedding = service.embed(text)
                    if embedding and node_id in self.nodes:
                        self.nodes[node_id].embedding = embedding
                        count += 1
                except Exception:
                    pass
            self._pending_node_embeddings = []
            return count

    def embed_pending_links(self) -> int:
        """Generate embeddings for all pending links in batch. Returns count embedded."""
        if not self._pending_link_embeddings:
            return 0

        service = _get_embedding_service()
        if not service:
            return 0

        # Collect texts to embed
        texts = []
        link_indices = []
        for idx in self._pending_link_embeddings:
            if idx < len(self.links):
                link = self.links[idx]
                if link.embedding is None:
                    text = _link_to_embed_text(link, self)
                    texts.append(text)
                    link_indices.append(idx)

        if not texts:
            self._pending_link_embeddings = []
            return 0

        # Batch embed
        try:
            embeddings = service.embed_batch(texts)
            for idx, embedding in zip(link_indices, embeddings):
                if embedding and idx < len(self.links):
                    self.links[idx].embedding = embedding
            self._pending_link_embeddings = []
            return len(embeddings)
        except Exception as e:
            # Fallback to single embed if batch fails
            count = 0
            for idx, text in zip(link_indices, texts):
                try:
                    embedding = service.embed(text)
                    if embedding and idx < len(self.links):
                        self.links[idx].embedding = embedding
                        count += 1
                except Exception:
                    pass
            self._pending_link_embeddings = []
            return count

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def query_nodes(
        self,
        node_type: Optional[str] = None,
        subtype: Optional[str] = None,
        **kwargs
    ) -> List[GraphNode]:
        """Query nodes by node_type and subtype (type field)."""
        results = []
        for node in self.nodes.values():
            if node_type and node.node_type != node_type:
                continue
            if subtype and node.type != subtype:
                continue
            # Additional property filters
            match = True
            for k, v in kwargs.items():
                if hasattr(node, k) and getattr(node, k) != v:
                    match = False
                    break
            if match:
                results.append(node)
        return results

    def create_link(self, link: GraphLink, fill_missing: bool = True) -> None:
        """
        Create a link between nodes.

        If fill_missing=True (default), fills in missing physics/synthesis
        fields without overwriting existing values. Embeddings are deferred
        and generated in batch via embed_pending().
        """
        # Avoid duplicates (same endpoints + synthesis)
        for existing in self.links:
            if (existing.node_a == link.node_a and
                existing.node_b == link.node_b and
                existing.synthesis == link.synthesis):
                return

        # Fill missing fields (embedding handled via embed_pending batch)
        if fill_missing:
            fill_missing_link_fields(link, self)

        # Track links that need embeddings
        if link.embedding is None:
            self._pending_link_embeddings.append(len(self.links))

        self.links.append(link)
        self._links_by_from.setdefault(link.node_a, []).append(link)
        self._links_by_to.setdefault(link.node_b, []).append(link)

    def get_links_from(self, node_id: str, synthesis_filter: Optional[str] = None) -> List[GraphLink]:
        """Get outgoing links from a node (node_a = node_id)."""
        links = self._links_by_from.get(node_id, [])
        if synthesis_filter:
            links = [l for l in links if synthesis_filter in l.synthesis]
        return links

    def get_links_to(self, node_id: str, synthesis_filter: Optional[str] = None) -> List[GraphLink]:
        """Get incoming links to a node (node_b = node_id)."""
        links = self._links_by_to.get(node_id, [])
        if synthesis_filter:
            links = [l for l in links if synthesis_filter in l.synthesis]
        return links

    def delete_node(self, node_id: str) -> bool:
        """Delete a node and its links."""
        if node_id not in self.nodes:
            return False

        del self.nodes[node_id]

        # Remove links
        self.links = [l for l in self.links
                      if l.node_a != node_id and l.node_b != node_id]
        self._links_by_from.pop(node_id, None)
        self._links_by_to.pop(node_id, None)

        return True


# =============================================================================
# NODE CREATION HELPERS
# =============================================================================

def create_issue_node(
    task_type: str,
    severity: str,
    path: str,
    message: str,
    module: str,
    details: Optional[Dict[str, Any]] = None,
) -> IssueNarrative:
    """Create an issue narrative node with full content.

    ID format: narrative_PROBLEM_{type}-{module}-{file}_{hash}
    Example: narrative_PROBLEM_monolith-engine-physics-graph-ops_a7

    Physics defaults:
        weight: 2.0 (issues matter)
        energy: 3.0 (active problems)
    """
    issue_id = generate_issue_id(task_type, module, path)
    file_stem = Path(path).stem if path else "root"

    # Build rich content
    content_lines = [
        f"## {task_type}",
        f"",
        f"**Module:** {module}",
        f"**File:** {path}" if path else "**Scope:** module-level",
        f"**Severity:** {severity}",
        f"",
        f"### Description",
        message,
    ]

    if details:
        content_lines.extend([
            "",
            "### Details",
            "```yaml",
        ])
        for k, v in details.items():
            content_lines.append(f"{k}: {v}")
        content_lines.append("```")

    content = "\n".join(content_lines)

    # Energy scales with severity
    energy = {"critical": 4.0, "warning": 3.0, "info": 1.5}.get(severity, 3.0)

    return IssueNarrative(
        id=issue_id,
        name=f"{task_type} in {module}/{file_stem}",
        node_type=NodeType.NARRATIVE.value,
        type=NarrativeSubtype.PROBLEM.value,
        description=message,
        # Physics
        weight=2.0,
        energy=energy,
        # Semantics
        synthesis=generate_issue_synthesis(task_type, severity),
        content=content,
        # Issue-specific
        task_type=task_type,
        severity=severity,
        module=module,
        path=path,
        message=message,
        properties={"details": details or {}}
    )


def create_objective_node(objective_type: str, module: str) -> ObjectiveNarrative:
    """Create an objective narrative node with full content.

    ID format: narrative_OBJECTIVE_{module}-{type}
    Example: narrative_OBJECTIVE_engine-physics-documented

    Physics defaults:
        weight: 3.0 (objectives are important)
        energy: 2.0 (goals are stable attractors)
    """
    obj_id = generate_objective_id(objective_type, module)

    # Build rich content describing the objective
    criteria = {
        "documented": [
            "Module is mapped in modules.yaml",
            "Doc chain exists: PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC",
            "All code files have DOCS: references",
            "No placeholder content in docs",
        ],
        "synced": [
            "SYNC file updated within 14 days",
            "IMPLEMENTATION doc reflects current code",
            "No code changes without doc updates",
        ],
        "maintainable": [
            "No files over 800 lines",
            "No functions over 100 lines",
            "Naming conventions followed",
            "No magic values or hardcoded config",
        ],
        "tested": [
            "Test coverage exists",
            "All tests passing",
            "Invariants have test coverage",
        ],
        "healthy": [
            "Health signals defined and passing",
            "No errors in logs",
            "Invariants not violated",
        ],
        "secure": [
            "No hardcoded secrets",
            "No exposed credentials",
        ],
        "resolved": [
            "No open escalations",
            "No unresolved questions",
            "No pending suggestions",
        ],
    }

    obj_criteria = criteria.get(objective_type, [f"All {objective_type} issues resolved"])

    content_lines = [
        f"## Objective: {module} is {objective_type}",
        "",
        "### Criteria",
    ]
    for c in obj_criteria:
        content_lines.append(f"- [ ] {c}")

    content = "\n".join(content_lines)

    return ObjectiveNarrative(
        id=obj_id,
        name=f"{module} is {objective_type}",
        node_type=NodeType.NARRATIVE.value,
        type=NarrativeSubtype.OBJECTIVE.value,
        description=f"Objective: module {module} achieves {objective_type} status",
        # Physics
        weight=3.0,
        energy=2.0,
        # Semantics
        synthesis=generate_objective_synthesis(objective_type),
        content=content,
        # Objective-specific
        objective_type=objective_type,
        module=module,
        criteria=obj_criteria
    )


def create_task_node(
    task_type: str,
    module: str,
    skill: str,
    issue_ids: List[str],
    objective_id: Optional[str] = None,
    objective_type: str = "",
    index: int = 1,
    missing_nodes: Optional[List[str]] = None
) -> TaskNarrative:
    """Create a task narrative node with full content.

    ID format: narrative_TASK_{type}-{module}-{objective}_{index}
    Example: narrative_TASK_serve-engine-physics-documented_01

    Physics defaults:
        weight: 2.0 (tasks are actionable)
        energy: 4.0 (high activation, ready to work)
    """
    task_id = generate_task_id(task_type, module, objective_type, index)

    # Build rich content based on task type
    if task_type == "serve":
        name = f"Serve {objective_type} for {module}"
        content_lines = [
            f"## Task: {name}",
            "",
            f"**Type:** serve",
            f"**Module:** {module}",
            f"**Objective:** {objective_id or objective_type}",
            f"**Skill:** {skill}",
            "",
            f"### Issues ({len(issue_ids)})",
        ]
        for iid in issue_ids:
            content_lines.append(f"- [ ] `{iid}`")

    elif task_type == "reconstruct":
        name = f"Reconstruct chain for {module}"
        content_lines = [
            f"## Task: {name}",
            "",
            f"**Type:** reconstruct",
            f"**Module:** {module}",
            f"**Skill:** {skill}",
            "",
            "### Missing Nodes",
        ]
        for node in (missing_nodes or []):
            content_lines.append(f"- {node}")
        content_lines.extend([
            "",
            "### Steps",
            "1. Create missing Space/docs nodes",
            "2. Establish links",
            "3. Re-run doctor to verify",
            "",
            f"### Related Issues ({len(issue_ids)})",
        ])
        for iid in issue_ids:
            content_lines.append(f"- `{iid}`")

    else:  # triage
        name = f"Triage orphan code: {module}"
        content_lines = [
            f"## Task: {name}",
            "",
            f"**Type:** triage",
            f"**Module:** {module}",
            f"**Skill:** {skill}",
            "",
            "### Decision Required",
            "No objective defined for this code. Evaluate:",
            "- **integrate**: Move to existing module",
            "- **create_module**: Define new module with objectives",
            "- **deprecate**: Archive for reference",
            "- **delete**: Remove if unused",
            "",
            "### Investigation",
            "- [ ] Check if code is imported elsewhere",
            "- [ ] Check git history for recent activity",
            "- [ ] Check for existing tests",
            "",
            f"### Related Issues ({len(issue_ids)})",
        ]
        for iid in issue_ids:
            content_lines.append(f"- `{iid}`")

    content = "\n".join(content_lines)

    return TaskNarrative(
        id=task_id,
        name=name,
        node_type=NodeType.NARRATIVE.value,
        type=NarrativeSubtype.TASK.value,
        description=content_lines[0].replace("## Task: ", ""),
        # Physics
        weight=2.0,
        energy=4.0,
        # Semantics
        synthesis=generate_task_synthesis(task_type),
        content=content,
        # Task-specific
        task_type=task_type,
        objective_id=objective_id,
        module=module,
        skill=skill,
        issue_ids=issue_ids,
        missing_nodes=missing_nodes or []
    )


def create_space_node(module: str, space_type: str = "MODULE", description: str = "") -> SpaceNode:
    """Create a space node for a module.

    ID format: space_{SUBTYPE}_{instance}
    Example: space_MODULE_engine-physics

    Physics defaults:
        weight: 3.0 for areas, 2.0 for modules (structural anchors)
        energy: 1.0 (low baseline, containers are stable)
    """
    space_id = generate_space_id(module, space_type)
    weight = 3.0 if space_type.upper() == "AREA" else 2.0

    return SpaceNode(
        id=space_id,
        name=module,
        node_type=NodeType.SPACE.value,
        type=space_type.lower(),
        description=description or f"Module: {module}",
        # Physics
        weight=weight,
        energy=1.0,
        # Semantics
        synthesis=generate_space_synthesis(space_type, module),
    )


def create_thing_node(path: str, thing_type: str = "FILE", description: str = "") -> ThingNode:
    """Create a thing node for a file.

    ID format: thing_{SUBTYPE}_{slugified_path}
    Example: thing_FILE_engine-physics-graph-ops-py

    Physics defaults:
        weight: 1.0 (files are passive artifacts)
        energy: 0.5 (low activation)
    """
    thing_id = generate_thing_id(path, thing_type)
    filename = Path(path).name

    return ThingNode(
        id=thing_id,
        name=filename,
        node_type=NodeType.THING.value,
        type=thing_type.lower(),
        uri=path,
        description=description or f"File: {path}",
        # Physics
        weight=1.0,
        energy=0.5,
        # Semantics
        synthesis=generate_thing_synthesis(filename),
    )


# =============================================================================
# LINK CREATION HELPERS
# =============================================================================

def link_space_contains(space_id: str, node_id: str) -> GraphLink:
    """Create contains link: Space → Node.

    Example ID: linked_CONTAINS_space-module-engine-physics_TO_narrative-issue-a7

    Physics defaults:
        polarity: [0.7, 0.3] (forward-biased)
        hierarchy: -0.8 (strong containment)
        permanence: 1.0 (structural, stable)
        emotions: neutral
    """
    link_id = generate_link_id("linked", space_id, node_id, "CONTAINS")
    is_space_child = node_id.startswith("space_")

    return GraphLink(
        id=link_id,
        node_a=space_id,
        node_b=node_id,
        synthesis="contains",
        # Physics
        weight=1.0,
        energy=0.5,
        # Semantic Axes
        polarity=[0.7, 0.3] if is_space_child else [0.6, 0.4],
        hierarchy=-0.8 if is_space_child else -0.7,
        permanence=1.0,
        # Emotions (neutral)
        joy_sadness=0.0,
        trust_disgust=0.0,
        fear_anger=0.0,
        surprise_anticipation=0.0,
    )


def link_issue_blocks_objective(issue_id: str, objective_id: str) -> GraphLink:
    """Create link: Issue blocks Objective.

    Example ID: linked_BLOCKS_narrative-issue-a7_TO_narrative-objective-b3

    Physics defaults:
        polarity: [0.9, 0.1] (strong forward)
        hierarchy: 0.0 (peer relationship)
        permanence: 0.7 (can be resolved)
        emotions: trust:-0.4, fear:+0.3 (problematic)
    """
    link_id = generate_link_id("linked", issue_id, objective_id, "BLOCKS")
    return GraphLink(
        id=link_id,
        node_a=issue_id,
        node_b=objective_id,
        synthesis="blocks",
        # Physics
        weight=2.0,
        energy=3.0,
        # Semantic Axes
        polarity=[0.9, 0.1],
        hierarchy=0.0,
        permanence=0.7,
        # Emotions
        joy_sadness=-0.3,
        trust_disgust=-0.4,
        fear_anger=0.3,
        surprise_anticipation=0.0,
    )


def link_task_serves_objective(task_id: str, objective_id: str) -> GraphLink:
    """Create link: Task serves Objective.

    Example ID: linked_SERVES_narrative-task-01_TO_narrative-objective-b3

    Physics defaults:
        polarity: [0.85, 0.15] (strong forward)
        hierarchy: 0.5 (task elaborates objective)
        permanence: 0.6 (evolves as work progresses)
        emotions: trust:+0.4, joy:+0.2 (constructive)
    """
    link_id = generate_link_id("linked", task_id, objective_id, "SERVES")
    return GraphLink(
        id=link_id,
        node_a=task_id,
        node_b=objective_id,
        synthesis="serves",
        # Physics
        weight=2.0,
        energy=2.5,
        # Semantic Axes
        polarity=[0.85, 0.15],
        hierarchy=0.5,
        permanence=0.6,
        # Emotions
        joy_sadness=0.2,
        trust_disgust=0.4,
        fear_anger=0.0,
        surprise_anticipation=0.3,
    )


def link_task_includes_issue(task_id: str, issue_id: str) -> GraphLink:
    """Create link: Task includes Issue.

    Example ID: linked_INCLUDES_narrative-task-01_TO_narrative-issue-a7

    Physics defaults:
        polarity: [0.7, 0.3] (forward)
        hierarchy: -0.5 (task subsumes issue)
        permanence: 0.8 (stable grouping)
        emotions: neutral
    """
    link_id = generate_link_id("linked", task_id, issue_id, "INCLUDES")
    return GraphLink(
        id=link_id,
        node_a=task_id,
        node_b=issue_id,
        synthesis="includes",
        # Physics
        weight=1.5,
        energy=2.0,
        # Semantic Axes
        polarity=[0.7, 0.3],
        hierarchy=-0.5,
        permanence=0.8,
        # Emotions (neutral)
        joy_sadness=0.0,
        trust_disgust=0.0,
        fear_anger=0.0,
        surprise_anticipation=0.0,
    )


def link_issue_about_thing(issue_id: str, thing_id: str) -> GraphLink:
    """Create link: Issue is about Thing.

    Example ID: linked_ABOUT_narrative-issue-a7_TO_thing-file-b3

    Physics defaults:
        polarity: [0.8, 0.2] (forward)
        hierarchy: 0.3 (issue elaborates thing)
        permanence: 0.9 (stable reference)
        emotions: trust:-0.3 (issue = problem with thing)
    """
    link_id = generate_link_id("linked", issue_id, thing_id, "ABOUT")
    return GraphLink(
        id=link_id,
        node_a=issue_id,
        node_b=thing_id,
        synthesis="is about",
        # Physics
        weight=1.5,
        energy=2.0,
        # Semantic Axes
        polarity=[0.8, 0.2],
        hierarchy=0.3,
        permanence=0.9,
        # Emotions
        joy_sadness=0.0,
        trust_disgust=-0.3,
        fear_anger=0.0,
        surprise_anticipation=0.0,
    )


# =============================================================================
# GRAPH OPERATIONS
# =============================================================================

def upsert_issue(
    task_type: str,
    severity: str,
    path: str,
    message: str,
    module: str,
    store: DoctorGraphStore,
    details: Optional[Dict[str, Any]] = None,
) -> IssueNarrative:
    """
    Create or update an issue narrative node.

    If exists: update severity, message, detected_at (preserves physics/embedding)
    If new: create with links to space and thing

    Physics fields (weight, energy, synthesis, embedding) are only set if null/0.
    Use fill_missing_node_fields() to regenerate if needed.
    """
    issue_id = generate_issue_id(task_type, module, path)
    existing = store.get_node(issue_id)

    if existing and isinstance(existing, IssueNarrative):
        # Update existing - preserve physics, update semantic content
        existing.severity = severity
        existing.message = message
        existing.detected_at = datetime.now().isoformat()
        existing.status = "open"
        existing.properties["details"] = details or {}

        # Rebuild rich content
        content_lines = [
            f"## {task_type}",
            "",
            f"**Module:** {module}",
            f"**File:** {path}" if path else "**Scope:** module-level",
            f"**Severity:** {severity}",
            "",
            "### Description",
            message,
        ]
        if details:
            content_lines.extend(["", "### Details", "```yaml"])
            for k, v in details.items():
                content_lines.append(f"{k}: {v}")
            content_lines.append("```")
        existing.content = "\n".join(content_lines)

        # upsert_node will fill missing fields (but preserve existing ones)
        store.upsert_node(existing)
        return existing

    # Create new
    issue = create_issue_node(task_type, severity, path, message, module, details)
    store.upsert_node(issue)

    # Ensure space exists
    space_id = generate_space_id(module)
    if not store.get_node(space_id):
        space = create_space_node(module)
        store.upsert_node(space)

    # Link space contains issue
    store.create_link(link_space_contains(space_id, issue.id))

    # Link issue about thing (file)
    if path:
        thing_id = generate_thing_id(path)
        if not store.get_node(thing_id):
            thing = create_thing_node(path)
            store.upsert_node(thing)
        store.create_link(link_issue_about_thing(issue.id, thing_id))

    return issue


def resolve_issue(issue_id: str, store: DoctorGraphStore) -> bool:
    """Mark an issue as resolved."""
    issue = store.get_node(issue_id)
    if issue and isinstance(issue, IssueNarrative):
        issue.status = "resolved"
        issue.resolved_at = datetime.now().isoformat()
        issue.energy = 0.0  # No longer active
        store.upsert_node(issue)
        return True
    return False


def ensure_module_objectives(module: str, store: DoctorGraphStore) -> List[ObjectiveNarrative]:
    """Ensure standard objectives exist for a module."""
    objectives = []
    space_id = generate_space_id(module)

    # Ensure space exists
    if not store.get_node(space_id):
        space = create_space_node(module)
        store.upsert_node(space)

    for obj_type in STANDARD_OBJECTIVE_TYPES:
        obj_id = generate_objective_id(obj_type, module)
        existing = store.get_node(obj_id)

        if existing and isinstance(existing, ObjectiveNarrative):
            objectives.append(existing)
        else:
            obj = create_objective_node(obj_type, module)
            store.upsert_node(obj)
            store.create_link(link_space_contains(space_id, obj.id))
            objectives.append(obj)

    return objectives


def fetch_objectives(store: DoctorGraphStore, module: Optional[str] = None) -> List[ObjectiveNarrative]:
    """Fetch objective narrative nodes from graph."""
    nodes = store.query_nodes(
        node_type=NodeType.NARRATIVE.value,
        subtype=NarrativeSubtype.OBJECTIVE.value
    )
    objectives = [n for n in nodes if isinstance(n, ObjectiveNarrative)]

    if module:
        objectives = [o for o in objectives if o.module == module]

    return objectives


# =============================================================================
# TRAVERSAL: Issue → Objective
# =============================================================================

def traverse_to_objective(
    issue: IssueNarrative,
    store: DoctorGraphStore,
    modules: Dict[str, Any]
) -> TraversalResult:
    """
    Traverse from issue up to objective.

    Returns TraversalResult with outcome:
    - SERVE: Found objective
    - RECONSTRUCT: Missing nodes in chain
    - TRIAGE: No objective defined
    """
    path = [issue.id]
    missing_nodes = []

    # Step 1: Find space for this module
    space_id = generate_space_id(issue.module)
    space = store.get_node(space_id)

    if not space:
        missing_nodes.append(f"Space:{issue.module}")
    else:
        path.append(space_id)

    # Step 2: Check for documentation chain in module config
    module_info = modules.get(issue.module, {})
    docs_path = module_info.get("docs") if isinstance(module_info, dict) else None

    if docs_path:
        # Check for required doc narrative nodes (PATTERNS, SYNC at minimum)
        for doc_type in ["patterns", "sync"]:
            doc_id = f"narrative_{doc_type}_{issue.module}"
            doc_node = store.get_node(doc_id)
            if not doc_node:
                missing_nodes.append(f"{doc_type.upper()}:{issue.module}")

    # Step 3: Find objective
    objective_types = ISSUE_BLOCKS_OBJECTIVE.get(issue.task_type, ["documented"])

    objective = None
    for obj_type in objective_types:
        obj_id = generate_objective_id(obj_type, issue.module)
        obj_node = store.get_node(obj_id)
        if obj_node and isinstance(obj_node, ObjectiveNarrative):
            objective = obj_node
            path.append(obj_id)
            break

    # Determine outcome
    if missing_nodes:
        return TraversalResult(
            outcome=TraversalOutcome.RECONSTRUCT,
            space_id=space_id if space else None,
            missing_nodes=missing_nodes,
            path=path
        )
    elif objective:
        return TraversalResult(
            outcome=TraversalOutcome.SERVE,
            objective=objective,
            space_id=space_id,
            path=path
        )
    else:
        return TraversalResult(
            outcome=TraversalOutcome.TRIAGE,
            space_id=space_id if space else None,
            path=path
        )


# =============================================================================
# TASK CREATION FROM ISSUES
# =============================================================================

MAX_ISSUES_PER_TASK = 5


def group_issues_by_outcome(
    issues: List[IssueNarrative],
    store: DoctorGraphStore,
    modules: Dict[str, Any]
) -> Dict[TraversalOutcome, Dict[str, List[Tuple[IssueNarrative, TraversalResult]]]]:
    """Group issues by traversal outcome and module."""
    grouped: Dict[TraversalOutcome, Dict[str, List[Tuple[IssueNarrative, TraversalResult]]]] = {
        TraversalOutcome.SERVE: {},
        TraversalOutcome.RECONSTRUCT: {},
        TraversalOutcome.TRIAGE: {},
    }

    for issue in issues:
        result = traverse_to_objective(issue, store, modules)
        key = issue.module or "orphan"

        if key not in grouped[result.outcome]:
            grouped[result.outcome][key] = []
        grouped[result.outcome][key].append((issue, result))

    return grouped


def create_tasks_from_issues(
    issues: List[IssueNarrative],
    store: DoctorGraphStore,
    modules: Dict[str, Any]
) -> List[TaskNarrative]:
    """
    Create task narrative nodes from issues.

    1. Traverse each issue to objective
    2. Group by outcome and module
    3. Split if too many issues
    4. Create task narrative nodes with proper links

    Note: Agent assignment (actor → task links) happens separately via
    AgentGraph.assign_agent_to_work() when agents are runed.
    """
    grouped = group_issues_by_outcome(issues, store, modules)
    tasks: List[TaskNarrative] = []

    # SERVE tasks - group by objective
    for module, issue_results in grouped[TraversalOutcome.SERVE].items():
        # Ensure module Space exists
        space_id = generate_space_id(module)
        if not store.get_node(space_id):
            space = create_space_node(module)
            store.upsert_node(space)

        by_objective: Dict[str, List[IssueNarrative]] = {}
        for issue, result in issue_results:
            if result.objective:
                obj_id = result.objective.id
                by_objective.setdefault(obj_id, []).append(issue)

        for obj_id, obj_issues in by_objective.items():
            objective = store.get_node(obj_id)
            if not objective or not isinstance(objective, ObjectiveNarrative):
                continue

            skill = OBJECTIVE_TO_SKILL.get(objective.objective_type, "implement_write_or_modify_code")

            # Split if too many
            chunks = [obj_issues[i:i + MAX_ISSUES_PER_TASK]
                      for i in range(0, len(obj_issues), MAX_ISSUES_PER_TASK)]

            for idx, chunk in enumerate(chunks, 1):
                task = create_task_node(
                    task_type="serve",
                    module=module,
                    skill=skill,
                    issue_ids=[i.id for i in chunk],
                    objective_id=obj_id,
                    objective_type=objective.objective_type,
                    index=idx
                )
                store.upsert_node(task)
                tasks.append(task)

                # Links
                store.create_link(link_space_contains(space_id, task.id))  # Module contains Task
                store.create_link(link_task_serves_objective(task.id, obj_id))
                for issue in chunk:
                    store.create_link(link_task_includes_issue(task.id, issue.id))
                    store.create_link(link_issue_blocks_objective(issue.id, obj_id))

    # RECONSTRUCT tasks
    for module, issue_results in grouped[TraversalOutcome.RECONSTRUCT].items():
        # Ensure module Space exists
        space_id = generate_space_id(module)
        if not store.get_node(space_id):
            space = create_space_node(module)
            store.upsert_node(space)

        all_missing: Set[str] = set()
        all_issues: List[IssueNarrative] = []
        for issue, result in issue_results:
            all_missing.update(result.missing_nodes)
            all_issues.append(issue)

        task = create_task_node(
            task_type="reconstruct",
            module=module,
            skill="create_module_documentation",
            issue_ids=[i.id for i in all_issues],
            missing_nodes=list(all_missing)
        )
        store.upsert_node(task)
        tasks.append(task)

        # Links
        store.create_link(link_space_contains(space_id, task.id))  # Module contains Task
        for issue in all_issues:
            store.create_link(link_task_includes_issue(task.id, issue.id))

    # TRIAGE tasks
    for module, issue_results in grouped[TraversalOutcome.TRIAGE].items():
        # Ensure module Space exists
        space_id = generate_space_id(module)
        if not store.get_node(space_id):
            space = create_space_node(module)
            store.upsert_node(space)

        all_issues = [issue for issue, _ in issue_results]

        task = create_task_node(
            task_type="triage",
            module=module,
            skill="triage_unmapped_code",
            issue_ids=[i.id for i in all_issues]
        )
        store.upsert_node(task)
        tasks.append(task)

        # Links
        store.create_link(link_space_contains(space_id, task.id))  # Module contains Task
        for issue in all_issues:
            store.create_link(link_task_includes_issue(task.id, issue.id))

    return tasks


def update_objective_status(objective_id: str, store: DoctorGraphStore) -> str:
    """Update objective status based on blocking issues."""
    objective = store.get_node(objective_id)
    if not objective or not isinstance(objective, ObjectiveNarrative):
        return "unknown"

    # Find issues blocking this objective via links with negative trust_disgust (opposition)
    blocking_links = store.get_links_to(objective_id)
    blocking_links = [l for l in blocking_links if l.trust_disgust < -0.2]

    open_blockers = 0
    for link in blocking_links:
        issue = store.get_node(link.node_a)
        if issue and isinstance(issue, IssueNarrative) and issue.status == "open":
            open_blockers += 1

    if open_blockers == 0:
        objective.status = "achieved"
    else:
        objective.status = "open"

    store.upsert_node(objective)
    return objective.status


# =============================================================================
# FILE THING NODE OPERATIONS
# =============================================================================

def upsert_file_thing(
    path: str,
    module: str,
    store: DoctorGraphStore,
    file_type: str = "FILE",
) -> ThingNode:
    """
    Create or update a Thing node for a file.

    Creates the Thing node and links it to its containing Space (module).

    Args:
        path: File path relative to project root
        module: Module name (for Space linkage)
        store: Graph store instance
        file_type: Thing subtype (default: FILE)

    Returns:
        The created/updated ThingNode
    """
    thing_id = generate_thing_id(path, file_type)
    existing = store.get_node(thing_id)

    if existing and isinstance(existing, ThingNode):
        # Update existing
        existing.updated_at_s = int(time.time())
        store.upsert_node(existing)
        return existing

    # Create new Thing node
    thing = create_thing_node(path, file_type)
    store.upsert_node(thing)

    # Ensure Space exists and link
    space_id = generate_space_id(module)
    if not store.get_node(space_id):
        space = create_space_node(module)
        store.upsert_node(space)

    # Create contains link: Space → Thing
    store.create_link(link_space_contains(space_id, thing.id))

    return thing


def upsert_all_file_things(
    target_dir: Path,
    store: DoctorGraphStore,
    ignore_patterns: List[str],
    modules_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Scan all files in target_dir and create Thing nodes for each.

    Respects .gitignore and .mindignore patterns.
    Creates Space nodes for areas/modules with hierarchy links.
    Creates Thing nodes for files with contains links.

    Graph structure:
        Space (AREA) --contains--> Space (MODULE) --contains--> Thing (FILE)

    Args:
        target_dir: Project root directory
        store: Graph store instance
        ignore_patterns: List of ignore patterns from config
        modules_config: Optional modules.yaml config for module mapping

    Returns:
        Dict with stats: {files_scanned, things_created, things_updated, spaces_created, space_links}
    """
    from .doctor_files import should_ignore_path, is_binary_file
    from .core_utils import IGNORED_EXTENSIONS

    stats = {
        "files_scanned": 0,
        "things_created": 0,
        "things_updated": 0,
        "spaces_created": 0,
        "space_links": 0,
        "modules": set(),
        "areas": set(),
    }

    # Track Space hierarchy: parent_space_id -> set of child_space_ids
    space_hierarchy: Dict[str, Set[str]] = {}

    # Skip directories that should never be scanned
    skip_dirs = {
        '.git', '.mind', '__pycache__', '.venv', 'venv',
        'node_modules', '.next', 'dist', 'build', '.cache',
        '.pytest_cache', '.mypy_cache', 'coverage', '.tox',
    }

    def ensure_space_hierarchy(rel_path: Path) -> str:
        """
        Ensure Space nodes exist for directory hierarchy.
        Returns the immediate parent Space ID for the file.

        For path like 'engine/physics/graph.py':
        - Creates space_AREA_engine (if not exists)
        - Creates space_MODULE_engine-physics (if not exists)
        - Links: engine --contains--> engine-physics
        - Returns: space_MODULE_engine-physics
        """
        parts = rel_path.parts[:-1]  # Exclude filename

        if not parts:
            # Root-level file
            return generate_space_id("root", "MODULE")

        # First level = AREA
        area_name = parts[0]
        area_id = generate_space_id(area_name, "AREA")

        if not store.get_node(area_id):
            area_node = SpaceNode(
                id=area_id,
                name=area_name,
                node_type=NodeType.SPACE.value,
                type="area",
                description=f"Area: {area_name}"
            )
            store.upsert_node(area_node)
            stats["spaces_created"] += 1
        stats["areas"].add(area_name)

        if len(parts) == 1:
            # File directly in area (e.g., engine/runner.py)
            return area_id

        # Second level = MODULE (area-subdir)
        module_name = f"{parts[0]}-{parts[1]}" if len(parts) > 1 else parts[0]
        module_id = generate_space_id(module_name, "MODULE")

        if not store.get_node(module_id):
            module_node = SpaceNode(
                id=module_id,
                name=module_name,
                node_type=NodeType.SPACE.value,
                type="module",
                description=f"Module: {module_name}"
            )
            store.upsert_node(module_node)
            stats["spaces_created"] += 1

            # Link area -> module
            if area_id not in space_hierarchy:
                space_hierarchy[area_id] = set()
            if module_id not in space_hierarchy[area_id]:
                space_hierarchy[area_id].add(module_id)
                store.create_link(link_space_contains(area_id, module_id))
                stats["space_links"] += 1

        stats["modules"].add(module_name)
        return module_id

    def scan_directory(directory: Path, depth: int = 0) -> None:
        """Recursively scan directory for files."""
        if depth > 10:  # Prevent too deep recursion
            return

        try:
            items = list(directory.iterdir())
        except PermissionError:
            return

        for item in items:
            # Skip hidden files/dirs
            if item.name.startswith('.'):
                continue

            # Skip known skip directories
            if item.is_dir() and item.name in skip_dirs:
                continue

            # Check ignore patterns
            if should_ignore_path(item, ignore_patterns, target_dir):
                continue

            if item.is_dir():
                scan_directory(item, depth + 1)
            elif item.is_file():
                # Skip binary files
                if is_binary_file(item):
                    continue

                # Skip ignored extensions
                if item.suffix.lower() in IGNORED_EXTENSIONS:
                    continue

                stats["files_scanned"] += 1

                # Get relative path for storage
                try:
                    rel_path = item.relative_to(target_dir)
                    rel_path_str = str(rel_path)
                except ValueError:
                    rel_path = Path(str(item))
                    rel_path_str = str(item)

                # Ensure Space hierarchy exists and get parent Space
                parent_space_id = ensure_space_hierarchy(rel_path)

                # Check if Thing already exists
                thing_id = generate_thing_id(rel_path_str)
                existing = store.get_node(thing_id)

                if existing:
                    stats["things_updated"] += 1
                else:
                    stats["things_created"] += 1

                # Create Thing node
                thing = create_thing_node(rel_path_str)
                store.upsert_node(thing)

                # Link parent Space -> Thing
                store.create_link(link_space_contains(parent_space_id, thing.id))

    # Start scan from target_dir
    scan_directory(target_dir)

    # Convert sets to counts for return
    stats["modules_count"] = len(stats["modules"])
    stats["areas_count"] = len(stats["areas"])
    del stats["modules"]
    del stats["areas"]

    return stats


def _node_to_embed_text(node: GraphNode) -> str:
    """Convert any node to embeddable text."""
    parts = [node.name]
    if node.description:
        parts.append(node.description)

    # Add type-specific content
    if isinstance(node, ThingNode):
        parts.append(f"file: {node.uri}")
    elif isinstance(node, SpaceNode):
        parts.append(f"module: {node.type}")
    elif isinstance(node, (IssueNarrative, TaskNarrative, ObjectiveNarrative)):
        if hasattr(node, 'content') and node.content:
            parts.append(node.content[:500])  # Truncate long content
        if hasattr(node, 'message') and node.message:
            parts.append(node.message)

    return ". ".join(p for p in parts if p)


def _link_to_embed_text(link: GraphLink, store: DoctorGraphStore) -> str:
    """Convert a link to embeddable text."""
    parts = []

    # Get node names for context
    node_a = store.get_node(link.node_a)
    node_b = store.get_node(link.node_b)
    a_name = node_a.name if node_a else link.node_a
    b_name = node_b.name if node_b else link.node_b

    parts.append(f"{a_name} {link.synthesis} {b_name}")

    return ". ".join(p for p in parts if p)


def sync_file_things_to_graph(
    target_dir: Path,
    store: DoctorGraphStore,
    ignore_patterns: List[str],
    graph_ops: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Sync doctor graph nodes and links to external graph database.

    First builds local store with upsert_all_file_things,
    then syncs to external graph if graph_ops provided.

    Syncs (all with embeddings for semantic search):
        - Thing nodes (files)
        - Space nodes (modules)
        - IssueNarrative nodes (doctor issues)
        - TaskNarrative nodes (work items)
        - ObjectiveNarrative nodes (goals)
        - All link types with embeddings

    Args:
        target_dir: Project root directory
        store: Local graph store instance
        ignore_patterns: List of ignore patterns
        graph_ops: Optional external graph operations instance

    Returns:
        Dict with sync stats
    """
    # Build local store
    stats = upsert_all_file_things(target_dir, store, ignore_patterns)

    if not graph_ops:
        return stats

    # Sync to external graph
    sync_stats = {
        "nodes_synced": 0,
        "links_synced": 0,
        "embeddings_generated": 0,
        "nodes_with_embedding": 0,
        "nodes_without_embedding": 0,
        "links_with_embedding": 0,
        "links_without_embedding": 0,
        "embedding_service_available": False,
    }

    # Load embedding service (always generate embeddings)
    embedding_service = None
    try:
        from runtime.infrastructure.embeddings.service import get_embedding_service
        embedding_service = get_embedding_service()
        sync_stats["embedding_service_available"] = embedding_service is not None
    except ImportError:
        pass  # Embeddings not available

    now = int(time.time())

    try:
        # BATCH: Collect all nodes needing embeddings first
        nodes_needing_embed = []
        texts_to_embed = []
        for node_id, node in store.nodes.items():
            if node.embedding is None:
                embed_text = _node_to_embed_text(node)
                if embed_text:
                    nodes_needing_embed.append(node)
                    texts_to_embed.append(embed_text)

        # BATCH: Generate all node embeddings at once
        if texts_to_embed and embedding_service:
            try:
                embeddings = embedding_service.embed_batch(texts_to_embed)
                for node, embedding in zip(nodes_needing_embed, embeddings):
                    if embedding:
                        node.embedding = embedding
                        sync_stats["embeddings_generated"] += 1
            except Exception:
                # Fallback to individual if batch fails
                for node, text in zip(nodes_needing_embed, texts_to_embed):
                    try:
                        embedding = embedding_service.embed(text)
                        if embedding:
                            node.embedding = embedding
                            sync_stats["embeddings_generated"] += 1
                    except Exception:
                        pass

        # Sync all nodes to graph
        for node_id, node in store.nodes.items():
            embedding = node.embedding

            # Track embedding stats
            if embedding:
                sync_stats["nodes_with_embedding"] += 1
            else:
                sync_stats["nodes_without_embedding"] += 1

            if isinstance(node, ThingNode):
                cypher = """
                MERGE (t:Thing {id: $id})
                SET t.node_type = $node_type,
                    t.type = $type,
                    t.name = $name,
                    t.uri = $uri,
                    t.description = $description,
                    t.synthesis = $synthesis,
                    t.weight = $weight,
                    t.energy = $energy,
                    t.created_at_s = $created_at_s,
                    t.updated_at_s = $updated_at_s
                """
                params = {
                    "id": node.id,
                    "node_type": node.node_type,
                    "type": node.type,
                    "name": node.name,
                    "uri": node.uri,
                    "description": node.description,
                    "synthesis": node.synthesis or "",
                    "weight": node.weight,
                    "energy": node.energy,
                    "created_at_s": node.created_at_s,
                    "updated_at_s": node.updated_at_s,
                }
                # Only write embedding if we have one (don't overwrite existing)
                if embedding:
                    cypher = cypher.rstrip() + ",\n                    t.embedding = $embedding"
                    params["embedding"] = embedding
                graph_ops._query(cypher, params)
                sync_stats["nodes_synced"] += 1

            elif isinstance(node, SpaceNode):
                cypher = """
                MERGE (s:Space {id: $id})
                SET s.node_type = $node_type,
                    s.type = $type,
                    s.name = $name,
                    s.description = $description,
                    s.synthesis = $synthesis,
                    s.weight = $weight,
                    s.energy = $energy,
                    s.created_at_s = $created_at_s,
                    s.updated_at_s = $updated_at_s
                """
                params = {
                    "id": node.id,
                    "node_type": node.node_type,
                    "type": node.type,
                    "name": node.name,
                    "description": node.description,
                    "synthesis": node.synthesis or "",
                    "weight": node.weight,
                    "energy": node.energy,
                    "created_at_s": node.created_at_s,
                    "updated_at_s": node.updated_at_s,
                }
                # Only write embedding if we have one (don't overwrite existing)
                if embedding:
                    cypher = cypher.rstrip() + ",\n                    s.embedding = $embedding"
                    params["embedding"] = embedding
                graph_ops._query(cypher, params)
                sync_stats["nodes_synced"] += 1

            elif isinstance(node, IssueNarrative):
                cypher = """
                MERGE (n:Narrative {id: $id})
                SET n.node_type = $node_type,
                    n.type = $type,
                    n.name = $name,
                    n.content = $content,
                    n.description = $description,
                    n.synthesis = $synthesis,
                    n.task_type = $task_type,
                    n.severity = $severity,
                    n.status = $status,
                    n.module = $module,
                    n.path = $path,
                    n.message = $message,
                    n.weight = $weight,
                    n.energy = $energy,
                    n.detected_at = $detected_at,
                    n.created_at_s = $created_at_s,
                    n.updated_at_s = $updated_at_s
                """
                params = {
                    "id": node.id,
                    "node_type": node.node_type,
                    "type": node.type,
                    "name": node.name,
                    "content": node.content,
                    "description": node.description,
                    "synthesis": node.synthesis or "",
                    "task_type": node.task_type,
                    "severity": node.severity,
                    "status": node.status,
                    "module": node.module,
                    "path": node.path,
                    "message": node.message,
                    "weight": node.weight,
                    "energy": node.energy,
                    "detected_at": node.detected_at,
                    "created_at_s": node.created_at_s,
                    "updated_at_s": node.updated_at_s,
                }
                # Only write embedding if we have one (don't overwrite existing)
                if embedding:
                    cypher = cypher.rstrip() + ",\n                    n.embedding = $embedding"
                    params["embedding"] = embedding
                graph_ops._query(cypher, params)
                sync_stats["nodes_synced"] += 1

            elif isinstance(node, TaskNarrative):
                cypher = """
                MERGE (n:Narrative {id: $id})
                SET n.node_type = $node_type,
                    n.type = $type,
                    n.name = $name,
                    n.content = $content,
                    n.description = $description,
                    n.synthesis = $synthesis,
                    n.task_type = $task_type,
                    n.objective_id = $objective_id,
                    n.module = $module,
                    n.skill = $skill,
                    n.status = $status,
                    n.weight = $weight,
                    n.energy = $energy,
                    n.created_at_s = $created_at_s,
                    n.updated_at_s = $updated_at_s
                """
                params = {
                    "id": node.id,
                    "node_type": node.node_type,
                    "type": node.type,
                    "name": node.name,
                    "content": node.content,
                    "description": node.description,
                    "synthesis": node.synthesis or "",
                    "task_type": node.task_type,
                    "objective_id": node.objective_id or "",
                    "module": node.module,
                    "skill": node.skill,
                    "status": node.status,
                    "weight": node.weight,
                    "energy": node.energy,
                    "created_at_s": node.created_at_s,
                    "updated_at_s": node.updated_at_s,
                }
                if embedding:
                    cypher = cypher.rstrip() + ",\n                    n.embedding = $embedding"
                    params["embedding"] = embedding
                graph_ops._query(cypher, params)
                sync_stats["nodes_synced"] += 1

            elif isinstance(node, ObjectiveNarrative):
                cypher = """
                MERGE (n:Narrative {id: $id})
                SET n.node_type = $node_type,
                    n.type = $type,
                    n.name = $name,
                    n.content = $content,
                    n.description = $description,
                    n.synthesis = $synthesis,
                    n.objective_type = $objective_type,
                    n.module = $module,
                    n.status = $status,
                    n.weight = $weight,
                    n.energy = $energy,
                    n.created_at_s = $created_at_s,
                    n.updated_at_s = $updated_at_s
                """
                params = {
                    "id": node.id,
                    "node_type": node.node_type,
                    "type": node.type,
                    "name": node.name,
                    "content": node.content,
                    "description": node.description,
                    "synthesis": node.synthesis or "",
                    "objective_type": node.objective_type,
                    "module": node.module,
                    "status": node.status,
                    "weight": node.weight,
                    "energy": node.energy,
                    "created_at_s": node.created_at_s,
                    "updated_at_s": node.updated_at_s,
                }
                if embedding:
                    cypher = cypher.rstrip() + ",\n                    n.embedding = $embedding"
                    params["embedding"] = embedding
                graph_ops._query(cypher, params)
                sync_stats["nodes_synced"] += 1

        # BATCH: Collect all links needing embeddings first
        links_needing_embed = []
        link_texts_to_embed = []
        for link in store.links:
            if link.embedding is None:
                embed_text = _link_to_embed_text(link, store)
                if embed_text:
                    links_needing_embed.append(link)
                    link_texts_to_embed.append(embed_text)

        # BATCH: Generate all link embeddings at once
        if link_texts_to_embed and embedding_service:
            try:
                link_embeddings = embedding_service.embed_batch(link_texts_to_embed)
                for link, embedding in zip(links_needing_embed, link_embeddings):
                    if embedding:
                        link.embedding = embedding
                        sync_stats["embeddings_generated"] += 1
            except Exception:
                # Fallback to individual if batch fails
                for link, text in zip(links_needing_embed, link_texts_to_embed):
                    try:
                        embedding = embedding_service.embed(text)
                        if embedding:
                            link.embedding = embedding
                            sync_stats["embeddings_generated"] += 1
                    except Exception:
                        pass

        # Sync all links to graph
        for link in store.links:
            embedding = link.embedding

            # Track embedding stats
            if embedding:
                sync_stats["links_with_embedding"] += 1
            else:
                sync_stats["links_without_embedding"] += 1

            cypher = """
            MATCH (a {id: $from_id})
            MATCH (b {id: $to_id})
            MERGE (a)-[r:LINKED]->(b)
            SET r.synthesis = $synthesis,
                r.weight = $weight,
                r.energy = $energy,
                r.polarity = $polarity,
                r.hierarchy = $hierarchy,
                r.permanence = $permanence,
                r.joy_sadness = $joy_sadness,
                r.trust_disgust = $trust_disgust,
                r.fear_anger = $fear_anger,
                r.surprise_anticipation = $surprise_anticipation,
                r.created_at_s = $created_at_s,
                r.updated_at_s = $updated_at_s
            """
            params = {
                "from_id": link.node_a,
                "to_id": link.node_b,
                "synthesis": link.synthesis or "",
                "weight": link.weight,
                "energy": link.energy,
                "polarity": link.polarity,
                "hierarchy": link.hierarchy,
                "permanence": link.permanence,
                "joy_sadness": link.joy_sadness,
                "trust_disgust": link.trust_disgust,
                "fear_anger": link.fear_anger,
                "surprise_anticipation": link.surprise_anticipation,
                "created_at_s": link.created_at_s,
                "updated_at_s": link.updated_at_s,
            }
            if embedding:
                cypher = cypher.rstrip() + ",\n                r.embedding = $embedding"
                params["embedding"] = embedding
            graph_ops._query(cypher, params)
            sync_stats["links_synced"] += 1

    except Exception as e:
        sync_stats["error"] = str(e)

    stats.update(sync_stats)
    return stats


# =============================================================================
# FUNCTION ALIAS
# =============================================================================

# doctor_tasks.py imports use this name
upsert_issue_from_check = upsert_issue
