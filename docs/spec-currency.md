<!-- ABOUTME: Spec-currency guide. 2026-07-28 is the current final MCP revision; 2025-11-25 is prior.
ABOUTME: The default examples run on stable FastMCP 3.4.x; a labeled preview rides FastMCP 4.0 beta. -->

# Spec Currency: `2026-07-28` (current) and `2025-11-25` (prior stable)

The current MCP revision is **`2026-07-28`**, which went **final on 2026-07-28** and replaces
`2025-11-25`. It is the largest revision since launch: the protocol core is now stateless, extensions
are first-class, and authorization is hardened.

Verified 2026-07-28 against primary sources:

- `blog.modelcontextprotocol.io/posts/2026-07-28/` announces the final release ("officially pushing
  the release button on the next version of the MCP specification, `2026-07-28`").
- The official Python `mcp` SDK is **2.0.0** (published 2026-07-28); a compatibility `1.29.0` shipped
  the same day for the prior line. The TypeScript SDK is `@modelcontextprotocol/sdk` 1.30.0.

## What the default examples run on, and why

The examples in this repo are built on **FastMCP** (the ergonomic Python framework), not the raw SDK.
As of 2026-07-28 the FastMCP lines resolve like this (confirmed by `uv`):

- **FastMCP 3.4.x → `mcp` 1.29**: implements through the `2025-11-25` semantics. **Stable.**
- **FastMCP 4.0 → `mcp` 2.0**: the `2026-07-28` line. **Pre-release (4.0.0b1 beta) at time of writing.**

So the default examples stay on **stable FastMCP 3.4.x**. This repo's standing rule is that a
pre-release SDK is never the default path. That means the working code presently implements through the
`2025-11-25` semantics while the spec itself has moved to `2026-07-28`. That gap is stated here plainly
rather than papered over, and it closes when FastMCP 4.0 reaches stable.

To keep the `2026-07-28` core from being merely described, a **labeled preview** package,
`01-fundamentals/server-python-preview/`, runs on the FastMCP 4.0 beta line (`mcp` 2.0) and
demonstrates the stateless handle pattern and the new cache hints. It is isolated from the default
examples and its lockfile is excluded from the cross-package version check.

## Why this matters for the portfolio

Sitting on the stable framework while demonstrating the current spec at the version boundary is itself
the credibility signal: it shows the protocol is understood as it changes, not frozen at one snapshot,
and it is honest about the difference between what the spec says and what the shipped framework
supports today. When FastMCP 4.0 ships stable, the default examples migrate and this guide is refreshed.

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

- **FastMCP 4.0 reaches stable.** Re-pin the default examples off 3.4.x, migrate them to the stateless
  core, and fold the preview package's approach into the mainline fundamentals server.
- The conformance suite (SEP-2484) publishes. Run the relevant examples against it.
- A revision after `2026-07-28` reaches Release Candidate. Re-verify every change above against the
  ratified text and add forward-compat preview code as the boundary demands.
