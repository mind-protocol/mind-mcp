"""
Tests for Moment Perception Routing.

Validates:
- ALG-5: Route moments to actors with direct and inherited access
- B4: Moment Recording (perception routing part)

DOCS: docs/universe/ALGORITHM_Universe_Graph.md (ALG-5)
      docs/universe/IMPLEMENTATION_Universe_Graph.md (Phase U6)
"""

import pytest

from runtime.universe.space_and_hierarchy_manager import SpaceManager
from runtime.universe.access_resolution_and_link_manager import AccessResolver
from runtime.universe.moment_perception_router import MomentPerceptionRouter


@pytest.fixture
def routing_setup(adapter_with_two_actors):
    """Provide MomentPerceptionRouter with two actors."""
    # Add a third actor
    adapter_with_two_actors.add_node("actor_charlie", {"Actor"}, {
        "id": "actor_charlie",
        "name": "Charlie",
        "node_type": "actor",
    })

    sm = SpaceManager(adapter_with_two_actors)
    ar = AccessResolver(adapter_with_two_actors, sm)
    router = MomentPerceptionRouter(adapter_with_two_actors, ar, sm)
    return adapter_with_two_actors, sm, ar, router


class TestDirectPerception:
    """ALG-5: Direct access perception."""

    def test_direct_members_perceive(self, routing_setup):
        """Actors with direct HAS_ACCESS see the moment."""
        adapter, sm, ar, router = routing_setup

        space_id = sm.create_space("actor_alice", "chat")
        ar.grant_access("actor_alice", "actor_bob", space_id, role="member")

        moment_id = sm.create_moment_in_space(
            "actor_alice", space_id, "hello"
        )

        actors = router.route(moment_id, space_id)
        assert "actor_alice" in actors
        assert "actor_bob" in actors

    def test_non_members_excluded(self, routing_setup):
        """Actors without access do NOT see the moment."""
        adapter, sm, ar, router = routing_setup

        space_id = sm.create_space("actor_alice", "private")
        moment_id = sm.create_moment_in_space(
            "actor_alice", space_id, "secret"
        )

        actors = router.route(moment_id, space_id)
        assert "actor_alice" in actors
        assert "actor_bob" not in actors
        assert "actor_charlie" not in actors


class TestInheritedPerception:
    """ALG-5: Inherited access perception."""

    def test_ancestor_members_perceive(self, routing_setup):
        """Actors with access to parent Space perceive child moments."""
        adapter, sm, ar, router = routing_setup

        parent_id = sm.create_space("actor_alice", "parent")
        child_id = sm.create_space("actor_alice", "child", parent_space_id=parent_id)

        # Grant Bob access to parent only
        ar.grant_access("actor_alice", "actor_bob", parent_id, role="member")

        moment_id = sm.create_moment_in_space(
            "actor_alice", child_id, "in-child"
        )

        actors = router.route(moment_id, child_id)
        # Alice has direct access to child (she created it)
        assert "actor_alice" in actors
        # Bob has inherited access via parent
        assert "actor_bob" in actors

    def test_deep_inheritance_perception(self, routing_setup):
        """Actors with access to grandparent perceive grandchild moments."""
        adapter, sm, ar, router = routing_setup

        root_id = sm.create_space("actor_alice", "root")
        mid_id = sm.create_space("actor_alice", "mid", parent_space_id=root_id)
        leaf_id = sm.create_space("actor_alice", "leaf", parent_space_id=mid_id)

        # Grant Bob access to root
        ar.grant_access("actor_alice", "actor_bob", root_id, role="member")

        moment_id = sm.create_moment_in_space(
            "actor_alice", leaf_id, "deep-msg"
        )

        actors = router.route(moment_id, leaf_id)
        assert "actor_bob" in actors


class TestDeduplication:
    """Routing deduplicates actors."""

    def test_no_duplicate_actors(self, routing_setup):
        """An actor with both direct and inherited access appears once."""
        adapter, sm, ar, router = routing_setup

        parent_id = sm.create_space("actor_alice", "parent")
        child_id = sm.create_space("actor_alice", "child", parent_space_id=parent_id)

        # Alice is owner of both parent and child
        moment_id = sm.create_moment_in_space(
            "actor_alice", child_id, "msg"
        )

        actors = router.route(moment_id, child_id)
        # Alice should appear only once
        assert actors.count("actor_alice") == 1


class TestRouteAndInject:
    """Convenience route + inject method."""

    def test_route_and_inject_returns_actors(self, routing_setup):
        adapter, sm, ar, router = routing_setup

        space_id = sm.create_space("actor_alice", "chat")
        moment_id = sm.create_moment_in_space(
            "actor_alice", space_id, "msg"
        )

        actors = router.route_and_inject(moment_id, space_id)
        assert "actor_alice" in actors

    def test_inject_stimulus_does_not_raise(self, routing_setup):
        """inject_stimulus is a safe placeholder that logs but does not crash."""
        adapter, sm, ar, router = routing_setup

        # Should not raise even with nonexistent IDs
        router.inject_stimulus("actor_alice", "moment_test", "space_test", encrypted=False)
        router.inject_stimulus("actor_alice", "moment_test", "space_test", encrypted=True)
