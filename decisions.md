# Decisions Log

Append-only audit trail of approvals, amendments, backward steps, and conditional-skip rationales.
See [[state-persistence]] for schema.

## 2026-06-23T16:11:23Z · init · state persistence initialized

init-state ran in this repo and migrated a pre-lifecycle `PROJECT_STATE.md` to the lifecycle
schema per [[lifecycle-phases]] (3 phases × 3 steps). The existing body was preserved below the
prepended header. Phase deduced as **1.2 Plan**: research is ingested and the build plan is
written, but no plan has been formally approved (1.3) and no code exists yet. No prior decisions
to import.

## 2026-06-23T16:11:23Z · 1.2 · added Phase 6 exam-prep track to the plan

Scope addition (Michael's request): a thoroughly researched MCP curriculum plus a Railway-deployable
quiz/exam app (`06-exam-prep/`). Defaults: FastAPI + versioned YAML question bank + light HTML
frontend. Curriculum research spike launched. Railway project creation deferred until the app
exists and Michael gives explicit go-ahead (account-level action).

## 2026-06-24 · 2.3 · best-practice verification pass + remediation

Ran a three-reviewer verification (currency, security correctness, best-practice alignment) plus
deterministic checks. Fixed in-pass: 1 HIGH (signed-registry malformed-key crash now fails closed)
and 6 MED (policy allow-rule semantics, required audit_sink, redaction honesty + broader shapes,
OAuth list-audience + structural passthrough prohibition, CI concurrency/timeouts/PR-filter). Pinned
Python 3.13 for reproducibility. Currency rechecked: spec + Python SDK v2 unchanged; rmcp/C#/pnpm pins
bumped. Deferred operational items (SHA-pin actions, gh-pages, mypy, cosign backend, CodeQL) recorded
in `docs/best-practice-verification-2026-06-24.md`. Verdict: the path is best-practice and current.

## 2026-06-25 · 3.3 · all tracks complete; quiz app deployed to Railway

All six post-foundation tracks built, tested, and promoted to main (80 tests; security, fundamentals,
tooling, architecture, use-cases, exam-prep). Michael directed: do NOT build the operational
follow-ups (SHA-pin actions, gh-pages, mypy, cosign backend, Go accent); keep pnpm (no npm switch).
On his explicit go-ahead, deployed the quiz app to Railway: project `mcp-exam-quiz`, production env,
live at https://mcp-exam-quiz-production.up.railway.app, verified (/health, /exam, /exam/submit). CLI
deploy (not GitHub-connected); the railway.json (Railpack + uvicorn + /health) drives the build.

## 2026-06-23T16:25:45Z · 1.3 · build plan APPROVED by Michael

Michael formally approved `docs/BUILD_PLAN.md`. Contract sealed: sha256:e0bb135ce836 (full:
e0bb135ce8360f252086110c37dcdbe3ae982c253ccf82d078a7878d24fd4df5). The plan is now read-only;
amendments require `/prd-amend` + re-approval. Advanced to Phase 2.2 to finish Phase 0 scaffolding.
2.1 Test is CONDITIONAL-skipped for the config scaffolding (root CLAUDE.md, settings.json, Taskfile,
CI shell, mkdocs.yml, README): no application logic to test yet. Test infrastructure (pytest/vitest)
lands with Phase 1 security code, where 2.1 becomes mandatory.

## 2026-06-26T01:30:00Z · 3.x · /remediate round 4 over the senior review

Executed the /remediate TDD loop against the 2026-06-25 senior/architecture review. Eleven phases,
each a single red→green→gate→commit cycle on `staging`: H3 redaction prefixes, H1 forwarded-client
rate key, H2 streaming body cap + answer length bounds, H4 LICENSE + CHANGELOG, M5 recursive guardrail
redaction, M6 cursor→offset rename, M8 k8s find_pods error contract, M10 type enforcement
(disallow_untyped_defs, tsc --noEmit in check, noUncheckedIndexedAccess), M11 incremental progress,
M7 fingerprint docstring + server.json schema verification, and the low-priority lock contracts.

Two findings were corrected rather than implemented as written, with evidence:
- server.json `$schema`: the review said bump to 2025-11-25. Probed the CDN on 2026-06-26; that
  registry schema returns 404. The registry schema versions independently of the protocol revision,
  and 2025-09-29 is the latest published, so the file is left unchanged. Recorded in todo.md.
- A new Taskfile `ts:test` bug surfaced (uses `pnpm -r`, which fails at the repo root with no pnpm
  workspace; CI loops per-package and is unaffected). Deferred, not fixed in this pass (out of scope).

Deferred items unchanged: M9 eval-namespacing metric, A2A async seam, pagination DRY. Repo is at 118
tests, all green. Staging is ahead of main; promotion pending per the standing "keep promoting to main"
directive.
