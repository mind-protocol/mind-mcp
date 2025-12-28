# @mind-protocol/connectome

Graph visualization components for Mind Protocol.

## Overview

Connectome provides React components for visualizing and interacting with Mind Protocol graphs. It's used by:

- **mind-mcp dev tool**: Local debugging and visualization (`mind connectome`)
- **mind-platform**: Public web UI at platform.mindprotocol.ai

## Installation

```bash
npm install @mind-protocol/connectome
```

## Usage

### Basic Setup

```tsx
import { ConnectomeCanvas, NodeKit, EdgeKit } from '@mind-protocol/connectome';
import { LocalAdapter } from '@mind-protocol/connectome/adapters/local';
// or
import { RemoteAdapter } from '@mind-protocol/connectome/adapters/remote';

// For local development (mind-mcp)
const adapter = new LocalAdapter({
  neo4j_uri: 'bolt://localhost:7687',
  graph_name: 'my-project',
});

// For platform (mind-platform)
const adapter = new RemoteAdapter({
  api_url: 'https://api.mindprotocol.ai',
  ws_url: 'wss://api.mindprotocol.ai/ws',
});

function App() {
  return (
    <ConnectomeCanvas adapter={adapter}>
      <NodeKit />
      <EdgeKit />
    </ConnectomeCanvas>
  );
}
```

### Adapter Interface

Both adapters implement the same interface:

```typescript
interface ConnectomeAdapter {
  getNodes(): Promise<Node[]>;
  getLinks(): Promise<Link[]>;
  search(query: string, opts?: SearchOpts): Promise<SearchResult[]>;
  subscribe(handler: (event: FlowEvent) => void): Unsubscribe;

  // Dev-only (LocalAdapter)
  nextStep?(): Promise<StepResult>;
  restart?(): void;
  loadScript?(events: FlowEvent[]): void;

  disconnect(): void;
}
```

### Dev Tool Features

The LocalAdapter supports additional features for debugging:

```tsx
// Stepper mode - step through events one at a time
const result = await adapter.nextStep();

// Restart playback
adapter.restart();

// Load a recorded script
adapter.loadScript(recordedEvents);
```

## Architecture

```
connectome/
├── core/
│   ├── components/     # React components (NodeKit, EdgeKit, etc.)
│   ├── types/          # TypeScript types
│   └── styles/         # CSS
├── adapters/
│   ├── local.ts        # LocalAdapter (Neo4j)
│   └── remote.ts       # RemoteAdapter (L4 API)
├── lib/
│   ├── state-store.ts  # Zustand store
│   └── runtime-engine.ts
└── server/             # CLI dev server
```

## Development

Components are migrated from `mind-platform/app/connectome/components/`.

See `.mind/state/SYNC_Project_State.md` for current migration status.
