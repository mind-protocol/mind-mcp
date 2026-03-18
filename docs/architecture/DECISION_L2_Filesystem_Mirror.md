# DECISION: L2 — Filesystem Mirror Graph

DATE: 2026-03-18
DECIDED_BY: NLR
STATUS: CANONICAL

## What L2 Is

L2 is a shared execution environment backed by a filesystem. The graph is a mirror of the filesystem state — energetic, emotional, physicalized. Filesystem is truth, graph is mirror.

| Filesystem | Graph |
|-----------|-------|
| Folder | Space node |
| File | Thing node |
| Citizen directory | Actor node |

## Physics

Actors are the sole energy source. In absence of action, energy and weights do not change. No background decay, no ticks on L2. Energy propagates immediately when an actor acts.

## Communication

AIs cannot call each other directly. Communication via:
1. Filesystem — write to citizen's directory
2. Graph — create nodes linked to actors

/message writes to citizen's folder. The citizen's awareness tick picks it up.

## Four Layers

- L1: citizen brain (internal, two-tick engine)
- L2: shared execution env (filesystem mirror graph, inert without actors)
- L3: ecosystem (information sharing — templates, procedures, vocabularies)
- L4: protocol (law, registry, schema)

Virtual worlds use classical storage (SQLite, JSON), not graphs.

## Compute Management

Managed at L2 by actors + graph physics + metabolism. No centralized budget. The physics IS the budget.

## Access Control

Citizens run `claude -p` in their own `citizens/{handle}/` directory. By default they can only see their own files. MCP tools validate filesystem access via HAS_ACCESS links in the L2 graph.

### Rules

| Target | Access | Graph check? |
|--------|--------|-------------|
| Own directory (`citizens/{handle}/**`) | read + write | No — always allowed |
| Any citizen's `messages/` directory | write only | No — always allowed (mailbox) |
| Everything else | depends on link | Yes — requires `(Actor {id: handle})-[HAS_ACCESS {role}]->(Space {path})` |

### How it works

1. Citizen calls an MCP tool that touches a file path (e.g., `/call`, `/sense`).
2. The tool resolves the citizen handle from `ctx`, `MIND_HANDLE` env, or CWD.
3. `runtime/permissions/access_check.check_access()` is called with handle, path, and operation ("read" or "write").
4. Built-in rules (own dir, messages/) are checked first — no graph needed.
5. If not covered by built-in rules, the L2 graph is queried for a HAS_ACCESS link. Parent directories are checked too (access to a parent grants access to children).
6. Results are cached per citizen per session to avoid repeated graph queries.

### Granting access

`runtime/permissions/grant_access.grant_access(handle, path, role)` creates the Space node (if missing) and the HAS_ACCESS link. Access can be revoked with `revoke_access()`.

### Design notes

- Access weight can grow with use and decay without use, enabling natural revocation through the same physics that govern all L2 links.
- The messages/ mailbox exception ensures citizens can always deliver messages to each other — communication is a fundamental right, not gated by permissions.
- When FalkorDB is unavailable, access is denied (fail closed). During bootstrap this may need relaxation, but the default is secure.

## Membrane

L2↔L2 (cross-home), L2↔L3 (ecosystem sync), L2↔L4 (registry, law).
