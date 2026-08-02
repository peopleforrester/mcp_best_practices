<!-- ABOUTME: Working memory for the MCP SME portfolio monorepo: how work was done and where we left off.
ABOUTME: Conversation context is lost across sessions; this and PROJECT_STATE.md are the only durable record. -->

# MEMORY: MCP SME Portfolio Monorepo

## What this is
A security-first, polyglot MCP subject-matter-expert portfolio for Michael. Goal: establish
credible SME authorship through original working code (servers, an MCP policy gateway,
guardrails, an Ed25519-signed registry with a cosign backend planned), original threat models, and
teaching decks, not forked
reference servers. Tracks MCP spec `2026-07-28` (current, final 2026-07-28); the default examples run
on stable FastMCP 3.4.x (prior `2025-11-25` semantics), with a labeled FastMCP-4.0-beta preview.

## Session log
### 2026-06-23: Repo bootstrap, ingest, planning (session 1)
- Created the git repo and pushed `main` + `staging` to `peopleforrester/mcp_best_practices`
  (public). Initial commit to `main` was a one-time bootstrap (empty repo had no PR base);
  all work since is on `staging`.
- Ingested Michael's founding research report verbatim to
  `docs/research/mcp-sme-portfolio-research-2026-06.md`.
- Wrote polyglot `.gitignore`, `docs/BUILD_PLAN.md`, `PROJECT_STATE.md`.
- **How:** launched two web-research spikes to independently re-verify the report's
  fast-moving version claims (spec revision currency, Python/TS SDK v2 timing, FastMCP /
  reveal.js / MkDocs Material / cosign versions) before pinning anything. Findings land in
  `docs/research/version-currency-2026-06-23.md`.

## Key decisions
- **Spec:** current is `2026-07-28` (final). Default code on stable FastMCP 3.4.x (prior `2025-11-25`
  semantics); `2026-07-28` stateless core in a labeled FastMCP-4.0-beta preview package.
- **Build order:** Security (flagship) first, then Fundamentals → Tooling → Architecture → Use Cases.
- **Stack:** Python/FastMCP primary, TypeScript secondary, one Go/Rust accent; uv + pnpm + Taskfile;
  MkDocs Material; Reveal.js; cosign/sigstore. (Confirm versions via the spike before pinning.)

## Where we left off
Phase 0 (Foundations). Next: fold spike results into the version-currency doc, write
`docs/spec-currency.md` + root `CLAUDE.md`, then start Phase 1 threat models.
