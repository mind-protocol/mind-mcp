# IMPLEMENTATION -- Universe Graph

```
STATUS: DESIGNING
CREATED: 2026-03-14
UPDATED_BY: Force 1 (architect)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Universe_Graph.md
PATTERNS:        ./PATTERNS_Universe_Graph.md
BEHAVIORS:       ./BEHAVIORS_Universe_Graph.md
ALGORITHM:       ./ALGORITHM_Universe_Graph.md
VALIDATION:      ./VALIDATION_Universe_Graph.md
THIS:            ./IMPLEMENTATION_Universe_Graph.md
SYNC:            ./SYNC_Universe_Graph.md

IMPL:            runtime/universe/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/
├── universe/
│   ├── __init__.py                                  # Exports: SpaceManager, AccessResolver, UniverseBootstrap
│   ├── space_and_hierarchy_manager.py               # Space CRUD, containment hierarchy, sub-Space traversal
│   ├── access_resolution_and_link_manager.py        # HAS_ACCESS link creation, ALG-1 resolution, role checks
│   ├── organization_lifecycle_manager.py            # Org creation (Narrative + hall Space), membership, dissolution check
│   ├── moment_perception_router.py                  # ALG-5: route moments to actors with access
│   ├── universe_bootstrap_and_metadata.py           # Universe graph init, metadata node, migration from flat graph
│   └── constants_l3_physics.py                      # L3-specific physics parameters (thresholds, intervals, decay rates)
├── crypto/
│   ├── __init__.py                                  # Exports: KeyManager, ContentEncryptor
│   ├── aes256_content_encryptor.py                  # AES-256-GCM encrypt/decrypt for content, synthesis, embedding
│   ├── rsa_key_manager.py                           # RSA key pair generation, public key registry, key wrapping
│   ├── space_key_distribution_and_rotation.py       # Per-Space symmetric key lifecycle: create, grant, rotate
│   └── encrypted_field_codec.py                     # Base64 encode/decode, plaintext detection, field-level helpers
├── physics/
│   ├── l3_energy_propagation_and_decay.py           # ALG-6: L3 energy injection, propagation (Law 2), decay (Law 3)
│   ├── l3_weight_consolidation.py                   # ALG-6: L3 consolidation (Law 6) with structural_utility gate
│   └── l3_macro_crystallization.py                  # ALG-3: dense cluster detection, hub creation, post-crystallization
mcp/
├── tools/
│   ├── space_management_handler.py                  # MCP tool: space_manage (create, list, grant_access, revoke_access)
│   └── universe_admin_handler.py                    # MCP tool: universe_admin (bootstrap, migrate, status, validate)
tests/
├── universe/
│   ├── __init__.py
│   ├── test_space_crud_and_hierarchy.py             # Unit: Space creation, containment, sub-Space traversal
│   ├── test_access_resolution_and_inheritance.py    # Unit: ALG-1, direct access, inherited access, edge cases
│   ├── test_encryption_roundtrip_and_coverage.py    # Unit: ALG-2, key encrypt/decrypt, field coverage, rotation
│   ├── test_organization_lifecycle.py               # Unit: ALG-7, org creation, membership, dissolution
│   ├── test_l3_energy_and_crystallization.py        # Unit: ALG-3, ALG-6, propagation conservation, crystallization
│   ├── test_moment_perception_routing.py            # Unit: ALG-5, stimulus injection to accessing actors
│   ├── test_invariants_structural.py                # INV-1 through INV-12 verification
│   └── test_integration_universe_lifecycle.py       # Integration: full lifecycle from bootstrap to crystallization
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines Est. | Status |
|------|---------|----------------------|------------|--------|
| `runtime/universe/space_and_hierarchy_manager.py` | Space CRUD + containment hierarchy | `SpaceManager.create_space()`, `.get_sub_spaces()`, `.parent_space()` | ~250 | OK |
| `runtime/universe/access_resolution_and_link_manager.py` | HAS_ACCESS resolution (ALG-1) | `AccessResolver.has_access()`, `.grant_access()`, `.revoke_access()`, `.resolve_key_chain()` | ~300 | OK |
| `runtime/universe/organization_lifecycle_manager.py` | Org = Narrative + hall Space | `OrgManager.create_organization()`, `.join_organization()`, `.check_dissolution()` | ~200 | OK |
| `runtime/universe/moment_perception_router.py` | Route moments to accessing actors | `MomentPerceptionRouter.route()`, `.inject_stimulus()` | ~150 | OK |
| `runtime/universe/universe_bootstrap_and_metadata.py` | Init universe, migration | `UniverseBootstrap.initialize()`, `.migrate_flat_graph()`, `.validate_metadata()` | ~200 | OK |
| `runtime/universe/constants_l3_physics.py` | L3 physics parameters | Constants only: `L3_DECAY_RATE`, `L3_CRYSTALLIZATION_*`, `L3_PROPAGATION_*` | ~80 | OK |
| `runtime/crypto/aes256_content_encryptor.py` | AES-256-GCM encrypt/decrypt | `ContentEncryptor.encrypt()`, `.decrypt()`, `.encrypt_embedding()` | ~150 | OK |
| `runtime/crypto/rsa_key_manager.py` | RSA key lifecycle | `KeyManager.generate_keypair()`, `.load_private_key()`, `.get_public_key()`, `.rsa_encrypt()`, `.rsa_decrypt()` | ~200 | OK |
| `runtime/crypto/space_key_distribution_and_rotation.py` | Per-Space key ops | `SpaceKeyManager.create_space_key()`, `.grant_key()`, `.rotate_key()`, `.re_encrypt_content()` | ~250 | OK |
| `runtime/crypto/encrypted_field_codec.py` | Base64 + plaintext detection | `encode_b64()`, `decode_b64()`, `is_plaintext()`, `is_plaintext_vector()` | ~80 | OK |
| `runtime/physics/l3_energy_propagation_and_decay.py` | L3 energy model | `l3_inject_energy()`, `l3_propagate()`, `l3_decay()` | ~180 | OK |
| `runtime/physics/l3_weight_consolidation.py` | L3 Law 6 | `l3_consolidate()`, `compute_structural_utility()` | ~120 | OK |
| `runtime/physics/l3_macro_crystallization.py` | L3 Law 10 | `detect_crystallization_candidates()`, `crystallize()`, `L3CrystallizationParams` | ~300 | OK |
| `mcp/tools/space_management_handler.py` | MCP tool for Spaces | `handle_space_manage()`, `TOOL_SCHEMA` | ~250 | OK |
| `mcp/tools/universe_admin_handler.py` | MCP tool for universe ops | `handle_universe_admin()`, `TOOL_SCHEMA` | ~200 | OK |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Layered services with shared database adapter

**Why this pattern:** The existing codebase uses `runtime/infrastructure/database/` adapters (FalkorDB, Neo4j) accessed through a factory. Universe graph operations are a new service layer that composes the existing `DatabaseAdapter` interface. No new database abstractions -- all queries go through `adapter.query()` and `adapter.execute()`.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Adapter | `DatabaseAdapter` (existing) | Abstract FalkorDB/Neo4j behind uniform interface |
| Factory | `get_database_adapter()` (existing) | Resolve database backend from config |
| Service | `SpaceManager`, `AccessResolver`, `OrgManager` | Encapsulate domain logic, depend on adapter |
| Dataclass | `AccessResult`, `SpaceChild`, `L3CrystallizationParams` | Typed return values without Pydantic overhead |

### Anti-Patterns to Avoid

- **Property-based ACL**: Never store access lists on node properties. All access via HAS_ACCESS links (INV-2).
- **Type-branching**: Never branch on `space_type` in any physics/access/crystallization code (INV-11).
- **Node-level trust**: Never store trust/reputation on nodes (INV-7).
- **Encrypt-later**: Never commit plaintext content to an encrypted Space and "encrypt later" (INV-3 edge case).
- **Fallback decryption**: If decryption fails, raise. Do not return empty content as a fallback.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Universe service layer | Space/Access/Org logic | MCP tools, physics engine | `SpaceManager`, `AccessResolver`, `OrgManager` public methods |
| Crypto layer | Key management, AES/RSA ops | Universe service, MCP tools | `KeyManager`, `ContentEncryptor`, `SpaceKeyManager` |
| L3 physics | Energy/decay/crystallization at L3 | L1 cognitive engine (Force 5) | `l3_propagate()`, `l3_decay()`, `l3_consolidate()`, `crystallize()` |
| MCP tools | HTTP/JSON schema, arg parsing | Universe service layer | `handle_space_manage()`, `handle_universe_admin()` |

---

## PHASE BREAKDOWN

### Phase U1: Core Space/Moment Model (FalkorDB Schema, CRUD)

**Goal:** Spaces exist as nodes in the universe graph. Containment hierarchy works. Sub-Space traversal works.

**Files created:**
- `runtime/universe/__init__.py`
- `runtime/universe/space_and_hierarchy_manager.py`
- `runtime/universe/universe_bootstrap_and_metadata.py`
- `runtime/universe/constants_l3_physics.py`
- `tests/universe/__init__.py`
- `tests/universe/test_space_crud_and_hierarchy.py`

**Key interfaces:**

```python
# runtime/universe/space_and_hierarchy_manager.py

from dataclasses import dataclass
from typing import List, Optional
from runtime.infrastructure.database.adapter import DatabaseAdapter

@dataclass
class SpaceChild:
    space_id: str
    name: str
    depth: int
    containment_weight: float

class SpaceManager:
    def __init__(self, adapter: DatabaseAdapter):
        self._adapter = adapter

    def create_space(
        self,
        creator_actor_id: str,
        name: str,
        parent_space_id: Optional[str] = None,
        space_type: Optional[str] = None,
    ) -> str:
        """Create a Space node + owner HAS_ACCESS link.
        Returns the new Space node ID.
        Implements: B1 (Space Creation).
        Validates: INV-1 (no orphan Spaces -- owner link always created).
        """
        ...

    def get_sub_spaces(self, space_id: str, max_depth: int = 10) -> List[SpaceChild]:
        """ALG-4 downward traversal. Returns all descendant Spaces."""
        ...

    def parent_space(self, space_id: str) -> Optional[str]:
        """ALG-4 upward traversal. Returns parent Space ID or None."""
        ...

    def delete_space(self, admin_actor_id: str, space_id: str) -> None:
        """Delete Space and all containment links. Requires owner role.
        Validates: caller has owner role via AccessResolver.
        """
        ...
```

```python
# runtime/universe/universe_bootstrap_and_metadata.py

class UniverseBootstrap:
    def __init__(self, adapter: DatabaseAdapter):
        self._adapter = adapter

    def initialize(self, universe_name: str) -> str:
        """Create universe metadata node (Thing, type='universe_metadata').
        Validates: INV-4 (single universe per graph).
        Returns universe metadata node ID.
        """
        ...

    def migrate_flat_graph(self, root_space_name: str, owner_actor_id: str) -> str:
        """Migration from flat mind_mcp graph:
        1. Create root Space.
        2. Link all existing nodes to root Space.
        3. Create HAS_ACCESS (owner) from primary actor.
        Returns root Space ID.
        """
        ...

    def validate_metadata(self) -> bool:
        """Check INV-4: exactly one universe_metadata node exists."""
        ...
```

**Dependencies:** `runtime/infrastructure/database/` (existing adapter), `runtime/schema/` (existing node/link models).

**Independently testable:** Yes. Tests create Spaces, verify hierarchy traversal, verify metadata invariant. No encryption or access logic needed.

---

### Phase U2: HAS_ACCESS Link-Based Access Control

**Goal:** Access resolution works. Granting and revoking access works. Hierarchical access inheritance works.

**Files created:**
- `runtime/universe/access_resolution_and_link_manager.py`
- `tests/universe/test_access_resolution_and_inheritance.py`

**Key interfaces:**

```python
# runtime/universe/access_resolution_and_link_manager.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class AccessResult:
    granted: bool
    role: Optional[str] = None        # "owner", "admin", "member"
    encrypted_key: Optional[bytes] = None  # decrypted Space symmetric key (if available)
    inherited_from: Optional[str] = None   # ancestor Space ID if inherited

class AccessResolver:
    def __init__(self, adapter: DatabaseAdapter):
        self._adapter = adapter

    def has_access(self, actor_id: str, space_id: str) -> AccessResult:
        """ALG-1: Check if actor can access space.
        Step 1: Direct HAS_ACCESS link check.
        Step 2: Hierarchical traversal up containment chain.
        Step 3: Return AccessResult(granted=False) if no path found.
        Validates: INV-2 (all access via links), INV-8 (link structure).
        """
        ...

    def grant_access(
        self,
        grantor_id: str,
        target_actor_id: str,
        space_id: str,
        role: str = "member",
    ) -> None:
        """ALG-2: Grant access.
        Requires grantor has owner/admin role.
        Creates HAS_ACCESS link with role and encrypted_key.
        Implements: B2 (Access Granting).
        Validates: INV-8 (link structure: actor -> space, role in content).
        """
        ...

    def revoke_access(
        self,
        revoker_id: str,
        target_actor_id: str,
        space_id: str,
        adversarial: bool = False,
    ) -> None:
        """Remove HAS_ACCESS link.
        If adversarial=True, triggers key rotation via SpaceKeyManager.
        Implements: B3 (Access Revocation).
        """
        ...

    def list_space_members(self, space_id: str) -> list:
        """Return all actors with direct HAS_ACCESS to this Space, with roles."""
        ...

    def list_actor_spaces(self, actor_id: str) -> list:
        """Return all Spaces this actor has direct HAS_ACCESS to."""
        ...
```

**Dependencies:** Phase U1 (`SpaceManager` for hierarchy traversal). Phase U3 (encryption) is optional at this stage -- access resolution works without encryption (encrypted_key field is None for unencrypted Spaces).

**Independently testable:** Yes. Tests create Spaces, grant access, verify resolution, verify revocation, test hierarchical inheritance.

**Validation coverage:**
- INV-1: Verified via `create_space` always creating owner link
- INV-2: Static analysis test -- grep for property-based access patterns
- INV-8: Every HAS_ACCESS link validated at creation
- INV-9: Cycle detection in containment hierarchy

---

### Phase U3: Encrypted Brains (AES-256 Content Encryption)

**Goal:** Content in encrypted Spaces is AES-256-GCM encrypted. Keys are RSA-wrapped per actor. Key rotation works.

**Files created:**
- `runtime/crypto/__init__.py`
- `runtime/crypto/aes256_content_encryptor.py`
- `runtime/crypto/rsa_key_manager.py`
- `runtime/crypto/space_key_distribution_and_rotation.py`
- `runtime/crypto/encrypted_field_codec.py`
- `tests/universe/test_encryption_roundtrip_and_coverage.py`

**Key interfaces:**

```python
# runtime/crypto/aes256_content_encryptor.py

class ContentEncryptor:
    """AES-256-GCM encryption for node content, synthesis, and embedding fields."""

    @staticmethod
    def encrypt(plaintext: str, key: bytes) -> bytes:
        """Encrypt a string field. Returns IV + ciphertext + tag."""
        ...

    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes) -> str:
        """Decrypt a string field. Raises CryptoError on failure (no fallback)."""
        ...

    @staticmethod
    def encrypt_embedding(embedding: list[float], key: bytes) -> bytes:
        """Encrypt a float vector. Serializes to bytes, then AES-256-GCM."""
        ...

    @staticmethod
    def decrypt_embedding(ciphertext: bytes, key: bytes) -> list[float]:
        """Decrypt a float vector. Raises CryptoError on failure."""
        ...
```

```python
# runtime/crypto/rsa_key_manager.py

class KeyManager:
    """RSA-2048 key pair management for actors."""

    @staticmethod
    def generate_keypair() -> tuple[bytes, bytes]:
        """Generate (private_key_pem, public_key_pem)."""
        ...

    @staticmethod
    def load_private_key(path: str) -> 'RSAPrivateKey':
        """Load private key from .keys/ directory."""
        ...

    @staticmethod
    def get_public_key(actor_id: str, adapter: DatabaseAdapter) -> bytes:
        """Retrieve actor's public key from graph (stored on actor node or metadata)."""
        ...

    @staticmethod
    def rsa_encrypt(data: bytes, public_key_pem: bytes) -> bytes:
        """Encrypt data (typically an AES key) with RSA-OAEP."""
        ...

    @staticmethod
    def rsa_decrypt(ciphertext: bytes, private_key: 'RSAPrivateKey') -> bytes:
        """Decrypt RSA-OAEP ciphertext. Raises CryptoError on failure."""
        ...
```

```python
# runtime/crypto/space_key_distribution_and_rotation.py

class SpaceKeyManager:
    """Per-Space AES-256 symmetric key lifecycle."""

    def __init__(self, adapter: DatabaseAdapter, key_manager: KeyManager):
        self._adapter = adapter
        self._km = key_manager

    def create_space_key(self) -> bytes:
        """Generate a new AES-256 key (32 bytes)."""
        ...

    def grant_key(
        self,
        space_key: bytes,
        target_actor_id: str,
    ) -> str:
        """RSA-encrypt space_key with target actor's public key.
        Returns base64-encoded encrypted key for storage on HAS_ACCESS link content.
        """
        ...

    def rotate_key(
        self,
        admin_id: str,
        space_id: str,
    ) -> None:
        """ALG-2 key rotation:
        1. Generate new AES-256 key.
        2. Re-encrypt all content in Space with new key.
        3. Re-encrypt new key for all remaining HAS_ACCESS links.
        4. Update parent containment link if sub-Space.
        """
        ...

    def resolve_key_chain(
        self,
        actor_id: str,
        target_space_id: str,
        ancestor_space_id: str,
        actor_private_key: 'RSAPrivateKey',
    ) -> bytes:
        """ALG-1 key chain resolution:
        Walk DOWN from ancestor to target, decrypting child key at each level.
        """
        ...
```

```python
# runtime/crypto/encrypted_field_codec.py

import base64

def encode_b64(data: bytes) -> str:
    """Encode bytes to base64 string for graph storage."""
    ...

def decode_b64(s: str) -> bytes:
    """Decode base64 string back to bytes."""
    ...

def is_plaintext(value: str) -> bool:
    """Heuristic: check if a string looks like plaintext (not base64-encoded ciphertext).
    Used by INV-3 validation.
    """
    ...

def is_plaintext_vector(value) -> bool:
    """Check if an embedding value is an unencrypted float list.
    Used by INV-3 validation.
    """
    ...
```

**External dependency:** `cryptography` (Python package, already in requirements -- used for `Fernet` elsewhere; we use `cryptography.hazmat` for AES-GCM and RSA-OAEP).

**Independently testable:** Yes. Tests generate key pairs, encrypt/decrypt content, verify roundtrip, test key rotation, verify INV-3 (no plaintext in encrypted Space).

---

### Phase U4: Organizations as Narratives

**Goal:** Organizations are Narrative nodes with hall Spaces. Membership via HAS_ACCESS + BELIEVES link.

**Files created:**
- `runtime/universe/organization_lifecycle_manager.py`
- `tests/universe/test_organization_lifecycle.py`

**Key interfaces:**

```python
# runtime/universe/organization_lifecycle_manager.py

from dataclasses import dataclass

@dataclass
class OrganizationInfo:
    narrative_id: str
    hall_space_id: str
    founder_id: str
    name: str
    mission: str

class OrgManager:
    def __init__(
        self,
        adapter: DatabaseAdapter,
        space_manager: 'SpaceManager',
        access_resolver: 'AccessResolver',
    ):
        self._adapter = adapter
        self._space_mgr = space_manager
        self._access = access_resolver

    def create_organization(
        self,
        founder_id: str,
        name: str,
        mission_statement: str,
    ) -> OrganizationInfo:
        """ALG-7: Create org.
        1. Create hall Space via SpaceManager (founder = owner).
        2. Create Narrative node (type='organization').
        3. Link Narrative to hall Space (hierarchy=-1, permanence=0.9).
        4. Link founder to Narrative (BELIEVES: trust=0.8, affinity=0.7).
        Implements: B5 (Organization Creation).
        """
        ...

    def join_organization(
        self,
        actor_id: str,
        org_narrative_id: str,
    ) -> None:
        """Grant HAS_ACCESS (member) to hall Space + create BELIEVES link.
        Implements: B6 (Organization Membership).
        Requires: an existing member with admin/owner role grants access.
        """
        ...

    def compute_org_reputation(self, org_narrative_id: str) -> float:
        """ALG-8 applied to the org Narrative node.
        reputation = sum(link.trust * link.weight) / sum(link.weight)
        for all inbound links with trust > 0.
        """
        ...

    def check_dissolution(self, org_narrative_id: str) -> bool:
        """Check if org should dissolve:
        All HAS_ACCESS links to hall below threshold AND
        all BELIEVES links below threshold.
        Returns True if dissolution conditions met.
        """
        ...
```

**Dependencies:** Phase U1 (SpaceManager), Phase U2 (AccessResolver).

**Independently testable:** Yes. Tests create org, join, compute reputation, verify dissolution detection.

---

### Phase U5: L3 Physics -- Energy, Consolidation, Macro-Crystallization

**Goal:** L3 energy model works. Macro-crystallization detects dense clusters and creates hub Narratives. Weight consolidation uses structural utility.

**Files created:**
- `runtime/physics/l3_energy_propagation_and_decay.py`
- `runtime/physics/l3_weight_consolidation.py`
- `runtime/physics/l3_macro_crystallization.py`
- `tests/universe/test_l3_energy_and_crystallization.py`

**Key interfaces:**

```python
# runtime/universe/constants_l3_physics.py (created in U1, populated here)

# --- L3 Decay (Law 3) ---
L3_DECAY_RATE = 0.01           # Slower than L1's 0.02
L3_RECENCY_DECAY = 0.005

# --- L3 Propagation (Law 2) ---
L3_PROPAGATION_THRESHOLD = 1.0

# --- L3 Consolidation (Law 6) ---
L3_CONSOLIDATION_ALPHA = 0.1   # Learning rate for weight consolidation

# --- L3 Crystallization (Law 10) ---
L3_CRYSTALLIZATION_MIN_SIZE = 50
L3_CRYSTALLIZATION_DENSITY = 0.15
L3_CRYSTALLIZATION_WEIGHT = 3.0
L3_CRYSTALLIZATION_CHECK_INTERVAL = 500  # ticks
L3_CRYSTALLIZATION_DAMPING = 0.7
L3_CRYSTALLIZATION_HUB_HIERARCHY = True  # hubs can crystallize into meta-hubs

# --- L3 Energy Injection Split ---
L3_ENERGY_SPACE_SHARE = 0.6
L3_ENERGY_ACTOR_SHARE = 0.3
L3_ENERGY_CONTEXT_SHARE = 0.1

# --- L3 Forgetting (Law 7) ---
L3_DISSOLUTION_WEIGHT_THRESHOLD = 0.01
L3_STRUCTURAL_DECAY_MULTIPLIER = 0.25  # 4x slower for containment/abstracts links
```

```python
# runtime/physics/l3_energy_propagation_and_decay.py

def l3_inject_energy(
    adapter: DatabaseAdapter,
    actor_id: str,
    action_type: str,
    space_id: str,
    energy_amount: float,
) -> str:
    """ALG-6: Inject energy from L1 action into L3.
    Creates or updates Moment node.
    Splits energy: 60% Space, 30% Actor, 10% context.
    Returns moment_id.
    """
    ...

def l3_propagate(adapter: DatabaseAdapter, node_id: str) -> None:
    """ALG-6 Law 2: Surplus spill-over.
    If node.energy > L3_PROPAGATION_THRESHOLD, distribute surplus
    proportional to outbound link weights.
    No compatibility filter (Law 8 off at L3).
    Validates: INV-10 (energy conservation within propagation step).
    """
    ...

def l3_decay(adapter: DatabaseAdapter, node_id: str) -> None:
    """ALG-6 Law 3: Energy and recency decay.
    node.energy *= (1 - L3_DECAY_RATE)
    node.recency *= (1 - L3_RECENCY_DECAY)
    """
    ...
```

```python
# runtime/physics/l3_weight_consolidation.py

def compute_structural_utility(adapter: DatabaseAdapter, link) -> float:
    """ALG-6 Law 6 utility gate (L3 analog of limbic significance).
    - Service/Thing nodes: normalized_usage_count
    - Actor-Actor links: co_activation_frequency
    - Space links: presence_intensity (aggregate actor hours)
    F2 dependency: Formula 1 (Progressive Pricing) uses U_S from this.
    F2 dependency: Formula 4 (Batch Settlement) uses weight(thing_used) from this.
    """
    ...

def l3_consolidate(adapter: DatabaseAdapter, link) -> None:
    """ALG-6 Law 6: Weight consolidation.
    dW = ALPHA * link.avg_energy * U * (1 - link.weight)
    link.weight += dW
    """
    ...
```

```python
# runtime/physics/l3_macro_crystallization.py

from dataclasses import dataclass

@dataclass
class CrystallizationCandidate:
    node_ids: list[str]
    density: float
    avg_co_activation: float
    internal_link_count: int
    external_links: list  # links crossing cluster boundary

def detect_crystallization_candidates(
    adapter: DatabaseAdapter,
) -> list[CrystallizationCandidate]:
    """ALG-3: Find dense clusters exceeding L3 thresholds.
    Runs every L3_CRYSTALLIZATION_CHECK_INTERVAL ticks.
    MIN_SIZE >= 50, DENSITY >= 0.15, AVG_WEIGHT >= 3.0.
    """
    ...

def crystallize(
    adapter: DatabaseAdapter,
    cluster: CrystallizationCandidate,
) -> str:
    """ALG-3: Create hub Narrative from dense cluster.
    1. Determine hub type (majority rule; moments -> narrative).
    2. Compute centroid embedding.
    3. Find medoid node.
    4. Create hub node.
    5. Create bidirectional links (contains + abstracts).
    6. Connect hub to external links.
    Returns hub node ID.
    Validates: INV-12 (hub integrity).
    """
    ...
```

**Dependencies:** Existing `runtime/physics/` infrastructure for embedding/cosine operations. Existing `runtime/graph/ops/` for node/link creation.

**Independently testable:** Yes. Tests create a graph with known density, trigger crystallization, verify hub properties, verify energy conservation.

---

### Phase U6: MCP Tool Integration + Moment Perception Routing

**Goal:** MCP tools `space_manage` and `universe_admin` expose Space operations to agents. Moment perception routing connects L3 events to L1 stimulus injection.

**Files created:**
- `mcp/tools/space_management_handler.py`
- `mcp/tools/universe_admin_handler.py`
- `runtime/universe/moment_perception_router.py`
- `tests/universe/test_moment_perception_routing.py`
- `tests/universe/test_integration_universe_lifecycle.py`

**Key interfaces:**

```python
# mcp/tools/space_management_handler.py

TOOL_SCHEMA = {
    "name": "space_manage",
    "description": (
        "[ACT] Manage Spaces in the universe graph. "
        "Create Spaces, grant/revoke access, list members, list sub-Spaces."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "list", "grant_access", "revoke_access", "members", "sub_spaces"],
            },
            "space_name": {"type": "string"},
            "space_id": {"type": "string"},
            "parent_space_id": {"type": "string"},
            "target_actor_id": {"type": "string"},
            "role": {"type": "string", "enum": ["owner", "admin", "member"]},
            "space_type": {"type": "string"},
        },
        "required": ["action"],
    },
}

def handle_space_manage(args: dict, ctx: 'ServerContext') -> dict:
    """Route to SpaceManager/AccessResolver based on action."""
    ...
```

```python
# mcp/tools/universe_admin_handler.py

TOOL_SCHEMA = {
    "name": "universe_admin",
    "description": (
        "[ACT] Universe graph administration. "
        "Bootstrap a new universe, migrate from flat graph, run validation, check status."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["bootstrap", "migrate", "validate", "status"],
            },
            "universe_name": {"type": "string"},
            "owner_actor_id": {"type": "string"},
        },
        "required": ["action"],
    },
}

def handle_universe_admin(args: dict, ctx: 'ServerContext') -> dict:
    """Route to UniverseBootstrap based on action."""
    ...
```

```python
# runtime/universe/moment_perception_router.py

class MomentPerceptionRouter:
    def __init__(self, adapter: DatabaseAdapter, access_resolver: AccessResolver):
        self._adapter = adapter
        self._access = access_resolver

    def route(self, moment_id: str, space_id: str) -> list[str]:
        """ALG-5: Determine which actors should perceive this moment.
        1. Find all actors with direct HAS_ACCESS to this Space.
        2. Find all actors with HAS_ACCESS to ancestor Spaces.
        3. Return list of actor_ids.
        Implements: B4 (Moment Recording -- perception routing part).
        """
        ...

    def inject_stimulus(
        self,
        actor_id: str,
        moment_id: str,
        space_id: str,
        encrypted: bool,
    ) -> None:
        """Inject moment as L1 stimulus via membrane.
        Uses existing runtime/membrane/stimulus.py infrastructure.
        If encrypted, the actor's MCP server decrypts using its key.
        """
        ...
```

**Modifications to existing files:**
- `home_server.py`: Register `space_manage` and `universe_admin` tools in the MCP tool registry.
- `mcp/__init__.py` or tool registry: Add imports for new handlers.

**Dependencies:** All previous phases. Existing `runtime/membrane/stimulus.py` for L1 injection.

**Independently testable:** Yes. Integration tests create universe, create Spaces, record Moments, verify perception routing.

---

## SHARED INTERFACES

### What Other Forces Need From F1

| Consumer | What They Need | Provided By | Phase |
|----------|---------------|-------------|-------|
| **F2 (Metabolic Economy)** | Hook on Space creation for economic cost validation | `SpaceManager.create_space()` emits event via `graph_ops_events.emit_event("space_created", ...)` | U1 |
| **F2 (Metabolic Economy)** | `compute_structural_utility()` for Formula 1 (U_S) and Formula 4 (weight) | `runtime/physics/l3_weight_consolidation.py` | U5 |
| **F2 (Metabolic Economy)** | List of actors with HAS_ACCESS to a Space (for UBC redistribution proximity) | `AccessResolver.list_space_members()` | U2 |
| **F4 (Trust/Value)** | Link dimensions (trust, affinity, aversion, friction) available on L3 links | Standard `LinkBase` fields -- already in schema. No F1 code needed. | -- |
| **F4 (Trust/Value)** | `compute_reputation()` for on-demand Actor reputation | `OrgManager.compute_org_reputation()` or standalone function | U4 |
| **F5 (Cognitive Engine)** | Per-citizen brain Space management | `SpaceManager.create_space()` with encrypted=True + `ContentEncryptor` + `SpaceKeyManager` | U1+U3 |
| **F5 (Cognitive Engine)** | Read/decrypt/process/encrypt cycle for brain tick | `ContentEncryptor.encrypt/decrypt` + `SpaceKeyManager.resolve_key_chain()` | U3 |
| **F5 (Cognitive Engine)** | Moment perception routing (L3 -> L1 membrane) | `MomentPerceptionRouter.route()` + `.inject_stimulus()` | U6 |

### What F1 Needs From Other Forces

| Provider | What F1 Needs | Status | Impact |
|----------|--------------|--------|--------|
| **F2 (Metabolic Economy)** | Economic cost callback for Space creation | Not yet implemented | F1 emits event; F2 registers listener. F1 does not block on F2 absence. |
| **F5 (Cognitive Engine)** | L1 tick engine to consume `inject_stimulus()` | Not yet implemented | Routing works independently; actual L1 processing depends on F5. |
| **Existing infra** | `DatabaseAdapter` (FalkorDB/Neo4j) | Available | Core dependency. |
| **Existing infra** | `EmbeddingService` | Available | Needed for crystallization centroid computation. |
| **Existing infra** | `runtime/membrane/stimulus.py` | Available | Needed for moment perception injection. |

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| Universe bootstrap | `runtime/universe/universe_bootstrap_and_metadata.py:UniverseBootstrap.initialize()` | `home_server.py` startup or `universe_admin` MCP tool |
| Space creation | `runtime/universe/space_and_hierarchy_manager.py:SpaceManager.create_space()` | `space_manage` MCP tool (action: create) |
| Access check | `runtime/universe/access_resolution_and_link_manager.py:AccessResolver.has_access()` | Every graph_query and graph_write that touches a Space |
| Access grant | `runtime/universe/access_resolution_and_link_manager.py:AccessResolver.grant_access()` | `space_manage` MCP tool (action: grant_access) |
| Org creation | `runtime/universe/organization_lifecycle_manager.py:OrgManager.create_organization()` | Agent/user action via MCP |
| Moment routing | `runtime/universe/moment_perception_router.py:MomentPerceptionRouter.route()` | After any Moment creation in a Space |
| L3 tick | `runtime/physics/l3_energy_propagation_and_decay.py:l3_propagate()` | L3 tick runner (new, or integrated into existing tick_runner.py) |
| Crystallization | `runtime/physics/l3_macro_crystallization.py:detect_crystallization_candidates()` | Every L3_CRYSTALLIZATION_CHECK_INTERVAL ticks |

---

## DATA FLOW: Space Creation to Moment Perception

```
Agent calls space_manage(action="create", space_name="dev-chat")
  --> handle_space_manage()
    --> SpaceManager.create_space("actor_claude", "dev-chat")
      --> adapter.execute(CREATE Space node)
      --> adapter.execute(CREATE HAS_ACCESS link, role=owner)
      --> emit_event("space_created", {space_id, actor_id})
      --> [F2 listener: validate economic cost] (async, non-blocking if absent)
      --> return space_id

Agent sends message in dev-chat
  --> graph_write(node_type="moment", content="...", space_id=space_id)
    --> MomentPerceptionRouter.route(moment_id, space_id)
      --> find HAS_ACCESS links to space_id (direct)
      --> walk up containment to find inherited access
      --> for each accessing actor:
          --> inject_stimulus(actor_id, moment_id, space_id, encrypted=False)
            --> membrane.stimulus.inject(actor_id, "moment_perception", moment_id)
```

---

## LOGIC CHAINS

### LC1: Access Resolution (ALG-1)

```
has_access(actor_id, space_id)
  --> find_link(actor_id -> space_id, type="has_access")      # O(1) lookup
    --> if found: return AccessResult(granted=True, role, key)
    --> if not found:
      --> parent = parent_space(space_id)                      # O(1) per level
        --> while parent is not null:
          --> find_link(actor_id -> parent, type="has_access")
            --> if found: return AccessResult(granted=True, inherited_role, resolved_key)
          --> parent = parent_space(parent)
        --> return AccessResult(granted=False)
```

### LC2: Key Rotation (ALG-2)

```
rotate_key(admin_id, space_id)
  --> new_key = generate_aes256_key()
  --> for node in nodes_in_space(space_id):
    --> old_content = decrypt(node.content, old_key)
    --> node.content = encrypt(old_content, new_key)
  --> for link in find_links(to=space_id, type="has_access"):
    --> actor_pub = get_public_key(link.node_a)
    --> link.content.encrypted_key = rsa_encrypt(new_key, actor_pub)
  --> update parent containment link if sub-Space
```

### LC3: Macro-Crystallization (ALG-3)

```
detect_crystallization_candidates(universe_graph)
  --> find_dense_clusters()                                    # community detection
    --> for each cluster:
      --> check size >= 50, density >= 0.15, avg_weight >= 3.0
      --> if passes: add to candidates
  --> for each candidate:
    --> crystallize(cluster)
      --> hub_type = majority_rule(cluster.nodes)
      --> centroid = mean(embeddings)
      --> medoid = argmin(cosine_distance to centroid)
      --> hub = create_node(hub_type, medoid.name, centroid)
      --> create contains links (hub -> constituents)
      --> create abstracts links (constituents -> hub)
      --> connect hub to external links
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
mcp/tools/space_management_handler.py
    └── imports --> runtime/universe/space_and_hierarchy_manager.py
    └── imports --> runtime/universe/access_resolution_and_link_manager.py

mcp/tools/universe_admin_handler.py
    └── imports --> runtime/universe/universe_bootstrap_and_metadata.py

runtime/universe/space_and_hierarchy_manager.py
    └── imports --> runtime/infrastructure/database/adapter.py (DatabaseAdapter)

runtime/universe/access_resolution_and_link_manager.py
    └── imports --> runtime/universe/space_and_hierarchy_manager.py (parent_space)
    └── imports --> runtime/crypto/space_key_distribution_and_rotation.py (key ops)
    └── imports --> runtime/infrastructure/database/adapter.py

runtime/universe/organization_lifecycle_manager.py
    └── imports --> runtime/universe/space_and_hierarchy_manager.py
    └── imports --> runtime/universe/access_resolution_and_link_manager.py

runtime/universe/moment_perception_router.py
    └── imports --> runtime/universe/access_resolution_and_link_manager.py
    └── imports --> runtime/membrane/stimulus.py

runtime/crypto/space_key_distribution_and_rotation.py
    └── imports --> runtime/crypto/aes256_content_encryptor.py
    └── imports --> runtime/crypto/rsa_key_manager.py
    └── imports --> runtime/crypto/encrypted_field_codec.py

runtime/physics/l3_macro_crystallization.py
    └── imports --> runtime/physics/link_scoring.py (cosine_similarity)
    └── imports --> runtime/infrastructure/embeddings/ (embedding service)
    └── imports --> runtime/universe/constants_l3_physics.py
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `cryptography` | AES-256-GCM, RSA-OAEP, key serialization | `runtime/crypto/*.py` |
| `numpy` | Centroid/medoid embedding computation | `runtime/physics/l3_macro_crystallization.py` |
| `falkordb` | Graph database operations | `runtime/infrastructure/database/falkordb_adapter.py` (existing) |

---

## TEST PLAN

### Phase U1 Tests

| Test | File | Validates |
|------|------|-----------|
| `test_create_space_returns_id` | `test_space_crud_and_hierarchy.py` | B1: Space creation produces node |
| `test_create_space_creates_owner_link` | `test_space_crud_and_hierarchy.py` | INV-1: No orphan Spaces |
| `test_create_sub_space_containment_link` | `test_space_crud_and_hierarchy.py` | B1: Sub-Space containment |
| `test_get_sub_spaces_depth` | `test_space_crud_and_hierarchy.py` | ALG-4: Downward traversal |
| `test_parent_space_returns_parent` | `test_space_crud_and_hierarchy.py` | ALG-4: Upward traversal |
| `test_parent_space_root_returns_none` | `test_space_crud_and_hierarchy.py` | ALG-4: Root termination |
| `test_universe_bootstrap_creates_metadata` | `test_space_crud_and_hierarchy.py` | INV-4: Single universe |
| `test_universe_bootstrap_rejects_duplicate` | `test_space_crud_and_hierarchy.py` | INV-4: Duplicate rejection |

### Phase U2 Tests

| Test | File | Validates |
|------|------|-----------|
| `test_has_access_direct` | `test_access_resolution_and_inheritance.py` | ALG-1 step 1 |
| `test_has_access_inherited` | `test_access_resolution_and_inheritance.py` | ALG-1 step 2 |
| `test_has_access_denied` | `test_access_resolution_and_inheritance.py` | ALG-1 step 3 |
| `test_grant_access_creates_link` | `test_access_resolution_and_inheritance.py` | B2, INV-8 |
| `test_grant_access_requires_admin` | `test_access_resolution_and_inheritance.py` | ALG-2: role check |
| `test_revoke_access_removes_link` | `test_access_resolution_and_inheritance.py` | B3 |
| `test_revoke_access_adversarial_rotates_key` | `test_access_resolution_and_inheritance.py` | B3 + ALG-2 rotation |
| `test_hierarchy_acyclicity_rejects_cycle` | `test_access_resolution_and_inheritance.py` | INV-9 |
| `test_has_access_link_structure` | `test_access_resolution_and_inheritance.py` | INV-8: actor->space, valid role |
| `test_no_property_based_access` | `test_invariants_structural.py` | INV-2: static analysis |

### Phase U3 Tests

| Test | File | Validates |
|------|------|-----------|
| `test_aes_encrypt_decrypt_roundtrip` | `test_encryption_roundtrip_and_coverage.py` | ALG-2: content encryption |
| `test_aes_encrypt_embedding_roundtrip` | `test_encryption_roundtrip_and_coverage.py` | Embedding encryption |
| `test_rsa_encrypt_decrypt_roundtrip` | `test_encryption_roundtrip_and_coverage.py` | ALG-2: key wrapping |
| `test_encrypted_space_content_unreadable` | `test_encryption_roundtrip_and_coverage.py` | INV-3 |
| `test_encrypted_space_synthesis_unreadable` | `test_encryption_roundtrip_and_coverage.py` | INV-3 |
| `test_encrypted_space_embedding_unreadable` | `test_encryption_roundtrip_and_coverage.py` | INV-3 |
| `test_key_rotation_old_key_fails` | `test_encryption_roundtrip_and_coverage.py` | ALG-2: post-rotation |
| `test_key_rotation_new_key_works` | `test_encryption_roundtrip_and_coverage.py` | ALG-2: post-rotation |
| `test_key_chain_resolution` | `test_encryption_roundtrip_and_coverage.py` | ALG-1: inherited key chain |
| `test_no_encrypt_later` | `test_encryption_roundtrip_and_coverage.py` | INV-3 edge case |

### Phase U4 Tests

| Test | File | Validates |
|------|------|-----------|
| `test_create_org_creates_narrative_and_hall` | `test_organization_lifecycle.py` | ALG-7, B5 |
| `test_create_org_narrative_type_organization` | `test_organization_lifecycle.py` | B5: correct type |
| `test_create_org_founder_has_access` | `test_organization_lifecycle.py` | B5: owner link |
| `test_create_org_founder_believes` | `test_organization_lifecycle.py` | B5: BELIEVES link |
| `test_join_org_creates_member_access` | `test_organization_lifecycle.py` | B6 |
| `test_join_org_creates_believes_link` | `test_organization_lifecycle.py` | B6 |
| `test_org_reputation_computation` | `test_organization_lifecycle.py` | ALG-8 |
| `test_org_dissolution_detection` | `test_organization_lifecycle.py` | ALG-7 dissolution |

### Phase U5 Tests

| Test | File | Validates |
|------|------|-----------|
| `test_l3_energy_injection_splits` | `test_l3_energy_and_crystallization.py` | ALG-6: 60/30/10 split |
| `test_l3_propagation_conservation` | `test_l3_energy_and_crystallization.py` | INV-10 |
| `test_l3_propagation_no_compatibility_filter` | `test_l3_energy_and_crystallization.py` | ALG-6: Law 8 off |
| `test_l3_decay` | `test_l3_energy_and_crystallization.py` | ALG-6: Law 3 |
| `test_structural_utility_service_usage` | `test_l3_energy_and_crystallization.py` | ALG-6: L6 gate |
| `test_structural_utility_co_activation` | `test_l3_energy_and_crystallization.py` | ALG-6: L6 gate |
| `test_crystallization_trigger` | `test_l3_energy_and_crystallization.py` | ALG-3: threshold check |
| `test_crystallization_below_threshold` | `test_l3_energy_and_crystallization.py` | ALG-3: no false trigger |
| `test_crystallization_hub_integrity` | `test_l3_energy_and_crystallization.py` | INV-12 |
| `test_crystallization_hub_type_majority` | `test_l3_energy_and_crystallization.py` | ALG-3: type derivation |
| `test_plutchik_frozen_at_l3` | `test_invariants_structural.py` | INV-6 |
| `test_relation_kind_null_at_l3` | `test_invariants_structural.py` | INV-5 |
| `test_no_space_type_branching` | `test_invariants_structural.py` | INV-11: static analysis |
| `test_no_node_level_trust` | `test_invariants_structural.py` | INV-7: static analysis |

### Phase U6 Tests

| Test | File | Validates |
|------|------|-----------|
| `test_moment_perception_direct_access` | `test_moment_perception_routing.py` | ALG-5: direct members perceive |
| `test_moment_perception_inherited_access` | `test_moment_perception_routing.py` | ALG-5: ancestor members perceive |
| `test_moment_perception_no_access` | `test_moment_perception_routing.py` | ALG-5: excluded actors |
| `test_moment_perception_encrypted_space` | `test_moment_perception_routing.py` | ALG-5: encrypted flag set |
| `test_integration_bootstrap_to_moment` | `test_integration_universe_lifecycle.py` | B1+B4: create universe, Space, record Moment |
| `test_integration_org_membership_access` | `test_integration_universe_lifecycle.py` | B5+B6: create org, join, verify access |
| `test_integration_crystallization_lifecycle` | `test_integration_universe_lifecycle.py` | B7+B8: moments -> crystallization -> hub |
| `test_integration_brain_encryption_isolation` | `test_integration_universe_lifecycle.py` | B9: brain content encrypted, others cannot read |
| `test_integration_access_decay_via_law7` | `test_integration_universe_lifecycle.py` | B8: unused HAS_ACCESS decays |

---

## RISK ASSESSMENT

### R1: FalkorDB Community Detection Performance

**Risk:** ALG-3 (macro-crystallization) requires finding dense clusters in a graph with potentially millions of nodes. FalkorDB does not have built-in community detection algorithms (unlike Neo4j GDS).

**Impact:** Crystallization may be too slow or require external computation.

**Mitigation:** Implement a simple bounded-region density scan rather than global community detection. Start from high-energy nodes and expand outward. Limit scan radius. If insufficient, consider periodic export to NetworkX for community detection, then import results.

**Phase:** U5.

### R2: Encryption Performance at Scale

**Risk:** Key rotation (ALG-2) requires re-encrypting all content in a Space. For large Spaces with thousands of nodes, this is a bulk operation.

**Impact:** Key rotation could block the graph for seconds to minutes.

**Mitigation:** Batch re-encryption with progress tracking. Allow async rotation. Mark Space as "rotating" during the process (prevent writes until complete).

**Phase:** U3.

### R3: Cross-Force Integration Timing

**Risk:** F2 needs `compute_structural_utility()` for pricing formulas. F5 needs `ContentEncryptor` for brain ticks. These forces may not be implemented in parallel.

**Impact:** Interfaces must be stable before consumers arrive.

**Mitigation:** Define interfaces (function signatures, return types) in U1/U2/U3. Implement with real logic. Other forces code against the interface, not the implementation. Event-based hooks (`emit_event`) for F2 Space creation cost -- F2 registers a listener when ready; F1 does not block.

**Phase:** All.

### R4: Migration from Flat Graph

**Risk:** Existing `mind_mcp` graphs have no Spaces, no HAS_ACCESS links. Migration must be non-destructive.

**Impact:** Incorrect migration could orphan existing nodes or break existing queries.

**Mitigation:** Migration creates a root Space and links all existing nodes to it. Existing queries (graph_query, graph_write) continue to work because they operate on nodes regardless of Space membership. Access checks are additive -- they gate new operations, not existing ones. Provide a `validate` action in universe_admin to verify post-migration integrity.

**Phase:** U1.

### R5: L3 Tick Timing vs F2 Daily Epoch

**Risk:** L3 tick interval is undefined. F2 operates on daily epochs (00:00 UTC) and 6-hour settlement epochs. If L3 ticks are too fast, crystallization checks are too frequent. If too slow, energy stagnates.

**Impact:** Physics behavior may not align with economic cycle.

**Mitigation:** Start with L3 tick = 1 minute (1440 ticks/day). Crystallization check every 500 ticks = ~8.3 hours, which is slightly longer than the F2 6-hour settlement epoch. This gives a natural rhythm: settlement -> crystallization check -> settlement -> crystallization check. Tune after observation.

**Phase:** U5.

### R6: Hierarchy Depth and Access Resolution Latency

**Risk:** ALG-1 traverses up the containment hierarchy. Deep hierarchies (10+ levels) could slow access checks.

**Impact:** Every graph_query and graph_write touches access resolution.

**Mitigation:** Max depth = 10 (already in ALG-4). Cache access results per actor per session (TTL = 60 seconds). The hierarchy is a DAG (INV-9 enforced), so traversal always terminates.

**Phase:** U2.

---

## MODIFICATIONS TO EXISTING FILES

| File | Change | Phase |
|------|--------|-------|
| `home_server.py` | Register `space_manage` and `universe_admin` tools; call `UniverseBootstrap.initialize()` on startup | U6 |
| `mcp/tools/graph_write_handler.py` | Add optional `space_id` parameter; call `AccessResolver.has_access()` before write; call `MomentPerceptionRouter.route()` after Moment creation | U6 |
| `mcp/tools/graph_query_handler.py` | Add optional `space_id` filter; call `AccessResolver.has_access()` to filter results by accessible Spaces | U6 |
| `runtime/physics/constants.py` | Import L3 constants from `runtime/universe/constants_l3_physics.py` (or keep separate -- prefer separate to avoid coupling) | U5 |
| `runtime/schema/nodes.py` | No changes needed -- `Space` model already exists with correct fields. The `SpaceType` enum becomes advisory only (no algorithm reads it). | -- |
| `runtime/schema/links.py` | No changes needed -- `LinkBase` already has all required dimensions (trust, hierarchy, permanence, polarity). | -- |

---

## MARKERS

<!-- @mind:todo U1: Implement SpaceManager and UniverseBootstrap -->
<!-- @mind:todo U2: Implement AccessResolver with ALG-1 hierarchy traversal -->
<!-- @mind:todo U3: Implement crypto layer (AES-256-GCM, RSA-OAEP, key rotation) -->
<!-- @mind:todo U4: Implement OrgManager (Narrative + hall Space) -->
<!-- @mind:todo U5: Implement L3 physics (energy, consolidation, crystallization) -->
<!-- @mind:todo U6: Wire MCP tools and moment perception routing -->
<!-- @mind:escalation R5: L3 tick timing must be reconciled with F2 daily epoch before U5 implementation -->
<!-- @mind:proposition Consider caching AccessResolver results with TTL to reduce hierarchy traversal cost (R6) -->
