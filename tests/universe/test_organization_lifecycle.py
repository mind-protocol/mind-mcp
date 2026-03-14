"""
Tests for Organization Lifecycle Manager.

Validates:
- ALG-7: Organization creation (Narrative + hall Space)
- ALG-8: Reputation computation
- B5: Organization Creation
- B6: Organization Membership (join)
- Dissolution detection

DOCS: docs/universe/ALGORITHM_Universe_Graph.md (ALG-7, ALG-8)
      docs/universe/IMPLEMENTATION_Universe_Graph.md (Phase U4)
"""

import json

import pytest

from runtime.universe.space_and_hierarchy_manager import SpaceManager
from runtime.universe.access_resolution_and_link_manager import AccessResolver
from runtime.universe.organization_lifecycle_manager import OrgManager, OrgError


@pytest.fixture
def org_setup(adapter_with_two_actors):
    """Provide OrgManager with two actors."""
    sm = SpaceManager(adapter_with_two_actors)
    ar = AccessResolver(adapter_with_two_actors, sm)
    om = OrgManager(adapter_with_two_actors, sm, ar)
    return adapter_with_two_actors, sm, ar, om


class TestCreateOrganization:
    """ALG-7, B5: Organization Creation."""

    def test_create_org_returns_info(self, org_setup):
        adapter, sm, ar, om = org_setup
        org = om.create_organization(
            founder_id="actor_alice",
            name="MindForge",
            mission_statement="Build the protocol",
        )

        assert org.narrative_id is not None
        assert org.narrative_id.startswith("narrative_")
        assert org.hall_space_id is not None
        assert org.hall_space_id.startswith("space_")
        assert org.founder_id == "actor_alice"
        assert org.name == "MindForge"

    def test_create_org_creates_narrative(self, org_setup):
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        # Verify Narrative node exists
        node = adapter.nodes.get(org.narrative_id)
        assert node is not None
        assert node.props.get("type") == "organization"
        assert node.props.get("node_type") == "narrative"

    def test_create_org_creates_hall_space(self, org_setup):
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        # Verify hall Space exists
        space_info = sm.get_space(org.hall_space_id)
        assert space_info is not None
        assert "hall" in space_info.name.lower()

    def test_create_org_founder_has_access(self, org_setup):
        """B5: Founder has owner access to hall Space."""
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        result = ar.has_access("actor_alice", org.hall_space_id)
        assert result.granted is True
        assert result.role == "owner"

    def test_create_org_narrative_links_to_hall(self, org_setup):
        """Narrative -> hall Space link with hierarchy=-1."""
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        narrative_to_hall = [
            l for l in adapter.links
            if l.src_id == org.narrative_id
            and l.dst_id == org.hall_space_id
            and l.props.get("hierarchy") == -1
        ]
        assert len(narrative_to_hall) == 1

    def test_create_org_founder_believes(self, org_setup):
        """B5: Founder has BELIEVES link to Narrative."""
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        believes_links = [
            l for l in adapter.links
            if l.src_id == "actor_alice"
            and l.dst_id == org.narrative_id
            and l.props.get("type") == "believes"
        ]
        assert len(believes_links) == 1
        assert believes_links[0].props.get("trust") == 0.8


class TestJoinOrganization:
    """B6: Organization Membership."""

    def test_join_org_creates_member_access(self, org_setup):
        """Joining creates HAS_ACCESS (member) to hall Space."""
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        om.join_organization("actor_bob", org.narrative_id, "actor_alice")

        result = ar.has_access("actor_bob", org.hall_space_id)
        assert result.granted is True
        assert result.role == "member"

    def test_join_org_creates_believes_link(self, org_setup):
        """Joining creates BELIEVES link to Narrative."""
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        om.join_organization("actor_bob", org.narrative_id, "actor_alice")

        believes_links = [
            l for l in adapter.links
            if l.src_id == "actor_bob"
            and l.dst_id == org.narrative_id
            and l.props.get("type") == "believes"
        ]
        assert len(believes_links) == 1

    def test_join_org_nonexistent_raises(self, org_setup):
        """Joining a nonexistent org raises OrgError."""
        adapter, sm, ar, om = org_setup

        with pytest.raises(OrgError, match="no hall Space"):
            om.join_organization("actor_bob", "narrative_nonexistent", "actor_alice")


class TestOrgReputation:
    """ALG-8: Reputation computation."""

    def test_org_reputation_single_link(self, org_setup):
        """Reputation from a single BELIEVES link."""
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        # Founder has believes link with trust=0.8, weight=1.0
        rep = om.compute_org_reputation(org.narrative_id)
        assert rep == pytest.approx(0.8, abs=0.01)

    def test_org_reputation_multiple_links(self, org_setup):
        """Reputation from multiple BELIEVES links is weighted average."""
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        om.join_organization("actor_bob", org.narrative_id, "actor_alice")

        # Alice: trust=0.8, weight=1.0
        # Bob: trust=0.5, weight=0.5
        # reputation = (0.8*1.0 + 0.5*0.5) / (1.0 + 0.5) = 1.05 / 1.5 = 0.7
        rep = om.compute_org_reputation(org.narrative_id)
        assert rep == pytest.approx(0.7, abs=0.01)

    def test_org_reputation_no_links(self, org_setup):
        """Reputation is 0.0 when no qualifying links exist."""
        adapter, sm, ar, om = org_setup

        rep = om.compute_org_reputation("narrative_nonexistent")
        assert rep == 0.0


class TestDissolution:
    """ALG-7: Dissolution detection."""

    def test_not_dissolved_when_active(self, org_setup):
        """Active org should not be dissolved."""
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        assert om.check_dissolution(org.narrative_id) is False

    def test_dissolved_when_no_hall(self, org_setup):
        """Org with no hall Space is effectively dissolved."""
        adapter, sm, ar, om = org_setup

        # Create narrative without hall
        adapter.add_node("narrative_orphan", {"Narrative"}, {
            "id": "narrative_orphan",
            "name": "Orphan Org",
            "node_type": "narrative",
            "type": "organization",
        })

        assert om.check_dissolution("narrative_orphan") is True

    def test_dissolved_when_all_links_decayed(self, org_setup):
        """Org where all links have decayed below threshold should dissolve."""
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "A test org")

        # Manually decay all HAS_ACCESS links to hall
        for link in adapter.links:
            if link.dst_id == org.hall_space_id and link.props.get("type") == "has_access":
                link.props["weight"] = 0.001

        # Decay BELIEVES links
        for link in adapter.links:
            if link.dst_id == org.narrative_id and link.props.get("type") == "believes":
                link.props["weight"] = 0.001

        assert om.check_dissolution(org.narrative_id) is True


class TestGetOrganization:
    """Organization retrieval."""

    def test_get_organization(self, org_setup):
        adapter, sm, ar, om = org_setup
        org = om.create_organization("actor_alice", "TestOrg", "Build things")

        retrieved = om.get_organization(org.narrative_id)
        assert retrieved is not None
        assert retrieved.name == "TestOrg"
        assert retrieved.founder_id == "actor_alice"

    def test_get_organization_nonexistent(self, org_setup):
        adapter, sm, ar, om = org_setup
        result = om.get_organization("narrative_nonexistent")
        assert result is None
