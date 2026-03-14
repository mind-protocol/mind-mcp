"""
Tests for Universe Bootstrap and Metadata.

Validates:
- INV-4: Single universe per graph (exactly one metadata node)
- Migration from flat graph to universe model
- Universe initialization creates metadata + root Space

DOCS: docs/universe/IMPLEMENTATION_Universe_Graph.md (Phase U1)
      docs/universe/VALIDATION_Universe_Graph.md (INV-4)
"""

import pytest

from runtime.universe.space_and_hierarchy_manager import SpaceManager
from runtime.universe.universe_bootstrap_and_metadata import (
    UniverseBootstrap,
    BootstrapError,
)


@pytest.fixture
def bootstrap_setup(adapter_with_actor):
    """Provide UniverseBootstrap with one actor."""
    sm = SpaceManager(adapter_with_actor)
    ub = UniverseBootstrap(adapter_with_actor, sm)
    return adapter_with_actor, sm, ub


class TestInitialize:
    """Universe initialization."""

    def test_initialize_creates_metadata(self, bootstrap_setup):
        """Bootstrap creates a metadata node."""
        adapter, sm, ub = bootstrap_setup

        metadata_id = ub.initialize("venezia", "actor_alice")
        assert metadata_id is not None
        assert metadata_id.startswith("thing_")

        # Verify metadata node exists
        meta = ub.get_metadata()
        assert meta is not None
        assert meta.universe_name == "venezia"

    def test_initialize_creates_root_space(self, bootstrap_setup):
        """Bootstrap creates a root Space owned by the actor."""
        adapter, sm, ub = bootstrap_setup

        ub.initialize("venezia", "actor_alice")

        root_id = ub.get_root_space_id()
        assert root_id is not None

        # Verify root Space exists
        space_info = sm.get_space(root_id)
        assert space_info is not None
        assert "root" in space_info.name.lower()

    def test_initialize_rejects_duplicate(self, bootstrap_setup):
        """INV-4: Cannot initialize twice."""
        adapter, sm, ub = bootstrap_setup

        ub.initialize("venezia", "actor_alice")

        with pytest.raises(BootstrapError, match="already initialized"):
            ub.initialize("venezia-2", "actor_alice")

    def test_validate_metadata_true_after_init(self, bootstrap_setup):
        """validate_metadata returns True after initialization."""
        adapter, sm, ub = bootstrap_setup

        ub.initialize("venezia", "actor_alice")
        assert ub.validate_metadata() is True

    def test_validate_metadata_false_before_init(self, bootstrap_setup):
        """validate_metadata returns False before initialization."""
        adapter, sm, ub = bootstrap_setup

        assert ub.validate_metadata() is False


class TestMigration:
    """Flat graph migration."""

    def test_migrate_creates_root_space(self, bootstrap_setup):
        """Migration creates a root Space."""
        adapter, sm, ub = bootstrap_setup

        root_id = ub.migrate_flat_graph("venezia", "actor_alice")
        assert root_id is not None

        space_info = sm.get_space(root_id)
        assert space_info is not None

    def test_migrate_links_orphan_nodes(self, bootstrap_setup):
        """Migration links orphan nodes to root Space."""
        adapter, sm, ub = bootstrap_setup

        # Add some orphan nodes
        adapter.add_node("moment_old_1", {"Moment"}, {
            "id": "moment_old_1",
            "name": "old moment",
            "node_type": "moment",
        })
        adapter.add_node("thing_old_1", {"Thing"}, {
            "id": "thing_old_1",
            "name": "old thing",
            "node_type": "thing",
        })

        root_id = ub.migrate_flat_graph("venezia", "actor_alice")

        # Verify orphans are linked to root
        orphan_links = [
            l for l in adapter.links
            if l.src_id == root_id
            and l.dst_id in ("moment_old_1", "thing_old_1")
        ]
        assert len(orphan_links) == 2

    def test_migrate_rejects_if_already_initialized(self, bootstrap_setup):
        """Cannot migrate if universe is already initialized."""
        adapter, sm, ub = bootstrap_setup

        ub.initialize("venezia", "actor_alice")

        with pytest.raises(BootstrapError, match="already initialized"):
            ub.migrate_flat_graph("venezia-2", "actor_alice")


class TestGetMetadata:
    """Metadata retrieval."""

    def test_get_metadata_before_init(self, bootstrap_setup):
        adapter, sm, ub = bootstrap_setup
        assert ub.get_metadata() is None

    def test_get_metadata_after_init(self, bootstrap_setup):
        adapter, sm, ub = bootstrap_setup
        ub.initialize("test-universe", "actor_alice")

        meta = ub.get_metadata()
        assert meta is not None
        assert meta.universe_name == "test-universe"
        assert meta.version == "1.0.0"

    def test_get_root_space_before_init(self, bootstrap_setup):
        adapter, sm, ub = bootstrap_setup
        assert ub.get_root_space_id() is None
