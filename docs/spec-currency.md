<!-- ABOUTME: Migration guide between MCP spec 2025-11-25 (stable baseline) and the 2026-07-28 RC.
ABOUTME: The repo builds on the stable revision; RC-targeted code is labeled preview. -->

# Spec Currency: `2025-11-25` to `2026-07-28` RC

This repository builds against MCP **`2025-11-25`** (the latest stable, ratified revision). Every
example runs and passes on that baseline. Code that targets the **`2026-07-28`** revision is a
**Release Candidate** as of this writing and is always labeled `preview`, never the default.

Verified 2026-06-23 (see `research/version-currency-2026-06-23.md`):

- `2025-11-25` is the latest stable revision; `modelcontextprotocol.io/specification` resolves to it.
- `2026-07-28` is a Release Candidate: locked 2026-05-21, scheduled final 2026-07-28, with a
  10-week SDK-validation window. It is the largest revision since launch and contains breaking
  changes. Treat everything in it as subject to change until it goes final.

## Why this matters for the portfolio

Building on the stable revision while documenting the path to the RC is itself the credibility
signal. It shows the protocol is understood at the version boundary, not just at one snapshot. When
the RC goes final on 2026-07-28 (and when Python SDK v2 and TypeScript SDK v2 land alongside it),
this guide and every example get refreshed. That refresh is a tracked benchmark, not an afterthought.

## Transport and revision history

Each revision is dated `YYYY-MM-DD` to mark the last backward-incompatible change. SEP-1400 proposes
moving to SemVer 2.0.0 but has not landed.

| Revision | Headline changes |
|---|---|
| `2024-11-05` | Launch. stdio + HTTP+SSE transports. |
| `2025-03-26` | Streamable HTTP replaces HTTP+SSE. OAuth 2.1. Tool annotations. JSON-RPC batching added. |
| `2025-06-18` | Structured tool output. Elicitation. OAuth Resource Server + mandatory Resource Indicators (RFC 8707). Batching removed. |
| `2025-11-25` | **Current stable.** Tasks (experimental), enhanced sampling, elicitation, server-side agent loops, Client ID Metadata Documents, client security requirements, extensions system. |
| `2026-07-28` | **Release Candidate.** Stateless protocol core, first-class extensions, auth hardening, deprecations. See below. |

HTTP+SSE has been legacy since `2025-03-26`. Streamable HTTP is the production transport. Examples
in this repo use stdio for local/teaching cases and Streamable HTTP for anything network-facing.

## What changes in the `2026-07-28` RC

Grouped by the work each change forces on a server or client author. SEP numbers are cited so a
reader can track each change upstream.

### 1. Stateless protocol core (the headline breaking change)

- The `initialize` / `initialized` handshake is removed (SEP-2575).
- The `Mcp-Session-Id` header and protocol-level sessions are removed (SEP-2567).
- Protocol version, client info, and client capabilities now travel in `_meta` on every request
  (`io.modelcontextprotocol/protocolVersion`, `clientInfo`, `clientCapabilities`).
- A new `server/discover` RPC advertises server capabilities in place of the handshake.
- Cross-call state moves to explicit server-minted handles passed as ordinary tool arguments. The
  canonical example is `create_basket` returning a `basket_id` that later calls pass back in.
- Server-to-client requests are restricted. A server may only issue one (for example, elicitation)
  while it is actively processing a client request (SEP-2260). Multi-round-trip requests return an
  `InputRequiredResult` carrying `requestState` instead of holding an SSE stream open (SEP-2322).

Migration impact: a stateless server can sit behind a plain round-robin load balancer with no shared
session store. Any example that relied on session-scoped state must move that state into a handle.

### 2. Routable, cacheable, traceable transport

- `Mcp-Method` and `Mcp-Name` headers are required on Streamable HTTP POST, so gateways and load
  balancers route without inspecting the body (SEP-2243). This is directly relevant to the security
  track's policy gateway.
- `ttlMs` and `cacheScope` appear on list/read results (SEP-2549).
- W3C Trace Context (`traceparent`, `tracestate`, `baggage`) is standardized in `_meta` for
  OpenTelemetry correlation (SEP-414).

### 3. Extensions become first-class

- Extensions get reverse-DNS IDs, dedicated `ext-*` repos, and independent versioning (SEP-2133).
- Two official extensions ship: **MCP Apps** (server-rendered sandboxed-iframe HTML UIs, SEP-1865)
  and **Tasks**, which graduates out of the experimental core into an extension. `tasks/list` is
  removed; the lifecycle is `tasks/get` / `tasks/update` / `tasks/cancel`.

### 4. Authorization hardening

Six SEPs tighten the OAuth model that has been in place since `2025-06-18`:

- Validate `iss` per RFC 9207 (SEP-2468).
- OIDC `application_type` in Dynamic Client Registration (SEP-837).
- Credential binding to issuer (SEP-2352).
- Refresh-token guidance (SEP-2207).
- Scope accumulation on step-up (SEP-2350).
- `.well-known` suffix clarification (SEP-2351).

The core rules carry forward unchanged and the security track teaches them on the stable baseline:
OAuth 2.1 + PKCE for remote servers, servers act as OAuth Resource Servers, Resource Indicators
(RFC 8707) are mandatory so tokens are audience-bound, and token passthrough is forbidden (the
confused-deputy mitigation).

### 5. Deprecations (annotation-only, with a removal window of at least 12 months)

Roots, Sampling, and Logging are deprecated (SEP-2577). They still function. Replacements:

- Roots: tool parameters and resource URIs.
- Sampling: direct LLM provider APIs.
- Logging: stderr plus OpenTelemetry.

Because the removal window is at least a year, the stable examples keep using these where natural and
flag the deprecation inline rather than rewriting around features that still work.

### 6. Schema and error-code changes

- Full JSON Schema 2020-12 for tool input and output schemas (SEP-2106).
- `structuredContent` may be any JSON value.
- The resource-not-found error code changes from `-32002` to `-32602` Invalid Params (SEP-2164).

### 7. Process: lifecycle and conformance

A formal feature lifecycle and deprecation policy plus a conformance suite now gate Final status
(SEP-2484). An SDK tier system scores official SDKs against it; Tier 1 SDKs are expected to support
new revisions within the 10-week RC window.

## How this repo handles both revisions

1. **Default to stable.** Unmarked code targets `2025-11-25` and is expected to pass there.
2. **Label RC code as preview.** Anything that depends on a `2026-07-28` behavior (stateless core,
   the handle pattern, the new transport headers, the Tasks extension) lives behind a clear
   `preview` marker in its directory and README, and is never wired as the default path.
3. **Teach the boundary explicitly.** The Fundamentals track contrasts the stable session handshake
   against the RC stateless single-request form. The Architecture track demonstrates the handle
   pattern (RC) next to session state (stable) so the difference is concrete, not described.
4. **Pin SDKs to stable lines.** Python `mcp>=1.28,<2`, TypeScript SDK `^1.29`. SDK v2 lines align
   with the RC and are pre-stable; they are not used for the default examples yet.

## Refresh triggers (revisit this guide when any of these happen)

- `2026-07-28` goes final (scheduled 2026-07-28). Re-verify every change above against the ratified
  text, since RC details can shift.
- Python SDK v2 reaches stable (targeted around 2026-07-27) and TypeScript SDK v2 lands. Re-pin and
  re-run all examples.
- The conformance suite (SEP-2484) publishes. Run the relevant examples against it.

Until those land, the stable baseline is the source of truth and the RC content here is forward-looking.
