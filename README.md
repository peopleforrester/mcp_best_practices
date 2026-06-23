# MCP Best Practices

> **Spec baseline:** built against MCP `2025-11-25` (latest stable). Forward-compatible notes for the
> `2026-07-28` Release Candidate; RC-only code is labeled preview. See
> [`docs/spec-currency.md`](docs/spec-currency.md).

A security-first, polyglot portfolio demonstrating Model Context Protocol expertise through original
working code, threat models, and teaching material. Primary language Python (FastMCP), secondary
TypeScript, with a Go or Rust accent for CNCF range.

## Tracks (build order)

| # | Track | What it ships |
|---|---|---|
| 1 | **Security (flagship)** | Policy-enforcing MCP gateway, guardrails, cosign-signed registry, STRIDE threat models mapped to OWASP MCP Top 10 + NSA CSI, confused-deputy demo |
| 2 | Fundamentals | FastMCP + TypeScript servers, minimal client, conformance-style tests |
| 3 | Tooling | Good vs anti-pattern tools, eval harness, elicitation/HITL, structured output |
| 4 | Architecture | Multi-server orchestration, stateless vs stateful, self-hosted registry |
| 5 | Use cases & ecosystem | Production-style server, MCP + A2A demo, honest ecosystem map |
| 6 | Exam prep | Researched curriculum + Railway-deployable quiz app |

Each track ships working code, a `guidebook.md`, and a Reveal.js deck under `slides/`.

## Repository

- [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) : the approved, sequenced plan and locked stack pins.
- [`docs/spec-currency.md`](docs/spec-currency.md) : the spec migration guide.
- [`docs/research/`](docs/research/) : founding report, verified version currency, exam curriculum.
- `PROJECT_STATE.md` / `decisions.md` : live status and the append-only decision log.

## Develop

```bash
task              # list tasks
task lint:prose   # check authored docs for em-dashes
task docs:serve   # preview the docs site
task check        # run all currently-applicable checks
```

Python uses `uv`, TypeScript uses `pnpm`, cross-language orchestration uses [Taskfile](https://taskfile.dev).
Work happens on `staging` and is promoted to `main` only after CI is green.

## Status

Phase 0 (foundations) is closing out. The flagship security track is next. See `PROJECT_STATE.md`.
