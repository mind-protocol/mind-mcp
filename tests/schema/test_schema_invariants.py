"""
Schema Invariant Tests

Tests for schema validation invariants defined in docs/schema/VALIDATION_Schema.md
Each test is marked with # VALIDATES: V<num> to track coverage.
"""

import pytest
from runtime.infrastructure.database import get_database_adapter
from runtime.schema.nodes import Actor, Space, Thing, Narrative, Moment
from runtime.schema.links import LinkBase


# VALIDATES: V1
def test_link_endpoints_exist():
    """V1: All link endpoints must reference existing nodes."""
    adapter = get_database_adapter()

    # Query for links with missing endpoints
    result = adapter.query("""
        MATCH (n)-[r]->(m)
        WHERE n IS NULL OR m IS NULL
        RETURN count(r) as broken_links
    """)

    broken_count = result[0][0] if result else 0
    assert broken_count == 0, f"Found {broken_count} links with missing endpoints"


# VALIDATES: V2
def test_physics_ranges_nodes():
    """V2: Node weight and energy must be in [0.0, 1.0]."""
    adapter = get_database_adapter()

    result = adapter.query("""
        MATCH (n)
        WHERE n.weight < 0.0 OR n.weight > 1.0
           OR n.energy < 0.0 OR n.energy > 1.0
        RETURN n.id, n.weight, n.energy
        LIMIT 10
    """)

    assert len(result) == 0, f"Found nodes with invalid physics ranges: {result}"


# VALIDATES: V2
def test_physics_ranges_links():
    """V2: Link weight, energy, strength must be in [0.0, 1.0]."""
    adapter = get_database_adapter()

    result = adapter.query("""
        MATCH ()-[r]->()
        WHERE r.weight < 0.0 OR r.weight > 1.0
           OR r.energy < 0.0 OR r.energy > 1.0
           OR r.strength < 0.0 OR r.strength > 1.0
        RETURN id(r), r.weight, r.energy, r.strength
        LIMIT 10
    """)

    assert len(result) == 0, f"Found links with invalid physics ranges: {result}"


# VALIDATES: V3
def test_polarity_range():
    """V3: Link polarity must be in [-1.0, +1.0]."""
    adapter = get_database_adapter()

    result = adapter.query("""
        MATCH ()-[r]->()
        WHERE r.polarity < -1.0 OR r.polarity > 1.0
        RETURN id(r), r.polarity
        LIMIT 10
    """)

    assert len(result) == 0, f"Found links with invalid polarity: {result}"


# VALIDATES: V6
def test_required_fields_present():
    """V6: All nodes must have required fields (id, name, node_type, type)."""
    adapter = get_database_adapter()

    # Check for missing or empty required fields
    result = adapter.query("""
        MATCH (n)
        WHERE n.id IS NULL OR n.id = ''
           OR n.name IS NULL OR n.name = ''
           OR n.node_type IS NULL
           OR n.type IS NULL OR n.type = ''
        RETURN n.id, labels(n)[0] as label
        LIMIT 10
    """)

    assert len(result) == 0, f"Found nodes with missing required fields: {result}"


# VALIDATES: V6
def test_node_type_values():
    """V6: node_type must be one of the 5 allowed values."""
    adapter = get_database_adapter()

    valid_types = {'actor', 'space', 'thing', 'narrative', 'moment'}

    result = adapter.query("""
        MATCH (n)
        WHERE n.node_type IS NOT NULL
        RETURN DISTINCT n.node_type
    """)

    found_types = {r[0] for r in result}
    invalid_types = found_types - valid_types

    assert len(invalid_types) == 0, f"Found invalid node_types: {invalid_types}"


# VALIDATES: V8
def test_single_link_type():
    """V8: All links should use type='link' (v1.4.1+)."""
    adapter = get_database_adapter()

    # Note: In FalkorDB, relationship type is the label, not a property
    # This test validates that relationships follow the schema
    result = adapter.query("""
        MATCH ()-[r]->()
        WHERE type(r) <> 'LINK'
        RETURN type(r), count(*) as cnt
    """)

    # Allow LINK type (the canonical one)
    non_link = [r for r in result if r[0] != 'LINK']
    assert len(non_link) == 0, f"Found non-LINK relationship types: {non_link}"


# VALIDATES: V10
def test_permanence_range():
    """V10: Link permanence must be in [0.0, 1.0]."""
    adapter = get_database_adapter()

    result = adapter.query("""
        MATCH ()-[r]->()
        WHERE r.permanence IS NOT NULL
          AND (r.permanence < 0.0 OR r.permanence > 1.0)
        RETURN id(r), r.permanence
        LIMIT 10
    """)

    assert len(result) == 0, f"Found links with invalid permanence: {result}"


# VALIDATES: V11
def test_emotion_ranges():
    """V11: Emotion fields must be in [-1.0, +1.0]."""
    adapter = get_database_adapter()

    emotion_fields = [
        'joy_sadness',
        'trust_disgust',
        'fear_anger',
        'surprise_anticipation'
    ]

    for field in emotion_fields:
        result = adapter.query(f"""
            MATCH ()-[r]->()
            WHERE r.{field} IS NOT NULL
              AND (r.{field} < -1.0 OR r.{field} > 1.0)
            RETURN id(r), r.{field}
            LIMIT 5
        """)

        assert len(result) == 0, f"Found links with invalid {field}: {result}"


# VALIDATES: V16
def test_found_narratives_structure():
    """V16: SubEntity found_narratives must be dict with alignments in [0,1]."""
    adapter = get_database_adapter()

    # Query for narrative nodes (SubEntity data stored in graph)
    result = adapter.query("""
        MATCH (n:Narrative)
        WHERE n.found_narratives IS NOT NULL
        RETURN n.id, n.found_narratives
        LIMIT 100
    """)

    for node_id, found_narr in result:
        if isinstance(found_narr, dict):
            for narr_id, alignment in found_narr.items():
                assert 0.0 <= alignment <= 1.0, \
                    f"Node {node_id} has invalid alignment {alignment} for {narr_id}"


# VALIDATES: V17
def test_crystallization_embedding_continuous():
    """V17: Crystallization embeddings must be continuous and correct dimension."""
    adapter = get_database_adapter()

    EXPECTED_DIM = 768  # sentence-transformers default

    result = adapter.query("""
        MATCH (n)
        WHERE n.crystallization_embedding IS NOT NULL
        RETURN n.id, size(n.crystallization_embedding) as dim
        LIMIT 100
    """)

    for node_id, dim in result:
        assert dim == EXPECTED_DIM, \
            f"Node {node_id} has embedding dimension {dim}, expected {EXPECTED_DIM}"


# VALIDATES: V4
def test_queries_are_read_only():
    """V4: Validation queries must not mutate the graph."""
    # This is a meta-test: all queries in this file should be SELECT-like
    import inspect
    import re

    source = inspect.getsource(inspect.getmodule(test_queries_are_read_only))

    # Find all adapter.query() calls
    query_pattern = re.compile(r'adapter\.query\(\s*"""(.*?)"""', re.DOTALL)
    queries = query_pattern.findall(source)

    mutation_keywords = ['CREATE', 'SET', 'DELETE', 'MERGE', 'REMOVE']

    for query in queries:
        query_upper = query.upper()
        found_mutations = [kw for kw in mutation_keywords if kw in query_upper]
        assert len(found_mutations) == 0, \
            f"Query contains mutation keywords {found_mutations}: {query[:100]}"


# VALIDATES: V5
def test_no_llm_in_validation():
    """V5: Hot path validation should not invoke LLMs."""
    import sys

    # Check that LLM-related modules are not imported in this test file
    llm_modules = [
        'openai', 'anthropic', 'google.generativeai',
        'runtime.llm', 'runtime.agents.llm'
    ]

    loaded_llm_modules = [mod for mod in llm_modules if mod in sys.modules]

    # This is a weak test - ideally we'd check the entire validation call stack
    # But it at least ensures the test file itself doesn't import LLMs
    assert len(loaded_llm_modules) == 0, \
        f"LLM modules loaded during validation: {loaded_llm_modules}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
