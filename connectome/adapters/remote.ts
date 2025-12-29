/**
 * RemoteAdapter
 *
 * Connects Connectome to the L4 API via GraphQL and WebSocket.
 * Used by mind-platform for the web UI.
 *
 * Features:
 * - GraphQL queries for nodes and links
 * - WebSocket subscription for realtime events
 * - No stepper mode (read-only public view)
 */

import type {
  ConnectomeAdapter,
  RemoteAdapterConfig,
  Node,
  Link,
  SearchOpts,
  SearchResult,
  FlowEvent,
  GraphState,
  Unsubscribe,
  Schema,
} from '../core/types';

export class RemoteAdapter implements ConnectomeAdapter {
  private config: RemoteAdapterConfig;
  private ws: WebSocket | null = null;
  private subscribers: Set<(event: FlowEvent) => void> = new Set();

  constructor(config: RemoteAdapterConfig) {
    this.config = config;
  }

  /**
   * Get schema - RemoteAdapter doesn't load local schema
   */
  getSchema(): Schema | null {
    return null;
  }

  /**
   * Fetch full graph (nodes + links)
   */
  async fetchGraph(): Promise<GraphState> {
    const [nodes, links] = await Promise.all([
      this.getNodes(),
      this.getLinks(),
    ]);
    return { nodes, links };
  }

  async getNodes(): Promise<Node[]> {
    // TODO: Implement via GraphQL query to L4 API
    const response = await fetch(`${this.config.api_url}/graphql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.auth_token && { Authorization: `Bearer ${this.config.auth_token}` }),
      },
      body: JSON.stringify({
        query: `
          query GetNodes {
            nodes {
              id
              name
              node_type
              type
              weight
              energy
              synthesis
              content
            }
          }
        `,
      }),
    });

    const data = await response.json();
    return data?.data?.nodes || [];
  }

  async getLinks(): Promise<Link[]> {
    // TODO: Implement via GraphQL query to L4 API
    const response = await fetch(`${this.config.api_url}/graphql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.auth_token && { Authorization: `Bearer ${this.config.auth_token}` }),
      },
      body: JSON.stringify({
        query: `
          query GetLinks {
            links {
              id
              node_a
              node_b
              weight
              energy
              polarity
              hierarchy
              permanence
              joy_sadness
              trust_disgust
              fear_anger
              surprise_anticipation
              synthesis
            }
          }
        `,
      }),
    });

    const data = await response.json();
    return data?.data?.links || [];
  }

  async search(query: string, opts?: SearchOpts): Promise<SearchResult[]> {
    const response = await fetch(`${this.config.api_url}/graphql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.auth_token && { Authorization: `Bearer ${this.config.auth_token}` }),
      },
      body: JSON.stringify({
        query: `
          query Search($query: String!, $opts: SearchOptsInput) {
            search(query: $query, opts: $opts) {
              node {
                id
                name
                node_type
                synthesis
              }
              score
            }
          }
        `,
        variables: { query, opts },
      }),
    });

    const data = await response.json();
    return data?.data?.search || [];
  }

  subscribe(handler: (event: FlowEvent) => void): Unsubscribe {
    this.subscribers.add(handler);

    // Connect WebSocket if not already connected
    if (!this.ws && this.config.ws_url) {
      this.connectWebSocket();
    }

    return () => {
      this.subscribers.delete(handler);
      if (this.subscribers.size === 0 && this.ws) {
        this.ws.close();
        this.ws = null;
      }
    };
  }

  private connectWebSocket(): void {
    if (!this.config.ws_url) return;

    this.ws = new WebSocket(this.config.ws_url);

    this.ws.onmessage = (event) => {
      try {
        const flowEvent: FlowEvent = JSON.parse(event.data);
        for (const handler of this.subscribers) {
          handler(flowEvent);
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      this.ws = null;
      // Reconnect after delay if there are still subscribers
      if (this.subscribers.size > 0) {
        setTimeout(() => this.connectWebSocket(), 5000);
      }
    };
  }

  // RemoteAdapter doesn't support stepper mode
  // nextStep, restart, loadScript are not implemented

  disconnect(): void {
    this.subscribers.clear();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
