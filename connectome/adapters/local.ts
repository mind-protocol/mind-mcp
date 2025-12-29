/**
 * LocalAdapter
 *
 * Connects Connectome to local graph database via Python GraphReadOps.
 * Supports both FalkorDB (default) and Neo4j via database_config.yaml.
 *
 * Communication: Subprocess to Python CLI (mind.physics.graph.connectome_read_cli)
 *
 * Features:
 * - Direct graph queries via Python backend
 * - Stepper mode for step-by-step traversal
 * - Script playback for recorded sessions
 * - Runtime schema validation
 */

import { spawn } from 'child_process';
import {
  ConnectomeAdapter,
  LocalAdapterConfig,
  Node,
  Link,
  SearchOpts,
  SearchResult,
  FlowEvent,
  StepResult,
  GraphState,
  Unsubscribe,
  Schema,
  loadSchema,
  validateNode,
  validateLink,
} from '../core/types';

interface PythonResponse {
  nodes?: Node[];
  links?: Link[];
  matches?: Array<Node & { similarity: number }>;
  graphs?: string[];
  error?: string;
  type?: string;
}

export class LocalAdapter implements ConnectomeAdapter {
  private config: LocalAdapterConfig;
  private schema: Schema | null = null;
  private subscribers: Set<(event: FlowEvent) => void> = new Set();
  private script: FlowEvent[] = [];
  private scriptIndex = 0;

  constructor(config: LocalAdapterConfig = {}) {
    this.config = {
      api_url: config.api_url || 'http://localhost:8765',
      graph_name: config.graph_name || process.env.GRAPH_NAME || 'seed',
      schema_path: config.schema_path,
    };
  }

  /**
   * Get loaded schema
   */
  getSchema(): Schema | null {
    return this.schema;
  }

  /**
   * Initialize - load schema
   */
  async initialize(): Promise<void> {
    try {
      this.schema = await loadSchema(this.config.schema_path);
    } catch (e) {
      console.warn('Could not load schema:', e);
    }
  }

  /**
   * Call Python CLI and parse JSON response
   */
  private async callPython(args: string[]): Promise<PythonResponse> {
    return new Promise((resolve, reject) => {
      const fullArgs = [
        '-m', 'mind.physics.graph.connectome_read_cli',
        '--graph', this.config.graph_name || 'seed',
        ...args
      ];

      const proc = spawn('python3', fullArgs, {
        env: {
          ...process.env,
          PYTHONPATH: process.cwd(),
        },
      });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      proc.on('close', (code) => {
        if (code !== 0) {
          try {
            const parsed = JSON.parse(stdout);
            if (parsed.error) {
              reject(new Error(parsed.error));
              return;
            }
          } catch {
            // Not JSON error
          }
          reject(new Error(`Python CLI failed (${code}): ${stderr || stdout}`));
          return;
        }

        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          reject(new Error(`Invalid JSON from Python: ${stdout}`));
        }
      });

      proc.on('error', (err) => {
        reject(new Error(`Failed to spawn Python: ${err.message}`));
      });
    });
  }

  /**
   * Fetch full graph (nodes + links)
   */
  async fetchGraph(): Promise<GraphState> {
    const result = await this.callPython([]);

    const nodes = (result.nodes || []).map(n => this.normalizeNode(n));
    const links = (result.links || []).map(l => this.normalizeLink(l));

    return { nodes, links };
  }

  /**
   * Get all nodes
   */
  async getNodes(): Promise<Node[]> {
    const { nodes } = await this.fetchGraph();
    return nodes;
  }

  /**
   * Get all links
   */
  async getLinks(): Promise<Link[]> {
    const { links } = await this.fetchGraph();
    return links;
  }

  /**
   * Semantic search
   */
  async search(query: string, opts?: SearchOpts): Promise<SearchResult[]> {
    const args = [
      '--search', query,
      '--threshold', String(opts?.threshold ?? 0.3),
      '--hops', String(opts?.hops ?? 1),
      '--limit', String(opts?.limit ?? 50),
    ];

    const result = await this.callPython(args);

    // matches contains nodes with similarity score
    const matches = result.matches || [];
    return matches.map(m => ({
      node: this.normalizeNode(m),
      similarity: m.similarity || 0,
    }));
  }

  /**
   * List available graphs
   */
  async listGraphs(): Promise<string[]> {
    const result = await this.callPython(['--list-graphs']);
    return result.graphs || [];
  }

  /**
   * Subscribe to events
   */
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

  /**
   * Normalize node from Python response
   */
  private normalizeNode(raw: Record<string, unknown>): Node {
    const node: Node = {
      id: String(raw.id || ''),
      name: String(raw.name || raw.id || ''),
      node_type: String(raw.type || raw.node_type || 'thing'),
      ...raw,
    };

    // Validate if schema loaded
    if (this.schema) {
      const errors = validateNode(this.schema, node);
      if (errors.length > 0) {
        console.warn(`Node ${node.id} validation:`, errors);
      }
    }

    return node;
  }

  /**
   * Normalize link from Python response
   */
  private normalizeLink(raw: Record<string, unknown>): Link {
    const link: Link = {
      id: String(raw.id || `${raw.from_id}-${raw.to_id}`),
      node_a: String(raw.from_id || raw.node_a || ''),
      node_b: String(raw.to_id || raw.node_b || ''),
      ...raw,
    };

    // Validate if schema loaded
    if (this.schema) {
      const errors = validateLink(this.schema, link);
      if (errors.length > 0) {
        console.warn(`Link ${link.id} validation:`, errors);
      }
    }

    return link;
  }

  // ==========================================================================
  // Dev-only: Stepper Mode
  // ==========================================================================

  async nextStep(): Promise<StepResult> {
    if (this.scriptIndex >= this.script.length) {
      const state = await this.fetchGraph();
      return {
        event: {
          type: 'health_update',
          timestamp: Date.now(),
          payload: {
            node_count: state.nodes.length,
            link_count: state.links.length,
            total_energy: 0,
            active_subentities: 0,
          },
        },
        state,
        has_more: false,
      };
    }

    const event = this.script[this.scriptIndex++];
    this.emit(event);

    const state = await this.fetchGraph();

    return {
      event,
      state,
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
