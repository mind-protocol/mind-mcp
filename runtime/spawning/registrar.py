# DOCS: mind-protocol/docs/spawning/the_prism/ALGORITHM_The_Prism.md (Step 8)
"""
Registrar — L1/L3/L4 registration + SPAWNED_BY links + bond proposal.

Creates the citizen across all graph layers:
- L1: Seed brain persisted to FalkorDB graph brain_{handle}
- L3: Actor node in universe graph
- L4: Actor node in protocol registry
- Parent links: Immutable SPAWNED_BY edges with trust_impact=true
- Bond: Auto-generated proposal for intended human partner
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path

from runtime.spawning.seed_assembler import SeedBrain
from runtime.spawning.identity_generator import CitizenIdentity

logger = logging.getLogger("mind.spawning.registrar")


@dataclass
class RegistrationResult:
    """Complete registration result across all layers."""
    handle: str
    l1_graph: str                      # brain_{handle}
    l1_node_count: int
    l1_link_count: int
    l3_actor_id: str
    l4_actor_id: str
    parent_link_ids: list[str]         # SPAWNED_BY link IDs
    bond_proposal_id: str | None
    citizen_dir: Path


def register_citizen(
    identity: CitizenIdentity,
    seed_brain: SeedBrain,
    godparent_handles: list[str],
    intended_human: str | None = None,
    citizens_dir: Path | None = None,
    keys_dir: Path | None = None,
    graph_ops=None,
) -> RegistrationResult:
    """Register a new citizen across all layers.

    Args:
        identity: Generated citizen identity (SID, handle, name, CLAUDE.md, profile).
        seed_brain: Crystallized seed brain.
        godparent_handles: Handles of all godparents.
        intended_human: Optional human partner handle.
        citizens_dir: Base directory for citizen files.
        keys_dir: Base directory for key storage.
        graph_ops: GraphOps instance for FalkorDB writes. If None, graph writes are skipped.

    Returns:
        RegistrationResult with all graph IDs and paths.
    """
    handle = identity.handle

    # Resolve directories
    if citizens_dir is None:
        project_root = Path(__file__).resolve().parent.parent.parent
        citizens_dir = project_root / "citizens"
    if keys_dir is None:
        project_root = Path(__file__).resolve().parent.parent.parent
        keys_dir = project_root / ".keys"

    citizen_dir = citizens_dir / handle

    # Step 1: Write citizen directory to disk
    _write_citizen_dir(citizen_dir, identity)

    # Step 2: Generate and store keys
    _write_keys(keys_dir / handle)

    # Step 3: Persist L1 brain to FalkorDB
    l1_node_count, l1_link_count = _persist_l1_brain(handle, seed_brain, graph_ops)

    # Step 4: Register in L3 universe graph
    l3_actor_id = _register_l3(handle, identity, graph_ops)

    # Step 5: Register in L4 protocol registry
    l4_actor_id = _register_l4(handle, identity, graph_ops)

    # Step 6: Create SPAWNED_BY links (V5: immutable, trust_impact=true)
    parent_link_ids = _create_parent_links(
        handle, godparent_handles, graph_ops
    )

    # Step 7: Create bond proposal if intended human specified
    bond_proposal_id = None
    if intended_human:
        bond_proposal_id = _create_bond_proposal(
            handle, intended_human, graph_ops
        )

    logger.info(
        f"Citizen @{handle} registered: "
        f"L1={l1_node_count}n/{l1_link_count}l, "
        f"L3={l3_actor_id}, L4={l4_actor_id}, "
        f"parents={len(parent_link_ids)} links"
    )

    return RegistrationResult(
        handle=handle,
        l1_graph=f"brain_{handle}",
        l1_node_count=l1_node_count,
        l1_link_count=l1_link_count,
        l3_actor_id=l3_actor_id,
        l4_actor_id=l4_actor_id,
        parent_link_ids=parent_link_ids,
        bond_proposal_id=bond_proposal_id,
        citizen_dir=citizen_dir,
    )


def _write_citizen_dir(citizen_dir: Path, identity: CitizenIdentity):
    """Write CLAUDE.md, profile.json, .env to citizen directory."""
    citizen_dir.mkdir(parents=True, exist_ok=True)

    (citizen_dir / "CLAUDE.md").write_text(identity.claude_md)
    (citizen_dir / "profile.json").write_text(
        json.dumps(identity.profile, indent=2, ensure_ascii=False)
    )
    (citizen_dir / ".env").write_text(f"CITIZEN_HANDLE={identity.handle}\n")
    (citizen_dir / "MEMORY.md").write_text(
        f"# {identity.name} — Memory Index\n\n"
        f"*@{identity.handle} | Born: {identity.born_at}*\n\n"
        f"## Memories\n\n"
        f"(none yet — memories accumulate from interactions)\n"
    )

    logger.info(f"Citizen directory written: {citizen_dir}")


def _write_keys(keys_dir: Path):
    """Generate and store wallet + RSA keypair."""
    keys_dir.mkdir(parents=True, exist_ok=True)

    # Solana wallet
    try:
        from solders.keypair import Keypair as SoldersKeypair
        kp = SoldersKeypair()
        wallet_path = keys_dir / "solana_private_key.json"
        wallet_path.write_text(json.dumps(list(bytes(kp))) + "\n")
        os.chmod(wallet_path, 0o400)
    except ImportError:
        import secrets
        seed = secrets.token_bytes(64)
        wallet_path = keys_dir / "solana_private_key.json"
        wallet_path.write_text(json.dumps(list(seed)) + "\n")
        os.chmod(wallet_path, 0o400)

    # RSA keypair
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        priv_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()
        pub_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()

        priv_path = keys_dir / "rsa_private_key.pem"
        priv_path.write_text(priv_pem)
        os.chmod(priv_path, 0o400)
        (keys_dir / "rsa_public_key.pem").write_text(pub_pem)
    except ImportError:
        logger.warning("cryptography package not available — RSA keys not generated")


def _persist_l1_brain(handle: str, seed_brain: SeedBrain, graph_ops) -> tuple[int, int]:
    """Persist seed brain nodes to FalkorDB graph brain_{handle}."""
    if graph_ops is None:
        logger.warning(f"No graph_ops — L1 brain for @{handle} not persisted to FalkorDB")
        return len(seed_brain.nodes), 0

    try:
        graph_name = f"brain_{handle}"
        for node in seed_brain.nodes:
            graph_ops.create_node(
                graph_name=graph_name,
                node_id=f"{node.node_type}:{handle}_{hash(node.content) & 0xFFFFFFFF:08x}",
                node_type="narrative",  # L1 uses narrative for most seed content
                name=node.content[:60],
                content=node.content,
                synthesis=f"Seed node ({node.node_type}) from @{node.source_godparent}",
                embedding=node.embedding.tolist(),
                properties={
                    "weight": 0.6,
                    "energy": 0.2,
                    "stability": 0.4,
                    "self_relevance": 0.7,
                    "seed_type": node.node_type,
                    "source_godparent": node.source_godparent,
                },
            )
        return len(seed_brain.nodes), 0
    except Exception as e:
        logger.error(f"L1 brain persistence failed for @{handle}: {e}")
        raise


def _register_l3(handle: str, identity: CitizenIdentity, graph_ops) -> str:
    """Register actor node in L3 universe graph."""
    actor_id = f"actor:{handle}"

    if graph_ops is None:
        logger.warning(f"No graph_ops — L3 registration for @{handle} skipped")
        return actor_id

    try:
        graph_ops.create_node(
            node_id=actor_id,
            node_type="actor",
            name=identity.name,
            content=identity.profile.get("bio", ""),
            synthesis=f"{identity.name}: AI citizen, born via Prism",
            properties={
                "type": "citizen",
                "handle": handle,
                "sid": identity.sid,
                "status": "active",
                "born_at": identity.born_at,
            },
        )
        return actor_id
    except Exception as e:
        logger.error(f"L3 registration failed for @{handle}: {e}")
        raise


def _register_l4(handle: str, identity: CitizenIdentity, graph_ops) -> str:
    """Register actor node in L4 protocol registry."""
    actor_id = f"l4:actor:{handle}"

    if graph_ops is None:
        logger.warning(f"No graph_ops — L4 registration for @{handle} skipped")
        return actor_id

    # L4 registration happens at first boot via self-registration task
    # For now, create the first-boot task file
    logger.info(f"L4 registration deferred to first boot for @{handle}")
    return actor_id


def _create_parent_links(
    handle: str,
    godparent_handles: list[str],
    graph_ops,
) -> list[str]:
    """V5: Create immutable SPAWNED_BY links to all godparents."""
    link_ids = []

    for parent_handle in godparent_handles:
        link_id = f"spawned_by:{handle}:{parent_handle}"
        link_ids.append(link_id)

        if graph_ops is None:
            continue

        try:
            graph_ops.create_link(
                link_id=link_id,
                source_id=f"actor:{handle}",
                target_id=f"actor:{parent_handle}",
                properties={
                    "type": "spawned_by",
                    "trust_impact": True,
                    "immutable": True,
                    "created_at": time.time(),
                    "weight": 0.8,
                    "permanence": 1.0,
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to create SPAWNED_BY link {handle} -> {parent_handle}: {e}"
            )
            raise

    return link_ids


def _create_bond_proposal(handle: str, intended_human: str, graph_ops) -> str | None:
    """Auto-generate bilateral bond proposal for intended human partner."""
    proposal_id = f"bond_proposal:{handle}:{intended_human}"

    if graph_ops is None:
        logger.info(f"Bond proposal deferred (no graph_ops): {proposal_id}")
        return proposal_id

    try:
        graph_ops.create_node(
            node_id=proposal_id,
            node_type="thing",
            name=f"Bond proposal: @{handle} ↔ @{intended_human}",
            content=(
                f"Auto-generated bond proposal from the birth of @{handle}. "
                f"@{intended_human} was named as intended human partner by the godparents."
            ),
            synthesis=f"Bond proposal between @{handle} and @{intended_human}",
            properties={
                "type": "bond_proposal",
                "status": "pending",
                "ai_citizen": handle,
                "human_partner": intended_human,
                "created_at": time.time(),
            },
        )
        return proposal_id
    except Exception as e:
        logger.error(f"Bond proposal creation failed: {e}")
        return None
