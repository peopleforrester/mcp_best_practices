<!-- ABOUTME: Guidebook for the Fundamentals track: MCP primitives in Python and TypeScript.
ABOUTME: Reads top to bottom; each section points at runnable, tested code. -->

# Fundamentals Guidebook

The primitives, shown twice (Python and TypeScript) so the concepts stand apart from any one SDK.
Built against the stable MCP `2025-11-25` spec; the `2026-07-28` RC stateless changes are covered in
the Architecture track and `docs/spec-currency.md`.

## What MCP gives a server

Three primitives, each demonstrated in the hello server:

- **Tools**: typed, callable functions the model can invoke (`echo`).
- **Resources**: read-only data addressed by a URI, here a templated one (`greeting://{name}`).
- **Prompts**: reusable, parameterized prompt templates (`summarize`).

A client connects, negotiates capabilities, then lists and calls these. The tests drive exactly that
flow over an in-memory transport, so they are conformance-style: they assert the protocol surface,
not just the function output.

## Python (`server-python/`, FastMCP)

- `hello.py`: `build_hello_server()` registers the three primitives with decorators (`@mcp.tool`,
  `@mcp.resource`, `@mcp.prompt`).
- `catalog.py`: a non-trivial server. `search_items` is search-focused and paginated (a `cursor` and a
  `next_cursor`, `None` on the last page), reports progress through the `Context`, and returns a typed
  `SearchPage`. `get_item` returns a typed `ItemView` and raises `ToolError` on an unknown id. This is
  the effective-tool-design guidance from the Tooling track applied: search over list-everything,
  structured output, human-meaningful fields.
- Tests use the FastMCP in-memory `Client`. Note: `result.data` hydrates structured output into a
  model object, while `result.structured_content` is the plain dict, which is what the tests assert on.

## TypeScript (`server-typescript/`, @modelcontextprotocol/sdk v1.29)

- `src/hello.ts`: the same three primitives via `McpServer.registerTool/registerResource/registerPrompt`.
  Tool input schemas are Zod raw shapes (a plain object of Zod validators, not a wrapped `z.object`).
- `test/hello.test.ts`: connects a `Client` to the server through `InMemoryTransport.createLinkedPair()`
  and asserts the same behavior as the Python suite. Run with `pnpm test`; type-check with `pnpm typecheck`.

A verification note worth keeping: the published SDK ships a `./*` export wildcard, so the high-level
classes import from deep paths (`@modelcontextprotocol/sdk/server/mcp.js`, `.../inMemory.js`). The
package was probed directly to confirm those paths rather than trusting documentation alone.

## Run it

```bash
cd 01-fundamentals/server-python      && uv run pytest -q
cd 01-fundamentals/server-typescript  && pnpm install && pnpm test && pnpm typecheck
```

## Transports

Both servers are transport-agnostic builders. In tests they run over an in-memory transport. In
deployment, a local server uses stdio and a remote server uses Streamable HTTP (HTTP+SSE has been
legacy since `2025-03-26`). The Architecture track shows the stateful-session and stateless-handle
forms of an HTTP server.
