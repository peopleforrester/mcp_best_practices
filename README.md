# MCP Best Practices

> **Spec:** the current MCP revision is `2026-07-28` (final 2026-07-28), which this repo tracks. The
> default examples run on stable FastMCP 3.4.x (implementing through the prior `2025-11-25` semantics);
> a labeled preview rides the FastMCP 4.0 beta line for the stateless core. See
> [`docs/spec-currency.md`](docs/spec-currency.md).

A security-first portfolio demonstrating Model Context Protocol expertise through original working
code, threat models, and teaching material. Primary language Python (FastMCP), secondary TypeScript;
a Go or Rust example for CNCF range is planned, not yet built.

**Live demo:** the exam-prep track's quiz app runs at
[mcp-exam-quiz-production.up.railway.app](https://mcp-exam-quiz-production.up.railway.app):
18 researched questions, strict CSP, per-client rate limiting, scored per domain. `/health` reports
the deployed commit.

## Tracks (build order)

| # | Track | What it ships |
|---|---|---|
| 1 | **Security (flagship)** | Policy-enforcing MCP gateway (allowlist, consent, rules, rate limit, audit), guardrails, Ed25519-signed registry (cosign backend planned), STRIDE threat models mapped to OWASP MCP Top 10 + NSA CSI, confused-deputy demo, composed capstone |
| 2 | Fundamentals | FastMCP + TypeScript servers, minimal client, conformance-style tests |
| 3 | Tooling | Good vs anti-pattern tools, eval harness, elicitation/HITL confirmation demo, structured output |
| 4 | Architecture | Multi-server orchestration, stateless vs stateful, self-hosted registry |
| 5 | Use cases & ecosystem | Production-style server, MCP + A2A seam demo, honest ecosystem map |
| 6 | Exam prep | Researched curriculum + the live Railway quiz app |

Each track ships working code, a `guidebook.md`, and a Reveal.js deck under `slides/`.

## Teaching material

- Guidebooks:
  [security](04-security/guidebook.md) ·
  [fundamentals](01-fundamentals/guidebook.md) ·
  [tooling](03-tooling/guidebook.md) ·
  [architecture](02-architecture/guidebook.md) ·
  [use cases](05-use-cases-ecosystem/guidebook.md) ·
  [exam prep](06-exam-prep/guidebook.md)
- [STRIDE threat models](04-security/threat-models/) : six trust zones, each mapped to OWASP MCP
  Top 10 + NSA CSI, with an explicit implemented-vs-target-design boundary.
- [Ecosystem map](05-use-cases-ecosystem/ecosystem-map.md) : adoption claims labeled verified vs
  vendor-reported.
- [Exam curriculum](06-exam-prep/curriculum/README.md) : the ordered study path behind the quiz app.
- Reveal.js decks: `0*/slides/index.html` per track.

## Repository

- [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) : the approved, sequenced plan and locked stack pins
  (sealed 2026-06-23; live status lives in `PROJECT_STATE.md`).
- [`docs/spec-currency.md`](docs/spec-currency.md) : the spec migration guide.
- [`docs/research/`](docs/research/) : founding report, verified version currency, exam curriculum,
  and the per-track research spikes.
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

All six tracks are built, tested, and promoted to `main`; the repo is in review and maintenance, with
seven review-remediation rounds recorded in `PROJECT_STATE.md` and `decisions.md`. The quiz app is
live on Railway with GitHub-connected auto-deploy from `main`.
