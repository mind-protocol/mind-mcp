/**
 * Connectome Adapters
 *
 * Two adapters for different use cases:
 * - LocalAdapter: For mind-mcp dev tool (connects to local Neo4j)
 * - RemoteAdapter: For mind-platform (connects to L4 API)
 */

export { LocalAdapter } from './local';
export { RemoteAdapter } from './remote';
