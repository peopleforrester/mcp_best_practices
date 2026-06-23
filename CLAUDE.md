<!-- ABOUTME: Root conventions for the MCP SME portfolio monorepo; shared rules + codebase map.
ABOUTME: Per-track CLAUDE.md files hold stack specifics. Keep this file under ~200 lines. -->

# CLAUDE.md: MCP SME Portfolio

A polyglot, security-first portfolio demonstrating Model Context Protocol subject-matter expertise
through original working code, threat models, and teaching material. Read `PROJECT_STATE.md` first
each session; it is the live status. The approved plan is `docs/BUILD_PLAN.md` (read-only contract).

## Spec baseline (non-negotiable)

- Default target: MCP **`2025-11-25`** (latest stable). All examples build and pass here.
- `2026-07-28` is a Release Candidate. RC-only code is labeled **preview** and is never the default.
- Migration detail: `docs/spec-currency.md`. Verified versions: `docs/research/version-currency-2026-06-23.md`.

## Codebase map

| Path | What |
|---|---|
| `docs/` | MkDocs Material site: build plan, spec-currency guide, research, glossary |
| `docs/research/` | Founding report + verified-currency + exam-curriculum spikes |
| `04-security/` | FLAGSHIP: policy gateway, guardrails, signed registry, threat models, OAuth demo |
| `01-fundamentals/` | FastMCP + TS hello-world and non-trivial servers, minimal client, conformance tests |
| `03-tooling/` | Tool design, eval harness, elicitation/HITL, structured output |
| `02-architecture/` | Multi-server orchestration, stateless vs stateful, registry demo |
| `05-use-cases-ecosystem/` | Production-style server, MCP+A2A demo, ecosystem map |
| `06-exam-prep/` | Researched curriculum + Railway-deployable quiz app |

Tracks are built in this order: security first, then fundamentals, tooling, architecture, use-cases,
exam-prep. Each track ships working code + `guidebook.md` + a Reveal.js deck under `slides/`.

## Stack and pins (verified 2026-06-23)

| Concern | Choice | Pin |
|---|---|---|
| Primary | Python + FastMCP | `mcp>=1.28,<2`; FastMCP `3.4.x` |
| Secondary | TypeScript | `@modelcontextprotocol/sdk@^1.29` |
| Polyglot accent | Go (preferred) or Rust | `go-sdk@v1.6.1` / `rmcp@1.7` |
| Python tooling | uv | `0.11.x` |
| TS tooling | pnpm | `11.8.x` (Node >=22) |
| Task runner | Taskfile (go-task) | `3.51.x` |
| Docs | MkDocs Material | `9.7.x` (maintenance mode) |
| Slides | Reveal.js | `6.0.1` |
| Provenance | cosign / sigstore | cosign `3.x` |

Never trust training data for a version. Re-verify any pin older than ~6 months against the source.
Research a framework new to a track before writing code in it (official docs, current year).

## Working rules

- **Branch workflow:** work on `staging`, commit and push there first. Never push directly to `main`;
  promote via fast-forward only after staging is green. This is a code repo, so the staging gate applies.
- **TDD:** for application code (servers, gateway, guardrails, quiz app), write the failing test first,
  then the minimal code to pass. Every track package needs unit + integration tests; the security and
  use-case tracks also need end-to-end. Config scaffolding (this file, CI, Taskfile) is exempt.
- **Smallest reasonable change.** No drive-by refactors outside the contracted scope. Document unrelated
  improvements as issues, do not fold them in.
- **No mocks, no silent fallbacks.** Use real data and APIs. Code fails explicitly rather than defaulting.
  Ask before adding any workaround, fallback, or mock.
- **Authorship hygiene:** original code and original threat models only. Reference servers (the 7
  maintained ones) are cited as comparison, never copied. Conventional commits; keep a CHANGELOG.
- **Adoption claims:** always label verified vs vendor/community self-reported.

## Prose standard (all human-facing text)

No em-dashes (U+2014) anywhere: use a period, comma, colon, parentheses, or a connector. No en-dashes
in prose (use "to"/"through"). Avoid the LLM tells: antithesis reflex ("not X, but Y"), hedging
scaffolds ("it's worth noting"), triadic filler, aphoristic closings, hype vocabulary. Run
`task lint:prose` before committing docs. The verbatim founding report under `docs/research/` is the
one exempt source artifact (it is Michael's text, ingested as-is).

## Per-track sessions

For single-track work, start the session in that track's directory and read its local `CLAUDE.md`.
Keep this root file lean; push stack specifics down to the track. Commit `.claude/settings.json`
permission denies.

## Common commands

```bash
task                 # list available tasks
task lint:prose      # check authored docs for em-dashes
task docs:serve      # preview the MkDocs site locally
task docs:build      # strict docs build (fails on broken nav/links)
```

Python work uses `uv run ...`; TypeScript uses `pnpm ...`; cross-language orchestration uses `task`.
