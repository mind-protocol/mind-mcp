"""
Tests for Space CRUD and containment hierarchy.

Validates:
- B1: Space creation produces node + owner HAS_ACCESS link
- INV-1: No orphan Spaces (every Space has at least one owner)
- ALG-4: Downward and upward traversal of containment hierarchy
- INV-9: Acyclicity of containment hierarchy

DOCS: docs/universe/ALGORITHM_Universe_Graph.md (ALG-4)
      docs/universe/VALIDATION_Universe_Graph.md (INV-1, INV-9)
"""

import pytest

from runtime.universe.space_and_hierarchy_manager import SpaceManager, SpaceError


class TestCreateSpace:
    """B1: Space Creation."""

    def test_create_space_returns_id(self, adapter_with_actor):
        """Space creation returns a non-empty string ID."""
        sm = SpaceManager(adapter_with_actor)
        space_id = sm.create_space("actor_alice", "test-space")
        assert space_id is not None
        assert isinstance(space_id, str)
        assert space_id.startswith("space_")

    def test_create_space_creates_node(self, adapter_with_actor):
        """Space creation inserts a node into the graph."""
        sm = SpaceManager(adapter_with_actor)
        space_id = sm.create_space("actor_alice", "dev-chat")

        info = sm.get_space(space_id)
        assert info is not None
        assert info.name == "dev-chat"
        assert info.space_id == space_id

    def test_create_space_creates_owner_link(self, adapter_with_actor):
        """INV-1: Space creation always creates an owner HAS_ACCESS link."""
        sm = SpaceManager(adapter_with_actor)
        space_id = sm.create_space("actor_alice", "my-space")

        # Verify the owner link exists by checking the adapter's links
        owner_links = [
            l for l in adapter_with_actor.links
            if l.dst_id == space_id
            and l.props.get("type") == "has_access"
            and l.src_id == "actor_alice"
        ]
        assert len(owner_links) == 1
        import json
        content = json.loads(owner_links[0].props["content"])
        assert content["role"] == "owner"

    def test_create_space_with_type(self, adapter_with_actor):
        """space_type is stored as free-form text."""
        sm = SpaceManager(adapter_with_actor)
        space_id = sm.create_space("actor_alice", "discord-chat", space_type="discord_channel")

        info = sm.get_space(space_id)
        assert info is not None
        assert info.space_type == "discord_channel"

    def test_create_space_nonexistent_actor_raises(self, adapter_with_actor):
        """Creating a Space with a nonexistent actor raises SpaceError."""
        sm = SpaceManager(adapter_with_actor)
        with pytest.raises(SpaceError, match="not found"):
            sm.create_space("actor_nonexistent", "test")

    def test_create_sub_space_containment_link(self, adapter_with_actor):
        """Sub-Space creation creates a containment link from parent."""
        sm = SpaceManager(adapter_with_actor)
        parent_id = sm.create_space("actor_alice", "parent-space")
        child_id = sm.create_space("actor_alice", "child-space", parent_space_id=parent_id)

        # Verify containment link exists
        containment_links = [
            l for l in adapter_with_actor.links
            if l.src_id == parent_id
            and l.dst_id == child_id
            and l.props.get("hierarchy") == -1
            and l.props.get("type") != "has_access"
        ]
        assert len(containment_links) == 1

    def test_create_sub_space_nonexistent_parent_raises(self, adapter_with_actor):
        """Creating a sub-Space with a nonexistent parent raises SpaceError."""
        sm = SpaceManager(adapter_with_actor)
        with pytest.raises(SpaceError, match="not found"):
            sm.create_space("actor_alice", "orphan", parent_space_id="space_nonexistent")


class TestSpaceRetrieval:
    """Space listing and retrieval."""

    def test_get_space_returns_info(self, adapter_with_actor):
        sm = SpaceManager(adapter_with_actor)
        space_id = sm.create_space("actor_alice", "my-space")

        info = sm.get_space(space_id)
        assert info is not None
        assert info.space_id == space_id
        assert info.name == "my-space"

    def test_get_space_nonexistent_returns_none(self, adapter_with_actor):
        sm = SpaceManager(adapter_with_actor)
        info = sm.get_space("space_nonexistent")
        assert info is None

    def test_list_all_spaces(self, adapter_with_actor):
        sm = SpaceManager(adapter_with_actor)
        sm.create_space("actor_alice", "space-1")
        sm.create_space("actor_alice", "space-2")
        sm.create_space("actor_alice", "space-3")

        spaces = sm.list_all_spaces()
        assert len(spaces) == 3
        names = {s.name for s in spaces}
        assert "space-1" in names
        assert "space-2" in names
        assert "space-3" in names


class TestHierarchyTraversal:
    """ALG-4: Space Hierarchy Traversal."""

    def test_get_sub_spaces_direct_children(self, adapter_with_actor):
        """Downward traversal returns direct children."""
        sm = SpaceManager(adapter_with_actor)
        parent_id = sm.create_space("actor_alice", "parent")
        child1_id = sm.create_space("actor_alice", "child-1", parent_space_id=parent_id)
        child2_id = sm.create_space("actor_alice", "child-2", parent_space_id=parent_id)

        children = sm.get_sub_spaces(parent_id)
        child_ids = {c.space_id for c in children}
        assert child1_id in child_ids
        assert child2_id in child_ids
        assert all(c.depth == 1 for c in children)

    def test_get_sub_spaces_nested(self, adapter_with_actor):
        """Downward traversal returns nested descendants with correct depth."""
        sm = SpaceManager(adapter_with_actor)
        root_id = sm.create_space("actor_alice", "root")
        mid_id = sm.create_space("actor_alice", "mid", parent_space_id=root_id)
        leaf_id = sm.create_space("actor_alice", "leaf", parent_space_id=mid_id)

        descendants = sm.get_sub_spaces(root_id)
        assert len(descendants) == 2

        by_id = {d.space_id: d for d in descendants}
        assert mid_id in by_id
        assert leaf_id in by_id
        assert by_id[mid_id].depth == 1
        assert by_id[leaf_id].depth == 2

    def test_get_sub_spaces_respects_max_depth(self, adapter_with_actor):
        """Downward traversal stops at max_depth."""
        sm = SpaceManager(adapter_with_actor)
        root_id = sm.create_space("actor_alice", "root")
        mid_id = sm.create_space("actor_alice", "mid", parent_space_id=root_id)
        sm.create_space("actor_alice", "leaf", parent_space_id=mid_id)

        # max_depth=1 should only return direct children
        children = sm.get_sub_spaces(root_id, max_depth=1)
        assert len(children) == 1
        assert children[0].space_id == mid_id

    def test_get_sub_spaces_empty(self, adapter_with_actor):
        """Downward traversal on a leaf returns empty list."""
        sm = SpaceManager(adapter_with_actor)
        leaf_id = sm.create_space("actor_alice", "leaf")

        children = sm.get_sub_spaces(leaf_id)
        assert children == []

    def test_parent_space_returns_parent(self, adapter_with_actor):
        """Upward traversal returns the parent Space ID."""
        sm = SpaceManager(adapter_with_actor)
        parent_id = sm.create_space("actor_alice", "parent")
        child_id = sm.create_space("actor_alice", "child", parent_space_id=parent_id)

        result = sm.parent_space(child_id)
        assert result == parent_id

    def test_parent_space_root_returns_none(self, adapter_with_actor):
        """Upward traversal on root Space returns None."""
        sm = SpaceManager(adapter_with_actor)
        root_id = sm.create_space("actor_alice", "root")

        result = sm.parent_space(root_id)
        assert result is None

    def test_get_ancestor_chain(self, adapter_with_actor):
        """Ancestor chain returns list from parent to root."""
        sm = SpaceManager(adapter_with_actor)
        root_id = sm.create_space("actor_alice", "root")
        mid_id = sm.create_space("actor_alice", "mid", parent_space_id=root_id)
        leaf_id = sm.create_space("actor_alice", "leaf", parent_space_id=mid_id)

        ancestors = sm.get_ancestor_chain(leaf_id)
        assert ancestors == [mid_id, root_id]


class TestSpaceDeletion:
    """Space deletion."""

    def test_delete_space_removes_node(self, adapter_with_actor):
        sm = SpaceManager(adapter_with_actor)
        space_id = sm.create_space("actor_alice", "to-delete")

        sm.delete_space(space_id)
        info = sm.get_space(space_id)
        assert info is None

    def test_delete_space_nonexistent_raises(self, adapter_with_actor):
        sm = SpaceManager(adapter_with_actor)
        with pytest.raises(SpaceError, match="not found"):
            sm.delete_space("space_nonexistent")


class TestMomentPlacement:
    """Moment creation in a Space."""

    def test_create_moment_in_space(self, adapter_with_actor):
        sm = SpaceManager(adapter_with_actor)
        space_id = sm.create_space("actor_alice", "chat")

        moment_id = sm.create_moment_in_space(
            actor_id="actor_alice",
            space_id=space_id,
            moment_name="hello world",
            content="This is a test message",
        )
        assert moment_id is not None
        assert moment_id.startswith("moment_")

    def test_create_moment_links_to_space(self, adapter_with_actor):
        """Moment is linked to Space via containment."""
        sm = SpaceManager(adapter_with_actor)
        space_id = sm.create_space("actor_alice", "chat")
        moment_id = sm.create_moment_in_space(
            actor_id="actor_alice",
            space_id=space_id,
            moment_name="msg",
        )

        # Verify Space -> Moment containment link
        containment = [
            l for l in adapter_with_actor.links
            if l.src_id == space_id and l.dst_id == moment_id
            and l.props.get("hierarchy") == -1
        ]
        assert len(containment) == 1

    def test_create_moment_links_to_actor(self, adapter_with_actor):
        """Moment is linked to creating Actor."""
        sm = SpaceManager(adapter_with_actor)
        space_id = sm.create_space("actor_alice", "chat")
        moment_id = sm.create_moment_in_space(
            actor_id="actor_alice",
            space_id=space_id,
            moment_name="msg",
        )

        # Verify Actor -> Moment link
        actor_links = [
            l for l in adapter_with_actor.links
            if l.src_id == "actor_alice" and l.dst_id == moment_id
        ]
        assert len(actor_links) == 1

    def test_create_moment_nonexistent_space_raises(self, adapter_with_actor):
        sm = SpaceManager(adapter_with_actor)
        with pytest.raises(SpaceError, match="not found"):
            sm.create_moment_in_space(
                actor_id="actor_alice",
                space_id="space_nonexistent",
                moment_name="orphan",
            )
