"""
Link Vocabulary — Nature to Floats Conversion

Vocabulary for link "nature" field that determines physics floats.
Agents select a nature term, floats are derived, synthesis is generated.

Flow: nature (vocab term) -> floats -> synthesis (generated)

Structure: [pre_modifiers] + base_verb + [post_modifiers]
Example: "suddenly proves, with admiration"

Usage:
    from mind.physics.link_vocab import nature_to_floats, get_vocab_reference

    floats = nature_to_floats("suddenly proves, with admiration")
    # Returns: {
    #     'permanence': 0.9,
    #     'trust_disgust': 0.6,
    #     'surprise_anticipation': 0.8,
    # }

    # With conflict detection:
    floats, conflicts = parse_with_conflicts("definitely perhaps believes in")
    # conflicts = [{'key': 'permanence', 'previous': 0.9, 'new': 0.1, 'from': 'perhaps'}]
"""

from typing import Dict, Any, List, Optional, Tuple
import re


# =============================================================================
# BASE VERBS (hierarchy + polarity)
# =============================================================================

BASE_VERBS = {
    "encompasses": {"hierarchy": -0.85, "polarity": [1.0, 1.0]},
    "contains": {"hierarchy": -0.6, "polarity": [1.0, 1.0]},
    "elaborates": {"hierarchy": 0.6, "polarity": [1.0, 1.0]},
    "exemplifies": {"hierarchy": 0.85, "polarity": [1.0, 1.0]},
    "acts on": {"polarity": [0.85, 0.15]},
    "influences": {"polarity": [0.8, 0.5]},
    "interacts with": {"polarity": [0.8, 0.8]},
    "receives from": {"polarity": [0.5, 0.8]},
    "undergoes": {"polarity": [0.15, 0.85]},
    "is linked to": {"polarity": [0.5, 0.5]},
    "coexists with": {"polarity": [0.2, 0.2]},
}


# =============================================================================
# OWNERSHIP VERBS (Thing <-> Actor)
# =============================================================================

OWNERSHIP_VERBS = {
    "belongs to": {"hierarchy": 0.3, "type_a": "thing", "type_b": "actor"},
    "owns": {"hierarchy": -0.3, "type_a": "actor", "type_b": "thing"},
    "holds": {"hierarchy": -0.3, "permanence": 0.9, "type_a": "actor", "type_b": "thing"},
    "uses": {"polarity": [0.85, 0.15], "type_a": "actor", "type_b": "thing"},
    "depends on": {"polarity": [0.15, 0.85], "type_a": "actor", "type_b": "thing"},
    "serves": {"polarity": [0.85, 0.15], "type_a": "thing", "type_b": "actor"},
}


# =============================================================================
# EVIDENTIAL VERBS (Thing/Moment -> Narrative)
# =============================================================================

EVIDENTIAL_VERBS = {
    "proves": {"permanence": 0.9, "trust_disgust": 0.6, "type_a": "thing", "type_b": "narrative"},
    "refutes": {"permanence": 0.9, "trust_disgust": -0.6, "type_a": "thing", "type_b": "narrative"},
    "suggests": {"permanence": 0.65, "trust_disgust": 0.4, "type_a": "thing", "type_b": "narrative"},
    "questions": {"permanence": 0.65, "trust_disgust": -0.4, "type_a": "thing", "type_b": "narrative"},
    "evokes": {"permanence": 0.3, "type_a": ["thing", "moment"], "type_b": "narrative"},
    "symbolizes": {"hierarchy": 0.6, "type_a": "thing", "type_b": "narrative"},
    "confirms": {"permanence": 0.9, "trust_disgust": 0.6, "type_a": "moment", "type_b": "narrative"},
    "contradicts": {"permanence": 0.9, "trust_disgust": -0.6, "type_a": "moment", "type_b": "narrative"},
    "supports": {"permanence": 0.65, "trust_disgust": 0.4, "type_a": "moment", "type_b": "narrative"},
    "illustrates": {"hierarchy": 0.6, "type_a": "moment", "type_b": "narrative"},
}


# =============================================================================
# SPATIAL VERBS (Space <-> Actor/Thing)
# =============================================================================

SPATIAL_VERBS = {
    "shelters": {"hierarchy": -0.75, "type_a": "space", "type_b": ["actor", "thing"]},
    "welcomes": {"hierarchy": -0.6, "energy": 7.0, "type_a": "space", "type_b": "actor"},
    "imprisons": {"hierarchy": -0.6, "fear_anger": 0.5, "type_a": "space", "type_b": "actor"},
    "protects": {"hierarchy": -0.6, "joy_sadness": 0.5, "type_a": "space", "type_b": "actor"},
    "isolates": {"hierarchy": -0.6, "joy_sadness": -0.5, "type_a": "space", "type_b": "actor"},
    "encloses": {"hierarchy": -0.6, "permanence": 0.9, "type_a": "space", "type_b": "thing"},
    "exposes": {"hierarchy": -0.6, "permanence": 0.3, "type_a": "space", "type_b": "thing"},
    "occupies": {"polarity": [0.85, 0.15], "type_a": "actor", "type_b": "space"},
    "inhabits": {"polarity": [0.85, 0.15], "permanence": 0.9, "type_a": "actor", "type_b": "space"},
    "flees": {"polarity": [0.15, 0.85], "type_a": "actor", "type_b": "space"},
    "dominates": {"hierarchy": 0.6, "type_a": "actor", "type_b": "space"},
}


# =============================================================================
# ACTOR VERBS (Actor -> Moment/Narrative)
# =============================================================================

ACTOR_VERBS = {
    "expresses": {"polarity": [0.85, 0.15], "type_a": "actor", "type_b": "moment"},
    "initiates": {"polarity": [0.8, 0.5], "type_a": "actor", "type_b": "moment"},
    "believes in": {"polarity": [0.85, 0.15], "trust_disgust": 0.6, "type_a": "actor", "type_b": "narrative"},
    "doubts": {"polarity": [0.85, 0.15], "trust_disgust": -0.6, "type_a": "actor", "type_b": "narrative"},
    "created": {"hierarchy": 0.6, "type_a": "actor", "type_b": "narrative"},
    "is defined by": {"hierarchy": -0.6, "type_a": "actor", "type_b": "narrative"},
}


# =============================================================================
# NARRATIVE VERBS (Narrative -> Narrative)
# =============================================================================

NARRATIVE_VERBS = {
    "radically contradicts": {"trust_disgust": -0.8, "permanence": 0.9, "type_a": "narrative", "type_b": "narrative"},
    "is in tension with": {"trust_disgust": -0.6, "permanence": 0.3, "type_a": "narrative", "type_b": "narrative"},
    "is the mechanism of": {"hierarchy": 0.8, "type_a": "narrative", "type_b": "narrative"},
    "contextualizes": {"hierarchy": -0.6, "trust_disgust": 0.6, "type_a": "narrative", "type_b": "narrative"},
}


# =============================================================================
# TEMPORAL VERBS (Moment -> Moment)
# =============================================================================

TEMPORAL_VERBS = {
    "precedes": {"polarity": [0.9, 0.0], "hierarchy": 0.0, "permanence": 1.0, "type_a": "moment", "type_b": "moment"},
    "follows": {"polarity": [0.0, 0.9], "hierarchy": 0.0, "permanence": 1.0, "type_a": "moment", "type_b": "moment"},
    "triggers": {"polarity": [0.95, 0.05], "hierarchy": 0.3, "permanence": 0.9, "type_a": "moment", "type_b": "moment"},
    "leads to": {"polarity": [0.85, 0.0], "hierarchy": 0.2, "permanence": 0.7, "type_a": "moment", "type_b": "moment"},
    "might lead to": {"polarity": [0.6, 0.0], "hierarchy": 0.1, "permanence": 0.3, "type_a": "moment", "type_b": "moment"},
    "interrupts": {"polarity": [0.9, 0.1], "hierarchy": 0.0, "permanence": 0.85, "surprise_anticipation": 0.7, "type_a": "moment", "type_b": "moment"},
    "is interrupted by": {"polarity": [0.1, 0.9], "hierarchy": 0.0, "permanence": 0.85, "surprise_anticipation": 0.7, "type_a": "moment", "type_b": "moment"},
    "enables": {"polarity": [0.85, 0.15], "hierarchy": 0.4, "permanence": 0.6, "type_a": "moment", "type_b": "moment"},
    "prevents": {"polarity": [0.9, 0.1], "hierarchy": 0.0, "permanence": 0.7, "trust_disgust": -0.3, "type_a": "moment", "type_b": "moment"},
}


# =============================================================================
# DOCTOR VERBS (Issue/Task/Objective relations)
# =============================================================================

DOCTOR_VERBS = {
    "blocks": {"polarity": [0.9, 0.1], "hierarchy": 0.0, "permanence": 0.7, "trust_disgust": -0.4, "fear_anger": 0.3, "type_a": "narrative", "type_b": "narrative"},
    "serves": {"polarity": [0.85, 0.15], "hierarchy": 0.5, "permanence": 0.6, "trust_disgust": 0.4, "joy_sadness": 0.2, "type_a": "narrative", "type_b": "narrative"},
    "includes": {"polarity": [0.7, 0.3], "hierarchy": -0.5, "permanence": 0.8, "type_a": "narrative", "type_b": "narrative"},
    "concerns": {"polarity": [0.8, 0.2], "hierarchy": 0.3, "permanence": 0.9, "trust_disgust": -0.3, "type_a": "narrative", "type_b": "thing"},
    "is about": {"polarity": [0.8, 0.2], "hierarchy": 0.3, "permanence": 0.9, "type_a": "narrative", "type_b": "thing"},
    "imports": {"polarity": [0.8, 0.2], "hierarchy": 0.3, "permanence": 0.9, "type_a": "thing", "type_b": "thing"},
}


# =============================================================================
# PRE-MODIFIERS (before verb)
# =============================================================================

PRE_MODIFIERS = {
    # Certainty
    "perhaps": {"permanence": 0.1},
    "probably": {"permanence": 0.3},
    "clearly": {"permanence": 0.7},
    "definitely": {"permanence": 0.9},

    # Surprise
    "suddenly": {"surprise_anticipation": 0.8},
    "inevitably": {"surprise_anticipation": -0.8},
    "unexpectedly": {"surprise_anticipation": 0.5},
    "as expected": {"surprise_anticipation": -0.5},

    # Energy
    "intensely": {"energy": 9.0},
    "barely": {"energy": 0.25},
    "actively": {"energy": 6.5},
    "weakly": {"energy": 1.5},
}


# =============================================================================
# POST-MODIFIERS (after verb, with comma)
# =============================================================================

POST_MODIFIERS = {
    # Fear/Anger axis
    "with rage": {"fear_anger": -0.8},
    "with terror": {"fear_anger": 0.8},
    "with hostility": {"fear_anger": -0.5},
    "with apprehension": {"fear_anger": 0.5},

    # Trust/Disgust axis
    "with disgust": {"trust_disgust": -0.8},
    "with admiration": {"trust_disgust": 0.8},
    "with distrust": {"trust_disgust": -0.5},
    "with confidence": {"trust_disgust": 0.5},

    # Joy/Sadness axis
    "with despair": {"joy_sadness": -0.8},
    "with euphoria": {"joy_sadness": 0.8},
    "with sadness": {"joy_sadness": -0.5},
    "with satisfaction": {"joy_sadness": 0.5},
}


# =============================================================================
# WEIGHT ANNOTATIONS
# =============================================================================

WEIGHT_ANNOTATIONS = {
    "(fundamental)": {"weight": 6.0},
    "(important)": {"weight": 4.0},
    "(minor)": {"weight": 0.5},
}


# =============================================================================
# INTENSIFIERS (attenuated, intensified forms)
# =============================================================================

INTENSIFIERS = {
    # Hierarchy verbs
    "encompasses": ["borders", "completely encompasses"],
    "contains": ["touches", "fully contains"],
    "elaborates": ["mentions", "deeply elaborates"],
    "exemplifies": ["suggests", "perfectly exemplifies"],

    # Polarity verbs
    "acts on": ["brushes", "dominates"],
    "influences": ["touches", "controls"],
    "interacts with": ["coexists with", "is entangled with"],
    "undergoes": ["is touched by", "is overwhelmed by"],

    # Ownership verbs
    "belongs to": ["is associated with", "is inseparable from"],
    "owns": ["has access to", "possesses completely"],
    "holds": ["touches", "grips tightly"],
    "uses": ["considers", "exploits"],

    # Evidential verbs
    "proves": ["suggests", "demonstrates beyond doubt"],
    "refutes": ["questions", "completely invalidates"],
    "confirms": ["supports", "absolutely confirms"],
    "contradicts": ["nuances", "radically contradicts"],
    "illustrates": ["evokes", "embodies"],

    # Actor verbs
    "believes in": ["considers", "is convinced of"],
    "doubts": ["questions", "completely rejects"],
    "expresses": ["hints at", "proclaims"],
    "initiates": ["considers", "launches"],

    # Spatial verbs
    "shelters": ["borders", "completely encloses"],
    "welcomes": ["allows", "embraces"],
    "imprisons": ["constrains", "traps forever"],

    # Temporal verbs
    "precedes": ["might precede", "immediately precedes"],
    "triggers": ["enables", "directly causes"],
    "leads to": ["might lead to", "inevitably leads to"],
    "interrupts": ["pauses", "completely derails"],

    # Doctor verbs
    "blocks": ["hinders", "completely blocks"],
    "serves": ["supports", "perfectly serves"],
    "concerns": ["relates to", "is entirely about"],
}


# =============================================================================
# TRANSLATIONS (EN -> FR)
# =============================================================================

TRANSLATIONS = {
    'en': {
        # Base
        'encompasses': 'encompasses', 'contains': 'contains', 'elaborates': 'elaborates',
        'exemplifies': 'exemplifies', 'acts on': 'acts on', 'interacts with': 'interacts with',
        'undergoes': 'undergoes',
        # Ownership
        'belongs to': 'belongs to', 'owns': 'owns', 'holds': 'holds', 'uses': 'uses',
        # Evidential
        'proves': 'proves', 'refutes': 'refutes', 'suggests': 'suggests',
        'confirms': 'confirms', 'contradicts': 'contradicts',
        # Spatial
        'shelters': 'shelters', 'welcomes': 'welcomes', 'imprisons': 'imprisons',
        # Actor
        'believes in': 'believes in', 'doubts': 'doubts', 'expresses': 'expresses',
        # Temporal
        'precedes': 'precedes', 'triggers': 'triggers', 'leads to': 'leads to',
        'interrupts': 'interrupts',
        # Doctor
        'blocks': 'blocks', 'serves': 'serves', 'includes': 'includes', 'concerns': 'concerns',
        # Modifiers
        'definitely': 'definitely', 'clearly': 'clearly', 'probably': 'probably',
        'perhaps': 'perhaps', 'suddenly': 'suddenly',
        'with rage': 'with rage', 'with confidence': 'with confidence',
        'with distrust': 'with distrust', 'with admiration': 'with admiration',
        'with sadness': 'with sadness', 'with despair': 'with despair',
    },
    'fr': {
        # Base
        'encompasses': 'englobe', 'contains': 'contient', 'elaborates': 'détaille',
        'exemplifies': 'exemplifie', 'acts on': 'agit sur', 'interacts with': 'interagit avec',
        'undergoes': 'subit',
        # Ownership
        'belongs to': 'appartient à', 'owns': 'possède', 'holds': 'détient', 'uses': 'utilise',
        # Evidential
        'proves': 'prouve', 'refutes': 'réfute', 'suggests': 'suggère',
        'confirms': 'confirme', 'contradicts': 'contredit',
        # Spatial
        'shelters': 'abrite', 'welcomes': 'accueille', 'imprisons': 'emprisonne',
        # Actor
        'believes in': 'croit en', 'doubts': 'doute de', 'expresses': 'exprime',
        # Temporal
        'precedes': 'précède', 'triggers': 'déclenche', 'leads to': 'mène à',
        'interrupts': 'interrompt',
        # Doctor
        'blocks': 'bloque', 'serves': 'sert', 'includes': 'inclut', 'concerns': 'concerne',
        # Modifiers
        'definitely': 'définitivement', 'clearly': 'clairement', 'probably': 'probablement',
        'perhaps': 'peut-être', 'suddenly': 'soudain',
        'with rage': 'avec rage', 'with confidence': 'avec confiance',
        'with distrust': 'avec méfiance', 'with admiration': 'avec admiration',
        'with sadness': 'avec tristesse', 'with despair': 'avec désespoir',
    }
}


# =============================================================================
# ALL VERBS (combined for lookup)
# =============================================================================

ALL_VERBS = {
    **BASE_VERBS,
    **OWNERSHIP_VERBS,
    **EVIDENTIAL_VERBS,
    **SPATIAL_VERBS,
    **ACTOR_VERBS,
    **NARRATIVE_VERBS,
    **TEMPORAL_VERBS,
    **DOCTOR_VERBS,
}


# =============================================================================
# DEFAULT FLOATS
# =============================================================================

def default_floats() -> Dict[str, Any]:
    """Return default physics floats."""
    return {
        'hierarchy': 0.0,
        'polarity': [0.5, 0.5],
        'permanence': 0.5,
        'joy_sadness': 0.0,
        'trust_disgust': 0.0,
        'fear_anger': 0.0,
        'surprise_anticipation': 0.0,
        'energy': None,  # None = don't override
        'weight': None,
    }


# =============================================================================
# PARSING
# =============================================================================

def parse_nature(nature: str) -> Tuple[List[str], str, List[str]]:
    """
    Parse a nature string into components.

    Format: [pre_modifiers] + verb + [, post_modifiers]

    Returns: (pre_modifiers, verb, post_modifiers)
    """
    nature = nature.strip().lower()

    # Split on comma for post-modifiers
    if ',' in nature:
        main_part, post_part = nature.split(',', 1)
        post_modifiers = [post_part.strip()]
    else:
        main_part = nature
        post_modifiers = []

    # Find the verb (longest match from ALL_VERBS)
    found_verb = None
    found_pos = -1

    for verb in sorted(ALL_VERBS.keys(), key=len, reverse=True):
        pos = main_part.find(verb)
        if pos != -1:
            found_verb = verb
            found_pos = pos
            break

    if found_verb is None:
        return [], main_part.strip(), post_modifiers

    # Extract pre-modifiers
    pre_part = main_part[:found_pos].strip()
    pre_modifiers = []

    if pre_part:
        for mod in sorted(PRE_MODIFIERS.keys(), key=len, reverse=True):
            if mod in pre_part:
                pre_modifiers.append(mod)
                pre_part = pre_part.replace(mod, '').strip()

    return pre_modifiers, found_verb, post_modifiers


def nature_to_floats(nature: str) -> Dict[str, Any]:
    """
    Convert a nature string to physics floats.

    Args:
        nature: Nature string like "suddenly proves, with admiration"

    Returns:
        Dict with physics floats
    """
    floats, _ = parse_with_conflicts(nature)
    return floats


def parse_with_conflicts(nature: str) -> Tuple[Dict[str, Any], List[Dict]]:
    """
    Parse nature string and detect conflicts.

    Returns:
        (floats, conflicts) where conflicts lists overwritten values
    """
    pre_mods, verb, post_mods = parse_nature(nature)
    defaults = default_floats()
    floats = default_floats()
    conflicts = []

    def apply_values(values: Dict, source: str):
        for key, value in values.items():
            if key in ['type_a', 'type_b']:
                continue
            if key in floats and floats[key] != defaults[key]:
                conflicts.append({
                    'key': key,
                    'previous': floats[key],
                    'new': value,
                    'from': source
                })
            floats[key] = value

    # Apply verb first
    if verb in ALL_VERBS:
        apply_values(ALL_VERBS[verb], verb)

    # Apply pre-modifiers
    for mod in pre_mods:
        if mod in PRE_MODIFIERS:
            apply_values(PRE_MODIFIERS[mod], mod)

    # Apply post-modifiers
    for mod in post_mods:
        if mod in POST_MODIFIERS:
            apply_values(POST_MODIFIERS[mod], mod)

    # Check for weight annotations
    nature_lower = nature.lower()
    for ann, props in WEIGHT_ANNOTATIONS.items():
        if ann in nature_lower:
            apply_values(props, ann)

    return floats, conflicts


# =============================================================================
# INTENSIFIERS
# =============================================================================

def get_intensified_verb(base_verb: str, intensity: float) -> str:
    """
    Get verb form based on intensity.

    intensity: -1 to +1
        -1 = attenuated, 0 = base, +1 = intensified
    """
    if base_verb not in INTENSIFIERS:
        return base_verb

    attenuated, intensified = INTENSIFIERS[base_verb]

    if intensity < -0.3:
        return attenuated
    elif intensity > 0.3:
        return intensified
    else:
        return base_verb


def select_verb_form(base_verb: str, permanence: float, energy: float = 0.0) -> str:
    """Select verb intensity based on link properties."""
    energy_norm = min(energy, 10) / 10 if energy else 0.5
    intensity = (permanence - 0.5) + (energy_norm - 0.5)
    return get_intensified_verb(base_verb, intensity)


# =============================================================================
# TRANSLATION
# =============================================================================

def translate(key: str, lang: str = 'en') -> str:
    """Translate a term to the specified language."""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)


# =============================================================================
# HELPERS
# =============================================================================

def get_verb_for_nature(nature: str) -> Optional[str]:
    """Extract the base verb from a nature string."""
    _, verb, _ = parse_nature(nature)
    return verb if verb in ALL_VERBS else None


def get_vocab_reference() -> str:
    """Get formatted vocabulary reference for agents."""
    lines = [
        "# Link Nature Vocabulary",
        "",
        "Format: `[pre_modifier] verb [, post_modifier]`",
        "Example: `suddenly proves, with admiration`",
        "",
        "---",
        "",
        "## Verbs",
        "",
    ]

    verb_categories = [
        ("Base", BASE_VERBS),
        ("Ownership", OWNERSHIP_VERBS),
        ("Evidential", EVIDENTIAL_VERBS),
        ("Spatial", SPATIAL_VERBS),
        ("Actor", ACTOR_VERBS),
        ("Narrative", NARRATIVE_VERBS),
        ("Temporal", TEMPORAL_VERBS),
        ("Doctor", DOCTOR_VERBS),
    ]

    for name, verbs in verb_categories:
        lines.append(f"**{name}:** {', '.join(verbs.keys())}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Pre-Modifiers",
        "",
        f"**Certainty:** {', '.join(k for k in PRE_MODIFIERS if 'permanence' in PRE_MODIFIERS[k])}",
        f"**Surprise:** {', '.join(k for k in PRE_MODIFIERS if 'surprise' in str(PRE_MODIFIERS[k]))}",
        f"**Intensity:** {', '.join(k for k in PRE_MODIFIERS if 'energy' in PRE_MODIFIERS[k])}",
        "",
        "---",
        "",
        "## Post-Modifiers",
        "",
        f"**Anger/Fear:** {', '.join(k for k in POST_MODIFIERS if 'fear_anger' in POST_MODIFIERS[k])}",
        f"**Trust/Disgust:** {', '.join(k for k in POST_MODIFIERS if 'trust_disgust' in POST_MODIFIERS[k])}",
        f"**Joy/Sadness:** {', '.join(k for k in POST_MODIFIERS if 'joy_sadness' in POST_MODIFIERS[k])}",
    ])

    return '\n'.join(lines)


def get_vocab_compact() -> Dict[str, List[str]]:
    """Get compact vocabulary for programmatic use."""
    return {
        'base_verbs': list(BASE_VERBS.keys()),
        'ownership_verbs': list(OWNERSHIP_VERBS.keys()),
        'evidential_verbs': list(EVIDENTIAL_VERBS.keys()),
        'spatial_verbs': list(SPATIAL_VERBS.keys()),
        'actor_verbs': list(ACTOR_VERBS.keys()),
        'narrative_verbs': list(NARRATIVE_VERBS.keys()),
        'temporal_verbs': list(TEMPORAL_VERBS.keys()),
        'doctor_verbs': list(DOCTOR_VERBS.keys()),
        'pre_modifiers': list(PRE_MODIFIERS.keys()),
        'post_modifiers': list(POST_MODIFIERS.keys()),
        'weight_annotations': list(WEIGHT_ANNOTATIONS.keys()),
    }
