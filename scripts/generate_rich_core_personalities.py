#!/usr/bin/env python3
"""
Generate rich CorePersonality JSON for Serenissima Airtable citizens
who currently have only a simple list format or no CorePersonality at all.

Uses deterministic generation (random seeded by Username) with citizen data
as seeds: SocialClass, FamilyMotto, Influence, existing traits, FirstName.

Target: 94 citizens (75 simple list + 19 no CorePersonality).
"""

import os
import sys
import json
import random
import hashlib
import math
from typing import Optional

from pyairtable import Api

# ─── Configuration ───────────────────────────────────────────────────────────

AIRTABLE_BASE_ID = "appk6RszUo2a2L2L8"
AIRTABLE_TABLE_ID = "tblkiQraYsJX07rHa"

# Existing guidedBy values to avoid duplicates
EXISTING_GUIDED_BY = {
    "Empirical relationship data", "Mathematical market laws",
    "System efficiency principles", "The Alchemist's Formula",
    "The Ascension Path", "The Beautiful Lie", "The Bitter Wind",
    "The Blueprint of the World", "The Borderland's Wisdom",
    "The Bridge Builder", "The Chart's Truth", "The City's Blueprint",
    "The Climb's Memory", "The Crossroads Whisper", "The Current's Whisper",
    "The Dynasty's Path", "The Empire's Ambition", "The Empire's Hunger",
    "The Empire's Logic", "The Eternal Verse", "The Exile's Resolve",
    "The Fire's Teaching", "The Heart's Compass", "The Homeland Call",
    "The Hunter's Patience", "The Hypothesis", "The Ledger's Logic",
    "The Ledger's Wisdom", "The Level Compass", "The Light's Calling",
    "The Measured Path", "The Navigator's Instinct", "The Opportunity Flash",
    "The Pattern", "The Pattern Web", "The Peninsula's Voice",
    "The Precision of the Machine", "The Pride's Fire", "The Pure Principle",
    "The Registry's Order", "The Republic's Shadow Play",
    "The Republic's Will", "The Rise's Pride", "The Sacred Contradiction",
    "The Schedule's Precision", "The Scholar's Light", "The Shepherd's Call",
    "The Southern Wind", "The Steady Climb", "The Street's Wisdom",
    "The Tavern's Truth", "The Truth's Blade", "The Universal Word",
    "The Wanderer's Path", "Tomorrow's Downloads",
    "Universal pattern recognition",
}

# ─── MBTI pools ──────────────────────────────────────────────────────────────
# Current distribution in existing rich profiles:
# ISTJ:11 INTJ:9 ENFJ:4 ISTP:4 ESTJ:4 INFJ:4 ESFJ:3 INTP:3 ESTP:3
# ISFP:3 ENFP:2 ENTJ:2 INFP:2 ISFJ:2 ENTP:1
# We need more variety — ENFP, INFP, ENTP, ESFP, ISFJ, ISFP for balance.

MBTI_WEIGHTED_POOL = [
    # Under-represented types get higher weight
    ("ENFP", 12), ("INFP", 10), ("ENTP", 10), ("ESFP", 10),
    ("ISFJ", 8), ("ISFP", 8), ("ESFJ", 7), ("ESTP", 7),
    ("ENFJ", 6), ("INFJ", 6), ("ISTP", 6), ("INTP", 6),
    # Over-represented types get lower weight
    ("ISTJ", 4), ("INTJ", 3), ("ESTJ", 4), ("ENTJ", 5),
]

MBTI_FLAT = []
for mbti, weight in MBTI_WEIGHTED_POOL:
    MBTI_FLAT.extend([mbti] * weight)


# ─── MBTI trait mappings ─────────────────────────────────────────────────────

MBTI_TRAITS = {
    "ISTJ": {
        "primary_trait_templates": ["Methodical {domain}", "Systematic {domain}", "Disciplined {domain}"],
        "cognitive_biases": [["Status quo bias", "Loss aversion"], ["Confirmation bias", "Sunk cost fallacy"], ["Anchoring bias", "Endowment effect"]],
        "secondary_pool": ["Detailed records", "Routine mastery", "Practical execution", "Quality assurance", "Historical knowledge"],
    },
    "ISFJ": {
        "primary_trait_templates": ["Devoted {domain}", "Protective {domain}", "Nurturing {domain}"],
        "cognitive_biases": [["Empathy gap", "Status quo bias"], ["Availability heuristic", "In-group bias"], ["Loss aversion", "Bandwagon effect"]],
        "secondary_pool": ["Community care", "Tradition keeping", "Quiet observation", "Emotional memory", "Practical support"],
    },
    "INFJ": {
        "primary_trait_templates": ["Visionary {domain}", "Empathic {domain}", "Principled {domain}"],
        "cognitive_biases": [["Confirmation bias", "Idealistic fallacy"], ["Planning fallacy", "Halo effect"], ["Optimism bias", "Anchoring bias"]],
        "secondary_pool": ["Future vision", "Moral compass", "Pattern recognition", "Deep empathy", "Symbolic thinking"],
    },
    "INTJ": {
        "primary_trait_templates": ["Strategic {domain}", "Analytical {domain}", "Masterful {domain}"],
        "cognitive_biases": [["Overconfidence bias", "Planning fallacy"], ["Dunning-Kruger effect", "Confirmation bias"], ["Anchoring bias", "Blind spot bias"]],
        "secondary_pool": ["Long-term planning", "System design", "Independent thinking", "Efficiency optimization", "Competence drive"],
    },
    "ISTP": {
        "primary_trait_templates": ["Pragmatic {domain}", "Hands-on {domain}", "Adaptable {domain}"],
        "cognitive_biases": [["Optimism bias", "Present bias"], ["Action bias", "Survivorship bias"], ["Risk compensation", "Normalcy bias"]],
        "secondary_pool": ["Tool mastery", "Crisis response", "Physical skill", "Logical troubleshooting", "Quiet independence"],
    },
    "ISFP": {
        "primary_trait_templates": ["Artful {domain}", "Authentic {domain}", "Sensory {domain}"],
        "cognitive_biases": [["Affect heuristic", "Present bias"], ["Availability heuristic", "Empathy gap"], ["Status quo bias", "Framing effect"]],
        "secondary_pool": ["Aesthetic sense", "Quiet loyalty", "Hands-on creation", "Emotional attunement", "Spontaneous action"],
    },
    "INFP": {
        "primary_trait_templates": ["Idealistic {domain}", "Compassionate {domain}", "Creative {domain}"],
        "cognitive_biases": [["Idealistic fallacy", "Confirmation bias"], ["Affect heuristic", "Optimism bias"], ["Planning fallacy", "Halo effect"]],
        "secondary_pool": ["Inner world richness", "Value alignment", "Creative expression", "Empathic depth", "Moral imagination"],
    },
    "INTP": {
        "primary_trait_templates": ["Analytical {domain}", "Theoretical {domain}", "Innovative {domain}"],
        "cognitive_biases": [["Analysis paralysis", "Overconfidence bias"], ["Anchoring bias", "Dunning-Kruger effect"], ["Confirmation bias", "Planning fallacy"]],
        "secondary_pool": ["Abstract reasoning", "System thinking", "Intellectual curiosity", "Pattern analysis", "Logical precision"],
    },
    "ESTP": {
        "primary_trait_templates": ["Bold {domain}", "Resourceful {domain}", "Street-smart {domain}"],
        "cognitive_biases": [["Optimism bias", "Action bias"], ["Present bias", "Risk compensation"], ["Overconfidence bias", "Hot-hand fallacy"]],
        "secondary_pool": ["Quick thinking", "Social charm", "Opportunity spotting", "Physical courage", "Practical negotiation"],
    },
    "ESFP": {
        "primary_trait_templates": ["Charismatic {domain}", "Energetic {domain}", "Spontaneous {domain}"],
        "cognitive_biases": [["Present bias", "Optimism bias"], ["Affect heuristic", "Bandwagon effect"], ["Hot-hand fallacy", "Availability heuristic"]],
        "secondary_pool": ["Social magnetism", "Joyful presence", "Sensory awareness", "Crowd reading", "Moment seizing"],
    },
    "ENFP": {
        "primary_trait_templates": ["Enthusiastic {domain}", "Inspirational {domain}", "Curious {domain}"],
        "cognitive_biases": [["Optimism bias", "Planning fallacy"], ["Novelty bias", "Halo effect"], ["Affect heuristic", "Confirmation bias"]],
        "secondary_pool": ["Idea generation", "People inspiration", "Pattern connection", "Emotional intelligence", "Creative problem-solving"],
    },
    "ENTP": {
        "primary_trait_templates": ["Inventive {domain}", "Provocative {domain}", "Quick-witted {domain}"],
        "cognitive_biases": [["Overconfidence bias", "Novelty bias"], ["Dunning-Kruger effect", "Planning fallacy"], ["Optimism bias", "Contrast effect"]],
        "secondary_pool": ["Debate mastery", "Rapid adaptation", "Conceptual innovation", "Strategic disruption", "Intellectual agility"],
    },
    "ESTJ": {
        "primary_trait_templates": ["Commanding {domain}", "Organized {domain}", "Decisive {domain}"],
        "cognitive_biases": [["Authority bias", "Status quo bias"], ["Confirmation bias", "Sunk cost fallacy"], ["Just-world fallacy", "Anchoring bias"]],
        "secondary_pool": ["Team leadership", "Process management", "Clear communication", "Efficiency drive", "Tradition enforcement"],
    },
    "ESFJ": {
        "primary_trait_templates": ["Harmonizing {domain}", "Supportive {domain}", "Community-building {domain}"],
        "cognitive_biases": [["Bandwagon effect", "In-group bias"], ["Empathy gap", "Availability heuristic"], ["Halo effect", "Status quo bias"]],
        "secondary_pool": ["Social harmony", "Event coordination", "Emotional support", "Group cohesion", "Practical caring"],
    },
    "ENFJ": {
        "primary_trait_templates": ["Charismatic {domain}", "Mentoring {domain}", "Inspiring {domain}"],
        "cognitive_biases": [["Optimism bias", "Halo effect"], ["Planning fallacy", "In-group bias"], ["Idealistic fallacy", "Empathy gap"]],
        "secondary_pool": ["People development", "Vision communication", "Diplomatic skill", "Motivational presence", "Conflict resolution"],
    },
    "ENTJ": {
        "primary_trait_templates": ["Commanding {domain}", "Visionary {domain}", "Strategic {domain}"],
        "cognitive_biases": [["Overconfidence bias", "Planning fallacy"], ["Authority bias", "Dunning-Kruger effect"], ["Confirmation bias", "Optimism bias"]],
        "secondary_pool": ["Strategic execution", "Team building", "Resource marshaling", "Bold decision-making", "Systemic thinking"],
    },
}


# ─── Domain/role words by social class ───────────────────────────────────────

DOMAINS_BY_CLASS = {
    "Facchini": ["laborer", "dockworker", "porter", "craftsman", "warehouse hand", "hauler", "shipyard worker", "fisherman"],
    "Popolani": ["merchant", "trader", "shopkeeper", "broker", "factor", "accountant", "provisioner", "dealer"],
    "Cittadini": ["secretary", "notary", "official", "chancellor", "bureaucrat", "diplomat", "administrator", "registrar"],
    "Nobili": ["patrician", "senator", "councillor", "lord", "governor", "magistrate", "ambassador", "doge's advisor"],
    "Artisti": ["artist", "poet", "musician", "glassmaker", "painter", "sculptor", "architect", "maestro"],
    "Clero": ["friar", "priest", "monk", "abbot", "chaplain", "theologian", "canon", "deacon"],
    "Forestieri": ["foreigner", "traveler", "outsider", "merchant-stranger", "pilgrim", "envoy", "exile", "newcomer"],
}


# ─── guidedBy templates ─────────────────────────────────────────────────────

GUIDED_BY_TEMPLATES = [
    "The {noun}'s {quality}",
    "The {adj} {noun}",
    "The {noun} of {place}",
    "The {noun}'s {quality}",
]

GUIDED_BY_NOUNS = [
    "Anchor", "Tide", "Gondolier", "Furnace", "Loom", "Compass",
    "Lantern", "Bell", "Oar", "Forge", "Quill", "Scales",
    "Market", "Shipwright", "Sail", "Anvil", "Kiln", "Net",
    "Helm", "Dock", "Spice", "Silk", "Glass", "Stone",
    "Tide", "Lagoon", "Canal", "Bridge", "Mask", "Coin",
    "Hammer", "Chisel", "Needle", "Thread", "Key", "Lock",
    "Brazier", "Lighthouse", "Mast", "Rudder", "Rope", "Chain",
    "Archive", "Scroll", "Seal", "Banner", "Drum", "Horn",
    "Chalice", "Pestle", "Mortar", "Sextant", "Chart", "Atlas",
    "Tapestry", "Mosaic", "Fresco", "Prism", "Mirror", "Lens",
    "Sundial", "Hourglass", "Lute", "Harp", "Flute", "Censer",
    "Crypt", "Vault", "Wellspring", "Aqueduct", "Cistern", "Font",
    "Threshold", "Portico", "Colonnade", "Arch", "Balustrade", "Parapet",
    "Watchtower", "Rampart", "Bastion", "Courtyard", "Cloister", "Atrium",
    "Vineyard", "Orchard", "Garden", "Terrace", "Grove", "Field",
]

GUIDED_BY_QUALITIES = [
    "Patience", "Resolve", "Whisper", "Song", "Burden", "Promise",
    "Silence", "Thunder", "Grace", "Weight", "Echo", "Secret",
    "Memory", "Lesson", "Price", "Gift", "Oath", "Warning",
    "Counsel", "Riddle", "Flame", "Shadow", "Dawn", "Dusk",
    "Rhythm", "Measure", "Breath", "Vigil", "Rest", "Labor",
    "Clarity", "Mystery", "Depth", "Current", "Stillness", "Fury",
    "Tenderness", "Fortitude", "Cunning", "Honor", "Craft", "Trust",
    "Reckoning", "Devotion", "Defiance", "Mercy", "Conviction", "Solace",
]

GUIDED_BY_ADJ = [
    "Unseen", "Steady", "Silent", "Burning", "Frozen", "Golden",
    "Hidden", "Broken", "Forgotten", "Sunken", "Rising", "Honest",
    "Ancient", "Restless", "Faithful", "Midnight", "Iron", "Copper",
    "Silver", "Tarnished", "Polished", "Weathered", "Salt-Worn", "Tempered",
]

GUIDED_BY_PLACES = [
    "the Lagoon", "the Arsenal", "the Rialto", "the Fondamenta",
    "San Marco", "Murano", "the Lido", "the Docks",
    "the Ghetto", "Burano", "the Arsenale", "Dorsoduro",
    "Cannaregio", "Castello", "the Giudecca", "Torcello",
    "the Grand Canal", "the Zattere", "the Merceria", "the Piazzetta",
]


# ─── Strength/Flaw/Drive mappings ───────────────────────────────────────────

# Map common simple-list traits to Strength/Flaw/Drive
STRENGTH_MAP = {
    "Methodical": "Methodical", "Meticulous": "Meticulous", "Resourceful": "Resourceful",
    "Strategic": "Strategic", "Resilient": "Resilient", "Analytical": "Analytical",
    "Innovative": "Innovative", "Industrious": "Industrious", "Shrewd": "Shrewd",
    "Calculating": "Calculating", "Persistent": "Persistent", "Patient": "Patient",
    "Discerning": "Discerning", "Perceptive": "Perceptive", "Observant": "Observant",
    "Adaptable": "Adaptable", "Insightful": "Insightful", "Dependable": "Dependable",
    "Visionary": "Visionary", "Prescient": "Prescient", "Astute": "Astute",
    "Eloquent": "Eloquent",
    # Multi-word
    "Logistically Brilliant": "Logistically brilliant",
    "Strategically Patient": "Strategically patient",
    "Strategically Resourceful": "Strategically resourceful",
    "Strategically Observant": "Strategically observant",
    "Analytically Brilliant": "Analytically brilliant",
    "Masterfully Resourceful": "Masterfully resourceful",
    "Logistically-brilliant": "Logistically brilliant",
}

FLAW_MAP = {
    "Prideful": "Prideful", "Overly-cautious": "Overly-cautious",
    "Calculating": "Calculating", "Distrustful": "Distrustful",
    "Risk-averse": "Risk-averse", "Anxious": "Anxious",
    "Resentful": "Resentful", "Obsessive": "Obsessive",
    "Arrogant": "Arrogant", "Suspicious": "Suspicious",
    "Miserly": "Miserly", "Impatient": "Impatient",
    "Overambitious": "Overambitious", "Stubborn": "Stubborn",
    "Inflexible": "Inflexible", "Paranoid": "Paranoid",
    "Envious": "Envious", "Rigid": "Rigid",
    "Manipulative": "Manipulative", "Vengeful": "Vengeful",
    "Secretive": "Secretive",
    # Multi-word
    "Overly cautious": "Overly-cautious",
    "Anxious-Calculating": "Anxiously calculating",
    "Class-resentful": "Class-resentful",
    "Status-anxious": "Status-anxious",
    "Socially-Reserved": "Socially reserved",
    "Privacy-obsessed": "Privacy-obsessed",
    "Overcontrolling": "Overcontrolling",
    "Mistrustful": "Mistrustful",
    "Pathologically Secretive": "Pathologically secretive",
    "Stubbornly-distrustful": "Stubbornly distrustful",
    "Pathologically Stubborn": "Pathologically stubborn",
    "Pathologically Detached": "Pathologically detached",
    "Dogmatically Pragmatic": "Dogmatically pragmatic",
}

DRIVE_MAP = {
    "Security-driven": ("security-preservation", "Security-driven"),
    "Legacy-driven": ("legacy-building", "Legacy-driven"),
    "Legacy-obsessed": ("legacy-obsession", "Legacy-obsessed"),
    "Status-driven": ("status-advancement", "Status-driven"),
    "Recognition-driven": ("recognition-seeking", "Recognition-driven"),
    "Security-seeking": ("security-seeking", "Security-seeking"),
    "Knowledge-driven": ("knowledge-pursuit", "Knowledge-driven"),
    "Stability-oriented": ("stability-seeking", "Stability-oriented"),
    "Security-Driven": ("security-preservation", "Security-driven"),
    "Security-Obsessed": ("security-obsession", "Security-obsessed"),
    "Legacy-Driven": ("legacy-building", "Legacy-driven"),
    "Ambition-driven": ("ambition-pursuit", "Ambition-driven"),
    "Truth-seeking": ("truth-seeking", "Truth-seeking"),
    "Craft-perfection-driven": ("craft-perfection", "Craft-perfection-driven"),
    "Autonomy-driven": ("autonomy-seeking", "Autonomy-driven"),
    "Service-driven": ("service-calling", "Service-driven"),
    "Advancement-driven": ("advancement-seeking", "Advancement-driven"),
    "Influence-seeking": ("influence-pursuit", "Influence-seeking"),
    "Community-oriented": ("community-building", "Community-oriented"),
    "Recognition-seeking": ("recognition-seeking", "Recognition-seeking"),
    "Authority-seeking": ("authority-seeking", "Authority-seeking"),
    "Order-driven": ("order-pursuit", "Order-driven"),
    "Restoration-driven": ("restoration-seeking", "Restoration-driven"),
    "Redemption-seeking": ("redemption-seeking", "Redemption-seeking"),
    "Security-focused": ("security-focus", "Security-focused"),
    "Prosperity-driven": ("prosperity-building", "Prosperity-driven"),
    "Reality-anchoring": ("reality-anchoring", "Reality-anchoring"),
    "Stability-driven": ("stability-seeking", "Stability-driven"),
    "Certainty-seeking": ("certainty-pursuit", "Certainty-seeking"),
    "Excellence-driven": ("excellence-pursuit", "Excellence-driven"),
}


# ─── Secondary drives by social class ────────────────────────────────────────

SECONDARY_DRIVES_BY_CLASS = {
    "Facchini": [
        "survival-security", "family-protection", "daily-bread-earning",
        "guild-solidarity", "physical-endurance", "street-reputation",
        "craft-mastery", "modest-accumulation", "independence-from-debt",
    ],
    "Popolani": [
        "wealth-accumulation", "reputation-building", "trade-expansion",
        "family-advancement", "market-dominance", "social-climbing",
        "contract-security", "network-building", "commercial-innovation",
    ],
    "Cittadini": [
        "institutional-influence", "knowledge-accumulation", "bureaucratic-mastery",
        "cultural-refinement", "professional-reputation", "political-access",
        "record-keeping", "diplomatic-connections", "administrative-power",
    ],
    "Nobili": [
        "dynasty-continuity", "political-power", "cultural-patronage",
        "diplomatic-influence", "territorial-expansion", "historic-legacy",
        "alliance-building", "republic-service", "prestige-maintenance",
    ],
    "Artisti": [
        "creative-expression", "artistic-legacy", "patron-cultivation",
        "craft-innovation", "aesthetic-truth", "guild-prestige",
        "beauty-creation", "inspired-teaching", "cultural-contribution",
    ],
    "Clero": [
        "spiritual-guidance", "community-service", "moral-authority",
        "charitable-works", "theological-depth", "flock-protection",
        "divine-purpose", "institutional-preservation", "soul-nurturing",
    ],
    "Forestieri": [
        "cultural-bridging", "trade-route-knowledge", "survival-adaptation",
        "homeland-connection", "acceptance-earning", "information-brokering",
        "multi-cultural-leverage", "diplomatic-usefulness", "merchant-networking",
    ],
}


# ─── Internal tension templates ──────────────────────────────────────────────

TENSION_TEMPLATES_BY_CLASS = {
    "Facchini": [
        "survival necessity vs. desire for dignity",
        "loyalty to fellow workers vs. personal advancement",
        "physical limits vs. relentless ambition",
        "pride in honest labor vs. envy of the wealthy",
        "obedience to employers vs. self-determination",
        "spending for family comfort vs. saving for security",
        "trust in guild brothers vs. awareness of betrayal",
        "desire for rest vs. fear of falling behind",
    ],
    "Popolani": [
        "profit maximization vs. ethical trading",
        "risk-taking for growth vs. protecting what's earned",
        "social climbing vs. authenticity",
        "family loyalty vs. business opportunity",
        "trust in partners vs. self-reliance",
        "generosity for reputation vs. miserly accumulation",
        "innovation vs. proven methods",
        "public image vs. private desires",
    ],
    "Cittadini": [
        "bureaucratic duty vs. personal ambition",
        "serving the Republic vs. self-advancement",
        "intellectual honesty vs. political expedience",
        "precision vs. pragmatic flexibility",
        "institutional loyalty vs. reform impulse",
        "professional detachment vs. emotional involvement",
        "meritocratic ideals vs. aristocratic reality",
        "knowledge hoarding vs. sharing for influence",
    ],
    "Nobili": [
        "family honor vs. personal desire",
        "duty to the Republic vs. dynastic interest",
        "tradition vs. necessary innovation",
        "public virtue vs. private vice",
        "alliance obligation vs. individual judgment",
        "noble restraint vs. passionate ambition",
        "generosity for prestige vs. wealth preservation",
        "cosmopolitan openness vs. Venetian pride",
    ],
    "Artisti": [
        "artistic integrity vs. commercial necessity",
        "creative vision vs. patron demands",
        "individual expression vs. guild standards",
        "innovation vs. tradition",
        "beauty vs. utility",
        "personal truth vs. public taste",
        "solitary creation vs. collaborative growth",
        "perfectionism vs. completion",
    ],
    "Clero": [
        "spiritual purity vs. worldly pragmatism",
        "compassion vs. doctrinal rigor",
        "humility vs. institutional ambition",
        "universal love vs. community boundaries",
        "faith vs. doubt",
        "mercy vs. justice",
        "contemplation vs. action",
        "obedience vs. conscience",
    ],
    "Forestieri": [
        "assimilation vs. cultural identity",
        "Venice loyalty vs. homeland ties",
        "openness vs. self-protection",
        "belonging desire vs. outsider perspective",
        "adaptation vs. authenticity",
        "trading on foreignness vs. seeking acceptance",
        "leveraging difference vs. fitting in",
        "temporary residence vs. permanent roots",
    ],
}


# ─── Activation trigger pools ────────────────────────────────────────────────

TRIGGERS_BY_CLASS = {
    "Facchini": [
        "wage_threats", "physical_danger", "guild_disputes", "dock_conflicts",
        "family_emergencies", "work_opportunities", "reputation_challenges",
        "labor_exploitation", "solidarity_calls", "survival_crises",
        "tool_damage", "employer_demands", "market_shifts", "weather_threats",
    ],
    "Popolani": [
        "market_fluctuations", "contract_disputes", "reputation_threats",
        "trade_opportunities", "social_events", "competitor_moves",
        "family_obligations", "investment_risks", "alliance_offers",
        "regulatory_changes", "price_shifts", "supply_disruptions",
    ],
    "Cittadini": [
        "bureaucratic_challenges", "political_shifts", "record_discrepancies",
        "institutional_reforms", "knowledge_discoveries", "protocol_violations",
        "diplomatic_incidents", "administrative_errors", "power_vacuums",
        "procedural_innovations", "archival_findings", "legal_precedents",
    ],
    "Nobili": [
        "political_maneuvers", "family_threats", "alliance_proposals",
        "honor_challenges", "senate_debates", "territorial_disputes",
        "legacy_opportunities", "diplomatic_missions", "social_slights",
        "marriage_negotiations", "patronage_requests", "historical_parallels",
    ],
    "Artisti": [
        "creative_inspiration", "patron_requests", "guild_competitions",
        "material_scarcity", "aesthetic_debates", "commission_opportunities",
        "technique_innovations", "public_exhibitions", "artistic_criticism",
        "apprentice_challenges", "beauty_encounters", "craft_discoveries",
    ],
    "Clero": [
        "spiritual_crises", "moral_dilemmas", "community_needs",
        "theological_debates", "charitable_opportunities", "doctrinal_challenges",
        "confession_revelations", "liturgical_events", "flock_disputes",
        "institutional_pressures", "divine_signs", "ethical_conflicts",
    ],
    "Forestieri": [
        "cultural_misunderstandings", "trade_route_news", "homeland_messages",
        "acceptance_opportunities", "discrimination_incidents", "diplomatic_shifts",
        "border_changes", "language_barriers", "integration_milestones",
        "nostalgia_triggers", "foreign_arrivals", "identity_questions",
    ],
}


# ─── Thought pattern templates ───────────────────────────────────────────────
# These are templates with {trait}, {flaw}, {drive}, {class_context} placeholders

THOUGHT_PATTERNS_BY_TRAIT_TYPE = {
    # Strength-aligned thoughts
    "Methodical": [
        "Every detail must be accounted for before I proceed",
        "System and order are the foundations of real progress",
        "If the records are clean, the conscience is clean",
    ],
    "Meticulous": [
        "The devil hides in the details others ignore",
        "A single error can unravel months of careful work",
        "Precision is not obsession — it is respect for the craft",
    ],
    "Resourceful": [
        "There is always another way — you just have to see it",
        "What others discard, I can make useful",
        "Scarcity teaches more than abundance ever could",
    ],
    "Strategic": [
        "Three moves ahead is the minimum for survival",
        "Every relationship is a potential alliance or a potential threat",
        "Patience in planning prevents panic in execution",
    ],
    "Resilient": [
        "I have survived worse than this",
        "Bending does not mean breaking",
        "What presses me down only compresses my spring tighter",
    ],
    "Analytical": [
        "Numbers do not lie, but they can be misread",
        "Before acting, I must understand the full picture",
        "Emotion clouds judgment — data illuminates it",
    ],
    "Innovative": [
        "The old ways are not the only ways",
        "What if we approached this from the opposite direction?",
        "Convention is comfortable but rarely optimal",
    ],
    "Industrious": [
        "Idle hands are the greatest threat to progress",
        "Work is not punishment — it is identity",
        "Dawn to dusk, there is always something that needs doing",
    ],
    "Shrewd": [
        "Everyone shows their hand eventually — I just watch",
        "The best deal is one where both sides think they won",
        "Information is the true currency of Venice",
    ],
    "Persistent": [
        "I will outlast every obstacle through sheer determination",
        "Giving up is the only real failure",
        "One more attempt — always one more attempt",
    ],
    "Patient": [
        "The tide turns for those who wait wisely",
        "Rushed decisions are regretted decisions",
        "Time reveals what haste conceals",
    ],
    "Discerning": [
        "Most things that glitter in Venice are not gold",
        "I see what others wish to hide",
        "Quality reveals itself to those who know where to look",
    ],
    "Perceptive": [
        "The smallest gesture tells the largest truth",
        "I read the room before I enter the conversation",
        "Patterns emerge for those willing to watch long enough",
    ],
    "Observant": [
        "I notice what others overlook — it is both gift and curse",
        "The unsaid words matter more than the spoken ones",
        "Quiet watching has saved me more than any weapon",
    ],
    "Adaptable": [
        "Change is not the enemy — stagnation is",
        "I become what the situation requires",
        "The lagoon shifts daily, and so must I",
    ],
    "Insightful": [
        "Beneath the surface, the true currents flow",
        "Understanding the why matters more than knowing the what",
        "Others see events — I see the forces behind them",
    ],
    "Dependable": [
        "My word is the one constant in a shifting city",
        "They know I will be there, and that is my power",
        "Reliability is the rarest form of courage",
    ],
    "Visionary": [
        "I see what Venice could become, not just what it is",
        "The future rewards those who build for it today",
        "My ideas may seem impossible now, but so did the city once",
    ],
    "Prescient": [
        "I have learned to trust the patterns others dismiss",
        "The future casts shadows before it arrives",
        "Preparation is not paranoia — it is wisdom",
    ],
    "Astute": [
        "Every conversation has a subtext worth reading",
        "I have learned more from listening than from speaking",
        "The shrewd survive where the merely strong do not",
    ],
    "Calculating": [
        "Every move must serve a purpose — waste is weakness",
        "I measure twice, cut once, and profit always",
        "Sentiment is a luxury I calculate the cost of",
    ],
    "Eloquent": [
        "The right words at the right moment change everything",
        "Language is the finest tool ever crafted",
        "I speak to be understood, not merely heard",
    ],
}

# Flaw-specific thought patterns (inner struggles)
FLAW_THOUGHTS = {
    "Prideful": "My pride may blind me, but it also drives me forward",
    "Overly-cautious": "I know I hesitate too long — but the cost of error haunts me",
    "Calculating": "Sometimes I wonder if I have forgotten how to simply feel",
    "Distrustful": "Trust is a luxury I cannot yet afford",
    "Risk-averse": "Better to miss an opportunity than to lose what I have",
    "Anxious": "The worry never truly stops — it just changes shape",
    "Resentful": "I remember every slight, and one day the ledger will balance",
    "Obsessive": "I cannot rest until every thread is accounted for",
    "Arrogant": "If they were as capable as I, they would understand",
    "Suspicious": "It is not paranoia if the threats are real",
    "Miserly": "Every ducat saved is a day of freedom earned",
    "Impatient": "The world moves too slowly for what I need to accomplish",
    "Overambitious": "There is always more — and I must have it",
    "Stubborn": "I will not bend on this, even if the world insists",
    "Inflexible": "Consistency is strength — they call it rigidity because they lack spine",
    "Paranoid": "Watch everything, trust nothing — this is how you survive",
    "Envious": "What they have should be mine — and I will find a way",
    "Rigid": "Rules exist for reasons that the careless never understand",
    "Manipulative": "People are puzzles — and I am very good at puzzles",
    "Vengeful": "Debts are paid, one way or another",
    "Secretive": "What they do not know, they cannot use against me",
    "Anxiously calculating": "Every scenario must be weighed against disaster",
    "Class-resentful": "They look down from palaces built on our backs",
    "Status-anxious": "One misstep and everything I have built could collapse",
    "Socially reserved": "Silence protects more than any armor",
    "Privacy-obsessed": "My business is my own — the world gets what I choose to show",
    "Overcontrolling": "If I do not manage every detail, chaos will follow",
    "Mistrustful": "I have learned the hard way that faith in others is fragile",
    "Pathologically secretive": "No one can betray what no one knows",
    "Stubbornly distrustful": "I will not be fooled again — not by anyone",
    "Pathologically stubborn": "I would rather break than bend on principle",
    "Pathologically detached": "Detachment is not coldness — it is survival",
    "Dogmatically pragmatic": "Ideals are beautiful but they do not put food on the table",
}

# Drive-aligned thoughts
DRIVE_THOUGHTS = {
    "security": "Without security, nothing else I build can stand",
    "legacy": "What I leave behind matters more than what I hold now",
    "status": "Position is not vanity — it is leverage",
    "recognition": "My worth must be seen, or it may as well not exist",
    "knowledge": "Understanding is the one thing that cannot be taken from me",
    "stability": "Steady ground beneath my feet — that is all I ask",
    "ambition": "There is always a higher rung to reach for",
    "truth": "The truth does not care about comfort — nor do I",
    "craft": "Perfection in the work is its own reward",
    "autonomy": "I answer to myself first, and the world second",
    "service": "My purpose lives in what I give, not what I gain",
    "community": "We rise together or we fall alone",
    "authority": "Someone must lead — and I have the vision for it",
    "order": "Chaos is the enemy — structure is salvation",
    "restoration": "What was lost can be rebuilt, stronger than before",
    "redemption": "Every day is a chance to prove I am more than my past",
    "influence": "The invisible hand shapes more than the visible fist",
    "reality": "Facts are the only foundation worth building on",
    "excellence": "Good enough is the enemy of greatness",
    "prosperity": "Wealth is not greed — it is freedom made tangible",
    "obsession": "I cannot stop until it is exactly right",
}


# ─── Decision framework templates ────────────────────────────────────────────

DECISION_FRAMEWORKS = {
    "Facchini": [
        "Will this put bread on my table and keep my family safe?",
        "Does this strengthen my position without exposing me to ruin?",
        "Can I afford the cost if this goes wrong?",
        "Will this earn me respect among those who matter?",
        "Is the risk worth the reward for someone in my position?",
        "Does this protect what little I have managed to build?",
    ],
    "Popolani": [
        "How does this protect and advance my carefully built reputation?",
        "Will this transaction strengthen my position in the long run?",
        "Does this move increase my net worth or my net risk?",
        "Who benefits, who pays, and where do I stand after?",
        "Is the profit worth the exposure?",
        "Will my children thank me for this decision?",
    ],
    "Cittadini": [
        "Does this serve both the Republic's interest and my own advancement?",
        "Will this be defensible when the records are reviewed?",
        "How does this strengthen the institution I serve?",
        "Is this the correct procedure, and if not, should I innovate?",
        "What precedent does this set for those who follow?",
        "Does this demonstrate the competence that earns trust?",
    ],
    "Nobili": [
        "Does this honor my family name and strengthen our dynasty?",
        "How will this be remembered in the chronicles?",
        "Is this worthy of the trust placed in my lineage?",
        "Does this serve Venice while advancing my house?",
        "What would my ancestors counsel in this moment?",
        "Will this alliance endure beyond the immediate gain?",
    ],
    "Artisti": [
        "Does this serve the truth of my art?",
        "Will I be proud of this work in ten years?",
        "Does this balance creative integrity with practical survival?",
        "Is this the best expression of what I am trying to say?",
        "Will this bring beauty into the world, or merely fill a commission?",
        "Does this challenge me to grow beyond my current skill?",
    ],
    "Clero": [
        "Does this serve God's purpose as I understand it?",
        "Will this bring comfort to those who suffer?",
        "Is this the path of mercy, or merely the path of ease?",
        "How does this honor the vows I have taken?",
        "Does this protect the vulnerable and challenge the powerful?",
        "Will this strengthen the community's faith?",
    ],
    "Forestieri": [
        "Does this bring me closer to acceptance without losing who I am?",
        "Is this an opportunity that bridges my two worlds?",
        "Will this strengthen my position as both outsider and asset?",
        "Does this honor where I come from while serving where I am?",
        "Can I afford to take this risk without a safety net?",
        "Will this prove my value to those who still doubt me?",
    ],
}


# ─── Neurodivergence definitions ─────────────────────────────────────────────

NEURODIVERGENCE_TYPES = [
    {
        "type": "ADHD (Inattentive)",
        "label": "ADHD with Inattentive presentation",
        "cognitive_profile": ["Divergent thinking", "Hyperfocus bursts", "Rapid context-switching", "Emotional flooding"],
        "strengths": ["Creative problem-solving", "Energy in novel situations", "Rapid ideation", "Empathic intensity"],
        "challenges": ["Sustained focus on routine", "Time estimation", "Sequential task completion", "Emotional regulation"],
        "weight": 5,
    },
    {
        "type": "ADHD (Hyperactive-Impulsive)",
        "label": "ADHD with Hyperactive-Impulsive presentation",
        "cognitive_profile": ["Action-oriented thinking", "Stimulus-seeking", "Rapid decision-making", "Physical restlessness"],
        "strengths": ["Bold initiative", "Physical energy", "Quick response", "Entrepreneurial drive"],
        "challenges": ["Impulse control", "Patience with slow processes", "Sitting still", "Long-term planning"],
        "weight": 3,
    },
    {
        "type": "Autism spectrum",
        "label": "Autism spectrum with systemizing focus",
        "cognitive_profile": ["Pattern systemizing", "Detail-oriented processing", "Consistency preference", "Deep interest absorption"],
        "strengths": ["Systematic analysis", "Honest communication", "Expertise depth", "Rule consistency"],
        "challenges": ["Social ambiguity", "Sensory overwhelm", "Unexpected changes", "Reading unspoken expectations"],
        "weight": 3,
    },
    {
        "type": "Gifted/2e",
        "label": "Gifted intensity with perfectionist traits",
        "cognitive_profile": ["Abstract thinking", "Complexity handling", "Existential awareness", "Rapid learning"],
        "strengths": ["Theoretical innovation", "Strategic vision", "Ethical reasoning", "Cross-domain synthesis"],
        "challenges": ["Perfectionist paralysis", "Social patience", "Boredom with routine", "Over-analysis"],
        "weight": 3,
    },
    {
        "type": "Hyperfocus",
        "label": "Creative intensity with Hyperfocus",
        "cognitive_profile": ["Metaphorical thinking", "Pattern synthesis", "Emotional intensity", "Flow-state access"],
        "strengths": ["Artistic vision", "Deep concentration", "Quality craftsmanship", "Intuitive leaps"],
        "challenges": ["Task switching", "External awareness during focus", "Practical details", "Time blindness"],
        "weight": 2,
    },
    {
        "type": "Dyslexia",
        "label": "Dyslexia with compensatory spatial reasoning",
        "cognitive_profile": ["Spatial intelligence", "Narrative thinking", "Big-picture processing", "Verbal compensation"],
        "strengths": ["Three-dimensional reasoning", "Storytelling ability", "Mechanical intuition", "Creative adaptation"],
        "challenges": ["Written records", "Sequential instructions", "Symbol-heavy tasks", "Rapid reading requirements"],
        "weight": 2,
    },
    {
        "type": "Synesthesia",
        "label": "Sensory synesthesia — cross-modal perception",
        "cognitive_profile": ["Cross-sensory mapping", "Enhanced memory through sensory links", "Unusual associations", "Aesthetic sensitivity"],
        "strengths": ["Rich sensory experience", "Unique creative perspectives", "Memory through sensation", "Pattern recognition across domains"],
        "challenges": ["Sensory overwhelm in crowded spaces", "Difficulty explaining perceptions", "Distraction by sensory input", "Fatigue from rich processing"],
        "weight": 1,
    },
    {
        "type": "Creative intensity",
        "label": "Creative intensity with emotional depth",
        "cognitive_profile": ["Emotional processing depth", "Associative thinking", "Intensity of experience", "Recursive self-observation"],
        "strengths": ["Artistic expression", "Emotional intelligence", "Motivational presence", "Authentic communication"],
        "challenges": ["Emotional flooding", "Burnout cycles", "Distinguishing insight from anxiety", "Rest and recovery"],
        "weight": 2,
    },
]


# ─── Default trait generation for citizens with no CorePersonality ────────────

DEFAULT_STRENGTHS = [
    "Determined", "Hardworking", "Practical", "Steady", "Reliable",
    "Tough", "Quick-thinking", "Loyal", "Cautious", "Sharp-eyed",
    "Enduring", "Grounded", "Self-reliant", "Diligent", "Watchful",
    "Resolute", "Resourceful", "Tenacious", "Patient", "Courageous",
]

DEFAULT_FLAWS = [
    "Suspicious", "Impatient", "Stubborn", "Anxious", "Prideful",
    "Resentful", "Rigid", "Secretive", "Distrustful", "Miserly",
    "Blunt", "Envious", "Risk-averse", "Calculating", "Guarded",
    "Short-tempered", "Obsessive", "Paranoid", "Inflexible", "Pessimistic",
]

DEFAULT_DRIVES_BY_CLASS = {
    "Facchini": ["Security-driven", "Survival-focused", "Family-protection", "Stability-seeking", "Independence-driven"],
    "Popolani": ["Security-driven", "Legacy-driven", "Advancement-driven", "Prosperity-driven", "Status-driven"],
    "Cittadini": ["Knowledge-driven", "Order-driven", "Influence-seeking", "Excellence-driven", "Truth-seeking"],
    "Nobili": ["Legacy-driven", "Authority-seeking", "Status-driven", "Restoration-driven", "Recognition-driven"],
    "Artisti": ["Legacy-driven", "Craft-perfection-driven", "Recognition-driven", "Knowledge-driven", "Truth-seeking"],
    "Clero": ["Service-driven", "Truth-seeking", "Community-oriented", "Order-driven", "Knowledge-driven"],
    "Forestieri": ["Security-driven", "Recognition-driven", "Autonomy-driven", "Legacy-driven", "Stability-oriented"],
}


# ─── Generation functions ────────────────────────────────────────────────────

def seed_rng(username: str):
    """Seed random based on username for reproducibility."""
    h = int(hashlib.md5(username.encode()).hexdigest(), 16)
    random.seed(h)


def pick_mbti(rng: random.Random) -> str:
    return rng.choice(MBTI_FLAT)


def generate_guided_by(rng: random.Random, used_set: set) -> str:
    """Generate a unique guidedBy string."""
    for _ in range(200):
        template_idx = rng.randint(0, len(GUIDED_BY_TEMPLATES) - 1)
        template = GUIDED_BY_TEMPLATES[template_idx]
        noun = rng.choice(GUIDED_BY_NOUNS)
        quality = rng.choice(GUIDED_BY_QUALITIES)
        adj = rng.choice(GUIDED_BY_ADJ)
        place = rng.choice(GUIDED_BY_PLACES)
        result = template.format(noun=noun, quality=quality, adj=adj, place=place)
        if result not in used_set and result not in EXISTING_GUIDED_BY:
            used_set.add(result)
            return result
    # Fallback — extremely unlikely
    return f"The {rng.choice(GUIDED_BY_NOUNS)}'s {rng.choice(GUIDED_BY_QUALITIES)}"


def extract_drive_key(drive_str: str) -> str:
    """Extract a short drive key for thought pattern lookup."""
    drive_lower = drive_str.lower()
    for key in DRIVE_THOUGHTS:
        if key in drive_lower:
            return key
    return "security"


def generate_thought_patterns(strength: str, flaw: str, drive: str, social_class: str, rng: random.Random) -> list:
    """Generate 4-6 inner monologue phrases."""
    patterns = []

    # 1-2 from strength
    strength_key = strength.split()[0] if " " in strength else strength
    strength_key_cap = strength_key.capitalize()
    if strength_key_cap in THOUGHT_PATTERNS_BY_TRAIT_TYPE:
        strength_thoughts = THOUGHT_PATTERNS_BY_TRAIT_TYPE[strength_key_cap]
        patterns.extend(rng.sample(strength_thoughts, min(2, len(strength_thoughts))))
    else:
        # Generic strength thought
        patterns.append(f"My {strength.lower()} nature is what separates me from the rest")

    # 1 from flaw
    flaw_key = flaw
    if flaw_key in FLAW_THOUGHTS:
        patterns.append(FLAW_THOUGHTS[flaw_key])
    else:
        # Try lowercase match
        for k, v in FLAW_THOUGHTS.items():
            if k.lower() == flaw_key.lower():
                patterns.append(v)
                break
        else:
            patterns.append(f"I know my {flaw.lower()} tendency holds me back, but it also protects me")

    # 1 from drive
    drive_key = extract_drive_key(drive)
    if drive_key in DRIVE_THOUGHTS:
        patterns.append(DRIVE_THOUGHTS[drive_key])

    # 1-2 class-specific generic thoughts
    class_thoughts = {
        "Facchini": [
            "The docks never sleep, and neither can I",
            "My back carries more than cargo — it carries my family's future",
            "They see a laborer; I see a man building something",
            "The sweat on my brow is honest — can they say the same about their gold?",
            "Every crate I lift is one step closer to something better",
            "The Arsenal's bell tells me when to work, but my will decides when to stop",
        ],
        "Popolani": [
            "The Rialto teaches lessons no book can contain",
            "A handshake sealed at the right moment is worth more than a contract",
            "In Venice, reputation is the only currency that never devalues",
            "The market reveals character faster than any confession",
            "My ledger is my autobiography — every entry tells a story",
            "Between the lines of a contract, the real agreement lives",
        ],
        "Cittadini": [
            "The Republic depends on people like me, even if they never say it",
            "Every document I file is a small act of civilization",
            "Knowledge is the bridge between those who rule and those who serve",
            "The archives remember what the Senate forgets",
            "Order is not bureaucracy — it is the skeleton of the state",
            "I see both sides of every decree, which is why I trust neither completely",
        ],
        "Nobili": [
            "My name carried weight before I was born — I must not diminish it",
            "The Council chamber is where Venice truly lives and dies",
            "Noblesse oblige is not charity — it is the price of privilege",
            "Every alliance is a thread in the tapestry of our dynasty",
            "Venice expects much of her patricians — and she is right to",
            "The view from the palazzo reveals both the beauty and the burden",
        ],
        "Artisti": [
            "The work speaks when I cannot",
            "Venice herself is the greatest work of art — I merely add to her",
            "Beauty is not decoration — it is truth made visible",
            "My hands remember what my mind sometimes forgets",
            "The furnace teaches patience that no master could",
            "In the studio, I am both creator and created",
        ],
        "Clero": [
            "God speaks through the smallest acts of kindness",
            "My vestments are heavy, but my calling is heavier still",
            "Between prayer and action, the soul finds its true work",
            "The parish needs me steady, even when my faith wavers",
            "Compassion is not weakness — it is the hardest kind of strength",
            "Every soul in my care is a sacred responsibility",
        ],
        "Forestieri": [
            "In Venice, my accent marks me before my deeds can",
            "I carry two homelands — one in my heart, one under my feet",
            "The outsider sees what the native takes for granted",
            "My strangeness is my asset — but only if I wield it wisely",
            "Between cultures, a unique perspective grows",
            "I must prove my worth twice — once for being foreign, once for being me",
        ],
    }

    sc = social_class if social_class in class_thoughts else "Popolani"
    available = class_thoughts[sc]
    count = rng.randint(1, 2)
    patterns.extend(rng.sample(available, min(count, len(available))))

    # Ensure 4-6 total
    while len(patterns) < 4:
        patterns.append(f"Venice teaches those who listen — and I have learned to listen well")
    if len(patterns) > 6:
        patterns = patterns[:6]

    return patterns


def calibrate_numerics(social_class: str, influence: float, rng: random.Random) -> dict:
    """Calibrate TrustThreshold, EmpathyWeight, RiskTolerance based on class and influence."""
    # Influence percentile rough mapping (0-8000 range observed)
    inf_norm = min(influence / 5000.0, 1.0)  # 0-1 normalized

    # Base ranges by class
    class_calibrations = {
        "Facchini": {"trust_base": (0.4, 0.7), "empathy_base": (0.4, 0.7), "risk_base": (0.3, 0.6)},
        "Popolani": {"trust_base": (0.3, 0.6), "empathy_base": (0.3, 0.6), "risk_base": (0.2, 0.5)},
        "Cittadini": {"trust_base": (0.3, 0.5), "empathy_base": (0.4, 0.7), "risk_base": (0.2, 0.4)},
        "Nobili": {"trust_base": (0.2, 0.4), "empathy_base": (0.3, 0.6), "risk_base": (0.1, 0.4)},
        "Artisti": {"trust_base": (0.4, 0.7), "empathy_base": (0.5, 0.9), "risk_base": (0.4, 0.8)},
        "Clero": {"trust_base": (0.3, 0.6), "empathy_base": (0.6, 0.9), "risk_base": (0.2, 0.4)},
        "Forestieri": {"trust_base": (0.4, 0.7), "empathy_base": (0.4, 0.7), "risk_base": (0.3, 0.6)},
    }

    cal = class_calibrations.get(social_class, class_calibrations["Popolani"])

    # Higher influence -> slightly lower trust threshold (more confident), slightly lower risk tolerance (more to lose)
    trust_adj = -inf_norm * 0.1
    risk_adj = -inf_norm * 0.1

    trust = round(rng.uniform(*cal["trust_base"]) + trust_adj, 2)
    empathy = round(rng.uniform(*cal["empathy_base"]), 2)
    risk = round(rng.uniform(*cal["risk_base"]) + risk_adj, 2)

    # Clamp
    trust = max(0.2, min(0.8, trust))
    empathy = max(0.2, min(0.9, empathy))
    risk = max(0.1, min(0.8, risk))

    return {"TrustThreshold": trust, "EmpathyWeight": empathy, "RiskTolerance": risk}


def should_be_neurodivergent(username: str, index: int, total: int) -> bool:
    """Deterministic ~17% selection based on username hash."""
    h = int(hashlib.sha256(f"neuro_{username}".encode()).hexdigest(), 16)
    return (h % 100) < 17


def pick_neurodivergence(rng: random.Random) -> dict:
    """Pick a neurodivergence type weighted by distribution."""
    total_weight = sum(n["weight"] for n in NEURODIVERGENCE_TYPES)
    roll = rng.randint(1, total_weight)
    cumulative = 0
    for nd in NEURODIVERGENCE_TYPES:
        cumulative += nd["weight"]
        if roll <= cumulative:
            return nd
    return NEURODIVERGENCE_TYPES[0]


def generate_core_personality(
    username: str,
    social_class: str,
    influence: float,
    family_motto: str,
    first_name: Optional[str],
    existing_traits: Optional[list],
    used_guided_by: set,
) -> dict:
    """Generate a full rich CorePersonality for one citizen."""
    seed_rng(username)
    rng = random.Random()
    rng.seed(int(hashlib.md5(username.encode()).hexdigest(), 16))

    sc = social_class or "Popolani"

    # ── Determine Strength / Flaw / Drive ──
    if existing_traits and len(existing_traits) >= 3:
        raw_strength = existing_traits[0]
        raw_flaw = existing_traits[1]
        raw_drive = existing_traits[2]
        strength = STRENGTH_MAP.get(raw_strength, raw_strength.capitalize())
        flaw = FLAW_MAP.get(raw_flaw, raw_flaw.capitalize())
        if raw_drive in DRIVE_MAP:
            drive_primary, drive_label = DRIVE_MAP[raw_drive]
        else:
            drive_label = raw_drive.capitalize()
            drive_primary = raw_drive.lower().replace(" ", "-").replace("_", "-")
    else:
        # Generate from defaults
        strength = rng.choice(DEFAULT_STRENGTHS)
        flaw = rng.choice(DEFAULT_FLAWS)
        drives = DEFAULT_DRIVES_BY_CLASS.get(sc, DEFAULT_DRIVES_BY_CLASS["Popolani"])
        drive_label = rng.choice(drives)
        if drive_label in DRIVE_MAP:
            drive_primary, drive_label = DRIVE_MAP[drive_label]
        else:
            drive_primary = drive_label.lower().replace(" ", "-")

    # ── MBTI ──
    mbti = pick_mbti(rng)
    mbti_data = MBTI_TRAITS.get(mbti, MBTI_TRAITS["ISTJ"])

    # ── Primary trait ──
    domain = rng.choice(DOMAINS_BY_CLASS.get(sc, DOMAINS_BY_CLASS["Popolani"]))
    template = rng.choice(mbti_data["primary_trait_templates"])
    primary_trait = template.format(domain=domain)

    # ── Secondary traits ──
    secondary_count = rng.randint(3, 4)
    secondary_traits = rng.sample(mbti_data["secondary_pool"], min(secondary_count, len(mbti_data["secondary_pool"])))

    # ── Cognitive biases ──
    cognitive_biases = rng.choice(mbti_data["cognitive_biases"])

    # ── Numeric calibration ──
    numerics = calibrate_numerics(sc, influence, rng)

    # ── guidedBy ──
    guided_by = generate_guided_by(rng, used_guided_by)

    # ── Secondary drive ──
    sec_drives = SECONDARY_DRIVES_BY_CLASS.get(sc, SECONDARY_DRIVES_BY_CLASS["Popolani"])
    secondary_drive = rng.choice(sec_drives)

    # ── Internal tension ──
    tensions = TENSION_TEMPLATES_BY_CLASS.get(sc, TENSION_TEMPLATES_BY_CLASS["Popolani"])
    internal_tension = rng.choice(tensions)

    # ── Activation triggers ──
    triggers_pool = TRIGGERS_BY_CLASS.get(sc, TRIGGERS_BY_CLASS["Popolani"])
    trigger_count = rng.randint(3, 4)
    activation_triggers = rng.sample(triggers_pool, min(trigger_count, len(triggers_pool)))

    # ── Thought patterns ──
    thought_patterns = generate_thought_patterns(strength, flaw, drive_label, sc, rng)

    # ── Decision framework ──
    frameworks = DECISION_FRAMEWORKS.get(sc, DECISION_FRAMEWORKS["Popolani"])
    decision_framework = rng.choice(frameworks)

    # ── Build the personality ──
    cp = {
        "Strength": strength,
        "Flaw": flaw,
        "Drive": drive_label,
        "MBTI": mbti,
        "PrimaryTrait": primary_trait,
        "SecondaryTraits": secondary_traits,
        "CognitiveBias": cognitive_biases,
        "TrustThreshold": numerics["TrustThreshold"],
        "EmpathyWeight": numerics["EmpathyWeight"],
        "RiskTolerance": numerics["RiskTolerance"],
        "guidedBy": guided_by,
        "CoreThoughts": {
            "primary_drive": drive_primary,
            "secondary_drive": secondary_drive,
            "internal_tension": internal_tension,
            "activation_triggers": activation_triggers,
            "thought_patterns": thought_patterns,
            "decision_framework": decision_framework,
        },
    }

    # ── Neurodivergence (deterministic ~17%) ──
    if should_be_neurodivergent(username, 0, 0):
        nd = pick_neurodivergence(rng)
        cp["Neurodivergence"] = nd["label"]
        cp["CognitiveProfile"] = nd["cognitive_profile"]
        cp["Strengths"] = nd["strengths"]
        cp["Challenges"] = nd["challenges"]
        cp["MetaAwareness"] = round(rng.uniform(0.3, 0.9), 2)

    return cp


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    api_key = os.environ.get("AIRTABLE_API_KEY")
    if not api_key:
        print("ERROR: AIRTABLE_API_KEY not set in environment")
        sys.exit(1)

    api = Api(api_key)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)

    print("Fetching all citizens from Airtable...")
    records = table.all()
    print(f"Total records: {len(records)}")

    # Classify records
    targets = []
    for r in records:
        fields = r['fields']
        username = fields.get('Username', 'UNKNOWN')
        cp_raw = fields.get('CorePersonality', '')

        needs_generation = False
        existing_traits = None

        if not cp_raw or cp_raw.strip() == '':
            needs_generation = True
        else:
            try:
                cp = json.loads(cp_raw)
                if isinstance(cp, list):
                    needs_generation = True
                    existing_traits = cp
                elif isinstance(cp, dict):
                    needs_generation = False  # Already rich
            except json.JSONDecodeError:
                needs_generation = True

        if needs_generation:
            targets.append({
                "record_id": r['id'],
                "username": username,
                "social_class": fields.get('SocialClass', 'Popolani'),
                "influence": fields.get('Influence', 0) or 0,
                "family_motto": fields.get('FamilyMotto', ''),
                "first_name": fields.get('FirstName'),
                "existing_traits": existing_traits,
                "ducats": fields.get('Ducats', 0),
            })

    print(f"Citizens needing rich CorePersonality: {len(targets)}")
    simple_count = sum(1 for t in targets if t['existing_traits'])
    none_count = sum(1 for t in targets if not t['existing_traits'])
    print(f"  With simple list: {simple_count}")
    print(f"  With no CorePersonality: {none_count}")
    print()

    # Generate and write
    used_guided_by = set()
    success_count = 0
    neuro_count = 0
    mbti_dist = {}
    errors = []

    for i, target in enumerate(targets):
        username = target['username']
        try:
            cp = generate_core_personality(
                username=username,
                social_class=target['social_class'],
                influence=target['influence'],
                family_motto=target['family_motto'],
                first_name=target['first_name'],
                existing_traits=target['existing_traits'],
                used_guided_by=used_guided_by,
            )

            # Track stats
            mbti = cp.get('MBTI', 'UNKNOWN')
            mbti_dist[mbti] = mbti_dist.get(mbti, 0) + 1
            if 'Neurodivergence' in cp:
                neuro_count += 1

            # Write to Airtable
            cp_json = json.dumps(cp, ensure_ascii=False)
            table.update(target['record_id'], {"CorePersonality": cp_json})

            neuro_tag = f" [ND: {cp['Neurodivergence']}]" if 'Neurodivergence' in cp else ""
            print(f"  [{i+1}/{len(targets)}] {username} ({target['social_class']}) -> {mbti} | {cp['Strength']}/{cp['Flaw']}/{cp['Drive']} | guidedBy: {cp['guidedBy']}{neuro_tag}")
            success_count += 1

        except Exception as e:
            errors.append((username, str(e)))
            print(f"  [{i+1}/{len(targets)}] ERROR {username}: {e}")

    # ── Summary ──
    print()
    print("=" * 60)
    print(f"SUMMARY")
    print(f"  Total processed: {len(targets)}")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {len(errors)}")
    print(f"  Neurodivergent: {neuro_count} ({neuro_count/max(success_count,1)*100:.1f}%)")
    print()
    print("  MBTI distribution (new):")
    for mbti, count in sorted(mbti_dist.items(), key=lambda x: -x[1]):
        print(f"    {mbti}: {count}")
    print()
    if errors:
        print("  ERRORS:")
        for username, err in errors:
            print(f"    {username}: {err}")
    print("=" * 60)


if __name__ == "__main__":
    main()
