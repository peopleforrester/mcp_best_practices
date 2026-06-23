<!-- ABOUTME: Foundational research report and build plan for the MCP SME portfolio monorepo.
ABOUTME: Ingested verbatim June 2026; version-sensitive claims tracked in version-currency-*.md. -->

# MCP SME Portfolio Monorepo: Research Report & Build Plan (June 2026)

> **Source note:** Ingested 2026-06-23 as the founding specification for this repo.
> Version-sensitive claims (spec revision, SDK versions, tooling status) are flagged in
> the report's own Caveats and tracked in `docs/research/version-currency-2026-06-23.md`.
> Treat that file as the live source of truth where it diverges from this report.

## TL;DR
- **Target the latest STABLE spec, `2025-11-25`, as your baseline, but architect every example to be forward-compatible with the `2026-07-28` release candidate** (final ships July 28, 2026), whose headline change is a stateless protocol core that removes the `initialize` handshake and `Mcp-Session-Id` header. Building against both — and documenting the migration — is itself a credible SME signal.
- **Build a polyglot monorepo with five competency directories, each containing working code + a guidebook + a Reveal.js deck**, anchored by a security competency (the user's lane) that ships an original policy-enforcing MCP gateway, a cosign-signed tool registry, and original threat models mapped to the OWASP MCP Top 10 and the NSA's May 2026 MCP guidance.
- **Prioritize original, buildable code over prose**: idiomatic Python (FastMCP) and TypeScript servers, an original gateway/guardrail proxy, conformance-style tests, and GitHub Actions CI with cosign signing establish authorship far more credibly than forked reference servers or diagrams.

## Key Findings

### Spec currency (the critical first task)
- **Latest stable/ratified revision: `2025-11-25`.** The official spec page (modelcontextprotocol.io/specification) redirects here and labels it latest. It shipped the largest change set since launch: async Tasks (experimental), enhanced sampling, elicitation, server-side agent loops, Client ID Metadata Documents, client security requirements, and the extensions system.
- **Next revision: `2026-07-28`, currently a Release Candidate (locked May 21, 2026; final July 28, 2026).** This matches the user's ~July 28, 2026 belief exactly. It is the largest revision since launch and contains breaking changes. Authored by lead maintainers David Soria Parra and Den Delimarsky.
- **What's in the `2026-07-28` RC (DRAFT/in-flight, NOT GA):**
  - **Stateless protocol core** — removes the `initialize`/`initialized` handshake (SEP-2575) and the `Mcp-Session-Id` header / protocol-level sessions (SEP-2567). Protocol version, client info, and capabilities now travel in `_meta` on every request (`io.modelcontextprotocol/protocolVersion`, `clientInfo`, `clientCapabilities`); a new `server/discover` RPC advertises capabilities. Cross-call state is handled via explicit server-minted handles (e.g., `basket_id`) passed as ordinary tool arguments. Server-to-client requests (e.g., elicitation) are restructured: a server may only issue them while actively processing a client request (SEP-2260), and multi-round-trip requests now return an `InputRequiredResult` with `requestState` rather than holding an SSE stream open (SEP-2322).
  - **Routable/cacheable/traceable transport** — required `Mcp-Method` and `Mcp-Name` headers on Streamable HTTP POST so gateways/load balancers route without inspecting the body (SEP-2243); `ttlMs` + `cacheScope` on list/read results (SEP-2549); W3C Trace Context (`traceparent`/`tracestate`/`baggage`) standardized in `_meta` for OpenTelemetry correlation (SEP-414).
  - **Extensions become first-class** (SEP-2133; reverse-DNS IDs, `ext-*` repos, independent versioning). Two official extensions: **MCP Apps** (SEP-1865; server-rendered sandboxed-iframe HTML UIs) and **Tasks** (graduated from experimental core to an extension; `tasks/list` removed; lifecycle `tasks/get`/`tasks/update`/`tasks/cancel`).
  - **Authorization hardening** — six SEPs: validate `iss` per RFC 9207 (SEP-2468), OIDC `application_type` in Dynamic Client Registration (SEP-837), credential binding to issuer (SEP-2352), refresh-token guidance (SEP-2207), scope accumulation on step-up (SEP-2350), `.well-known` suffix clarification (SEP-2351).
  - **Roots, Sampling, and Logging are DEPRECATED** (SEP-2577; annotation-only, ≥12-month removal window). Replacements: tool parameters/resource URIs (Roots), direct LLM provider APIs (Sampling), stderr + OpenTelemetry (Logging).
  - **Full JSON Schema 2020-12 for tool input/output schemas** (SEP-2106); `structuredContent` can be any JSON value; resource-not-found error code changes from `-32002` to `-32602` Invalid Params (SEP-2164).
  - Formal **feature lifecycle/deprecation policy** + conformance suite gating Final status (SEP-2484); SDK tier system scoring official SDKs against it.
- **Transport history to teach:** `2024-11-05` (stdio + HTTP+SSE) → `2025-03-26` (Streamable HTTP replaces HTTP+SSE; OAuth 2.1; tool annotations; JSON-RPC batching added) → `2025-06-18` (structured tool output, elicitation, OAuth Resource Server + mandatory Resource Indicators/RFC 8707, batching **removed**) → `2025-11-25` (current stable) → `2026-07-28` RC. **HTTP+SSE is legacy/deprecated** since 2025-03-26; Streamable HTTP is the production transport.
- **Versioning scheme:** date-based `YYYY-MM-DD` marking the last backward-incompatible change. SEP-1400 proposes moving to SemVer 2.0.0 but has not landed — flag as in-flight.
- **Governance:** Anthropic donated MCP to the Linux Foundation's **Agentic AI Foundation (AAIF)** on Dec 9, 2025 (platinum members: Anthropic, OpenAI, Google, Microsoft, AWS, Block, Cloudflare, Bloomberg). The March 2026 roadmap is organized around four priority areas (transport scalability, agent communication, governance maturation, enterprise readiness) rather than dated releases. An **SDK tiering system** classifies official SDKs; Tier 1 SDKs are expected to support new revisions within the 10-week RC window.

### SDKs (mid-2026 status)
- **Official SDKs (AAIF-governed):** Python, TypeScript, Go (with Google), C#/.NET (with Microsoft), Rust, Java, Kotlin, Ruby, Swift (with Loopwork), PHP. Major change from 2025, when only Python/TS were official.
- **Python SDK:** v1.x stable and recommended for production; **v2 in alpha**, targeting beta 2026-06-30 and stable v2 on 2026-07-27 (aligned with the new spec). Add a `<2` pin (e.g., `mcp>=1.27,<2`) before then. FastMCP is the dominant high-level framework (~1.9M downloads/day).
- **TypeScript SDK:** v1.x recommended for production; v2 stable expected ~Q1 2026.
- **Rust SDK (`rmcp`):** reached v1.0.0 March 3, 2026, iterated to v1.5.0 by mid-April — now stable, Tokio-based with procedural macros.
- **C# SDK:** stable/production-ready (requires .NET 10, Native AOT, NuGet); **Go SDK:** approaching stable (expected August), single `mcp` package with generics-based typed tools, built on the Go team's JSON-RPC implementation.
- **Tiering (community-reported, not an official ranking):** Python/TypeScript/C#/Go top tier; Java, Rust mid-tier; Swift, Ruby, PHP lower tier.

### Security & governance (the user's deep lane)
- **Authorization model:** Remote servers use OAuth 2.1 + PKCE; MCP servers are OAuth Resource Servers (since 2025-06-18) with protected resource metadata; **Resource Indicators (RFC 8707) are mandatory** so access tokens are audience-bound to the specific server.
- **Token passthrough is explicitly FORBIDDEN** by the authorization spec — a server must validate that tokens were issued for it and must not forward client tokens downstream. This prevents the **confused-deputy** problem; correct mitigations are per-client consent registries and token exchange, never passthrough. The official "Security Best Practices" page details the confused-deputy attack against MCP proxy servers using static client IDs + dynamic client registration + consent cookies.
- **Threat taxonomy:** prompt injection / indirect prompt injection (via tool results), tool poisoning (malicious instructions in tool descriptions, e.g., Invariant Labs' WhatsApp exfiltration demo), rug-pull attacks (tool definitions changing post-approval), the lethal trifecta (private data + untrusted content + exfiltration channel), shadow MCP servers, supply-chain attacks, token mismanagement.
- **Frameworks to map against (all dated, flag status):**
  - **OWASP MCP Top 10** — a living document maintained at owasp.org/www-project-mcp-top-10; risks are numbered **MCP01:2025 through MCP10:2025**, with categories stable enough to cite though rankings may shift as the Phase 3 beta wraps. Led by Vandana Verma Sehgal, CC BY-NC-SA 4.0. Categories include Token Mismanagement & Secret Exposure (MCP01), Tool Poisoning (MCP03), Supply Chain & Dependency Tampering (MCP04), Command Injection, Insufficient Authentication (MCP07), Shadow MCP Servers (MCP09), and Context Oversharing.
  - **OWASP "Secure MCP Server Development"** guide (Feb 2026) and OWASP Top 10 for Agentic Applications 2026 (ASI01 Agent Goal Hijack).
  - **NSA AISC Cybersecurity Information Sheet "Model Context Protocol (MCP): Security Design Considerations for AI-Driven Automation"** (published May 20, 2026; sole-NSA product, NSA Artificial Intelligence Security Center; doc IDs U/OO/6030316-26, PP-26-1834; PDF at media.defense.gov/2026/Jun/02/2003943289/-1/-1/0/CSI_MCP_SECURITY.PDF). Its ten concrete recommendations: (1) choose maintained/supported MCP projects and code-audit them; (2) design explicit **trust boundaries** — treat agents, plugins, models, and users as separate trust zones, and prefer local servers for private data; (3) **network egress control** via filtering proxy (Squid, tinyproxy) or DLP; (4) **validate parameters** against schemas and block ambiguous/user-sourced parameter forwarding; (5) **sandbox tool execution** with seccomp/AppArmor/SELinux/AppContainers under least privilege; (6) **sign and verify MCP messages** with expiration timestamps + replay protection (the protocol cannot enforce integrity beyond TLS); (7) treat all tool/model outputs as **untrusted input to the next stage** (cascading prompt-injection defense); (8) **log all invocations** with parameters, identities, and result hashes into SIEM; (9) track/patch MCP CVEs and maintain an inventory; (10) scan networks for open/unauthorized MCP servers (named tools: MCP Scanner, Ramparts, CyberMCP, Proximity). Key quote: *"Securing MCP systems requires treating the agentic environment as a continuum, where misaligned assumptions or subtle inconsistencies at any stage can propagate and compound into exploitable conditions."*
  - **CSA AI Controls Matrix (AICM)** — 243 control objectives, maps to ISO 42001/27001, NIST AI RMF 1.0, BSI AIC4.
- **Real incident signal (verified/secondhand mix):** Per Practical DevSecOps citing Unit 42, between January and February 2026 researchers filed **over 30 CVEs** targeting MCP servers, clients, and tooling, of which **43% were shell injections**. **CVE-2025-49596** (MCP Inspector RCE) carried a **Critical CVSS 9.4**, was disclosed by Oligo Security, and was fixed in **v0.14.1 on June 13, 2025** — per Oligo, versions below 0.14.1 allow unauthenticated requests to launch MCP commands over stdio. **CVE-2026-32211** exposed a missing auth layer on the Azure MCP Server. Anthropic's own Git MCP server had path-traversal/argument-injection bugs disclosed January 2026. Per Palo Alto Networks **Unit 42's 2026 Global Incident Response Report**, *"with five connected MCP servers, a single compromised server hit a 78.3% attack success rate."* Treat benchmark/vendor figures (MCPTox, tool-poisoning success rates) as research-reported, not audited.
- **Gateways (security control point):**
  - **agentgateway** (Rust; AAIF/Linux Foundation; agentgateway.dev) — discover/sign/scope/observe every tool call, MCP + A2A native, OPA-evaluated allow/deny per hop, OpenTelemetry by default, tamper-evident audit logs; integrated into **kgateway** (CNCF Sandbox, Envoy-based) v2.1. **Best fit for the user's CNCF/Kubernetes stack** and the strongest reference comparison for an original gateway.
  - **Lasso MCP Gateway** (OSS, security-first, plugin guardrails incl. Presidio PII), **Lunar MCPX** (OSS control plane), **Microsoft's OSS reverse proxy** for MCP on Kubernetes + Azure APIM, **Kong / Traefik Hub** (Traefik introduces Task-Based Access Control), plus commercial options (MintMCP SOC 2, MCP Manager). CNCF also has an "Agent Gateway" policy-enforcement effort underway.
- **Supply-chain/provenance:** sign server container images with **cosign/sigstore** (keyless OIDC via Fulcio, Rekor transparency log, in-toto/SLSA attestations), enforce at admission with **sigstore policy-controller or Kyverno**, attach SBOM attestations. MCP **Server Cards** (SEP-1649 / SEP-2127, `/.well-known/mcp/server-card.json`) for pre-connection discovery/validation are in DRAFT.

### Architecture & ecosystem
- **Topology:** host (Claude Desktop/Code, ChatGPT, Cursor, VS Code, Zed) → one client per server → servers. Stateful vs stateless server design is the central 2026 architecture debate; the RC pushes statelessness so servers run behind plain round-robin load balancers with no shared session store.
- **Registry:** the **official MCP Registry** (registry.modelcontextprotocol.io) launched preview Sept 2025, froze API at v0.1 (Oct 2025), still preview/pre-GA (~2,000 entries). Community registries index ~17,000+ servers; GA expected to add signing/trust scoring. Self-hostable via Docker (ko build) + PostgreSQL.
- **Reference servers:** only **7 remain actively maintained** by the steering group — Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time. ~13 (GitHub, GitLab, Slack, Google Drive, Postgres, Sentry, SQLite, Puppeteer, EverArt, Brave Search, etc.) were **archived** to `servers-archived` and handed to vendor maintenance (e.g., github/github-mcp-server). Flag this prominently: many tutorials still point at archived code.
- **Adoption (flag self-reported vs verified):** ~97M monthly SDK downloads (Python+TS, vendor-reported); Python SDK reportedly >164M monthly on PyPI by April 2026; 10,000+ active public servers (Linux Foundation, Dec 2025). Per Nerq's Q1 2026 census (via Knak), of 17,468 indexed servers **only 12.9% score "high trust" (70+/100)** for documentation, maintenance, and reliability. Adopted by OpenAI (March 2025), Google DeepMind/Gemini (April 2025), Microsoft, AWS. MCP Apps launched Jan 26, 2026 with day-one partners (Amplitude, Asana, Box, Canva, Clay, Figma, Hex, monday.com, Slack, Salesforce). Pinterest and Block (Goose) case studies are vendor-reported.
- **Complementary protocols:** **A2A** (agent-to-agent; Google; reached v1.0 April 2026; now AAIF-governed); **ACP** merged into A2A (Aug 2025); commerce protocols (x402, Agentic Commerce Protocol, Stripe). Consensus stack: MCP (tool access) + A2A (agent coordination). **Cross-App Access (XAA)** and **Agentic Resource Discovery (ARD)** (Microsoft/Google/GitHub/Hugging Face; GitHub "agent finder" launched June 2026) are emerging discovery layers — flag as new and in-flight.

### Tooling & interaction patterns
- **Anthropic's "Writing effective tools for AI agents"** is the canonical source. Principles: build for agents not developers; iterate prototype → evaluate → collaborate (use Claude Code to optimize tools against an eval); choose high-leverage tools not thin API wrappers; namespace tool names (`domain_action`); return meaningful human-readable context not raw IDs; manage tokens via pagination/truncation/filtering; make implicit context explicit; use unambiguous parameter names (`user_id` not `user`); prefer search-focused tools (`search_contacts`) over list-all.
- **Anthropic's "Code execution with MCP"** (Nov 2025): present tools as code on a filesystem and load on demand (or add a `search_tools` tool) rather than loading all definitions upfront — Anthropic reports this *"reduces the token usage from 150,000 tokens to 2,000 tokens—a time and cost saving of 98.7%."* Cloudflare's complementary "Code Mode" reports an even larger effect for its Cloudflare-API MCP server: *"reduces the number of input tokens used by 99.9%... An equivalent MCP server without Code Mode would consume 1.17 million tokens,"* collapsing 2,500+ endpoints into ~1,000 tokens.
- **Tool annotations:** `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` — but the spec says annotations are **untrusted unless from a trusted server**.
- **Elicitation:** server requests structured input mid-flow; FastMCP `ctx.elicit(message, schema)` returns Accepted/Declined/Cancelled; spec restricts to shallow objects with scalar/enum fields; form mode is visible to client/LLM (never for secrets — use URL mode).
- **Structured output:** FastMCP auto-generates output schemas from type annotations and validates; low-level server supports explicit `outputSchema`.

### Cross-cutting build decisions
- **Repo layout:** monorepo with per-competency directories, each holding working code + guidebook + slides, plus top-level docs. Nested `CLAUDE.md` files (root for shared conventions; per-package for stack specifics). Keep root `CLAUDE.md` under ~200 lines; use progressive disclosure (`@`-references / pointers, not embedded long docs). Start Claude Code sessions from the package directory for single-package tasks; commit `.claude/settings.json` permission denies.
- **Tooling:** for a polyglot CNCF-aligned repo, use a cross-language task runner (Taskfile or Makefile) rather than JS-only Turborepo/Nx; uv for Python, pnpm for TS, Go modules. GitHub Actions CI with per-language jobs, linting (ruff/eslint), tests (pytest/vitest), and a cosign signing job in the release workflow.
- **Reveal.js:** current framework by Hakim El Hattab; install via npm, run a local server (`npm start`); author slides in Markdown with `---`/`--` separators (horizontal/vertical); speaker notes via `Note:` or `<aside class="notes">` (press `S` for speaker view with timer + next-slide preview); code highlighting via the built-in highlight.js plugin with line-stepping syntax `[1-2|3|4]`; fragments; PDF export via `?print-pdf`. One deck per competency. Quarto's revealjs output is a good alternative if you prefer pure Markdown authoring with `::: {.notes}` blocks.
- **Docs framework:** **MkDocs Material entered maintenance mode (Nov 5, 2025)** — feature-frozen but security-patched through Nov 2026; successor is **Zensical**. Docusaurus (React/MDX) is more future-proof and supports interactive components but requires Node. For a code-heavy teaching portfolio, recommend **MkDocs Material now** (fastest setup, Python-native, matches the stack) while noting the maintenance-mode caveat; choose **Docusaurus** if you want embedded interactive React demos. Well-structured per-directory READMEs are the minimum viable layer.
- **Authorship credibility:** original working code (servers, gateway, guardrails, signed registry), original threat models mapped to OWASP/NSA, original architecture diagrams, original eval harnesses, and original teaching decks establish SME — versus forking reference servers. The "build against both `2025-11-25` and the `2026-07-28` RC and document the migration" exercise is a strong differentiator.

## Details

### Recommended repo structure
```
mcp-sme-portfolio/
├── README.md                      # portfolio overview, competency map, spec-version banner
├── CLAUDE.md                      # root conventions (<200 lines), pointers to per-area docs
├── Taskfile.yml / Makefile        # cross-language build/test/lint/serve targets
├── .github/workflows/             # CI per language + cosign signing + slide build/deploy
├── docs/                          # top-level MkDocs Material (or Docusaurus) site
│   ├── spec-currency.md           # 2025-11-25 vs 2026-07-28 RC migration guide
│   └── glossary.md
├── 01-fundamentals/
│   ├── servers/                   # python (FastMCP) + typescript "hello world" + non-trivial
│   ├── clients/                   # minimal client, capability negotiation, progress/cancel
│   ├── tests/                     # lifecycle/JSON-RPC conformance-style tests
│   ├── guidebook.md
│   └── slides/                    # reveal.js deck
├── 02-architecture/
│   ├── multi-server-orchestration/
│   ├── stateless-vs-stateful/     # demo handle-pattern (RC) vs session (stable)
│   ├── server-composition/
│   ├── registry-demo/             # self-hosted MCP Registry + server cards
│   ├── guidebook.md
│   └── slides/
├── 03-tooling/
│   ├── tool-design/               # good vs anti-pattern tools, annotations, structured output
│   ├── elicitation-hitl/
│   ├── eval-harness/              # Anthropic-style tool eval
│   ├── guidebook.md
│   └── slides/
├── 04-security/                   # FLAGSHIP
│   ├── policy-gateway/            # original MCP gateway: authz, allowlist, audit, OPA-style policy
│   ├── guardrails/                # input/output sanitization, prompt-injection filters, PII
│   ├── signed-registry/           # cosign-signed server provenance + admission verification
│   ├── threat-models/             # original STRIDE + OWASP MCP Top 10 + NSA CSI mapping
│   ├── oauth-confused-deputy/     # demo of token passthrough anti-pattern + correct flow
│   ├── guidebook.md
│   └── slides/
└── 05-use-cases-ecosystem/
    ├── production-server-example/ # a real, useful server (e.g., over a CNCF/k8s API)
    ├── mcp-plus-a2a-demo/
    ├── ecosystem-map/
    ├── guidebook.md
    └── slides/
```

### Per-competency buildable recommendations
1. **Fundamentals:** Ship an idiomatic FastMCP "hello world" (tool + resource + prompt over stdio) and a non-trivial server (a typed, paginated data server with progress + cancellation), plus a parallel TypeScript implementation. Add a minimal client showing initialize/capability negotiation. Include conformance-style tests using in-memory transport. Teach JSON-RPC 2.0 message types, lifecycle, and the stdio vs Streamable HTTP distinction — and explicitly contrast the RC's stateless single-request form against the stable session handshake.
2. **Architecture:** Demonstrate multi-server orchestration through one host, server composition/chaining, and the stateless handle pattern (`create_basket` → `basket_id` → `add_item`) versus session state. Stand up the official MCP Registry locally (Docker/ko + Postgres) and publish a `server.json` + a `.well-known` server card.
3. **Tooling:** Build a matched pair of well-designed vs poorly-designed tools and an eval harness that measures the difference, mirroring Anthropic's methodology. Demonstrate all four tool annotations, structured/typed output with `outputSchema`, elicitation with human-in-the-loop confirmation, pagination, and resource subscriptions.
4. **Security (flagship):** Build an **original policy-enforcing MCP gateway/proxy** that sits between client and servers and enforces tool allowlisting, per-client consent, SIEM-ready JSON audit logging, and OPA-style policy; integrate **guardrails** (input/output sanitization, indirect-prompt-injection detection, PII redaction via Presidio). Build a **signed tool registry** that verifies cosign/sigstore signatures before admitting a server. Write **original threat models** (STRIDE per component: host, client, LLM, server, data stores, auth server) and map each finding to OWASP MCP Top 10 and the NSA CSI's ten recommendations. Demo the confused-deputy/token-passthrough anti-pattern and the correct audience-bound (RFC 8707) flow. Reference agentgateway/kgateway as the production-grade comparison point.
5. **Use cases & ecosystem:** Build one genuinely useful production-style server (ideally over a Kubernetes/CNCF API to leverage the user's background), an MCP+A2A integration demo, and an honest ecosystem map separating verified adoption from vendor claims.

## Recommendations
1. **Lock the spec baseline first.** Put a version banner in the README: "Built against MCP `2025-11-25` (stable); forward-compatible notes for `2026-07-28` RC." Write `docs/spec-currency.md` as the migration guide. This is the single most credible SME artifact and directly answers the currency concern. **Benchmark to revisit:** when `2026-07-28` goes final (July 28, 2026) and when Python SDK v2 (stable ~July 27) and TS SDK v2 land — refresh all examples then.
2. **Build the security competency first and deepest** — it is the professional differentiator and the area with the most original-code opportunity. Stage: (a) threat models + OWASP/NSA mapping, (b) policy gateway, (c) guardrails, (d) signed registry, (e) OAuth/confused-deputy demo.
3. **Then Fundamentals → Tooling → Architecture → Use Cases**, so the teaching narrative builds from primitives to systems.
4. **Use FastMCP (Python) as the primary language and TypeScript as the secondary**, with one Go or Rust example in Architecture/Use Cases to show polyglot range and align with the CNCF stack.
5. **Tooling choices:** Taskfile + uv + pnpm + Go modules; GitHub Actions with per-language jobs and a cosign signing job; MkDocs Material for docs now (note maintenance mode / Zensical successor); Reveal.js per-competency decks built and deployed to GitHub Pages via CI.
6. **Structure for Claude Code:** root `CLAUDE.md` with shared conventions + a codebase map; per-competency `CLAUDE.md` files with stack-specific rules; `.claude/settings.json` with committed permission denies; progressive-disclosure pointers to guidebooks. Drive the build competency-by-competency, starting each session in the relevant package directory.
7. **Authorship hygiene:** write original code and original threat models; where you reference reference servers, cite them as comparison, don't copy. Keep a CHANGELOG and conventional commits to evidence authorship history.

## Caveats
- **Draft vs GA:** Everything in the `2026-07-28` RC (stateless core, MCP Apps, Tasks extension, auth hardening, deprecations) is **not final** and may change before July 28, 2026. Roots/Sampling/Logging are deprecated but still functional with a ≥12-month removal window. Build stable examples on `2025-11-25` and clearly label RC-targeted code as preview.
- **SDK churn:** Python SDK v2 and TypeScript SDK v2 are pre-stable and intentionally aligned with the new spec; pin versions and expect breaking changes around late July 2026.
- **Adoption metrics are largely vendor/community self-reported** (97M downloads, 164M PyPI, 10,000+ servers, Pinterest/Block case studies). Independent census data (Nerq's 17,468 servers, 12.9% high-trust) is more conservative. Treat all adoption claims as directional, not audited.
- **OWASP MCP Top 10 is beta** (Phase 3); MCP01–MCP10 numbering is stable enough to cite but rankings may shift. The NSA CSI (May 20, 2026) is authoritative and recent but is guidance, not a binding standard.
- **Tooling staleness risk:** MCP moves fast; flag anything older than ~6 months. MkDocs Material's maintenance-mode status (successor Zensical) is a live decision factor; Reveal.js, FastMCP, and the SDKs iterate quickly — re-verify versions at build time.
- **Reference-server archival** means many third-party tutorials are stale; always verify against the current `modelcontextprotocol/servers` README and the official registry before installing or citing.
