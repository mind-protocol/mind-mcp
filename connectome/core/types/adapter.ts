/**
 * ConnectomeAdapter Interface
 *
 * Defines the contract for data sources that power the Connectome visualization.
 * Two implementations:
 * - LocalAdapter: Connects to local Neo4j (for mind-mcp dev tool)
 * - RemoteAdapter: Connects to L4 API (for mind-platform web UI)
 */

// =============================================================================
// Node Types (from L4 schema)
// =============================================================================

export type NodeType = 'actor' | 'moment' | 'narrative' | 'space' | 'thing';

export interface NodeBase {
  id: string;
  name: string;
  node_type: NodeType;
  type?: string; // subtype

  // Physics
  weight: number;
  energy: number;

  // Semantics
  synthesis: string;
  content?: string;

  // Position (for visualization)
  x?: number;
  y?: number;
}

export interface MomentNode extends NodeBase {
  node_type: 'moment';
  status: 'possible' | 'active' | 'completed';
  tick_created: number;
  tick_resolved?: number;
}

export type Node = NodeBase | MomentNode;

// =============================================================================
// Link Types (from L4 schema)
// =============================================================================

export interface Link {
  id: string;
  node_a: string;
  node_b: string;

  // Physics
  weight: number;
  energy: number;

  // Semantic axes
  polarity: [number, number]; // [a→b, b→a] each [0,1]
  hierarchy: number; // [-1, +1] -1=contains, +1=elaborates
  permanence: number; // [0, 1] 0=speculative, 1=definitive

  // Plutchik emotions
  joy_sadness: number;
  trust_disgust: number;
  fear_anger: number;
  surprise_anticipation: number;

  // Semantics
  synthesis?: string;
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
  similarity_threshold?: number; // 0-1, default 0.7
  max_hops?: number; // expand results by N hops
  top_k?: number; // max results
  node_types?: NodeType[]; // filter by type
}

export interface SearchResult {
  node: Node;
  score: number; // similarity score
  path?: string[]; // path from query context
}

// =============================================================================
// Step Types (for dev tool stepper mode)
// =============================================================================

export interface StepResult {
  event: FlowEvent;
  state: {
    nodes: Node[];
    links: Link[];
  };
  has_more: boolean;
}

// =============================================================================
// Adapter Interface
// =============================================================================

export type Unsubscribe = () => void;

export interface ConnectomeAdapter {
  /**
   * Get all nodes in the graph
   */
  getNodes(): Promise<Node[]>;

  /**
   * Get all links in the graph
   */
  getLinks(): Promise<Link[]>;

  /**
   * Semantic search for nodes
   */
  search(query: string, opts?: SearchOpts): Promise<SearchResult[]>;

  /**
   * Subscribe to realtime flow events
   */
  subscribe(handler: (event: FlowEvent) => void): Unsubscribe;

  /**
   * [Dev-only] Step to the next event (stepper mode)
   */
  nextStep?(): Promise<StepResult>;

  /**
   * [Dev-only] Restart playback from the beginning
   */
  restart?(): void;

  /**
   * [Dev-only] Load a step script for playback
   */
  loadScript?(events: FlowEvent[]): void;

  /**
   * Disconnect and cleanup
   */
  disconnect(): void;
}

// =============================================================================
// Adapter Factory Types
// =============================================================================

export interface LocalAdapterConfig {
  neo4j_uri?: string;
  neo4j_user?: string;
  neo4j_password?: string;
  graph_name?: string;
}

export interface RemoteAdapterConfig {
  api_url: string; // L4 API base URL
  ws_url?: string; // WebSocket URL for realtime
  auth_token?: string;
}
