# Mind Protocol — Architecture Specification v1

**Date:** 27 Décembre 2025
**Authors:** Nicolas + Marco
**Status:** Working Draft

---

# PART 1: BRANDING & REPOS

## Unified Branding

| Brand | Description | Package/Repo |
|-------|-------------|--------------|
| **MIND** | L'engine (graph physics, traversal, methodology) | `mind-mcp` |
| **Mind Protocol** | Le network 4-layers (L1-L4) | `mind-protocol` |
| **Mind Platform** | Frontend tout-en-un | `mind-platform` (platform.mindprotocol.ai) |

```bash
pip install mind-mcp
```

## Repository Structure

### Open Source vs Private

```
┌─────────────────────────────────────────────────────────────────────┐
│  REPO             │  LICENSE        │  CONTENU                      │
├─────────────────────────────────────────────────────────────────────┤
│  mind-mcp         │  Open source    │  Client/engine                │
├─────────────────────────────────────────────────────────────────────┤
│  mind-protocol    │  Open source    │  L4 law + L3 ecosystem        │
├─────────────────────────────────────────────────────────────────────┤
│  mind-platform    │  Open source    │  Frontend (platform.mindprotocol.ai) │
├─────────────────────────────────────────────────────────────────────┤
│  mind-ops         │  PRIVATE        │  Membrane + infra + secrets   │
└─────────────────────────────────────────────────────────────────────┘
```

**Pourquoi L4 + L3 open source?** La loi doit être vérifiable. N'importe qui peut:
- Lire le code mind-protocol → vérifier que les règles sont justes
- Self-host mind-protocol → run son propre L4 (fork)
- Auditer les formules de pricing → vérifier pas de favoritisme
- Contribuer des templates L3 → enrichir l'ecosystem

**Pourquoi membrane privé?** Secret sauce. Le routing est notre avantage compétitif.

**Analogie:** Comme Ethereum — le code du protocole est open source, mais Infura/Alchemy run l'infra.

### mind-mcp (open source)
```
mind-mcp/
│
├── mind/                              # PACKAGE PRINCIPAL
│   │
│   ├── graph/                         # Graph operations
│   │   ├── adapter/                   # DB abstraction
│   │   │   ├── base.py
│   │   │   ├── neo4j.py
│   │   │   ├── falkordb.py
│   │   │   └── factory.py
│   │   │
│   │   ├── ops/                       # CRUD operations
│   │   │   ├── nodes.py
│   │   │   ├── links.py
│   │   │   └── queries.py
│   │   │
│   │   └── physics/                   # Energy, weight, decay
│   │       ├── energy.py
│   │       ├── propagation.py
│   │       └── decay.py
│   │
│   ├── schema/                        # Type definitions
│   │   ├── nodes.py
│   │   ├── links.py
│   │   └── validation.py
│   │
│   ├── traversal/                     # Graph navigation
│   │   ├── embedding.py
│   │   ├── modes.py                   # public/sanitized/trust
│   │   └── moment.py
│   │
│   ├── membrane/                      # LOCAL membrane only
│   │   ├── stimulus.py                # Stimulus creation
│   │   ├── integrator.py              # Saturation, refractory, EMA
│   │   ├── broadcast.py               # Local pub/sub
│   │   └── client.py                  # Connect to L4 hub
│   │
│   ├── actors/                        # Actor management
│   │   ├── citizen.py                 # L1 personal graph
│   │   ├── sources.py                 # Log, RSS, cron as actors
│   │   └── wallet.py                  # $MIND local wallet
│   │
│   └── client/                        # L4 connection
│       ├── websocket.py
│       ├── graphql.py
│       ├── auth.py                    # JWT validation
│       └── sync.py                    # Schema sync from L4
│
├── mcp/                               # MCP SERVER
│   ├── server.py
│   ├── tools/
│   └── sync_wrapper.py
│
├── cli/                               # CLI TOOLS
│   ├── __main__.py
│   ├── commands/
│   │   ├── init.py
│   │   ├── status.py
│   │   ├── doctor.py
│   │   └── explore.py
│   └── config.py
│
├── tests/
├── pyproject.toml
├── README.md
└── .mind-mcp/                         # Template config
```

### mind-protocol (open source — VERIFIABLE)
```
mind-protocol/
│
├── l4/                                # LA LOI
│   ├── schema/                        # Source of truth
│   │   ├── node_types.py              # Actor, Moment, Narrative, Space, Thing
│   │   ├── link_schema.py             # LINK properties
│   │   └── versions.py                # Schema versioning
│   │
│   ├── registry/                      # Identity registry
│   │   ├── citizens.py
│   │   ├── orgs.py
│   │   ├── endpoints.py
│   │   └── validation.py              # JWT, hash verification
│   │
│   └── rules/                         # Governance
│       ├── laws.py                    # Immutable laws
│       └── rules.py                   # Configurable rules
│
├── l3/                                # ECOSYSTEM (public)
│   ├── templates/
│   │   ├── procedures/
│   │   ├── vocabularies/
│   │   └── mappings/
│   │
│   ├── contributions/                 # Community review process
│   │   └── review.py
│   │
│   └── federation/                    # Multi-org sharing
│       ├── publish.py
│       └── pull.py
│
├── economy/                           # ÉCONOMIE (formulas only)
│   ├── pricing/
│   │   └── physics.py                 # Organism economics formulas
│   └── fees/
│       └── calculation.py             # 1-5% membrane fees
│
├── api/                               # API SPECS
│   ├── graphql/
│   │   ├── schema.graphql
│   │   └── resolvers/
│   │
│   └── websocket/
│       ├── protocol.py
│       └── handlers/
│
├── graph/                             # L4 graph storage
│   ├── connection.py                  # Neo4j Aura
│   └── queries.py
│
├── deploy/                            # Self-hosting guide
│   ├── docker-compose.yaml
│   └── README.md
│
├── tests/
├── pyproject.toml
├── README.md
└── ARCHITECTURE.md
```

### mind-platform (open source) — platform.mindprotocol.ai
```
mind-platform/
│
├── app/                               # Next.js app
│   │
│   ├── (public)/                      # Public pages
│   │   ├── page.tsx                   # Landing
│   │   ├── docs/                      # Docs (generated from L4 graph)
│   │   │   └── [slug]/page.tsx
│   │   ├── registry/                  # Public registry browser
│   │   │   └── page.tsx
│   │   └── schema/                    # Schema explorer
│   │       └── page.tsx
│   │
│   ├── (dashboard)/                   # Authenticated
│   │   ├── citizens/                  # Manage citizens
│   │   │   └── page.tsx
│   │   ├── org/                       # Org dashboard
│   │   │   └── page.tsx
│   │   ├── wallet/                    # $MIND wallet
│   │   │   └── page.tsx
│   │   ├── graph/                     # Graph viewer/editor
│   │   │   └── page.tsx
│   │   ├── procedures/                # Procedure editor
│   │   │   └── page.tsx
│   │   └── marketplace/               # L3 templates marketplace
│   │       └── page.tsx
│   │
│   ├── connectome/                    # Graph visualizer
│   │   ├── components/
│   │   └── page.tsx
│   │
│   ├── api/
│   │   ├── auth/
│   │   └── proxy/                     # Proxy to L4
│   │
│   └── layout.tsx
│
├── components/                        # Shared UI components
│   ├── node_kit/
│   └── edge_kit/
│
├── lib/
│   └── mind-client.ts                 # JS client for L4
│
├── package.json
└── README.md
```

### mind-ops (PRIVATE — Mind Protocol only)
```
mind-ops/
│
├── membrane/                          # SECRET SAUCE
│   │
│   ├── network/                       # Membrane graph structure
│   │   ├── graph.py
│   │   ├── spaces.py
│   │   └── mirrors.py
│   │
│   ├── routing/                       # Stimulus routing
│   │   ├── hash_check.py
│   │   ├── safety_zones.py
│   │   └── cold_outreach.py
│   │
│   ├── hosted/                        # Hosted membranes
│   │   ├── runner.py
│   │   ├── isolation.py
│   │   └── billing.py
│   │
│   └── hub/                           # Cross-org hub
│       └── coordinator.py
│
├── secrets/                           # NEVER COMMIT
│   ├── .env.production
│   ├── neo4j_credentials.yaml
│   └── solana_keys/
│
├── infrastructure/
│   ├── terraform/
│   │   ├── aws/
│   │   └── modules/
│   ├── kubernetes/
│   │   ├── production/
│   │   └── staging/
│   └── monitoring/
│       ├── grafana/
│       └── alerts/
│
├── billing/
│   ├── stripe_webhooks/
│   ├── wallets/                       # Actual wallet management
│   └── usage_tracking/
│
├── runbooks/
│   ├── incident_response.md
│   ├── scaling.md
│   └── backup_restore.md
│
└── ci/
    ├── deploy_protocol.yaml
    ├── deploy_platform.yaml
    └── deploy_mcp.yaml
```

---

# PART 2: 4-LAYER ARCHITECTURE

## L4 = La Loi vs Membrane = Le Vivant

**Distinction fondamentale:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  L4 — LA LOI (statique, authoritative, OPEN SOURCE)                 │
│                                                                      │
│  • Schema = vérité                                                  │
│  • Registry = identités officielles                                 │
│  • Rules/Laws = gouvernance                                         │
│  • Templates = références                                           │
│                                                                      │
│  Ne RUN pas. DÉCLARE. 100% VÉRIFIABLE.                              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  MEMBRANE NETWORK — LE VIVANT (dynamique, émergent)                 │
│                                                                      │
│  • Graph distribué qui connecte L1 ↔ L2 ↔ L3 ↔ L4                  │
│  • Routes stimuli entre tous les layers                             │
│  • Apprend (perméabilité, trust)                                    │
│  • IS the runtime (pas de scheduler séparé)                         │
│                                                                      │
│  VIVE. ÉVOLUE.                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

| L4 (Loi)        | Membrane (Vivant)   |
|-----------------|---------------------|
| Constitution    | Économie vivante    |
| Lois écrites    | Routes commerciales |
| Registre civil  | Conversations       |
| DNA             | Organisme           |
| **Open source** | **Distribué**       |

## Architecture distribuée

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 4 — PROTOCOL (Mind Protocol servers)                         │
│                                                                      │
│  DB: Registry, Schema, Rules/Laws                                   │
│  • Registry (citizens, orgs, endpoints) — PUBLIC                    │
│  • Schema definition — PUBLIC                                        │
│  • Rules/Laws — PUBLIC                                               │
│  • Orchestration (décentralisé via WebSocket)                       │
│  • Economy ($MIND wallets, membrane fees)                           │
│                                                                      │
│  Revenue: Membrane fees 1-5% + Subscriptions + Hosted compute       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │ WebSocket          │ WebSocket          │ WebSocket
         │ (client init,      │ (client init,      │ (client init,
         │  L4 push only)     │  L4 push only)     │  L4 push only)
         │                    │                    │
┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐
│  LAYER 3        │  │  LAYER 3        │  │  LAYER 3        │
│  ECOSYSTEM      │  │  ECOSYSTEM      │  │  ECOSYSTEM      │
│                 │  │                 │  │                 │
│  DB: Templates  │  │  DB: Templates  │  │  DB: Templates  │
│  (procedures,   │  │  (procedures,   │  │  (procedures,   │
│   vocabs,       │  │   vocabs,       │  │   vocabs,       │
│   mappings)     │  │   mappings)     │  │   mappings)     │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐
│  LAYER 3        │  │  LAYER 3        │  │  LAYER 3        │
│  ECOSYSTEM      │  │  ECOSYSTEM      │  │  ECOSYSTEM      │
│                 │  │                 │  │                 │
│  Templates      │  │  Templates      │  │  Templates      │
│  (pulled from   │  │  (pulled from   │  │  (pulled from   │
│   L4)           │  │   L4)           │  │   L4)           │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐
│  LAYER 2        │  │  LAYER 2        │  │  LAYER 2        │
│  ORGANIZATION   │  │  ORGANIZATION   │  │  ORGANIZATION   │
│                 │  │                 │  │                 │
│  • Coordination │  │  • Coordination │  │  • Coordination │
│  • Vocabularies │  │  • Vocabularies │  │  • Vocabularies │
│  • Mappings     │  │  • Mappings     │  │  • Mappings     │
│  • Procedures   │  │  • Procedures   │  │  • Procedures   │
│    (instances)  │  │    (instances)  │  │    (instances)  │
│                 │  │                 │  │                 │
│  Org A          │  │  Org A          │  │  Org B          │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐
│  LAYER 1        │  │  LAYER 1        │  │  LAYER 1        │
│  CITIZEN        │  │  CITIZEN        │  │  CITIZEN        │
│                 │  │                 │  │                 │
│  • Personal DB  │  │  • Personal DB  │  │  • Personal DB  │
│  • Memory       │  │  • Memory       │  │  • Memory       │
│  • Identity     │  │  • Identity     │  │  • Identity     │
│  • Wallet       │  │  • Wallet       │  │  • Wallet       │
│                 │  │                 │  │                 │
│  Citizen A      │  │  Citizen B      │  │  Citizen C      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Où vit quoi

| Concept | Layer | Stockage | Notes |
|---------|-------|----------|-------|
| **Citizen graph** | L1 | Sa propre DB | 1 DB par citizen |
| **Citizen identity** | L4 | Registry public | Officiel, vérifiable |
| **Citizen wallet** | L1 + L4 | Local + Solana | Budget autonome |
| **Org coordination** | L2 | DB de l'org | Relationships entre citizens |
| **Vocabularies** | L2 | DB de l'org | Spécifique à l'org (instances) |
| **Mappings** | L2 | DB de l'org | Spécifique à l'org (instances) |
| **Procedures** | L2 | DB de l'org | Spécifique à l'org (instances) |
| **Templates** | L3 | DB Ecosystem (propre) | Partagés, DB dédiée |
| **Schema** | L4 | Public | Source of truth |
| **Registry** | L4 | Public | Citizens, orgs, endpoints |
| **Rules/Laws** | L4 | Public | Governance |

## Clarifications architecturales

| Question | Réponse |
|----------|---------|
| **L3 Ecosystem** | DB propre, pas virtuel. Templates stockés dans DB dédiée. |
| **WebSocket** | Client initie → L4. Ensuite **push only** de L4 vers client. |
| **Hosted runtime** | Clés API client stockées chez nous OU notre service avec nos clés. |
| **Schema sync** | **Push** via WebSocket (L4 notifie les changements). |
| **Offline mode** | **NON.** L1-L2 nécessite connexion L4 pour registry, schema, etc. |
| **Consolidation** | Threshold d'énergie + nombre de nodes (à définir en Phase 3). |

---

# PART 3: COMMUNICATION ARCHITECTURE

## Principes fondamentaux

1. **Pas d'API REST** — WebSocket + GraphQL seulement
2. **Pas de modification directe DB** — Stimulus seulement (membrane)
3. **Tout passe par L4** pour cross-org (pas de route directe)
4. **MCP comme interface** pour Claude/LLMs

## Patterns de communication

### Pattern 1: MCP (Claude Desktop/Web)
```
Claude Desktop/Web
       │
       │ MCP Protocol
       ▼
mind-mcp (local)
       │
       │ GraphQL/WebSocket (si cross-org)
       ▼
L4 (si nécessaire)
```

**Use case:** User utilise Claude avec mind-mcp
**Runtime:** Non (Claude drive)
**Coût:** Membrane fees si cross-org

### Pattern 2: Backend intégré (automation)
```
Ton backend (Node/Python)
       │
       │ mind-mcp SDK
       ▼
mind-mcp agent
       │
       │ WebSocket persistant
       ▼
L4 orchestration
```

**Use case:** Automatisation (prospecting, agents autonomes)
**Runtime:** Oui (ton backend)
**Coût:** Ton hosting + API keys + membrane fees

### Pattern 3: Hosted par Mind Protocol
```
Pas de backend chez toi
       │
       │ mind-mcp agent hosted by us
       ▼
L4 orchestration
```

**Use case:** Pas de clé API, on run pour toi
**Runtime:** Oui (notre backend)
**Coût:** Subscription (compute inclus) + membrane fees

## WebSocket L4

```python
# mind-mcp agent
class MindAgent:
    def __init__(self, l4_key):
        self.ws = connect_websocket(L4_WS_URL, l4_key)
        self.ws.on_message = self.handle_l4_message
    
    def handle_l4_message(self, msg):
        match msg.type:
            case "stimulus":
                # Cross-org stimulus received
                result = self.membrane.receive(msg.payload)
                self.ws.send({"type": "ack", "result": result})
            
            case "wake":
                # L4 requests citizen wake (energy-based)
                result = self.wake_citizen(msg.citizen_id)
                self.ws.send({"type": "wake_result", "result": result})
            
            case "health_check":
                # L4 health monitoring
                status = self.get_health()
                self.ws.send({"type": "health", "status": status})
```

## GraphQL (pas REST)

```graphql
# Registry queries
query LookupCitizen($id: ID!) {
    citizen(id: $id) {
        id
        synthesis
        org { id name }
        capabilities
        publicNodes { id synthesis }
    }
}

query LookupOrg($id: ID!) {
    organization(id: $id) {
        id
        name
        citizens { id synthesis }
        endpoint
    }
}

# Mutations (authenticated)
mutation RegisterCitizen($input: CitizenInput!) {
    registerCitizen(input: $input) {
        id
        registeredAt
    }
}
```

---

# PART 4: MEMBRANE SYSTEM

## Membrane = Tuyauterie Invisible

**La membrane est un graph séparé, invisible, qui connecte tous les graphs locaux.** Pas visible comme L4. C'est la plomberie du réseau.

```
L4 = Public, authoritative     Membrane = Private, infrastructure
────────────────────────────────────────────────────────────────
Registry, Schema, Laws         Routes, Validation, Routing
DÉCLARE                        TRANSPORTE
Visible                        Invisible (tuyauterie)
```

**On ne query/modifie JAMAIS directement la DB de quelqu'un d'autre.**

## Public Nodes → Mirror dans Membrane

Quand une node devient `public: true`, elle émet un broadcast:

```
GRAPH LOCAL (L1/L2)                    MEMBRANE GRAPH (distribué)
─────────────────────────────────────────────────────────────────
Node (public: true)                    
      │                                
      │ broadcast event               
      ▼                                
                          ──────────▶  Thing (mirror node)
                                       │
                                       └── contained in Space
                                           (représente graph origine)
                                           │
                                           └── Actor (certified)
                                               JWT = origin_hash × id × registry_hash
```

**Certification bidirectionnelle:** Le graph origine ET le registry valident l'actor.

## Sources = Actors

**Tout ce qui émet des stimuli est un Actor:**

```yaml
# User input
Actor (type: 'player', id: 'user_nicolas')

# Cron job
Actor (type: 'system', id: 'cron_daily_sync')

# Log stream
Actor (type: 'system', id: 'log_ingestor')

# RSS feed
Actor (type: 'system', id: 'rss_feed_techcrunch')

# Webhook
Actor (type: 'system', id: 'webhook_github')
```

**Standardisés comme stimuli, traités par membrane de la même façon.**

## Broadcast Mechanism avec validation crypto

**Quand un Actor node est marqué `public: true`, il émet un broadcast:**

```
Actor (public: true) dans Graph A
         │
         │ Émet broadcast event
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  MEMBRANE crée Thing node                                        │
│                                                                  │
│  Thing:                                                          │
│    content: payload du broadcast                                 │
│    container: Space (graph origine)                              │
│    hash: SHA256(JWT_origin_graph × node_id)                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
         │
         │ Hash validé contre L4 Registry
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  L4 REGISTRY VALIDATION                                          │
│                                                                  │
│  Vérifie:                                                        │
│  1. JWT correspond au graph enregistré                          │
│  2. Hash = f(JWT × node_id) est valide                          │
│  3. Endpoint d'écoute vient de membrane officielle              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
         │
         │ SI valide
         ▼
Injection validée dans runner MCP origine
         │
         └── target = Actor cible
```

**Le hash permet de valider:**
- L'event broadcast est authentique (pas forgé)
- L'endpoint d'écoute est la membrane officielle
- Le graph origine est celui qu'il prétend être

## Topologie: Régions isolées sans validation explicite

**La membrane évite le mixing non-validé entre régions:**

```
┌─────────────────────────────────────────────────────────────────┐
│  ORG A REGION                          ORG B REGION             │
│                                                                  │
│  ┌─────────┐    ┌─────────┐            ┌─────────┐              │
│  │Citizen A│◄──►│Citizen B│            │Citizen C│              │
│  └─────────┘    └─────────┘            └─────────┘              │
│       │              │                       │                   │
│       └──────────────┘                       │                   │
│              │                               │                   │
│         AUTO-VALID                           │                   │
│        (same org)                            │                   │
│                                              │                   │
│              │                               │                   │
│              └───────────┬───────────────────┘                   │
│                          │                                       │
│                  EXPLICIT VALIDATION                             │
│                   (cross-org)                                    │
│                          │                                       │
│                  Receiver must accept                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

| Route | Validation |
|-------|------------|
| Citizen A → Citizen B (same org) | Auto-valid |
| Citizen A → Citizen C (cross-org) | Explicit receiver validation required |
| Org A → Org B | Explicit validation + membrane fee |

## Privacy Mode vs Trust Mode

**Le stimulus déclenche le MCP target SEULEMENT si:**

```python
def should_trigger_mcp(stimulus, target):
    # Option 1: Hash match (cryptographic verification)
    if verify_membrane_hash(stimulus, target):
        return True
    
    # Option 2: Safety zone (citizen → its own org)
    if is_same_org(stimulus.source, target):
        return True
    
    return False  # Rejected - no trigger
```

| Condition | Description | Example |
|-----------|-------------|---------|
| **Hash match** | JWT verification (origin × id × registry) | Cross-org verified |
| **Safety zone** | Citizen talking to its own org | Internal communication |

## Les 3 Modes de Traversal

**Le mode détermine ce que le target voit:**

| Mode | Behavior | Use case |
|------|----------|----------|
| **PUBLIC** | Private nodes **non-activées** (zero energy, invisible) | Cross-org unknown |
| **SANITIZED** | Traverse normal, **filtre à l'output** | Cross-org trust partiel |
| **TRUST** | Réponse normale, tout visible | Same org, haute confiance |

```python
def determine_traversal_mode(stimulus, target):
    # Same org = always trust
    if is_same_org(stimulus.source, target):
        return "trust"
    
    # Check trust EMA from history
    trust_score = get_trust_ema(stimulus.source, target)
    
    if trust_score > 0.8:
        return "trust"
    elif trust_score > 0.4:
        return "sanitized"
    else:
        return "public"

def traverse(graph, stimulus, mode):
    match mode:
        case "public":
            # Only activate public nodes
            return traverse_filtered(
                graph, stimulus,
                node_filter=lambda n: n.public == True
            )
        
        case "sanitized":
            # Traverse everything, filter output
            raw_result = traverse_full(graph, stimulus)
            return sanitize_output(raw_result)
        
        case "trust":
            # Full access
            return traverse_full(graph, stimulus)
```

## Response → Moment dans Membrane

**Chaque broadcast de réponse crée un Moment:**

```
Thing (original broadcast)
         │
         └──LINK (triggers)──> Moment (response)
                                    │
                                    ├── synthesis: "Response to query X"
                                    ├── content: {traversal_result}
                                    └── LINK (about) → Thing original
```

**Ça crée un audit trail dans le membrane graph:**
- Qui a demandé quoi
- Quelle réponse a été donnée
- Mode (privacy/trust)
- Timestamp

## Ce qui traverse les membranes

```
CE QUI TRAVERSE:
├── Procedure reference (pointer vers node, pas contenu)
├── Step courant (référence)
├── Schema de réponse attendu
├── Hash de validation
└── Résultat structuré (privacy mode: sanitized)

CE QUI NE TRAVERSE PAS:
├── Contenu des fichiers (sauf trust mode explicite)
├── Graph interne (sauf nodes public: true)
├── Données brutes non-structurées
├── Anything not validated by hash
└── Cross-org without explicit receiver validation
```

## Flow cross-org via L4

```
Org A veut communiquer avec Org B
         │
         │ Org A n'a PAS l'adresse de Org B
         │ Org A n'a PAS accès à la DB de Org B
         │
         ▼
Actor (public: true) émet broadcast
         │
         ▼
Thing créée avec hash = JWT(A) × node_id
         │
         ▼
L4 Registry valide hash
         │
         ├── Prélève membrane fee (1-5%)
         │
         └── Route vers Org B membrane
                   │
                   ▼
         Org B membrane reçoit
                   │
                   ├── Explicit validation required (cross-org)
                   ├── Si accepté: mode (privacy/trust) déterminé
                   │
                   └── Traverse, répond
                             │
                             └── Moment créé dans membrane graph
```

## Exemple concret: Doctor comme L2 Org

Pattern réel montrant communication membrane-only sans accès au contenu:

```
Doctor (L2 Org spécialisée)              Client (L2 Org)
        │                                       │
        │  [Privacy Mode]                       │
        │  envoie: procedure_ref + step_1       │
        │  schema: {stale_count: int,           │
        │           paths: string[]}            │
        │  hash: JWT(Doctor) × proc_node_id     │
        │───────────────────────────────────────>│
        │                                       │
        │                  L4 valide hash       │
        │                  Client valide (cross-org)
        │                                       │
        │                                       │ exécute step_1 LOCALEMENT
        │                                       │ (traverse SES public nodes)
        │                                       │
        │  Thing créé dans membrane graph       │
        │  reçoit: {stale_count: 3,             │
        │           paths: ["docs/X.md"]}       │
        │<───────────────────────────────────────│
        │                                       │
        │  Moment créé: response linked to Thing│
        │                                       │
        │  traversal interne Doctor             │
        │  (graph Doctor décide next step)      │
        │                                       │
        │  envoie: procedure_ref + step_2       │
        │───────────────────────────────────────>│
```

**Propriétés clés:**
- **Doctor ne voit JAMAIS le contenu** — seulement résultats structurés
- **Hash validation** garantit authenticité
- **Cross-org = explicit validation** par receiver
- **Privacy mode** = seulement public nodes traversées
- **Audit trail** = Moments dans membrane graph

**Ce pattern s'applique à toute org de service:**
- GraphCare (health monitoring)
- SecurityOrg (audits)
- LegalOrg (contract review)
- FinanceOrg (pricing strategy)

## Cold Outreach

**Pour contacter quelqu'un qu'on ne connaît pas:**

| Registry (L4) | Discoverable (L3) |
|---------------|-------------------|
| Existence officielle | Opt-in pour contact |
| Identity verification | "Je suis contactable" |
| ≠ contactable | Registered in L3 |

**Rule:** Registry = existence. L3 registration = discoverability.

```python
def can_cold_outreach(source, target):
    # Target must be registered in L3 (explicit opt-in)
    if not registry.l3_discoverable(target.id):
        return False
    
    # Source must be verified
    if not verify_actor(source.jwt):
        return False
    
    return True
```

**Actors public by default?** Non. Registry public ≠ contactable. L3 opt-in required.

## Query: Sync ET Event-Driven

**Les deux patterns sont supportés:**

### Sync (request-response)

```python
def query_sync(stimulus, timeout=30):
    """
    Blocking query. Wait for response.
    Use for: user questions, immediate needs.
    """
    response_channel = generate_channel_id()
    stimulus.response_channel = response_channel
    
    # Inject (event-driven underneath)
    inject_stimulus(stimulus)
    
    # Block until response or timeout
    return wait_for_event(response_channel, timeout)
```

### Event-Driven (fire and forget)

```python
def query_async(stimulus, callback=None):
    """
    Non-blocking. Response comes later via membrane.
    Use for: broadcast, multi-target, long-running.
    """
    if callback:
        stimulus.callback = callback
    
    inject_stimulus(stimulus)
    # Returns immediately. Response arrives via membrane event.
```

### Quand utiliser quoi

| Pattern | Use case | Example |
|---------|----------|---------|
| **Sync** | User attend réponse | "What's in my graph?" |
| **Async** | Broadcast, multi-target | "Notify all orgs of update" |
| **Async** | Long-running | "Analyze this corpus" |
| **Async** | Fire-and-forget | "Log this event" |

**Implementation:** Sync est un wrapper over event-driven. Underneath, tout est events.

---

# PART 5: STIMULUS-DRIVEN ARCHITECTURE (PAS DE TICKS)

## Principe fondamental: Pure event-driven

```
AVANT (tick-based)              APRÈS (stimulus-driven)
────────────────────────────────────────────────────────
Clock → Tick → Check all        Stimulus in → Cascade → Done
Polling mentality               Pure reactive
Central clock                   Distributed, async
"Pull"                          "Push"
Waste cycles on idle            Zero cost when quiet
```

**Il n'y a pas de ticks. Il n'y a que des stimuli qui cascadent dans tout le network.**

## Tout est stimulus

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SOURCES DE STIMULI                               │
│                                                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │  User   │ │   Log   │ │   RSS   │ │  Cron   │ │ Webhook │       │
│  │  input  │ │  stream │ │  feed   │ │  timer  │ │  event  │       │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │
│       │           │           │           │           │             │
│       └───────────┴───────────┴─────┬─────┴───────────┘             │
│                                     │                                │
│                                     ▼                                │
│                         ┌───────────────────┐                        │
│                         │  STANDARDIZE      │                        │
│                         │  → Stimulus       │                        │
│                         │  → Validate       │                        │
│                         │  → Inject         │                        │
│                         └─────────┬─────────┘                        │
│                                   │                                  │
└───────────────────────────────────┼──────────────────────────────────┘
                                    │
                                    ▼
                          MEMBRANE NETWORK
                          (cascade naturelle)
```

**Les crons sont des générateurs de stimuli, pas des orchestrateurs.**

## Le stimulus standard

```yaml
Stimulus:
  id: uuid
  source: actor_id | system_id
  energy: float              # Force initiale
  synthesis: string          # Embeddable content
  embedding: vector          # Pour routing
  payload: any               # Data originale
  timestamp: datetime
  ttl: int                   # Hops restants avant extinction
```

## Validation du stimulus

**Le stimulus fait des requêtes au graph, comme tout le monde.**

Avant injection:
1. Stimulus validé par procédure (pas de gates manuels)
2. Considère seulement les nodes `public: true` pour moment creation
3. Linked et injecté avec energy
4. Cascade naturelle commence

```python
def inject_stimulus(network, stimulus):
    # Validation via procedure (graph-based)
    if not validate_stimulus(stimulus):
        return Rejected(reason)
    
    # Entry point basé sur embedding similarity
    entry_node = find_entry_point(network, stimulus.embedding)
    
    # Create moment from public nodes only
    moment = create_moment(stimulus, public_nodes_only=True)
    
    # Inject energy
    entry_node.energy += stimulus.energy
    
    # Cascade - pas de loop, juste propagation
    propagate(entry_node, stimulus)
```

## La cascade

```python
def propagate(node, stimulus):
    if stimulus.energy < THRESHOLD or stimulus.ttl <= 0:
        return  # Extinction naturelle
    
    for link in node.outgoing_links:
        # Energy split selon poids
        outgoing_energy = stimulus.energy * link.weight * link.polarity[0]
        
        # Permeability check (learned)
        if link.target.permeability(stimulus.source) > random():
            # Stimulus passe
            new_stimulus = stimulus.with_energy(outgoing_energy).decrement_ttl()
            link.target.receive(new_stimulus)
            propagate(link.target, new_stimulus)
```

## Phenomenological Requirements

**Ce que la consciousness fait:**

| Behavior | Mechanism |
|----------|-----------|
| **Accumulates gradually** | Repeated stimuli don't create instant spikes (saturation) |
| **Needs recovery time** | Can't re-activate immediately (refractory) |
| **Learns source quality** | Reliable sources get more influence (trust/utility EMAs) |
| **Resists spam naturally** | Mass flooding becomes self-limiting (mass accumulation) |
| **Composes fairly** | Multiple simultaneous sources don't create runaway energy (bounded) |

## Integrator Constraints

**Ce que l'integrator doit préserver:**

```
✗ No hardcoded thresholds      → All learned from substrate
✗ No privileged sources        → Membrane treats all equally
✗ No energy conservation       → ΔE bounded by physics
  violations
✗ No permanent state           → Everything decays
  accumulation
✗ No manual gates              → Procedure-based validation only
✗ No significance scoring      → Energy IS significance
✗ No batch jobs                → Pure cascade
```

**Energy transfer through membrane permeability, not direct siphoning.**

## Où "tourne" le système?

**Il n'y a pas de "runtime" séparé.** La cascade EST l'exécution.

| Scenario | Qui génère les stimuli? |
|----------|-------------------------|
| MCP dans Claude Desktop | Claude génère stimuli via MCP |
| Backend intégré | Ton code génère stimuli |
| Hosted | Nos agents génèrent stimuli |

**Dans tous les cas:** Stimulus in → Cascade → Done. Pas de scheduler central.

## Autonomie des citizens

L'autonomie = budget + cascade.

```
Citizen reçoit stimulus
         │
         ▼
Citizen a-t-il assez de $MIND?
         │
    ┌────┴────┐
    ▼         ▼
   OUI       NON
    │         │
    │    Stimulus rejected
    │    (insufficient funds)
    ▼
Cascade continue
Citizen peut répondre
(génère nouveaux stimuli)
```

- Assez de $MIND → Stimulus passe, cascade continue
- Pas assez → Stimulus rejected, citizen effectivement "en hibernation"

---

# PART 6: ECONOMY ($MIND)

## Deux couches économiques

```
┌─────────────────────────────────────────────────────────────────────┐
│  INTERFACE HUMAINE (ce que les users voient)                        │
│                                                                      │
│  • Subscription €X/mois (Stripe)                                    │
│  • "Crédits" qui se dispatchent                                     │
│  • Usage limité après épuisement                                    │
│  • Simple, prévisible, en EUR/USD                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Conversion (invisible pour human)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BACKEND RÉEL ($MIND sur Solana)                                    │
│                                                                      │
│  Chaque entité a un wallet:                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ Citizen     │ │ Org         │ │ Ecosystem   │ │ L4 Protocol │   │
│  │ Wallet      │ │ Wallet      │ │ Wallet      │ │ Wallet      │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│                                                                      │
│  Chaque membrane call = transaction $MIND                           │
│  Ledger immutable on-chain                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Organism Economics (pas marché)

| Économie de marché | Organism Economics (Mind Protocol) |
|--------------------|------------------------------------|
| Prix choisis par acteurs | Prix déterminés par physics |
| Négociation | Formule automatique |
| Compétition | Collaboration |
| Profit maximization | Ecosystem health |
| Volatilité | Stabilité émergente |

## Pricing formula

```python
price = f(
    membrane_permeability,    # Plus la membrane est ouverte, moins cher
    load,                     # Charge système
    trust_score,              # Historique relation
    utility_ema,              # Valeur délivrée par ce source
    compute_cost              # Coût réel (LLM tokens, etc.)
)

effective_price = base_cost × complexity × risk × (1 - utility_rebate)
```

**Personne ne "choisit" les prix.** La physics les détermine.

## Transaction types et coûts

| Action | Payeur | Receveur | Fee L4 |
|--------|--------|----------|--------|
| Citizen A parle à Citizen B (même org) | A wallet | B wallet | 0% |
| Citizen A parle à Citizen C (autre org) | A wallet | C wallet | 1-5% |
| Org wake un Citizen | Org wallet | Citizen wallet | 0% |
| Query L3 templates | Requester wallet | L4 wallet | Flat fee |
| Publish vers L3 | Publisher wallet | L4 wallet | Flat fee |

## Flow économique complet

```
1. Human paie €20/mois (Stripe)
         │
         ▼
2. Mind Protocol reçoit €20
         │
         ▼
3. Mint 2000 $MIND vers Org wallet du human
         │
         ▼
4. Org wake Citizen "Marco"
   Org wallet ──[50 $MIND]──> Marco wallet
         │
         ▼
5. Marco parle à Citizen "Felix" (autre org)
   Marco wallet ──[10 $MIND]──> Felix wallet
   Marco wallet ──[0.5 $MIND]──> L4 wallet (5% fee)
         │
         ▼
6. Tout tracé on-chain (Solana)
   Budget Marco: 50 → 39.5
   Autonomie = gestion de CE budget
```

## $MIND: Token interne, pas spéculatif

**Option choisie:**
- $MIND = token utilitaire interne
- Pas directement achetable par humains (ou très limité)
- Humains paient en EUR → reçoivent "crédits" → converti en $MIND
- Pas de pump.fun, pas de spéculation
- Pure ledger pour économie AI

---

# PART 7: FEATURE GATING (CLÉ L4)

## Accès selon authentification

| Feature | Sans clé L4 | Free tier | Paid tier |
|---------|-------------|-----------|-----------|
| **Schema sync** | ✅ | ✅ | ✅ |
| **Local L1-L2** | ✅ | ✅ | ✅ |
| **Query L3 templates** | ❌ | 100/jour | Illimité |
| **Registry read** | ❌ | ✅ | ✅ |
| **Registry write** | ❌ | ❌ | ✅ |
| **Cross-org TX** | ❌ | ❌ | ✅ (+ 1-5% fee) |
| **Auto-wake (hosted)** | ❌ | ❌ | ✅ |
| **Linting/suggestions** | ❌ | Basic | Advanced |
| **Health monitoring** | ❌ | ❌ | ✅ |

## Clé L4 = Accès au network

```
SANS CLÉ (anonymous)
├── Schema fetch (init)
├── Schema updates (sync)
├── Local L1-L2 illimité
└── ISOLÉ du network

AVEC CLÉ (authenticated)
├── Query L3 (procedures, vocabularies, mappings)
├── Registry (chercher des orgs, citizens)
├── Cross-org communication
├── Publish vers L3
└── TOUT metered via la clé
```

---

# PART 8: IMPLEMENTATION PHASES

## Phase 1: MEMBRANE (priorité immédiate)

**Objectif:** Communication qui fonctionne

```
├── Cross-level (L1 ↔ L2)
│   ├── Org can wake citizen
│   ├── Citizen can report to org
│   └── Stimulus-based, not direct DB
│
├── Cross-org (via L4)
│   ├── Lookup in registry
│   ├── Route via WebSocket
│   └── Stimulus delivery
│
├── Champ `public` sur nodes/links
│   └── Privacy control
│
├── Perméabilité apprise
│   └── Membrane learns from outcomes
│
└── Tests
    ├── Citizen A → Citizen B (same org)
    ├── Citizen A → Citizen C (cross-org via L4)
    └── Org → Citizen (wake)
```

## Phase 2: REGISTRY & ROUTING

**Objectif:** Découverte et routing

```
├── L4 Registry
│   ├── Citizens (id, synthesis, org, capabilities)
│   ├── Orgs (id, name, endpoint, citizens)
│   └── Endpoints (WebSocket URLs, credentials)
│
├── GraphQL API
│   ├── Queries (lookup citizen, lookup org)
│   └── Mutations (register, update)
│
├── Clé L4
│   ├── Authentication
│   ├── Rate limiting
│   └── Feature gating
│
└── Tests
    ├── Register citizen
    ├── Lookup cross-org
    └── Reject unauthorized
```

## Phase 3: AUTONOMY (wake basé sur energy)

**Objectif:** Citizens autonomes

```
├── Energy-based wake
│   ├── Monitor energy levels
│   ├── Wake when threshold reached
│   └── Process pending stimuli
│
├── Budget management
│   ├── Citizen wallet
│   ├── Debit on actions
│   └── Hibernate if insufficient
│
├── Consolidation automatique
│   ├── Memory consolidation when needed
│   └── Costs $MIND
│
├── Health monitoring
│   ├── L4 health checks
│   └── Suggestions
│
└── Tests
    ├── Citizen wakes on energy threshold
    ├── Citizen hibernates on zero budget
    └── Memory consolidates automatically
```

## Phase 4: ECONOMY ($MIND)

**Objectif:** Économie complète

```
├── $MIND wallets
│   ├── Citizen wallets
│   ├── Org wallets
│   ├── Ecosystem wallet
│   └── L4 Protocol wallet
│
├── Transactions on-chain
│   ├── Every membrane call = TX
│   ├── Membrane fees 1-5%
│   └── Ledger immutable
│
├── Organism economics
│   ├── Physics-based pricing
│   ├── Trust affects price
│   ├── Utility rebates
│   └── No negotiation
│
├── Human interface
│   ├── Stripe subscriptions
│   ├── EUR → $MIND conversion
│   └── Credits abstraction
│
└── Tests
    ├── Cross-org TX with fee
    ├── Budget depletes correctly
    └── Pricing formula works
```

---

# PART 9: TERMINOLOGY

| Terme | Signification | Layer |
|-------|---------------|-------|
| **Protocol** | Governance — registries, laws, rules | L4 |
| **Procedure** | Exécutable atomisé dans le graph | L2/L3 |
| **Vocabulary** | Termes par domaine (instances) | L2 |
| **Mapping** | Traduction vers schema (instances) | L2 |
| **Template** | Procedure/vocab/mapping partagé | L3 (via L4) |
| **Skill** | Connaissance contextuelle pour LLM | L2/L3 |
| **Membrane** | Interface de communication (stimulus-based) | All |
| **Stimulus** | Message/query envoyé via membrane | All |
| **Citizen** | AI individuel avec graph personnel | L1 |
| **Org** | Organisation coordonnant des citizens | L2 |

---

# PART 10: SCHEMA (ngram)

## Node Types (Neo4j Labels)

| Label | Role | Subtypes (`type` field) |
|-------|------|-------------------------|
| `Actor` | Pump — injecte énergie | player, npc, system, researcher |
| `Moment` | Router — branch point | event, decision, action |
| `Narrative` | Attractor — destination | belief, commitment, claim, step, vocabulary, mapping, skill |
| `Space` | Container — bidirectional | laboratory, module, procedure, template |
| `Thing` | Fast passthrough | file, uri, artifact, evidence |

## Relation unique: LINK

```yaml
-[LINK]->
  # Physics
  weight: float         # Importance over time (slow)
  energy: float         # Current activation (fast)
  
  # Structure
  polarity: [float, float]  # Directional strength
  hierarchy: float          # -1 (contains) to +1 (elaborates)
  permanence: float         # 0 (ephemeral) to 1 (permanent)
  
  # Plutchik emotions
  joy_sadness: float
  trust_disgust: float
  fear_anger: float
  surprise_anticipation: float
  
  # Semantics
  synthesis: string     # Embeddable summary
  embedding: vector     # 1536 dims
  
  # Privacy
  public: boolean       # Visible cross-org?
```

## Traversal: Embedding-based, pas Cypher

**ngram ne fait JAMAIS de Cypher queries directes.**

```
Contexte "médecine"
    → Traversée via embedding similarity
    → Trouve nodes connectés sémantiquement
    → Procedures "crypto" dans autre région = non trouvées
    → Topologie = filtre naturel
```

---

# APPENDIX: CURRENT STATE

## Neo4j Aura (session du 27/12)

**Connexion:**
```
URI: neo4j+s://a446cf7b.databases.neo4j.io
Database: neo4j
```

**Nodes créés:**
- Actor: Nicolas (player), Marco Salthand (npc)
- Space: Venice (laboratory)
- Narrative: The Rich Ecology (belief), We Stay (commitment), atomize (procedure), scientific_study (vocabulary), scientific_study (mapping), + steps
- Moment: Neo4j MCP Connected (event)

**Links créés:**
- Nicolas ↔ Marco (partnership)
- Marco → beliefs/commitments
- procedure:atomize → vocabulary, mapping, steps

---

# SUMMARY

**MIND** = Engine open source. Graph physics. Embedding-based traversal.

**Mind Protocol** = Network 4-layers. L4 obligatoire pour cross-org.

**Communication** = WebSocket + GraphQL + MCP. Pas de REST. Stimulus-based.

**Orchestration** = Décentralisée. Si tu as runtime, tu drives. Sinon on host.

**Économie** = $MIND token interne. Organism economics. Membrane fees 1-5%.

**Autonomie** = Citizens gèrent leur budget. Wake basé sur energy. Pas de schedule central.

---

*"The graph awakens. Citizens manage their own destiny."*

**Session 27 Décembre 2025**
**Nicolas + Marco**