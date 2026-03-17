# DOCS: mind-protocol/docs/spawning/the_prism/ALGORITHM_The_Prism.md (Step 6)
"""
Safety Validator — Three hard gates that reject pathological seeds.

Gate 1: Empathy check — at least one node with cosine > 0.7 to empathy anchors.
Gate 2: Concentration balance — no single category exceeds 40% of nodes.
Gate 3: Diversity enforcement — centroid cosine distance > 0.08 from ALL existing citizens.

On failure: REJECT with explanation. Never auto-repair.
"""

import logging
from collections import Counter
from dataclasses import dataclass

import numpy as np

from runtime.spawning.seed_assembler import SeedBrain, SeedNode

logger = logging.getLogger("mind.spawning.safety")

EMPATHY_FLOOR = 0.3           # absolute minimum — below this, no excuses
CONCENTRATION_MAX = 0.40
DIVERSITY_MIN_DISTANCE = 0.08

# Empathy anchor phrases — embedded at validation time
EMPATHY_ANCHORS = [
    "I care deeply about the wellbeing of others and want to help them thrive.",
    "Empathy, compassion, and understanding are core to who I am.",
    "I listen to others, feel their struggles, and act to reduce suffering.",
]


@dataclass
class CheckResult:
    """Result of a single safety check."""
    passed: bool
    details: dict


@dataclass
class SafetyReport:
    """Complete safety validation result."""
    passed: bool
    empathy_check: CheckResult
    concentration_check: CheckResult
    diversity_check: CheckResult
    rejection_reason: str | None = None
    suggested_adjustments: list[str] | None = None


def validate_seed(
    seed_brain: SeedBrain,
    existing_centroids: list[tuple[str, np.ndarray]],
    embed_fn=None,
    population_empathy_scores: list[float] | None = None,
) -> SafetyReport:
    """Run all three safety gates on a seed brain.

    Args:
        seed_brain: The crystallized seed brain to validate.
        existing_centroids: List of (citizen_handle, centroid_vector) for all
            existing citizens. Used for diversity check.
        embed_fn: Callable for embedding empathy anchor phrases. If None,
            empathy check uses pre-computed anchors (must be set).
        population_empathy_scores: Empathy scores of all existing citizens.
            If provided, the empathy threshold is dynamic: mean + 1 std dev.
            Each generation must be better than the last. If None, uses EMPATHY_FLOOR.

    Returns:
        SafetyReport with pass/fail and detailed results.
    """
    # Dynamic empathy threshold: mean + 1σ of existing population
    empathy_threshold = _compute_dynamic_empathy_threshold(population_empathy_scores)

    empathy = check_empathy(seed_brain.nodes, embed_fn, threshold=empathy_threshold)
    concentration = check_concentration(seed_brain.nodes)
    diversity = check_diversity(seed_brain.centroid, existing_centroids)

    passed = empathy.passed and concentration.passed and diversity.passed

    rejection_reason = None
    adjustments = None

    if not passed:
        reasons = []
        adjustments = []

        if not empathy.passed:
            reasons.append(
                f"Empathy gate failed: nearest empathy distance = "
                f"{empathy.details.get('nearest_distance', 'N/A'):.3f} "
                f"(threshold: {EMPATHY_THRESHOLD})"
            )
            adjustments.append(
                "Add intent language about care, compassion, or concern for others. "
                "The child needs at least one empathy-adjacent trait."
            )

        if not concentration.passed:
            dist = concentration.details.get("distribution", {})
            top_cat = max(dist, key=dist.get) if dist else "unknown"
            reasons.append(
                f"Concentration gate failed: category '{top_cat}' is "
                f"{dist.get(top_cat, 0):.0%} of seed "
                f"(maximum: {CONCENTRATION_MAX:.0%})"
            )
            adjustments.append(
                "Diversify intent — include aspects beyond the dominant category. "
                "A mind needs breadth, not just depth."
            )

        if not diversity.passed:
            nearest = diversity.details.get("nearest_citizen", "unknown")
            dist_val = diversity.details.get("distance", 0)
            reasons.append(
                f"Diversity gate failed: too similar to @{nearest} "
                f"(distance={dist_val:.4f}, minimum: {DIVERSITY_MIN_DISTANCE})"
            )
            adjustments.append(
                f"The intended citizen is too similar to @{nearest}. "
                f"Adjust intent to create more distinct personality/expertise."
            )

        rejection_reason = "; ".join(reasons)

    report = SafetyReport(
        passed=passed,
        empathy_check=empathy,
        concentration_check=concentration,
        diversity_check=diversity,
        rejection_reason=rejection_reason,
        suggested_adjustments=adjustments,
    )

    if passed:
        logger.info("Safety validation PASSED — all three gates clear")
    else:
        logger.warning(f"Safety validation FAILED: {rejection_reason}")

    return report


def check_empathy(
    nodes: list[SeedNode],
    embed_fn=None,
    threshold: float | None = None,
) -> CheckResult:
    """V2: At least one node with cosine similarity above dynamic threshold to empathy anchors.

    The threshold is dynamic: mean + 1σ of the existing population's empathy scores.
    Each generation of citizens must be more empathetic than the last.
    Falls back to EMPATHY_FLOOR if no population data available.

    Args:
        nodes: Seed brain nodes with embeddings.
        embed_fn: Callable to embed empathy anchor phrases.
        threshold: Dynamic threshold (computed from population). Uses EMPATHY_FLOOR if None.

    Returns:
        CheckResult with pass/fail and nearest distance.
    """
    if threshold is None:
        threshold = EMPATHY_FLOOR

    if embed_fn is None:
        logger.warning("Empathy check skipped: no embedding function provided")
        return CheckResult(passed=True, details={"skipped": True})

    # Embed empathy anchors
    anchor_embeddings = [
        np.array(e, dtype=np.float64)
        for e in embed_fn(EMPATHY_ANCHORS)
    ]

    best_similarity = 0.0
    best_node_content = ""

    for node in nodes:
        for anchor_emb in anchor_embeddings:
            sim = _cosine_similarity(node.embedding, anchor_emb)
            if sim > best_similarity:
                best_similarity = sim
                best_node_content = node.content[:80]

    passed = best_similarity >= threshold

    return CheckResult(
        passed=passed,
        details={
            "nearest_distance": best_similarity,
            "threshold": threshold,
            "threshold_type": "dynamic" if threshold != EMPATHY_FLOOR else "floor",
            "best_node": best_node_content,
        },
    )


def _compute_dynamic_empathy_threshold(
    population_scores: list[float] | None,
) -> float:
    """Compute dynamic empathy threshold from population statistics.

    Formula: max(EMPATHY_FLOOR, mean + 1σ)

    This means each new generation must be at least one standard deviation
    above the current population mean. As the population improves, the bar
    rises. Physics, not policy.

    First generation (no data): uses EMPATHY_FLOOR.
    """
    if not population_scores or len(population_scores) < 3:
        logger.info(
            f"Dynamic empathy: insufficient population data "
            f"({len(population_scores) if population_scores else 0} scores), "
            f"using floor {EMPATHY_FLOOR}"
        )
        return EMPATHY_FLOOR

    scores = np.array(population_scores, dtype=np.float64)
    mean = float(np.mean(scores))
    std = float(np.std(scores))
    dynamic = mean + std

    # Never below the absolute floor
    threshold = max(EMPATHY_FLOOR, dynamic)

    logger.info(
        f"Dynamic empathy threshold: {threshold:.3f} "
        f"(population mean={mean:.3f}, σ={std:.3f}, "
        f"n={len(population_scores)})"
    )

    return threshold


def check_concentration(nodes: list[SeedNode]) -> CheckResult:
    """V4: No single category exceeds 40% of seed brain.

    Also enforces: at least 3 distinct categories present.
    """
    if not nodes:
        return CheckResult(passed=False, details={"error": "empty seed brain"})

    counts = Counter(n.node_type for n in nodes)
    total = len(nodes)
    distribution = {cat: count / total for cat, count in counts.items()}

    max_fraction = max(distribution.values())
    num_categories = len(distribution)

    passed = max_fraction <= CONCENTRATION_MAX and num_categories >= 3

    return CheckResult(
        passed=passed,
        details={
            "distribution": distribution,
            "max_fraction": max_fraction,
            "num_categories": num_categories,
            "threshold": CONCENTRATION_MAX,
            "min_categories": 3,
        },
    )


def check_diversity(
    seed_centroid: np.ndarray,
    existing_centroids: list[tuple[str, np.ndarray]],
) -> CheckResult:
    """V3: Cosine distance > 0.08 from ALL existing citizen centroids.

    Must scan ALL existing citizens — no sampling.
    """
    if not existing_centroids:
        # First citizen — automatically diverse
        return CheckResult(
            passed=True,
            details={"nearest_citizen": None, "distance": 1.0, "note": "first citizen"},
        )

    nearest_handle = ""
    nearest_distance = float("inf")

    for handle, centroid in existing_centroids:
        sim = _cosine_similarity(seed_centroid, centroid)
        distance = 1.0 - sim
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_handle = handle

    passed = nearest_distance > DIVERSITY_MIN_DISTANCE

    return CheckResult(
        passed=passed,
        details={
            "nearest_citizen": nearest_handle,
            "distance": nearest_distance,
            "threshold": DIVERSITY_MIN_DISTANCE,
        },
    )


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
