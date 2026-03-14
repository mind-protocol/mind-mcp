"""
Integration tests for the full universe lifecycle.

Tests the interaction between multiple universe components working together:
- Bootstrap -> Space creation -> Moment -> Perception routing
- Org creation -> Membership -> Access resolution
- Hierarchical access across nested Spaces

DOCS: docs/universe/IMPLEMENTATION_Universe_Graph.md (Phase U6)
"""

import pytest

from runtime.universe.space_and_hierarchy_manager import SpaceManager
from runtime.universe.access_resolution_and_link_manager import AccessResolver
from runtime.universe.organization_lifecycle_manager import OrgManager
from runtime.universe.moment_perception_router import MomentPerceptionRouter
from runtime.universe.universe_bootstrap_and_metadata import UniverseBootstrap


@pytest.fixture
def full_universe(adapter_with_two_actors):
    """Provide a fully wired universe with all managers and two actors."""
    # Add a third actor
    adapter_with_two_actors.add_node("actor_charlie", {"Actor"}, {
        "id": "actor_charlie",
        "name": "Charlie",
        "node_type": "actor",
    })

    sm = SpaceManager(adapter_with_two_actors)
    ar = AccessResolver(adapter_with_two_actors, sm)
    om = OrgManager(adapter_with_two_actors, sm, ar)
    router = MomentPerceptionRouter(adapter_with_two_actors, ar, sm)
    bootstrap = UniverseBootstrap(adapter_with_two_actors, sm)

    return {
        "adapter": adapter_with_two_actors,
        "space_manager": sm,
        "access_resolver": ar,
        "org_manager": om,
        "router": router,
        "bootstrap": bootstrap,
    }


class TestBootstrapToMoment:
    """B1 + B4: Create universe, Space, record Moment."""

    def test_full_lifecycle(self, full_universe):
        """Bootstrap -> create Space -> create Moment -> route perception."""
        u = full_universe

        # Bootstrap universe
        metadata_id = u["bootstrap"].initialize("venezia", "actor_alice")
        assert metadata_id is not None
        assert u["bootstrap"].validate_metadata() is True

        root_id = u["bootstrap"].get_root_space_id()
        assert root_id is not None

        # Create a sub-Space under root
        chat_id = u["space_manager"].create_space(
            "actor_alice", "general-chat", parent_space_id=root_id
        )
        assert chat_id is not None

        # Grant Bob access to chat
        u["access_resolver"].grant_access(
            "actor_alice", "actor_bob", chat_id, role="member"
        )

        # Create a moment in the chat
        moment_id = u["space_manager"].create_moment_in_space(
            "actor_alice", chat_id, "Hello everyone!"
        )
        assert moment_id is not None

        # Route perception
        actors = u["router"].route(moment_id, chat_id)
        assert "actor_alice" in actors
        assert "actor_bob" in actors
        assert "actor_charlie" not in actors


class TestOrgMembershipAccess:
    """B5 + B6: Create org, join, verify access."""

    def test_org_lifecycle(self, full_universe):
        """Create org -> join -> verify access to hall."""
        u = full_universe

        # Alice creates org
        org = u["org_manager"].create_organization(
            "actor_alice", "MindForge", "Build the protocol"
        )

        # Verify Alice has access
        assert u["access_resolver"].has_access("actor_alice", org.hall_space_id).granted

        # Bob joins (Alice approves)
        u["org_manager"].join_organization("actor_bob", org.narrative_id, "actor_alice")

        # Verify Bob has access
        result = u["access_resolver"].has_access("actor_bob", org.hall_space_id)
        assert result.granted is True
        assert result.role == "member"

        # Charlie has no access
        assert u["access_resolver"].has_access("actor_charlie", org.hall_space_id).granted is False

    def test_org_moment_routing(self, full_universe):
        """Moments in org hall Space are routed to org members."""
        u = full_universe

        org = u["org_manager"].create_organization(
            "actor_alice", "TestOrg", "Testing"
        )
        u["org_manager"].join_organization("actor_bob", org.narrative_id, "actor_alice")

        # Create moment in hall
        moment_id = u["space_manager"].create_moment_in_space(
            "actor_alice", org.hall_space_id, "Org announcement"
        )

        actors = u["router"].route(moment_id, org.hall_space_id)
        assert "actor_alice" in actors
        assert "actor_bob" in actors
        assert "actor_charlie" not in actors


class TestNestedSpaceAccess:
    """Hierarchical access across nested Spaces."""

    def test_nested_access_inheritance(self, full_universe):
        """Access to parent propagates to child as member."""
        u = full_universe

        # Create hierarchy: root -> project -> dev
        root_id = u["space_manager"].create_space("actor_alice", "root")
        project_id = u["space_manager"].create_space(
            "actor_alice", "project-x", parent_space_id=root_id
        )
        dev_id = u["space_manager"].create_space(
            "actor_alice", "dev-channel", parent_space_id=project_id
        )

        # Grant Bob admin to root
        u["access_resolver"].grant_access(
            "actor_alice", "actor_bob", root_id, role="admin"
        )

        # Bob should have inherited member access to dev channel
        result = u["access_resolver"].has_access("actor_bob", dev_id)
        assert result.granted is True
        assert result.role == "member"  # Downgraded
        assert result.inherited_from == root_id

        # Moment in dev should be visible to Bob
        moment_id = u["space_manager"].create_moment_in_space(
            "actor_alice", dev_id, "dev update"
        )
        actors = u["router"].route(moment_id, dev_id)
        assert "actor_bob" in actors

    def test_direct_overrides_inherited(self, full_universe):
        """Direct access takes precedence over inherited."""
        u = full_universe

        parent_id = u["space_manager"].create_space("actor_alice", "parent")
        child_id = u["space_manager"].create_space(
            "actor_alice", "child", parent_space_id=parent_id
        )

        # Grant Bob member to parent
        u["access_resolver"].grant_access(
            "actor_alice", "actor_bob", parent_id, role="member"
        )
        # Grant Bob admin to child directly
        u["access_resolver"].grant_access(
            "actor_alice", "actor_bob", child_id, role="admin"
        )

        # Direct access should win
        result = u["access_resolver"].has_access("actor_bob", child_id)
        assert result.granted is True
        assert result.role == "admin"
        assert result.inherited_from is None  # Direct, not inherited


class TestAccessIsolation:
    """Verify access control isolation."""

    def test_no_cross_space_access(self, full_universe):
        """Access to one Space does NOT imply access to a sibling."""
        u = full_universe

        parent_id = u["space_manager"].create_space("actor_alice", "parent")
        sibling_a = u["space_manager"].create_space(
            "actor_alice", "sibling-a", parent_space_id=parent_id
        )
        sibling_b = u["space_manager"].create_space(
            "actor_alice", "sibling-b", parent_space_id=parent_id
        )

        # Grant Bob direct access to sibling_a only
        u["access_resolver"].grant_access(
            "actor_alice", "actor_bob", sibling_a, role="member"
        )

        # Bob has access to sibling_a
        assert u["access_resolver"].has_access("actor_bob", sibling_a).granted is True

        # Bob does NOT have access to sibling_b (no parent access, no direct)
        assert u["access_resolver"].has_access("actor_bob", sibling_b).granted is False

    def test_revoked_access_prevents_perception(self, full_universe):
        """After access revocation, moments are no longer routed."""
        u = full_universe

        space_id = u["space_manager"].create_space("actor_alice", "chat")
        u["access_resolver"].grant_access(
            "actor_alice", "actor_bob", space_id, role="member"
        )

        # Bob sees moments
        moment1 = u["space_manager"].create_moment_in_space(
            "actor_alice", space_id, "msg1"
        )
        assert "actor_bob" in u["router"].route(moment1, space_id)

        # Revoke Bob's access
        u["access_resolver"].revoke_access("actor_alice", "actor_bob", space_id)

        # Bob no longer sees moments
        moment2 = u["space_manager"].create_moment_in_space(
            "actor_alice", space_id, "msg2"
        )
        assert "actor_bob" not in u["router"].route(moment2, space_id)
