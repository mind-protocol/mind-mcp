"""
Synthesis — v1.6.1 Grammar Floats ↔ Phrases

Bidirectional conversion between physics floats and natural language phrases.

FORWARD (floats → phrases):
    Given link/node physics values, generate natural language description.

BACKWARD (phrases → floats):
    Given natural language input, parse into approximate physics values.

DOCS: docs/schema/GRAMMAR_Link_Synthesis.md
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re


# =============================================================================
# VOCABULARY (English default)
# =============================================================================

VERBS = {
    # Base verbs from hierarchy + polarity
    'encompasses': 'encompasses',
    'contains': 'contains',
    'elaborates': 'elaborates',
    'exemplifies': 'exemplifies',
    'acts_on': 'acts on',
    'influences': 'influences',
    'interacts_with': 'interacts with',
    'receives_from': 'receives from',
    'undergoes': 'undergoes',
    'linked_to': 'is linked to',
    'coexists_with': 'coexists with',

    # Ownership
    'belongs_to': 'belongs to',
    'owns': 'owns',
    'possesses': 'possesses',
    'holds': 'holds',
    'uses': 'uses',
    'depends_on': 'depends on',

    # Evidential
    'proves': 'proves',
    'confirms': 'confirms',
    'contradicts': 'contradicts',
    'supports': 'supports',
    'suggests': 'suggests',
    'evokes': 'evokes',

    # Actor-specific
    'believes_in': 'believes in',
    'doubts': 'doubts',
    'expresses': 'expresses',
    'created': 'created',
}

PRE_MODIFIERS = {
    # From permanence
    'definitely': (0.8, 1.0, 'permanence'),
    'clearly': (0.6, 0.8, 'permanence'),
    'probably': (0.2, 0.4, 'permanence'),
    'perhaps': (0.0, 0.2, 'permanence'),

    # From energy
    'intensely': (8.0, float('inf'), 'energy'),
    'actively': (5.0, 8.0, 'energy'),
    'weakly': (0.5, 2.0, 'energy'),
    'barely': (0.0, 0.5, 'energy'),

    # From surprise
    'suddenly': (0.7, 1.0, 'surprise'),
    'unexpectedly': (0.4, 0.7, 'surprise'),
    'inevitably': (-1.0, -0.7, 'surprise'),
    'as expected': (-0.7, -0.4, 'surprise'),
}

POST_MODIFIERS = {
    # From fear_anger
    'with rage': (-1.0, -0.7, 'fear_anger'),
    'with hostility': (-0.7, -0.4, 'fear_anger'),
    'with apprehension': (0.4, 0.7, 'fear_anger'),
    'with terror': (0.7, 1.0, 'fear_anger'),

    # From trust_disgust
    'with disgust': (-1.0, -0.7, 'trust_disgust'),
    'with distrust': (-0.7, -0.4, 'trust_disgust'),
    'with confidence': (0.4, 0.7, 'trust_disgust'),
    'with admiration': (0.7, 1.0, 'trust_disgust'),

    # From joy_sadness
    'with despair': (-1.0, -0.7, 'joy_sadness'),
    'with sadness': (-0.7, -0.4, 'joy_sadness'),
    'with satisfaction': (0.4, 0.7, 'joy_sadness'),
    'with euphoria': (0.7, 1.0, 'joy_sadness'),
}

WEIGHT_ANNOTATIONS = {
    'fundamental': (5.0, float('inf')),
    'important': (3.0, 5.0),
    'minor': (0.0, 1.0),
}

INTENSIFIERS = {
    # verb_key: (attenuated, intensified)
    'believes_in': ('tends to believe', 'firmly believes'),
    'doubts': ('hesitates about', 'rejects'),
    'contradicts': ('nuances', 'radically contradicts'),
    'confirms': ('supports', 'absolutely confirms'),
    'influences': ('touches', 'dominates'),
    'contains': ('borders', 'imprisons'),
    'proves': ('suggests', 'demonstrates'),
    'expresses': ('sketches', 'proclaims'),
}


# =============================================================================
# FORWARD SYNTHESIS (Floats → Phrases)
# =============================================================================

@dataclass
class LinkPhysics:
    """Physics values for a link."""
    polarity_ab: float = 0.5
    polarity_ba: float = 0.5
    hierarchy: float = 0.0
    permanence: float = 0.5
    energy: float = 1.0
    weight: float = 1.0
    fear_anger: float = 0.0
    trust_disgust: float = 0.0
    joy_sadness: float = 0.0
    surprise: float = 0.0


def get_base_verb_key(hierarchy: float, polarity_ab: float, polarity_ba: float) -> str:
    """Determine base verb from hierarchy and polarity."""
    # Hierarchy-dominant
    if abs(hierarchy) > 0.5:
        if hierarchy < -0.7:
            return 'encompasses'
        elif hierarchy < -0.5:
            return 'contains'
        elif hierarchy > 0.7:
            return 'exemplifies'
        else:
            return 'elaborates'

    # Polarity-dominant
    if polarity_ab > 0.7 and polarity_ba < 0.3:
        return 'acts_on'
    elif polarity_ab > 0.7 and polarity_ba > 0.7:
        return 'interacts_with'
    elif polarity_ab > 0.7:
        return 'influences'
    elif polarity_ba > 0.7 and polarity_ab < 0.3:
        return 'undergoes'
    elif polarity_ba > 0.7:
        return 'receives_from'
    elif polarity_ab < 0.3 and polarity_ba < 0.3:
        return 'coexists_with'
    else:
        return 'linked_to'


def compute_intensity(permanence: float, polarity_ab: float, polarity_ba: float) -> float:
    """Compute intensity for verb modification."""
    polarity_strength = abs(polarity_ab - polarity_ba)
    return (permanence + polarity_strength) / 2


def apply_intensifier(verb_key: str, intensity: float) -> str:
    """Apply attenuated or intensified verb form."""
    if verb_key in INTENSIFIERS:
        attenuated, intensified = INTENSIFIERS[verb_key]
        if intensity < 0.4:
            return attenuated
        elif intensity > 0.8:
            return intensified

    return VERBS.get(verb_key, verb_key)


def get_pre_modifiers(physics: LinkPhysics) -> List[str]:
    """Get pre-modifiers based on physics values."""
    modifiers = []

    # Energy
    if physics.energy > 8.0:
        modifiers.append('intensely')
    elif physics.energy < 0.5:
        modifiers.append('barely')

    # Surprise
    if physics.surprise > 0.7:
        modifiers.append('suddenly')
    elif physics.surprise < -0.7:
        modifiers.append('inevitably')
    elif physics.surprise > 0.4:
        modifiers.append('unexpectedly')
    elif physics.surprise < -0.4:
        modifiers.append('as expected')

    # Permanence
    if physics.permanence > 0.8:
        modifiers.append('definitely')
    elif physics.permanence < 0.2:
        modifiers.append('perhaps')
    elif physics.permanence < 0.4:
        modifiers.append('probably')
    elif physics.permanence > 0.6:
        modifiers.append('clearly')

    return modifiers[:2]  # Max 2


def get_post_modifiers(physics: LinkPhysics) -> List[str]:
    """Get post-modifiers based on physics values."""
    modifiers = []

    # Fear-anger
    if physics.fear_anger < -0.7:
        modifiers.append('with rage')
    elif physics.fear_anger > 0.7:
        modifiers.append('with terror')
    elif physics.fear_anger < -0.4:
        modifiers.append('with hostility')
    elif physics.fear_anger > 0.4:
        modifiers.append('with apprehension')

    # Trust-disgust
    if physics.trust_disgust < -0.7:
        modifiers.append('with disgust')
    elif physics.trust_disgust > 0.7:
        modifiers.append('with admiration')
    elif physics.trust_disgust < -0.4:
        modifiers.append('with distrust')
    elif physics.trust_disgust > 0.4:
        modifiers.append('with confidence')

    # Joy-sadness
    if physics.joy_sadness < -0.7:
        modifiers.append('with despair')
    elif physics.joy_sadness > 0.7:
        modifiers.append('with euphoria')
    elif physics.joy_sadness < -0.4:
        modifiers.append('with sadness')
    elif physics.joy_sadness > 0.4:
        modifiers.append('with satisfaction')

    return modifiers[:2]  # Max 2


def get_weight_annotation(weight: float) -> Optional[str]:
    """Get weight annotation."""
    if weight > 5.0:
        return '(fundamental)'
    elif weight > 3.0:
        return '(important)'
    elif weight < 1.0:
        return '(minor)'
    return None


def synthesize_link(physics: LinkPhysics) -> str:
    """
    Generate natural language synthesis from link physics.

    Args:
        physics: LinkPhysics values

    Returns:
        Natural language description
    """
    # Get base verb
    verb_key = get_base_verb_key(
        physics.hierarchy,
        physics.polarity_ab,
        physics.polarity_ba,
    )

    # Apply intensifier
    intensity = compute_intensity(
        physics.permanence,
        physics.polarity_ab,
        physics.polarity_ba,
    )
    verb = apply_intensifier(verb_key, intensity)

    # Get modifiers
    pre_mods = get_pre_modifiers(physics)
    post_mods = get_post_modifiers(physics)

    # Assemble
    parts = []
    if pre_mods:
        parts.append(' '.join(pre_mods))
    parts.append(verb)
    if post_mods:
        parts.append(' and '.join(post_mods))

    result = ' '.join(parts)

    # Add weight annotation
    weight_ann = get_weight_annotation(physics.weight)
    if weight_ann:
        result = f"{result} {weight_ann}"

    return result


def synthesize_from_dict(link_dict: Dict[str, Any]) -> str:
    """
    Generate synthesis from link dictionary.

    Args:
        link_dict: Link with physics fields

    Returns:
        Natural language description
    """
    physics = LinkPhysics(
        polarity_ab=link_dict.get('polarity_ab', link_dict.get('polarity', [0.5, 0.5])[0] if isinstance(link_dict.get('polarity'), list) else 0.5),
        polarity_ba=link_dict.get('polarity_ba', link_dict.get('polarity', [0.5, 0.5])[1] if isinstance(link_dict.get('polarity'), list) else 0.5),
        hierarchy=link_dict.get('hierarchy', 0.0),
        permanence=link_dict.get('permanence', link_dict.get('weight', 1.0) / (link_dict.get('weight', 1.0) + 1)),
        energy=link_dict.get('energy', 1.0),
        weight=link_dict.get('weight', 1.0),
        fear_anger=link_dict.get('fear_anger', 0.0),
        trust_disgust=link_dict.get('trust_disgust', 0.0),
        joy_sadness=link_dict.get('joy_sadness', 0.0),
        surprise=link_dict.get('surprise_anticipation', link_dict.get('surprise', 0.0)),
    )
    return synthesize_link(physics)


# =============================================================================
# BACKWARD PARSING (Phrases → Floats)
# =============================================================================

@dataclass
class ParsedPhysics:
    """Parsed physics values with confidence."""
    polarity_ab: float = 0.5
    polarity_ba: float = 0.5
    hierarchy: float = 0.0
    permanence: float = 0.5
    energy: float = 1.0
    weight: float = 1.0
    fear_anger: float = 0.0
    trust_disgust: float = 0.0
    joy_sadness: float = 0.0
    surprise: float = 0.0
    confidence: float = 0.0  # 0-1 how confident in parse


# Reverse mappings for parsing
VERB_TO_PHYSICS = {
    'encompasses': {'hierarchy': -0.8},
    'contains': {'hierarchy': -0.6},
    'elaborates': {'hierarchy': 0.6},
    'exemplifies': {'hierarchy': 0.8},
    'acts on': {'polarity_ab': 0.9, 'polarity_ba': 0.1},
    'influences': {'polarity_ab': 0.8, 'polarity_ba': 0.5},
    'interacts with': {'polarity_ab': 0.8, 'polarity_ba': 0.8},
    'receives from': {'polarity_ab': 0.5, 'polarity_ba': 0.8},
    'undergoes': {'polarity_ab': 0.1, 'polarity_ba': 0.9},
    'is linked to': {'polarity_ab': 0.5, 'polarity_ba': 0.5},
    'coexists with': {'polarity_ab': 0.2, 'polarity_ba': 0.2},

    # Intensified forms
    'firmly believes': {'polarity_ab': 0.9, 'trust_disgust': 0.8, 'permanence': 0.9},
    'believes in': {'polarity_ab': 0.8, 'trust_disgust': 0.6},
    'tends to believe': {'polarity_ab': 0.6, 'trust_disgust': 0.4, 'permanence': 0.3},
    'doubts': {'polarity_ab': 0.7, 'trust_disgust': -0.6},
    'rejects': {'polarity_ab': 0.9, 'trust_disgust': -0.8, 'permanence': 0.9},
    'contradicts': {'trust_disgust': -0.6, 'permanence': 0.8},
    'radically contradicts': {'trust_disgust': -0.9, 'permanence': 0.95},
    'confirms': {'trust_disgust': 0.6, 'permanence': 0.8},
    'absolutely confirms': {'trust_disgust': 0.9, 'permanence': 0.95},
    'supports': {'trust_disgust': 0.5, 'permanence': 0.6},
    'dominates': {'polarity_ab': 0.95, 'hierarchy': 0.6},
    'touches': {'polarity_ab': 0.5, 'permanence': 0.3},
    'demonstrates': {'trust_disgust': 0.9, 'permanence': 0.95},
    'suggests': {'trust_disgust': 0.4, 'permanence': 0.5},
    'proclaims': {'polarity_ab': 0.9, 'permanence': 0.9},
    'expresses': {'polarity_ab': 0.8},
    'sketches': {'polarity_ab': 0.5, 'permanence': 0.3},
}

PRE_MODIFIER_TO_PHYSICS = {
    'definitely': {'permanence': 0.9},
    'clearly': {'permanence': 0.7},
    'probably': {'permanence': 0.3},
    'perhaps': {'permanence': 0.1},
    'intensely': {'energy': 9.0},
    'actively': {'energy': 6.0},
    'weakly': {'energy': 1.0},
    'barely': {'energy': 0.3},
    'suddenly': {'surprise': 0.85},
    'unexpectedly': {'surprise': 0.55},
    'inevitably': {'surprise': -0.85},
    'as expected': {'surprise': -0.55},
}

POST_MODIFIER_TO_PHYSICS = {
    'with rage': {'fear_anger': -0.85},
    'with hostility': {'fear_anger': -0.55},
    'with apprehension': {'fear_anger': 0.55},
    'with terror': {'fear_anger': 0.85},
    'with disgust': {'trust_disgust': -0.85},
    'with distrust': {'trust_disgust': -0.55},
    'with confidence': {'trust_disgust': 0.55},
    'with admiration': {'trust_disgust': 0.85},
    'with despair': {'joy_sadness': -0.85},
    'with sadness': {'joy_sadness': -0.55},
    'with satisfaction': {'joy_sadness': 0.55},
    'with euphoria': {'joy_sadness': 0.85},
}

WEIGHT_TO_PHYSICS = {
    'fundamental': 6.0,
    'important': 4.0,
    'minor': 0.5,
}


def parse_phrase(phrase: str) -> ParsedPhysics:
    """
    Parse natural language phrase into physics values.

    Args:
        phrase: Natural language description (e.g., "definitely influences with confidence")

    Returns:
        ParsedPhysics with estimated values and confidence
    """
    result = ParsedPhysics()
    phrase_lower = phrase.lower().strip()
    matches = 0

    # Check weight annotations
    for annotation, weight in WEIGHT_TO_PHYSICS.items():
        if f'({annotation})' in phrase_lower:
            result.weight = weight
            phrase_lower = phrase_lower.replace(f'({annotation})', '').strip()
            matches += 1

    # Check pre-modifiers
    for modifier, physics in PRE_MODIFIER_TO_PHYSICS.items():
        if modifier in phrase_lower:
            for key, value in physics.items():
                setattr(result, key, value)
            matches += 1

    # Check post-modifiers
    for modifier, physics in POST_MODIFIER_TO_PHYSICS.items():
        if modifier in phrase_lower:
            for key, value in physics.items():
                setattr(result, key, value)
            matches += 1

    # Check verbs (longest match first)
    verb_matches = sorted(VERB_TO_PHYSICS.keys(), key=len, reverse=True)
    for verb in verb_matches:
        if verb in phrase_lower:
            for key, value in VERB_TO_PHYSICS[verb].items():
                setattr(result, key, value)
            matches += 1
            break

    # Calculate confidence based on matches
    # More matches = higher confidence
    result.confidence = min(1.0, matches / 4.0)

    return result


def parse_and_merge(
    phrase: str,
    existing: Optional[Dict[str, float]] = None,
    merge_weight: float = 0.5,
) -> Dict[str, float]:
    """
    Parse phrase and optionally merge with existing physics.

    Args:
        phrase: Natural language description
        existing: Existing physics values to merge with
        merge_weight: Weight for parsed values (0-1)

    Returns:
        Merged physics dictionary
    """
    parsed = parse_phrase(phrase)

    result = {
        'polarity_ab': parsed.polarity_ab,
        'polarity_ba': parsed.polarity_ba,
        'hierarchy': parsed.hierarchy,
        'permanence': parsed.permanence,
        'energy': parsed.energy,
        'weight': parsed.weight,
        'fear_anger': parsed.fear_anger,
        'trust_disgust': parsed.trust_disgust,
        'joy_sadness': parsed.joy_sadness,
        'surprise': parsed.surprise,
    }

    if existing:
        # Merge with weighted average
        existing_weight = 1.0 - merge_weight
        for key in result:
            if key in existing:
                result[key] = existing_weight * existing[key] + merge_weight * result[key]

    return result


# =============================================================================
# NARRATIVE SYNTHESIS FROM CRYSTALLIZATION
# =============================================================================

def synthesize_narrative_name(
    found_narratives: List[Tuple[str, str, float]],  # (id, name, alignment)
    intention_text: str,
) -> str:
    """
    Generate name for crystallized narrative.

    Args:
        found_narratives: List of (id, name, alignment) tuples
        intention_text: Original intention text

    Returns:
        Generated narrative name
    """
    if not found_narratives:
        # Use intention as basis
        words = intention_text.split()[:5]
        return ' '.join(words).title()

    # Combine top aligned narratives
    sorted_narr = sorted(found_narratives, key=lambda x: x[2], reverse=True)
    top_names = [name for _, name, align in sorted_narr[:2] if align > 0.5]

    if len(top_names) >= 2:
        return f"{top_names[0]} through {top_names[1]}"
    elif top_names:
        return f"Path to {top_names[0]}"
    else:
        words = intention_text.split()[:4]
        return ' '.join(words).title()


def synthesize_narrative_content(
    found_narratives: List[Tuple[str, str, float]],  # (id, content, alignment)
    intention_text: str,
    path_summary: Optional[str] = None,
) -> str:
    """
    Generate content for crystallized narrative.

    Args:
        found_narratives: List of (id, content, alignment) tuples
        intention_text: Original intention text
        path_summary: Optional summary of traversal path

    Returns:
        Generated narrative content
    """
    parts = []

    # Start with intention
    parts.append(f"Exploration of: {intention_text}")

    # Add found narratives with alignment
    if found_narratives:
        sorted_narr = sorted(found_narratives, key=lambda x: x[2], reverse=True)
        connections = []
        for _, content, align in sorted_narr[:3]:
            if align > 0.7:
                connections.append(f"strongly connected to: {content[:100]}")
            elif align > 0.4:
                connections.append(f"relates to: {content[:80]}")
        if connections:
            parts.append("Discovered: " + "; ".join(connections))

    # Add path if provided
    if path_summary:
        parts.append(f"Through: {path_summary}")

    return ". ".join(parts)


def synthesize_from_crystallization(
    intention_text: str,
    found_narratives: List[Tuple[str, str, str, float]],  # (id, name, content, alignment)
    path_summary: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Generate name and content for crystallized narrative.

    Args:
        intention_text: Original intention text
        found_narratives: List of (id, name, content, alignment) tuples
        path_summary: Optional summary of traversal path

    Returns:
        Tuple of (name, content)
    """
    name_tuples = [(id, name, align) for id, name, _, align in found_narratives]
    content_tuples = [(id, content, align) for id, _, content, align in found_narratives]

    name = synthesize_narrative_name(name_tuples, intention_text)
    content = synthesize_narrative_content(content_tuples, intention_text, path_summary)

    return name, content
