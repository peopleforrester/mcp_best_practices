<!-- ABOUTME: Research spike on MCP architecture patterns and the official MCP Registry for the Architecture track.
ABOUTME: Verified against official sources on 2026-06-24; stable spec 2025-11-25, RC 2026-07-28 (not final). -->

# MCP Architecture Patterns and the Official Registry

Spike date: 2026-06-24
Verified against: modelcontextprotocol.io, github.com/modelcontextprotocol/registry,
github.com/modelcontextprotocol/servers, gofastmcp.com, blog.modelcontextprotocol.io.
Stable spec: `2025-11-25`. Release candidate: `2026-07-28` (locked 2026-05-21; final
publishes 2026-07-28; NOT final at spike date).

## 1. Multi-server orchestration and composition (FastMCP 3.x)

FastMCP composes servers two ways: `import_server()` for a one-time static copy of
components, and `mount()` for a live link where the parent delegates to the child.

Source: https://gofastmcp.com/servers/composition

> "FastMCP supports composition through two methods: import_server for a one-time copy
> of components with prefixing (static composition), and mount for creating a live link
> where the main server delegates requests to the subserver (dynamic composition)."

> "When you mount a server, all its tools, resources, and prompts become available
> through the parent. The connection is live: add a tool to the child after mounting,
> and it's immediately visible through the parent."

Mounting, with the v3 `namespace` parameter for conflict avoidance:

```python
main = FastMCP("Main")
main.mount(weather, namespace="weather")
main.mount(calendar, namespace="calendar")

@dynamic_server.tool
def added_later() -> str:
    return "Added after mounting!"
```

External / remote servers mount through a proxy:

```python
from fastmcp.server import create_proxy

mcp.mount(create_proxy("http://api.example.com/mcp"), namespace="api")
mcp.mount(create_proxy("./my_server.py"), namespace="local")
```

Namespacing (new in v3.0.0) rewrites component names so two children can expose the same
tool name: a tool `get_data` mounted under `namespace="weather"` is reached as
`weather_get_data`, and a resource `data://info` becomes `data://api/info`. When names
still collide, "the most recently mounted server takes precedence."

DRAFT / VERIFY: the exact `import_server()` signature and whether it is awaited could not
be confirmed verbatim. Repeated renders of the composition page returned only the
`mount()` code blocks. The prose above ("import_server for a one-time copy ... with
prefixing") is confirmed; the concrete call line is not. FastMCP v2 used a `prefix=`
parameter; v3 renders show `namespace=`. Treat `namespace=` as the v3 parameter and
re-pull the page source before publishing a code sample for `import_server()`.

Latency note (confirmed): "HTTP-based mounted servers can introduce significant latency
(300-400ms vs 1-2ms for local tools) ... importing tools via import_server() may be more
appropriate as it copies components once at startup rather than delegating requests at
runtime."

How a host aggregates servers: a host process holds one MCP client per connected server
(the spec's host/client/server split, https://modelcontextprotocol.io/specification/2025-11-25).
FastMCP composition is the server-side analogue: one parent server presents many children
as a single surface, so the host sees one connection while the parent fans out internally.

## 2. Stateful (2025-11-25) vs stateless (RC 2026-07-28)

### 2025-11-25: sessions via `Mcp-Session-Id`

Source: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports

> "A server using the Streamable HTTP transport MAY assign a session ID at initialization
> time, by including it in an `MCP-Session-Id` header on the HTTP response containing the
> `InitializeResult`."

> "If an `MCP-Session-Id` is returned by the server during initialization, clients using
> the Streamable HTTP transport MUST include it in the `MCP-Session-Id` header on all of
> their subsequent HTTP requests."

Session rules (verbatim points):
- Session ID "SHOULD be globally unique and cryptographically secure" and "MUST only
  contain visible ASCII characters (ranging from 0x21 to 0x7E)."
- "Servers that require a session ID SHOULD respond to requests without an
  `MCP-Session-Id` header (other than initialization) with HTTP 400 Bad Request."
- "The server MAY terminate the session at any time, after which it MUST respond to
  requests containing that session ID with HTTP 404 Not Found."
- On 404 the client "MUST start a new session by sending a new `InitializeRequest`."
- Clients done with a session "SHOULD send an HTTP DELETE to the MCP endpoint with the
  `MCP-Session-Id` header, to explicitly terminate the session."

Header example from the spec sequence diagram: `MCP-Session-Id: 1868a90c...`

### RC 2026-07-28: stateless core, state via server-minted handles

Source: https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/

> "The `initialize`/`initialized` handshake is removed" and "The `Mcp-Session-Id` header
> and the protocol-level session that came with it are also removed."

> "any MCP request can land on any server instance, and the sticky routing and shared
> session stores that horizontal deployments needed before are no longer required at the
> protocol layer."

State moves into the application layer as an explicit handle:

> "Servers that need to carry state across calls can do what HTTP APIs have always done:
> mint an explicit handle (a `basket_id`, a `browser_id`) from a tool and have the model
> pass it back as an ordinary argument on later calls."

Concrete handle pattern (from the blog's flow description):

> "the model calls create_basket, the MCP server returns a basket_id, and the model
> passes that same basket_id back as an argument to add_item."

Sketch of the handle pattern:

```python
@mcp.tool
def create_basket() -> dict:
    basket_id = new_id()
    store.create(basket_id)
    return {"basket_id": basket_id}

@mcp.tool
def add_item(basket_id: str, sku: str, qty: int) -> dict:
    store.add(basket_id, sku, qty)        # basket_id arrives as a normal tool argument
    return {"basket_id": basket_id, "items": store.count(basket_id)}
```

Status: release candidate "locked as of May 21, 2026. The final specification will be
published on July 28, 2026." NOT final. The Tasks feature shipped experimentally in
`2025-11-25` and in the RC moves to an extension (the new Extensions framework: reverse-DNS
IDs, negotiated through an `extensions` capability map, versioned independently).

## 3. The official MCP Registry

Source: https://github.com/modelcontextprotocol/registry

Status (confirmed): preview.

> "The registry has launched in preview ... this is still a preview release and breaking
> changes or data resets may occur."

> "The Registry API has entered an API freeze (v0.1) ... the API will remain stable with
> no breaking changes." (dated 2025-10-24)

So: API surface is frozen at v0.1, but the service itself is still labeled preview, not
GA. The production base URL is `registry.modelcontextprotocol.io` with staging and local
environments alongside.

### Self-hosting

Pre-built image (GitHub Container Registry):

```bash
docker run -p 8080:8080 ghcr.io/modelcontextprotocol/registry:latest
```

Tags include `latest`, `main` (continuous), and `main-<date>-<sha>` (development).

Local build requires `ko` and Go 1.24.x, backed by PostgreSQL:

```bash
make dev-compose
```

> "This starts the registry at `localhost:8080` with PostgreSQL."
> "The database uses ephemeral storage and is reset each time you restart the containers,
> ensuring a clean state for development and testing."

### `server.json` schema essentials

Source: https://github.com/modelcontextprotocol/registry (server-json reference)

Required: `name` (reverse-DNS, e.g. `io.modelcontextprotocol/filesystem`), `description`,
`version`, and at least one of `packages` or `remotes`. The `$schema` points at a dated
schema URL.

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.modelcontextprotocol.anonymous/brave-search",
  "description": "MCP server for Brave Search API integration",
  "title": "Brave Search",
  "websiteUrl": "https://anonymous.modelcontextprotocol.io/examples",
  "repository": {
    "url": "https://github.com/modelcontextprotocol/servers",
    "source": "github"
  },
  "version": "1.0.2",
  "packages": [
    {
      "registryType": "npm",
      "registryBaseUrl": "https://registry.npmjs.org",
      "identifier": "@modelcontextprotocol/server-brave-search",
      "version": "1.0.2",
      "transport": {
        "type": "stdio"
      },
      "environmentVariables": [
        {
          "name": "BRAVE_API_KEY",
          "description": "Brave Search API Key",
          "isRequired": true,
          "isSecret": true
        }
      ]
    }
  ]
}
```

`packages` describes locally-installed deployments (npm, pypi, etc.); `remotes` describes
cloud-hosted HTTP endpoints. A server may list either or both.

### Server card: `.well-known` discovery (SEP-1649 / SEP-2127)

DRAFT / unpublished. SEP-2127 ("MCP Server Cards - HTTP Server Discovery via .well-known")
supersedes SEP-1649 and is in Draft status. It is NOT in the stable `2025-11-25` spec.

Source: https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127 and the
SEP file under `seps/2127-mcp-server-cards.md`.

Purpose: a pre-connect discovery document so a client can read name, version, protocol
versions, capabilities, and primitive descriptions before opening a connection.

Approximate card shape (DRAFT, fields subject to change):

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json",
  "name": "io.modelcontextprotocol.anonymous/brave-search",
  "version": "1.0.2",
  "description": "MCP server for Brave Search API integration",
  "title": "Brave Search",
  "websiteUrl": "https://anonymous.modelcontextprotocol.io/examples",
  "repository": {},
  "icons": [],
  "remotes": [],
  "_meta": {}
}
```

CONFLICT / VERIFY: sources disagree on the exact well-known path. One source reports
`/.well-known/mcp/server-card.json` (with the SEP-1649/2127 "consensus"); the SEP file
render reports `/.well-known/mcp-server-card` with optional sub-paths
`/.well-known/mcp-server-card/{server-name}`. Resolve against the merged SEP text before
quoting a path. Either way the file is not part of the stable spec yet.

## 4. Reference servers: maintained vs archived

Source: https://github.com/modelcontextprotocol/servers

Seven maintained reference servers ("These servers aim to demonstrate MCP features and
the official SDKs"):

1. Everything (reference/test server with prompts, resources, and tools)
2. Fetch (web content fetching and conversion)
3. Filesystem (secure file operations with access controls)
4. Git (read, search, and manipulate repositories)
5. Memory (knowledge-graph-based persistent memory)
6. Sequential Thinking (dynamic problem-solving through thought sequences)
7. Time (time and timezone conversion)

Archived (moved to `servers-archived`): AWS KB Retrieval, Brave Search, EverArt, GitHub,
GitLab, Google Drive, Google Maps, PostgreSQL, Puppeteer, Redis, Sentry, Slack, SQLite.
Most archived entries were first-party demos for services that now ship their own
maintained MCP servers.

## Open items to verify before publishing

- `import_server()` exact signature and async/await behavior in FastMCP v3 (DRAFT).
- v3 parameter name: confirmed `namespace=` in current renders; v2 used `prefix=`.
- SEP-2127 well-known path (two conflicting forms above).
- Registry GA date: still preview at spike date; no GA date published.
