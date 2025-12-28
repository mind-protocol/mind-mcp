"""
Graph Physics Engine

Energy flow, decay, pressure, and flip detection.
The living world simulation that runs without LLM.

Usage:
    from mind.physics import GraphTickV1_2

    tick = GraphTickV1_2()
    result = tick.tick()

v1.6.1 Additions:
    - link_scoring: Link score formula for SubEntity traversal
    - flow: Forward/backward coloring for embedding propagation
    - crystallization: Narrative creation from exploration
    - synthesis: Grammar floats <-> phrases conversion
    - exploration: Async SubEntity coroutine runner

v1.8 Additions:
    - Query vs Intention separation (query=WHAT, intention=WHY)
    - IntentionType enum (SUMMARIZE, VERIFY, FIND_NEXT, EXPLORE, RETRIEVE)

v1.9 Additions:
    - cluster_presentation: Transform raw clusters to readable presentations
    - synthesis_unfold: Compact synthesis to prose conversion
"""

from .tick_v1_2 import GraphTickV1_2
from .constants import *
from .link_scoring import (
    cosine_similarity,
    max_cosine_against_set,
    calculate_permanence,
    get_polarity,
    calculate_link_score,
    score_outgoing_links,
    get_target_node_id,
    should_branch,
    select_branch_candidates,
)
from .flow import (
    blend_embeddings,
    calculate_color_weight,
    forward_color_link,
    backward_color_path,
    color_link_from_node,
    accumulate_path_energy,
    # v1.9: Plutchik axis functions
    blend_plutchik_axes,
    compute_query_axes,
    compute_path_axes,
    blend_query_axes,
    get_weighted_average_axes,
)
from .crystallization import (
    compute_crystallization_embedding,
    check_novelty,
    find_similar_narratives,
    crystallize,
    CrystallizedNarrative,
    SubEntityCrystallizationState,
    NOVELTY_THRESHOLD,
)
from .synthesis import (
    LinkPhysics,
    synthesize_link,
    synthesize_from_dict,
    parse_phrase,
    parse_and_merge,
    ParsedPhysics,
    synthesize_from_crystallization,
)
from .exploration import (
    ExplorationResult,
    ExplorationConfig,
    ExplorationRunner,
    ExplorationTimeoutError,
    run_exploration,
    run_exploration_sync,
    GraphInterface,
    present_exploration_result,
)
from .subentity import (
    SubEntity,
    SubEntityState,
    ExplorationContext,
    IntentionType,
    INTENTION_WEIGHTS,
    create_subentity,
)
from .cluster_presentation import (
    ClusterNode,
    ClusterLink,
    RawCluster,
    ClusterStats,
    Gap,
    PresentedCluster,
    Marker,
    RenderMode,
    present_cluster,
    cluster_from_dicts,
    find_direct_response,
    find_convergences,
    find_tensions,
    find_divergences,
    find_gaps,
    render_cluster,
    unfold_node_synthesis,
    unfold_link_synthesis,
)
from .synthesis_unfold import (
    ParsedNodeSynthesis,
    ParsedLinkSynthesis,
    parse_node_synthesis,
    parse_link_synthesis,
    unfold_node,
    unfold_link,
    unfold_node_link_node,
    compact_node,
    compact_link,
    to_adverb,
    to_participle,
)
from .link_vocab import (
    nature_to_floats,
    parse_nature,
    parse_with_conflicts,
    get_verb_for_nature,
    get_vocab_reference,
    get_vocab_compact,
    get_intensified_verb,
    select_verb_form,
    translate,
    default_floats,
    ALL_VERBS,
    PRE_MODIFIERS,
    POST_MODIFIERS,
    TEMPORAL_VERBS,
    DOCTOR_VERBS,
    INTENSIFIERS,
    TRANSLATIONS,
)

# Backwards compatibility alias
GraphTick = GraphTickV1_2

__all__ = [
    # Core tick
    'GraphTick',
    'GraphTickV1_2',
    # Link scoring (v1.6.1)
    'cosine_similarity',
    'max_cosine_against_set',
    'calculate_permanence',
    'get_polarity',
    'calculate_link_score',
    'score_outgoing_links',
    'get_target_node_id',
    'should_branch',
    'select_branch_candidates',
    # Coloring (v1.6.1)
    'blend_embeddings',
    'calculate_color_weight',
    'forward_color_link',
    'backward_color_path',
    'color_link_from_node',
    'accumulate_path_energy',
    # Query emotions (v1.6.1)
    'compute_query_emotion',
    'compute_path_emotion',
    'blend_query_emotions',
    # Crystallization (v1.6.1)
    'compute_crystallization_embedding',
    'check_novelty',
    'find_similar_narratives',
    'crystallize',
    'CrystallizedNarrative',
    'SubEntityCrystallizationState',
    'NOVELTY_THRESHOLD',
    # Synthesis (v1.6.1)
    'LinkPhysics',
    'synthesize_link',
    'synthesize_from_dict',
    'parse_phrase',
    'parse_and_merge',
    'ParsedPhysics',
    'synthesize_from_crystallization',
    # Exploration (v1.6.1)
    'SubEntity',
    'SubEntityState',
    'create_subentity',
    'IntentionType',
    'INTENTION_WEIGHTS',
    'ExplorationContext',
    'ExplorationTimeoutError',
    'ExplorationResult',
    'ExplorationConfig',
    'ExplorationRunner',
    'run_exploration',
    'run_exploration_sync',
    'GraphInterface',
    'present_exploration_result',
    # Cluster Presentation (v1.9.2)
    'ClusterNode',
    'ClusterLink',
    'RawCluster',
    'ClusterStats',
    'Gap',
    'PresentedCluster',
    'Marker',
    'RenderMode',
    'present_cluster',
    'cluster_from_dicts',
    'find_direct_response',
    'find_convergences',
    'find_tensions',
    'find_divergences',
    'find_gaps',
    'render_cluster',
    'unfold_node_synthesis',
    'unfold_link_synthesis',
    # Synthesis Unfolding (v1.9)
    'ParsedNodeSynthesis',
    'ParsedLinkSynthesis',
    'parse_node_synthesis',
    'parse_link_synthesis',
    'unfold_node',
    'unfold_link',
    'unfold_node_link_node',
    'compact_node',
    'compact_link',
    'to_adverb',
    'to_participle',
    # Link Vocabulary (v2.0)
    'nature_to_floats',
    'parse_nature',
    'get_verb_for_nature',
    'get_vocab_reference',
    'get_vocab_compact',
    'ALL_VERBS',
    'PRE_MODIFIERS',
    'POST_MODIFIERS',
]
