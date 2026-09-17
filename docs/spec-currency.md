<!-- ABOUTME: Spec-currency guide. 2026-07-28 is the current MCP revision; 2025-11-25 is prior.
ABOUTME: Every package runs on stable FastMCP 4.0 (mcp 2.x), which implements the current revision. -->

# Spec Currency: `2026-07-28` (current) and `2025-11-25` (prior)

The current MCP revision is **`2026-07-28`**, which went final on 2026-07-28 and replaces
`2025-11-25`. It is the largest revision since launch: the protocol core is now stateless, extensions
are first-class, and authorization is hardened.

Verified 2026-09-17 against primary sources:

- `blog.modelcontextprotocol.io` lists no revision after `2026-07-28`; it remains current.
- The Python `mcp` SDK is **2.2.0** and **FastMCP is 4.0.4** (PyPI). FastMCP 4.0.0 went stable on
  2026-08-31. The TypeScript SDK is `@modelcontextprotocol/sdk` 1.30.0 (npm).

## What the examples run on

The examples are built on **FastMCP** (the ergonomic Python framework) rather than the raw SDK. Every
package in this repo now runs on **stable FastMCP 4.0** (`mcp` 2.x), the line that implements
`2026-07-28`. Spec and implementation are aligned; there is no gap to declare.

This was not always true, and the history is the useful part. When `2026-07-28` went final, the only
FastMCP that implemented it was a 4.0 beta. This repo does not ship a pre-release SDK as its default
path, so for about a month the working code implemented the prior `2025-11-25` semantics while the
spec had moved on. That gap was stated here rather than papered over, and a single labeled package
demonstrated the new core against the beta. FastMCP 4.0 reached stable on 2026-08-31 and the whole
repo migrated. What is left of that package is
`01-fundamentals/server-python-stateless/`, now an ordinary example of the stateless shape.

The migration was cheaper than its headline suggested. Six of seven packages needed only a version
bump, because FastMCP 4.0 kept the decorator API source-compatible. Two things did change and are
worth knowing:

- **Server-initiated elicitation is gone.** `ctx.elicit` fails on a `2026-07-28` connection with
  "elicitation via server-initiated requests is unavailable", because a stateless request cannot hold
  a connection open waiting for a human (SEP-2260). The replacement is the multi-round-trip request
  (SEP-2322), and the tooling track's HITL gate is built on it: the tool returns an
  `InputRequiredResult` naming what it needs, the client answers, and the retry carries the answers
  plus a sealed `requestState`. See `03-tooling/src/mcp_tooling/hitl.py`.
- **`mcp` 2.x renamed its Python model fields to snake_case.** `ToolAnnotations(readOnlyHint=...)` is
  now `read_only_hint`, and `Tool.inputSchema` is `input_schema`. The wire format is unchanged, so
  these are still `readOnlyHint` and `inputSchema` on the JSON; only the Python attributes moved.

## Why this matters for the portfolio

Tracking a protocol across a breaking revision, in public, with the gap stated while it existed and
closed when the ecosystem caught up, is the credibility signal. It shows the protocol is understood as
it changes rather than frozen at one snapshot.

## Transport and revision history

Each revision is dated `YYYY-MM-DD` to mark the last backward-incompatible change. SEP-1400 proposes
moving to SemVer 2.0.0 but has not landed.

| Revision | Headline changes |
|---|---|
| `2024-11-05` | Launch. stdio + HTTP+SSE transports. |
| `2025-03-26` | Streamable HTTP replaces HTTP+SSE. OAuth 2.1. Tool annotations. JSON-RPC batching added. |
| `2025-06-18` | Structured tool output. Elicitation. OAuth Resource Server + mandatory Resource Indicators (RFC 8707). Batching removed. |
| `2025-11-25` | Prior stable. Tasks (experimental), enhanced sampling, elicitation, server-side agent loops, Client ID Metadata Documents, client security requirements, extensions system. |
| `2026-07-28` | **Current (final).** Stateless protocol core, first-class extensions, auth hardening, deprecations. See below. |

HTTP+SSE has been legacy since `2025-03-26`. Streamable HTTP is the production transport. Examples in
this repo use stdio for local/teaching cases and Streamable HTTP for anything network-facing.

## What `2026-07-28` changed from `2025-11-25`

Grouped by the work each change forces on a server or client author. SEP numbers are cited so a reader
can track each change upstream.

### 1. Stateless protocol core (the headline breaking change)

- The `initialize` / `initialized` handshake is removed (SEP-2575).
- The `Mcp-Session-Id` header and protocol-level sessions are removed (SEP-2567).
- Protocol version, client info, and client capabilities now travel in `_meta` on every request
  (`io.modelcontextprotocol/protocolVersion`, `clientInfo`, `clientCapabilities`).
- A new `server/discover` RPC advertises server capabilities in place of the handshake.
- Cross-call state moves to explicit server-minted handles passed as ordinary tool arguments. The
  canonical example is `open_cart` returning a `cart_id` that later calls pass back in (see the preview
  package and the architecture track's basket server).
- Server-to-client requests are restricted. A server may only issue one (for example, elicitation)
  while it is actively processing a client request (SEP-2260). Multi-round-trip requests return an
  `InputRequiredResult` carrying `requestState` instead of holding an SSE stream open (SEP-2322).

Migration impact: a stateless server can sit behind a plain round-robin load balancer with no shared
session store. Any example that relied on session-scoped state moves that state into a handle.

### 2. Routable, cacheable, traceable transport

- `Mcp-Method` and `Mcp-Name` headers are required on Streamable HTTP POST, so gateways and load
  balancers route without inspecting the body (SEP-2243). This is directly relevant to the security
  track's policy gateway.
- `ttlMs` and `cacheScope` appear on list/read results (SEP-2549). FastMCP 4.0 sets these at the server
  level; the preview package's `list_catalog` demonstrates a public-cacheable list.
- W3C Trace Context (`traceparent`, `tracestate`, `baggage`) is standardized in `_meta` for
  OpenTelemetry correlation (SEP-414).

### 3. Extensions become first-class

- Extensions get reverse-DNS IDs, dedicated `ext-*` repos, and independent versioning (SEP-2133).
- Two official extensions ship: **MCP Apps** (server-rendered sandboxed-iframe HTML UIs, SEP-1865) and
  **Tasks**, which graduates out of the experimental core into an extension. `tasks/list` is removed;
  the lifecycle is `tasks/get` / `tasks/update` / `tasks/cancel`.

### 4. Authorization hardening

Six SEPs tighten the OAuth model that has been in place since `2025-06-18`:

- Validate `iss` per RFC 9207 (SEP-2468).
- OIDC `application_type` in Dynamic Client Registration (SEP-837).
- Credential binding to issuer (SEP-2352).
- Refresh-token guidance (SEP-2207).
- Scope accumulation on step-up (SEP-2350).
- `.well-known` suffix clarification (SEP-2351).
- Migration from Dynamic Client Registration toward Client ID Metadata Documents (CIMD); DCR is
  formally deprecated through a backward-compatible transition.

The core rules carry forward unchanged and the security track teaches them: OAuth 2.1 + PKCE for remote
servers, servers act as OAuth Resource Servers, Resource Indicators (RFC 8707) are mandatory so tokens
are audience-bound, and token passthrough is forbidden (the confused-deputy mitigation).

### 5. Deprecations (annotation-only, with a removal window of at least 12 months)

Roots, Sampling, and Logging are deprecated (SEP-2577), plus the legacy HTTP+SSE transport. They still
function. Replacements:

- Roots: tool parameters and resource URIs.
- Sampling: direct LLM provider APIs.
- Logging: stderr plus OpenTelemetry.

Because the removal window is at least a year, the examples keep using these where natural and flag the
deprecation inline rather than rewriting around features that still work.

### 6. Schema and error-code changes

- Full JSON Schema 2020-12 for tool input and output schemas (SEP-2106).
- `structuredContent` may be any JSON value.
- The resource-not-found error code changes from `-32002` to `-32602` Invalid Params (SEP-2164).

### 7. Process: lifecycle and conformance

A formal feature lifecycle and deprecation policy plus a conformance suite gate Final status (SEP-2484).
An SDK tier system scores official SDKs against it; the four Tier 1 SDKs (TypeScript, Python, Go, C#)
shipped `2026-07-28` support, and Rust is in beta.

## Refresh triggers (revisit this guide when any of these happen)

- **A revision after `2026-07-28` reaches Release Candidate.** Re-verify every change above against
  the ratified text. If the shipped framework lags the spec again, say so here and demonstrate the new
  core in one labeled package rather than moving the default path onto a pre-release SDK. That is what
  was done between 2026-07-28 and 2026-08-31, and it is the pattern to repeat.
- The conformance suite (SEP-2484) publishes. Run the relevant examples against it.
- A FastMCP 5.0 line appears. Same rule: the default path waits for stable.

The "FastMCP 4.0 reaches stable" trigger fired on 2026-08-31 and was worked on 2026-09-17; the
reminder workflow now watches for the next major line.
