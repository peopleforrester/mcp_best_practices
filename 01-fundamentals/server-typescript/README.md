<!-- ABOUTME: Fundamentals TypeScript package: an MCP hello server mirroring the Python one.
ABOUTME: Built on @modelcontextprotocol/sdk v1.29; tested via the SDK in-memory transport pair. -->

# Fundamentals (TypeScript, @modelcontextprotocol/sdk)

`src/hello.ts` builds an `McpServer` with the same three primitives as the Python hello server: an
`echo` tool (Zod raw-shape input), a templated `greeting://{name}` resource, and a `summarize` prompt.

`test/hello.test.ts` connects a `Client` over `InMemoryTransport.createLinkedPair()` and asserts
capability negotiation, the tool, the resource, and the prompt.

The SDK is pinned to `^1.29` (stable v1; v2 is pre-alpha on the repo `main`). Zod is pinned to v3 to
match the SDK's schema handling. The high-level classes import from deep paths under the SDK's `./*`
export wildcard (`@modelcontextprotocol/sdk/server/mcp.js`, `.../client/index.js`, `.../inMemory.js`).

```bash
pnpm install
pnpm test       # vitest
pnpm typecheck  # tsc --noEmit
```
