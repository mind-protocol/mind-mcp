"""
Tests for HAS_ACCESS resolution and inheritance.

Validates:
- ALG-1: Direct access check + hierarchical traversal
- B2: Access granting
- B3: Access revocation
- INV-2: All access via HAS_ACCESS links
- INV-8: Link structure (actor -> space, role in content)
- INV-9: Acyclicity of containment

DOCS: docs/universe/ALGORITHM_Universe_Graph.md (ALG-1, ALG-2)
      docs/universe/VALIDATION_Universe_Graph.md (INV-2, INV-8, INV-9)
"""

import json

import pytest

from runtime.universe.space_and_hierarchy_manager import SpaceManager, SpaceError
from runtime.universe.access_resolution_and_link_manager import AccessResolver, AccessError


class TestDirectAccess:
    """ALG-1 Step 1: Direct HAS_ACCESS link check."""

    def test_has_access_direct_owner(self, adapter_with_two_actors):
        """Creator has direct owner access to their Space."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "my-space")
        result = ar.has_access("actor_alice", space_id)

        assert result.granted is True
        assert result.role == "owner"
        assert result.inherited_from is None

    def test_has_access_denied(self, adapter_with_two_actors):
        """Actor without HAS_ACCESS is denied."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "private")
        result = ar.has_access("actor_bob", space_id)

        assert result.granted is False
        assert result.role is None

    def test_has_access_after_grant(self, adapter_with_two_actors):
        """Granted member has direct access."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "team-space")
        ar.grant_access("actor_alice", "actor_bob", space_id, role="member")

        result = ar.has_access("actor_bob", space_id)
        assert result.granted is True
        assert result.role == "member"


class TestInheritedAccess:
    """ALG-1 Step 2: Hierarchical traversal."""

    def test_has_access_inherited_from_parent(self, adapter_with_two_actors):
        """Access to parent Space implies member access to child."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        parent_id = sm.create_space("actor_alice", "parent")
        child_id = sm.create_space("actor_alice", "child", parent_space_id=parent_id)

        # Alice is owner of parent -> she should have inherited access to child
        result = ar.has_access("actor_alice", child_id)
        # Alice has direct owner access to child (she created it)
        assert result.granted is True

    def test_inherited_access_role_downgraded_to_member(self, adapter_with_two_actors):
        """Inherited access downgrades role to at most 'member'."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        parent_id = sm.create_space("actor_alice", "parent")
        child_id = sm.create_space("actor_alice", "child", parent_space_id=parent_id)

        # Grant Bob owner access to parent only
        ar.grant_access("actor_alice", "actor_bob", parent_id, role="admin")

        # Bob has no direct link to child, but parent is ancestor
        result = ar.has_access("actor_bob", child_id)
        assert result.granted is True
        assert result.role == "member"  # Downgraded from admin
        assert result.inherited_from == parent_id

    def test_inherited_access_grandparent(self, adapter_with_two_actors):
        """Access to grandparent implies access to grandchild."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        root_id = sm.create_space("actor_alice", "root")
        mid_id = sm.create_space("actor_alice", "mid", parent_space_id=root_id)
        leaf_id = sm.create_space("actor_alice", "leaf", parent_space_id=mid_id)

        # Grant Bob member to root
        ar.grant_access("actor_alice", "actor_bob", root_id, role="member")

        result = ar.has_access("actor_bob", leaf_id)
        assert result.granted is True
        assert result.role == "member"
        assert result.inherited_from == root_id


class TestGrantAccess:
    """B2: Access Granting."""

    def test_grant_access_creates_link(self, adapter_with_two_actors):
        """Granting access creates a HAS_ACCESS link."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "team")
        ar.grant_access("actor_alice", "actor_bob", space_id, role="member")

        # Verify link exists in adapter
        access_links = [
            l for l in adapter_with_two_actors.links
            if l.src_id == "actor_bob"
            and l.dst_id == space_id
            and l.props.get("type") == "has_access"
        ]
        assert len(access_links) == 1
        content = json.loads(access_links[0].props["content"])
        assert content["role"] == "member"

    def test_grant_access_requires_admin_or_owner(self, adapter_with_two_actors):
        """Only admin/owner can grant access."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "restricted")

        # Add a third actor (charlie) with member role
        adapter_with_two_actors.add_node("actor_charlie", {"Actor"}, {
            "id": "actor_charlie",
            "name": "Charlie",
            "node_type": "actor",
        })
        ar.grant_access("actor_alice", "actor_charlie", space_id, role="member")

        # Charlie (member) tries to grant access to Bob -- should fail
        with pytest.raises(AccessError, match="only owner/admin"):
            ar.grant_access("actor_charlie", "actor_bob", space_id, role="member")

    def test_grant_access_no_access_raises(self, adapter_with_two_actors):
        """Actor with no access cannot grant access."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "private")

        with pytest.raises(AccessError, match="no access"):
            ar.grant_access("actor_bob", "actor_alice", space_id)

    def test_grant_access_invalid_role_raises(self, adapter_with_two_actors):
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "space")
        with pytest.raises(AccessError, match="Invalid role"):
            ar.grant_access("actor_alice", "actor_bob", space_id, role="superadmin")

    def test_grant_access_cannot_exceed_own_role(self, adapter_with_two_actors):
        """Cannot grant a role higher than your own."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "space")
        ar.grant_access("actor_alice", "actor_bob", space_id, role="admin")

        # Add charlie
        adapter_with_two_actors.add_node("actor_charlie", {"Actor"}, {
            "id": "actor_charlie", "name": "Charlie", "node_type": "actor",
        })

        # Bob (admin) tries to grant owner role -- should fail
        with pytest.raises(AccessError, match="Cannot grant role"):
            ar.grant_access("actor_bob", "actor_charlie", space_id, role="owner")

    def test_grant_access_idempotent(self, adapter_with_two_actors):
        """Granting same role twice is idempotent."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "space")
        ar.grant_access("actor_alice", "actor_bob", space_id, role="member")
        ar.grant_access("actor_alice", "actor_bob", space_id, role="member")

        # Should still have exactly one link
        access_links = [
            l for l in adapter_with_two_actors.links
            if l.src_id == "actor_bob"
            and l.dst_id == space_id
            and l.props.get("type") == "has_access"
        ]
        assert len(access_links) == 1


class TestRevokeAccess:
    """B3: Access Revocation."""

    def test_revoke_access_removes_link(self, adapter_with_two_actors):
        """Revoking access removes the HAS_ACCESS link."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "team")
        ar.grant_access("actor_alice", "actor_bob", space_id, role="member")

        # Verify Bob has access
        assert ar.has_access("actor_bob", space_id).granted is True

        # Revoke
        ar.revoke_access("actor_alice", "actor_bob", space_id)

        # Verify Bob no longer has access
        assert ar.has_access("actor_bob", space_id).granted is False

    def test_revoke_last_owner_raises(self, adapter_with_two_actors):
        """Cannot revoke the last owner (INV-1)."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "owned")

        with pytest.raises(AccessError, match="last owner"):
            ar.revoke_access("actor_alice", "actor_alice", space_id)

    def test_revoke_access_no_permission_raises(self, adapter_with_two_actors):
        """Non-admin/owner cannot revoke access."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "team")
        ar.grant_access("actor_alice", "actor_bob", space_id, role="member")

        with pytest.raises(AccessError, match="only owner/admin"):
            ar.revoke_access("actor_bob", "actor_alice", space_id)

    def test_admin_cannot_revoke_owner(self, adapter_with_two_actors):
        """Admin cannot revoke owner access."""
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        # Add charlie as a second owner so the "last owner" check doesn't fire first
        adapter_with_two_actors.add_node("actor_charlie", {"Actor"}, {
            "id": "actor_charlie", "name": "Charlie", "node_type": "actor",
        })
        space_id = sm.create_space("actor_alice", "team")
        ar.grant_access("actor_alice", "actor_charlie", space_id, role="owner")
        ar.grant_access("actor_alice", "actor_bob", space_id, role="admin")

        with pytest.raises(AccessError, match="Admin cannot revoke owner"):
            ar.revoke_access("actor_bob", "actor_alice", space_id)


class TestMembershipQueries:
    """Space membership listing."""

    def test_list_space_members(self, adapter_with_two_actors):
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space_id = sm.create_space("actor_alice", "team")
        ar.grant_access("actor_alice", "actor_bob", space_id, role="member")

        members = ar.list_space_members(space_id)
        member_ids = {m.actor_id for m in members}
        assert "actor_alice" in member_ids
        assert "actor_bob" in member_ids

    def test_list_actor_spaces(self, adapter_with_two_actors):
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        space1 = sm.create_space("actor_alice", "space-1")
        space2 = sm.create_space("actor_alice", "space-2")

        spaces = ar.list_actor_spaces("actor_alice")
        space_ids = {s.space_id for s in spaces}
        assert space1 in space_ids
        assert space2 in space_ids

    def test_list_actor_spaces_empty(self, adapter_with_two_actors):
        sm = SpaceManager(adapter_with_two_actors)
        ar = AccessResolver(adapter_with_two_actors, sm)

        spaces = ar.list_actor_spaces("actor_bob")
        assert spaces == []
