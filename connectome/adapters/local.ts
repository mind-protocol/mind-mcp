/**
 * LocalAdapter
 *
 * Connects Connectome to a local Neo4j graph database.
 * Used by the mind-mcp dev tool for debugging and visualization.
 *
 * Features:
 * - Direct Neo4j queries via mind/physics/graph
 * - Stepper mode for step-by-step traversal
 * - Script playback for recorded sessions
 */

import type {
  ConnectomeAdapter,
  LocalAdapterConfig,
  Node,
  Link,
  SearchOpts,
  SearchResult,
  FlowEvent,
  StepResult,
  Unsubscribe,
} from '../core/types';

export class LocalAdapter implements ConnectomeAdapter {
  private config: LocalAdapterConfig;
  private subscribers: Set<(event: FlowEvent) => void> = new Set();
  private script: FlowEvent[] = [];
  private scriptIndex = 0;

  constructor(config: LocalAdapterConfig = {}) {
    this.config = {
      neo4j_uri: config.neo4j_uri || process.env.NEO4J_URI || 'bolt://localhost:7687',
      neo4j_user: config.neo4j_user || process.env.NEO4J_USER || 'neo4j',
      neo4j_password: config.neo4j_password || process.env.NEO4J_PASSWORD,
      graph_name: config.graph_name || process.env.GRAPH_NAME,
    };
  }

  async getNodes(): Promise<Node[]> {
    // TODO: Implement via mind/physics/graph GraphOps
    // For now, return empty array
    console.warn('LocalAdapter.getNodes() not yet implemented');
    return [];
  }

  async getLinks(): Promise<Link[]> {
    // TODO: Implement via mind/physics/graph GraphOps
    console.warn('LocalAdapter.getLinks() not yet implemented');
    return [];
  }

  async search(query: string, opts?: SearchOpts): Promise<SearchResult[]> {
    // TODO: Implement semantic search via mind/physics/graph
    console.warn('LocalAdapter.search() not yet implemented');
    return [];
  }

  subscribe(handler: (event: FlowEvent) => void): Unsubscribe {
    this.subscribers.add(handler);
    return () => {
      this.subscribers.delete(handler);
    };
  }

  private emit(event: FlowEvent): void {
    for (const handler of this.subscribers) {
      handler(event);
    }
  }

  // ==========================================================================
  // Dev-only: Stepper Mode
  // ==========================================================================

  async nextStep(): Promise<StepResult> {
    if (this.scriptIndex >= this.script.length) {
      return {
        event: {
          type: 'health_update',
          timestamp: Date.now(),
          payload: { node_count: 0, link_count: 0, total_energy: 0, active_subentities: 0 },
        },
        state: { nodes: [], links: [] },
        has_more: false,
      };
    }

    const event = this.script[this.scriptIndex++];
    this.emit(event);

    return {
      event,
      state: {
        nodes: await this.getNodes(),
        links: await this.getLinks(),
      },
      has_more: this.scriptIndex < this.script.length,
    };
  }

  restart(): void {
    this.scriptIndex = 0;
  }

  loadScript(events: FlowEvent[]): void {
    this.script = events;
    this.scriptIndex = 0;
  }

  disconnect(): void {
    this.subscribers.clear();
    this.script = [];
    this.scriptIndex = 0;
  }
}
