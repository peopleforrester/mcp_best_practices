<!-- ABOUTME: Re-verified readiness spike for the MCP 2026-07-28 stateless Release Candidate, checked 2026-06-25.
ABOUTME: Every claim is labeled NORMATIVE (published/draft spec) vs DRAFT/BLOG (RC blog or SEP only), with source URLs. -->

# MCP 2026-07-28 Release Candidate: Readiness Spike (verified 2026-06-25)

Verification date: 2026-06-25. Prior baseline: `docs/best-practice-verification-2026-06-24.md`
and `docs/research/version-currency-2026-06-23.md`. This spike re-checks the pending revision
against official sources only and flags what moved in the last day.

## How claims are labeled

- **NORMATIVE (published)**: text under a finalized dated path, for example
  `modelcontextprotocol.io/specification/2025-11-25/...`.
- **NORMATIVE (draft)**: full spec prose with MUST/SHOULD requirements served under
  `modelcontextprotocol.io/specification/draft/...`. The RC was locked 2026-05-21; this content
  finalizes and moves to a dated `2026-07-28` path on 2026-07-28. It is real spec text, not a
  proposal, but it lives on the `draft` path today.
- **DRAFT/BLOG**: the claim is sourced from the official RC blog post or a SEP number quoted there,
  not independently confirmed on a normative spec page in this pass.

The single biggest normativity fact: there is **no dated `2026-07-28` spec page yet**.
`modelcontextprotocol.io/specification/2026-07-28/basic/authorization` returns **404** (confirmed).
The current published version remains **2025-11-25**. Source:
[Versioning](https://modelcontextprotocol.io/specification/versioning) (NORMATIVE published).

---

# PART 1: Current state of the 2026-07-28 revision

## Status, date, lock (no slip)

- **Status: still a Release Candidate.** Not final. **DRAFT/BLOG** plus
  **NORMATIVE (published)** versioning page (current = 2025-11-25, RC content = draft path).
- **Target GA date: still 2026-07-28.** No slip observed. **DRAFT/BLOG.**
- **RC locked: 2026-05-21.** Spec text can still change during the ten-week validation window if a
  blocking issue surfaces. **DRAFT/BLOG.**
- **Validation window: 10 weeks** (2026-05-21 lock to 2026-07-28 final), for SDK maintainers and
  client implementers to validate against real workloads. Tier 1 SDKs are expected to ship support
  within this window. **DRAFT/BLOG** plus **NORMATIVE** SDK-tiers page (below).

Source: [RC blog post](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/),
[Versioning](https://modelcontextprotocol.io/specification/versioning).

**Locked vs still moving:** the change set and SEP list are locked as the RC. Exact spec wording can
still shift until 2026-07-28. The dated normative URLs do not exist yet, so anything built against the
RC today is building against the `draft` path, which can move.

## Stateless protocol core

| Item | Detail | Label |
|---|---|---|
| Remove `initialize`/`initialized` handshake | SEP-2575 | NORMATIVE (draft) for the lifecycle change; SEP number is DRAFT/BLOG |
| Remove `Mcp-Session-Id` header and protocol-level session | SEP-2567 | NORMATIVE (draft); SEP number DRAFT/BLOG |
| New `server/discover` method | Clients fetch the server's supported versions and capabilities on demand instead of at a one-time handshake | NORMATIVE (draft); also confirmed in a normative SDK implementation (Go v1.7.0-pre.1 release notes) |
| Per-request `_meta` | Protocol version, client info, and client capabilities travel in `_meta` on every request. Exact keys: `_meta.io.modelcontextprotocol/protocolVersion`, `_meta.io.modelcontextprotocol/clientInfo`, `_meta.io.modelcontextprotocol/clientCapabilities` | Key names confirmed by **both** the RC blog and the Go SDK v1.7.0-pre.1 release notes (a normative SDK). The clientInfo key `io.modelcontextprotocol/clientInfo` matches the blog. |
| Application state pattern | Removing the protocol session does not force a stateless app. Servers mint an explicit handle (for example `basket_id`) from a tool and the model passes it back as an ordinary argument | DRAFT/BLOG |
| Version negotiation header | `MCP-Protocol-Version: 2026-07-28` carried explicitly | DRAFT/BLOG (the published versioning page still documents the old handshake-based negotiation for 2025-11-25) |

Exact `_meta` key names are the highest-value detail and are corroborated by an official SDK, not the
blog alone. Source for the SDK corroboration:
[go-sdk releases, v1.7.0-pre.1 (2026-06-24)](https://github.com/modelcontextprotocol/go-sdk/releases).

## Transport changes

All transport SEP numbers and header names below are **DRAFT/BLOG** in this pass (sourced from the RC
blog; not independently re-opened on a draft transport spec page).

| Item | Detail | SEP |
|---|---|---|
| Routing headers | `Mcp-Method` for operation routing, `Mcp-Name` for resource identification, so load balancers route without body inspection | SEP-2243 |
| Caching metadata | `ttlMs` (freshness duration for list/resource responses) and `cacheScope` (cache safety across user boundaries) | SEP-2549 |
| Distributed tracing | W3C Trace Context propagated in `_meta` with keys `traceparent`, `tracestate`, `baggage` (OpenTelemetry-compatible) | SEP-414 |
| Server-to-client requests | Server-initiated requests only during active client request processing | SEP-2260 |
| Multi round-trip | `InputRequiredResult` with `inputRequests`, `inputResponses`, echoed `requestState`, replacing held-open SSE streams | SEP-2322 |

## Extensions framework, MCP Apps, Tasks

All **DRAFT/BLOG** in this pass.

- **Extensions framework (SEP-2133):** reverse-DNS identifiers, negotiated via an `extensions` map in
  capabilities, independently versioned, with delegated maintainers and `ext-*` repositories.
- **MCP Apps (SEP-1865):** server-rendered HTML UIs in sandboxed iframes; tool UI templates declared
  ahead of time; a JSON-RPC protocol for UI callbacks. Ships as an extension, not the core.
- **Tasks as an extension (SEP-2663):** stateless lifecycle. Server answers `tools/call` with a task
  handle; client drives via `tasks/get`, `tasks/update`, `tasks/cancel`; server-directed creation;
  `tasks/list` removed. Long-running work is an extension, not part of the stateless core.

## Authorization hardening (six SEPs): NORMATIVE (draft)

All six already have full normative spec prose (MUST/SHOULD) under `modelcontextprotocol.io/specification/draft/basic/authorization` and its sub-pages. The SEP numbers come from the RC blog. So: **requirement text is NORMATIVE (draft); the SEP-number attribution is DRAFT/BLOG.** SEP-837 was independently cross-confirmed as GitHub PR #837.

| # | Topic | SEP | One-line requirement | Normative source (draft) |
|---|---|---|---|---|
| 1 | Issuer identification, RFC 9207 | SEP-2468 | Clients MUST validate the `iss` parameter on authorization responses to mitigate mix-up attacks | `/draft/basic/authorization` (Authorization Response Validation) |
| 2 | OIDC `application_type` | SEP-837 | Clients MUST specify an appropriate `application_type` (`native` vs `web`) during Dynamic Client Registration | `/draft/basic/authorization/client-registration` |
| 3 | Credential binding | SEP-2352 | Clients MUST bind persisted client credentials to the issuing AS `issuer` and MUST re-register when the resource's AS changes | `/draft/basic/authorization/client-registration` (Authorization Server Binding) |
| 4 | Refresh-token guidance | SEP-2207 | Documents requesting refresh tokens (`refresh_token` grant, optional `offline_access`); AS retains discretion to issue | `/draft/basic/authorization` (Refresh Tokens) |
| 5 | Scope accumulation | SEP-2350 | Client SHOULD compute the union of prior and newly challenged scopes during step-up so servers stay stateless | `/draft/basic/authorization` (Scope Challenge Handling) |
| 6 | `.well-known` discovery | SEP-2351 | Uses the default `oauth-authorization-server` suffix; clients MUST probe OAuth and OIDC well-known endpoints in priority order | `/draft/basic/authorization/authorization-server-discovery` |

Sources:
[draft authorization](https://modelcontextprotocol.io/specification/draft/basic/authorization),
[client-registration](https://modelcontextprotocol.io/specification/draft/basic/authorization/client-registration),
[authorization-server-discovery](https://modelcontextprotocol.io/specification/draft/basic/authorization/authorization-server-discovery),
[PR #837](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/837).

## Deprecations: Roots, Sampling, Logging (NORMATIVE draft policy)

- **Feature lifecycle and deprecation policy (SEP-2577):** features are annotated Deprecated, document
  a migration path, and remain in the spec for **at least 12 months** (or at least 90 days under an
  expedited-removal exception) before becoming eligible for Removed. This policy is **NORMATIVE**: it
  is on the published versioning page and the community feature-lifecycle page, and a deprecated
  features registry exists at `/specification/draft/deprecated`.
- **Deprecated in the RC** (DRAFT/BLOG for the specific feature list and migration targets):
  - **Roots** to tool parameters, resource URIs, or server config.
  - **Sampling** to direct LLM provider API integration.
  - **Logging** to `stderr` for stdio and OpenTelemetry for structured logs.
- Removal window: minimum 12 months, so these remain functional across this release and every spec
  version within one year. **NORMATIVE** for the window length;
  the specific features are **DRAFT/BLOG**.

Sources: [Versioning](https://modelcontextprotocol.io/specification/versioning),
[feature lifecycle](https://modelcontextprotocol.io/community/feature-lifecycle),
[deprecated registry (draft)](https://modelcontextprotocol.io/specification/draft/deprecated),
[RC blog post](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/).

## JSON Schema 2020-12 and the error-code change

Both **DRAFT/BLOG** in this pass.

- **JSON Schema 2020-12 for tool I/O (SEP-2106):** tool `inputSchema` may use composition (`oneOf`,
  `anyOf`, `allOf`), conditionals, and `$ref`/`$defs`, with the root still `type: "object"`.
  `outputSchema` is unrestricted and `structuredContent` accepts any JSON value, not just objects.
  Implementations must not auto-dereference external `$ref` URIs and should bound schema depth and
  validation time.
- **Error code change (SEP-2164):** the "missing resource" error moves from `-32002` to `-32602`
  (the JSON-RPC standard Invalid Params code).

## Conformance suite and SDK tier gating

- **Conformance requirement (SEP-2484):** a Standards Track SEP cannot reach Final without a matching
  scenario in the conformance suite. **DRAFT/BLOG** for the SEP number; the **suite repository is real
  and active** (below).
- **Conformance suite: exists and is usable today.** Repo
  [modelcontextprotocol/conformance](https://github.com/modelcontextprotocol/conformance). A server can
  be tested against the RC now with `--spec-version 2026-07-28` (or `--spec-version draft`); runnable
  via `npx @modelcontextprotocol/conformance`, with a GitHub Action available. **NORMATIVE/official
  tooling.** A specific suite version number was reported but not reliably pinned; treat the suite as
  active rather than relying on a pinned number.
- **SDK tier system: NORMATIVE.** Defined at
  [modelcontextprotocol.io/community/sdk-tiers](https://modelcontextprotocol.io/community/sdk-tiers)
  and [docs/sdk](https://modelcontextprotocol.io/docs/sdk), established via PR #1777. Tier 1 must hit
  100% conformance and ship new protocol features before a new spec release. Tier 1: TypeScript,
  Python, C#, Go. Tier 2: Java, Rust (80% conformance, 6-month feature window). Tier 3 (experimental):
  Swift, Ruby, PHP, Kotlin.

---

# PART 2: SDK and tooling readiness (verified 2026-06-25)

All SDK facts below are **NORMATIVE/official** (PyPI, npm, NuGet, official GitHub release pages),
except FastMCP, which is a community project.

| SDK | Stable | RC / stateless support | Readiness |
|---|---|---|---|
| Python `mcp` (Tier 1) | v1.28.0 (2026-06-16), maintenance mode, recommended for production | v2 still **alpha**: latest v2.0.0a2 (2026-06-16). The **2026-06-30 beta has NOT shipped** (5 days out). v2 carries the stateless RC support; new model uses Streamable HTTP with `stateless_http=True, json_response=True` | Alpha only |
| FastMCP 3.x (community, not the MCP org) | v3.4.2 (2026-06-06) | **Does NOT yet support the 2026-07-28 stateless core.** Docs reference up to 2025-11-25 only. Its "stateless" is the older `stateless_http` transport mode, not the new protocol core (no `server/discover`, no per-request `_meta`) | Not RC-ready |
| TypeScript `@modelcontextprotocol/sdk` (Tier 1) | v1.29.0 | v2 is **pre-alpha** on `main` (v2.0.0-alpha tags); stable v2 anticipated Q3 2026 alongside the spec. RC support not yet confirmable from release notes | Pre-alpha |
| Go `go-sdk` (Tier 1) | v1.6.1 (2026-05-22) | **v1.7.0-pre.1 (2026-06-24) brings full `2026-07-28` support**: stateless model, per-request `_meta` (`io.modelcontextprotocol/{protocolVersion,clientInfo,clientCapabilities}`), `server/discover` RPC replacing the handshake, Streamable HTTP accepting 2026-07-28 only when `Stateless = true`. Backward compatible with 2025-11-25. Pre-release, no stable RC build | Most RC-ready |
| Rust `rmcp` (Tier 2) | rmcp-v1.8.0 (2026-06-23; note a source-breaking `Peer::peer_info()` change despite the minor bump) | No confirmed 2026-07-28 / stateless support in release notes. As Tier 2, it has a 6-month feature window, not the RC window | Not confirmable as RC-ready |
| C# `ModelContextProtocol` (Tier 1) | v1.4.0 (2026-06-04) | No confirmed stateless support in release notes. Tier 1, so expected within the validation window | Not confirmable yet |

Sources: [PyPI mcp](https://pypi.org/project/mcp/),
[python-sdk releases](https://github.com/modelcontextprotocol/python-sdk/releases),
[PyPI fastmcp](https://pypi.org/project/fastmcp/), [gofastmcp.com/updates](https://gofastmcp.com/updates),
[typescript-sdk releases](https://github.com/modelcontextprotocol/typescript-sdk/releases),
[go-sdk releases](https://github.com/modelcontextprotocol/go-sdk/releases),
[rust-sdk releases](https://github.com/modelcontextprotocol/rust-sdk/releases),
[csharp-sdk releases](https://github.com/modelcontextprotocol/csharp-sdk/releases).

---

# What changed since 2026-06-24

1. **Go SDK v1.7.0-pre.1 shipped 2026-06-24** (one day before this check) with **full `2026-07-28`
   stateless support**. This is the first official SDK to implement the RC core end to end, and it
   pins down the exact per-request `_meta` keys
   (`io.modelcontextprotocol/{protocolVersion,clientInfo,clientCapabilities}`) and the `server/discover`
   RPC. The 2026-06-24 baseline had Go at stable v1.6.1 with no RC build. NORMATIVE/official.
2. **No status slip.** RC still RC, still dated 2026-07-28, still locked 2026-05-21. Current published
   version still 2025-11-25. Unchanged from 2026-06-24.
3. **Python v2 beta still not shipped.** Still alpha (v2.0.0a2); the 2026-06-30 target is now 5 days
   out. Unchanged from 2026-06-24.
4. Rust rmcp v1.8.0 (2026-06-23) and C# v1.4.0 (2026-06-04) match the pins already recorded in the
   2026-06-24 baseline. No new drift.

---

# Flags: not confirmable from an official source in this pass

- **Most transport SEP numbers and Extensions/JSON-Schema/error-code SEP numbers** (2243, 2549, 414,
  2260, 2322, 2133, 1865, 2663, 2106, 2164, 2575, 2567, 2577, 2484) are taken from the RC blog text,
  not from individually opened SEP/PR pages. The underlying requirement text for the stateless core,
  authorization, and the deprecation policy is normative (draft); the SEP-to-feature attribution is
  blog-sourced. SEP-837 is the only one cross-confirmed at PR level.
- **FastMCP RC support:** no official 2026-07-28 mention found, so treat as unsupported.
- **Rust and C# RC readiness:** no release-note confirmation; do not assume RC-ready.
- **Conformance suite version number:** not reliably pinned; the suite is active and usable.
- **No dated `2026-07-28` spec URLs exist yet.** Anything built against the RC is building against the
  `draft` path, which can still move until 2026-07-28.
