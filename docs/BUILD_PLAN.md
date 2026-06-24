<!-- ABOUTME: Phased build plan for the MCP SME portfolio monorepo, derived from the founding research report.
ABOUTME: Sequencing, tech stack, and milestones; PROJECT_STATE.md tracks live status against this plan. -->

# Build Plan: MCP SME Portfolio Monorepo

Derived from `docs/research/mcp-sme-portfolio-research-2026-06.md`. This plan sequences the
work and records the decisions that govern every competency. Live status lives in
`/PROJECT_STATE.md`.

## Spec baseline (locked)

- **Primary baseline:** MCP `2025-11-25` (latest stable): all examples build and pass here.
- **Forward-compat target:** `2026-07-28` RC: RC-specific code is labeled **preview** and never
  the default. Headline RC change: stateless protocol core (no `initialize` handshake, no
  `Mcp-Session-Id`); cross-call state via server-minted handles.
- **Revisit trigger:** when `2026-07-28` goes final (2026-07-28) and when Python SDK v2
  (stable ~2026-07-27) and TS SDK v2 land: refresh all examples then.

## Tech stack (locked, versions verified 2026-06-23, see `version-currency-2026-06-23.md`)

| Concern | Choice | Pin |
|---|---|---|
| Primary language | Python + FastMCP | `mcp>=1.28,<2`; FastMCP `3.4.x` |
| Secondary language | TypeScript | `@modelcontextprotocol/sdk@^1.29` |
| Polyglot accent | one Go or Rust example | Go `go-sdk@v1.6.1` (stable) or `rmcp@1.7` |
| Python tooling | uv | `0.11.x` |
| TS tooling | pnpm | `11.8.x` (Node ≥22) |
| Task runner | Taskfile (go-task) | `3.51.x`; not Turborepo/Nx |
| Lint/test | ruff + pytest / eslint + vitest | |
| CI | GitHub Actions, per-language jobs + cosign signing | |
| Docs site | MkDocs Material | `9.7.x` (maintenance mode; Zensical successor watched) |
| Slides | Reveal.js, one deck per competency | `6.0.1`; deploy to GitHub Pages via CI |
| Provenance | cosign / sigstore (keyless OIDC) | **cosign `3.x`** (bundle format default); policy-controller / Kyverno for admission verify |

## Build phases

> **Sequence rationale:** security first (the differentiator + most original-code surface),
> then primitives → systems for the teaching narrative.

### Phase 0: Foundations & spec lock  ← current
- [x] Repo init, remote, staging workflow
- [x] Ingest research report into `docs/research/`
- [x] Polyglot `.gitignore`
- [x] Verification spikes (spec + SDK versions; tooling + security tooling): see `version-currency-2026-06-23.md`
- [ ] `docs/spec-currency.md` migration guide (`2025-11-25` ↔ `2026-07-28` RC)
- [ ] Root `CLAUDE.md` (<200 lines) + `.claude/settings.json` permission denies
- [ ] Taskfile skeleton + GitHub Actions CI shell
- [ ] MkDocs Material scaffold + README version banner

### Phase 1: Security (FLAGSHIP) `04-security/`
- [x] (a) Threat models: STRIDE per component (host, client, LLM, server, data stores, auth server),
  mapped to OWASP MCP Top 10 + NSA CSI 10 recs → `04-security/threat-models/`
- [x] (b) Policy gateway: tool allowlisting, per-client consent, SIEM JSON audit, OPA-style policy.
  Core engine + audit + FastMCP middleware adapter done (TDD, e2e via in-memory client).
- [~] (c) Guardrails: injection detection + secret/PII redaction core done (TDD) in
  `04-security/guardrails/`; Presidio backend optional/later; wired into the gateway with the adapter
- [~] (d) Signed registry: cosign/sigstore verify before admitting a server. Ed25519 provenance core
  done (TDD) in `04-security/signed-registry/`; cosign `Verifier` backend planned (integration-tested).
- [x] (e) OAuth confused-deputy demo: token-passthrough anti-pattern vs RFC 8707 audience-bound flow
  (TDD, real Ed25519) in `04-security/oauth-confused-deputy/`
- [ ] Guidebook + Reveal.js deck

### Phase 2: Fundamentals `01-fundamentals/`  ✅ done
- [x] FastMCP hello server (tool + resource + prompt) + non-trivial typed/paginated catalog server
- [x] Parallel TypeScript implementation (@modelcontextprotocol/sdk v1.29)
- [x] Client via in-memory transport (capability negotiation asserted in tests)
- [x] Conformance-style tests (in-memory transport): Python 9, TypeScript 4
- [x] Guidebook + deck. (Go/Rust accent deferred: Go toolchain absent locally, would ship unrun)

### Phase 3: Tooling `03-tooling/`  ✅ done
- [x] Matched well-designed vs anti-pattern tool pair + deterministic offline eval harness (5 metrics)
- [x] All four annotations (tested); structured output (TypedDict) + pagination in the catalog/contacts
  tools; elicitation documented with the verified API (HITL flows live in the security track)
- [x] Guidebook + deck. 5 tests, ruff clean

### Phase 4: Architecture `02-architecture/`  ✅ done
- [x] Server composition via `FastMCP.mount(namespace=...)`; composite exposes both sub-servers
- [x] Stateless handle pattern (`create_basket`→`basket_id`→`add_item`/`get_basket`) vs session state
- [x] Registry `server.json` + offline validator + illustrative `.well-known` server card (card SEP draft).
  Self-hosting the registry (Docker/ko + Postgres) documented in the spike, not stood up here.
- [x] Guidebook + deck. 8 tests, ruff clean

### Phase 5: Use cases & ecosystem `05-use-cases-ecosystem/`  ✅ done
- [x] Read-only Kubernetes MCP server (injected CoreV1Api; offline-tested with real V1Pod models)
- [x] MCP + A2A delegation bridge (injected AgentDelegate seam; a2a-sdk wiring documented in the spike)
- [x] Honest ecosystem map (`ecosystem-map.md`), verified vs self-reported labeled
- [x] Guidebook + deck. 5 tests, ruff clean

### Phase 6: Exam prep: curriculum + quiz app `06-exam-prep/`  ✅ done
A thoroughly researched MCP learning track plus a deployable quiz/exam app that tests a learner
as if sitting an MCP exam. Doubles as an SME artifact (an authored body of knowledge + assessment).
- [x] Research spike: ordered MCP curriculum + exam blueprint + seed questions (in `docs/research/`)
- [x] `curriculum/`: ordered 13-module study path mapped to competencies (the "order of materials")
- [x] `quiz-app/`: FastAPI app, versioned YAML question bank (validated on load), pure scoring,
  per-domain results; answers hidden on GET /exam; questions tagged by domain + difficulty
- [x] Tests: question-bank schema validation, scoring logic, API integration (10 tests, pristine)
- [x] Railway config: `railway.json` (Railpack + uvicorn + /health); **creating/linking the project
  is an account-level action, left for Michael's go-ahead before `railway init` / `railway up`**
- [x] Guidebook + deck

> Stack defaults (redirect if desired): FastAPI + question bank in versioned YAML, SQLite for local
> runs / Postgres on Railway for results. Question bank is content, kept current with the spec
> baseline; flag RC-only questions as preview.

## Cross-cutting authorship rules
- Original code and original threat models only; reference servers are cited as comparison, never copied.
- Conventional commits + CHANGELOG to evidence authorship history.
- Every adoption metric labeled verified vs vendor/community self-reported.
- Re-verify any version/tooling fact older than ~6 months at build time.

## Resolved decisions (spikes complete 2026-06-23)
- `2025-11-25` confirmed latest stable; `2026-07-28` confirmed still RC (final 2026-07-28). ✓
- Python SDK v2 beta has **not** shipped: still alpha (`2.0.0a2`); pin `mcp>=1.28,<2`. ✓
- MkDocs Material confirmed in maintenance mode (feature-frozen at 9.7.0); Zensical is the
  successor. Proceed with MkDocs Material `9.7.x` now; revisit if Zensical reaches GA. ✓
- Pins set: Reveal.js `6.0.1`, FastMCP `3.4.x`, **cosign `3.x`** (was v2 in report). ✓

## Still open
- Polyglot accent: Go (`go-sdk` stable) vs Rust (`rmcp`) for the Architecture/Use-Cases example:
  decide when those phases start. Go is the safer CNCF-aligned, already-stable choice.
- Docs: MkDocs Material vs Docusaurus only revisits if interactive React demos become a requirement.
