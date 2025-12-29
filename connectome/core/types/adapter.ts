/**
 * ConnectomeAdapter Interface
 *
 * Types are loaded dynamically from .mind/schema.yaml at runtime.
 * See: ./schema.ts for runtime loader and validation.
 *
 * Two implementations:
 * - LocalAdapter: Calls Python GraphReadOps via HTTP (FalkorDB default, Neo4j supported)
 * - RemoteAdapter: Connects to L4 API via GraphQL/WebSocket
 */

import { loadSchemaSync, Schema, getNodeTypes } from './schema';

// =============================================================================
// Dynamic Types (loaded from schema.yaml)
// =============================================================================

// Load schema at module init (sync for type definitions)
let _schema: Schema | null = null;

function getSchema(): Schema {
  if (!_schema) {
    try {
      _schema = loadSchemaSync();
    } catch {
      // Schema not found - use minimal defaults for type safety
      console.warn('schema.yaml not found, using minimal types');
    }
  }
  return _schema!;
}

/**
 * Node type - dynamically from schema
 * Fallback: 'actor' | 'moment' | 'narrative' | 'space' | 'thing'
 */
export type NodeType = string; // Runtime validated against schema.nodes

/**
 * Get valid node types from loaded schema
 */
export function validNodeTypes(): string[] {
  const schema = getSchema();
  return schema ? getNodeTypes(schema) : ['actor', 'moment', 'narrative', 'space', 'thing'];
}

/**
 * Generic node - fields from schema.yaml NodeBase
 * All fields are dynamic, validated at runtime
 */
export interface Node {
  // Required (from schema)
  id: string;
  name: string;
  node_type: NodeType;

  // Optional fields loaded from schema
  [key: string]: unknown;
}

/**
 * Generic link - fields from schema.yaml LinkBase
 */
export interface Link {
  // Required (from schema)
  id: string;
  node_a: string;
  node_b: string;

  // Optional fields loaded from schema
  [key: string]: unknown;
}

// =============================================================================
// Flow Events (for visualization updates)
// =============================================================================

export type FlowEventType =
  | 'node_created'
  | 'node_updated'
  | 'node_deleted'
  | 'link_created'
  | 'link_updated'
  | 'link_deleted'
  | 'energy_pulse'
  | 'traversal_step'
  | 'health_update';

export interface FlowEvent {
  type: FlowEventType;
  timestamp: number;
  payload: unknown;
}

export interface TraversalStepEvent extends FlowEvent {
  type: 'traversal_step';
  payload: {
    from_node: string;
    to_node: string;
    via_link: string;
    energy_transferred: number;
    subentity_id?: string;
  };
}

export interface EnergyPulseEvent extends FlowEvent {
  type: 'energy_pulse';
  payload: {
    node_id: string;
    energy_delta: number;
    new_energy: number;
  };
}

export interface HealthUpdateEvent extends FlowEvent {
  type: 'health_update';
  payload: {
    node_count: number;
    link_count: number;
    total_energy: number;
    active_subentities: number;
  };
}

// =============================================================================
// Search Types
// =============================================================================

export interface SearchOpts {
  threshold?: number; // similarity threshold 0-1, default 0.3
  hops?: number; // expand results by N hops, default 1
  limit?: number; // max results, default 50
  node_types?: string[]; // filter by type
}

export interface SearchResult {
  node: Node;
  similarity: number;
}

// =============================================================================
// Step Types (for dev tool stepper mode)
// =============================================================================

export interface StepResult {
  event: FlowEvent;
  state: GraphState;
  has_more: boolean;
}

// =============================================================================
// Graph State
// =============================================================================

export interface GraphState {
  nodes: Node[];
  links: Link[];
}

// =============================================================================
// Adapter Interface
// =============================================================================

export type Unsubscribe = () => void;

export interface ConnectomeAdapter {
  /** Get the loaded schema */
  getSchema(): Schema | null;

  /** Get all nodes and links */
  fetchGraph(): Promise<GraphState>;

  /** Get all nodes */
  getNodes(): Promise<Node[]>;

  /** Get all links */
  getLinks(): Promise<Link[]>;

  /** Semantic search */
  search(query: string, opts?: SearchOpts): Promise<SearchResult[]>;

  /** Subscribe to realtime events */
  subscribe(handler: (event: FlowEvent) => void): Unsubscribe;

  /** List available graphs */
  listGraphs?(): Promise<string[]>;

  /** [Dev] Step to next event */
  nextStep?(): Promise<StepResult>;

  /** [Dev] Restart playback */
  restart?(): void;

  /** [Dev] Load step script */
  loadScript?(events: FlowEvent[]): void;

  /** Disconnect */
  disconnect(): void;
}

// =============================================================================
// Adapter Configs
// =============================================================================

export interface LocalAdapterConfig {
  /** Backend API URL (default: http://localhost:8765) */
  api_url?: string;
  /** Graph name (default: from config or "seed") */
  graph_name?: string;
  /** Path to schema.yaml (auto-detected if not provided) */
  schema_path?: string;
}

export interface RemoteAdapterConfig {
  /** L4 API base URL */
  api_url: string;
  /** WebSocket URL for realtime */
  ws_url?: string;
  /** Auth token */
  auth_token?: string;
}

// =============================================================================
// Re-exports from schema.ts
// =============================================================================

export {
  loadSchema,
  loadSchemaSync,
  validateNode,
  validateLink,
  applyNodeDefaults,
  applyLinkDefaults,
  getNodeFields,
  getLinkFields,
} from './schema';

export type { Schema, SchemaField, ValidationError } from './schema';
