<!-- ABOUTME: Durable project state for the MCP SME portfolio monorepo; read this FIRST each session.
ABOUTME: Reconcile against git log / git status / test results before trusting it. -->

# Project State: mcp_best_practices

Phase: 2.2 Implement (Phase 1 security: threat models)
Approved: 2026-06-23T16:25:45Z by Michael (sha256:e0bb135ce836)

## Lifecycle (Phase 1 security track; Phase 0 landed on staging, CI green)
- [x] 1.1 Research (founding report + curriculum spike cover the security body of knowledge)
- [x] 1.2 Plan (approved build plan scopes the security track)
- [x] 1.3 Approve
- [ ] 2.1 Test (CONDITIONAL: threat-model docs are prose, not code; tests begin with the gateway code)
- [ ] 2.2 Implement  ← you are here (threat models, fan-out in flight)
- [ ] 2.3 Verify
- [ ] 3.1 Stage
- [ ] 3.2 Confirm CI
- [ ] 3.3 Promote

> Phase 0 scaffolding reached 3.2 (CI green on staging, commit `ed8ca21`). 3.3 promote-to-main
> deferred: batching the promotion with the first security deliverable. Staging-only for now.

## Contracts
- 2026-06-23T16:25:45Z · sha256:e0bb135ce836 · **Build plan approved by Michael.** `docs/BUILD_PLAN.md`
  is the sealed contract: six tracks (security flagship first), stable `2025-11-25` baseline + RC
  forward-compat, stack pins as tabled. Changes require `/prd-amend` + re-approval.

<!-- ===== preserved pre-lifecycle body (migrated 2026-06-23T16:11:23Z) ===== -->

## Current Plan
Polyglot, security-first MCP subject-matter-expert portfolio. Six tracks:
five competency directories (security flagship → fundamentals → tooling → architecture →
use-cases) plus an exam-prep track (curriculum + Railway-deployable quiz app), each with working
code + guidebook + Reveal.js deck. Built against MCP `2025-11-25` (stable) with forward-compat
notes for the `2026-07-28` RC. Full plan in `docs/BUILD_PLAN.md`; founding research in
`docs/research/mcp-sme-portfolio-research-2026-06.md`.

### Phase 0 (Foundations) task checklist
- [x] Git repo init + remote `peopleforrester/mcp_best_practices` + main/staging
- [x] Research report ingested to `docs/research/`
- [x] Polyglot `.gitignore` (incl. cosign private-key patterns)
- [x] Build plan written (`docs/BUILD_PLAN.md`), incl. Phase 6 exam-prep track
- [x] Verification spikes complete → `docs/research/version-currency-2026-06-23.md`
- [x] Exam-prep curriculum research spike complete → `docs/research/exam-curriculum-2026-06-23.md`
- [x] `docs/spec-currency.md` (migration guide written)
- [x] Root `CLAUDE.md` + `.claude/settings.json`
- [x] Taskfile + GitHub Actions CI shell
- [x] MkDocs Material scaffold + README banner

**Phase 0 complete.** Phase 1 (Security) in progress:
- [x] (a) Threat models: 6 STRIDE-per-component models → `04-security/threat-models/`
- [x] (b) Policy gateway: core + **FastMCP middleware adapter** done (TDD, 13 tests incl. async
  in-memory-client e2e) → `04-security/policy-gateway/`. Verified against real FastMCP 3.x.
- [x] (c) Guardrails: injection detection + secret/PII redaction core (TDD, 9 tests) → `04-security/guardrails/`
- [x] (d) Signed registry: Ed25519 provenance verification core (TDD, 4 tests) → `04-security/signed-registry/`.
  cosign/sigstore backend planned as an integration-tested `Verifier`.
- [x] (e) OAuth confused-deputy demo: RFC 8707 audience binding + passthrough/exchange (TDD, 6 tests)
  → `04-security/oauth-confused-deputy/`
- [x] cross-component summary table (threat-models/README) + security guidebook + Reveal.js deck
- [ ] best-practice verification pass (final)  ← next

**Phase 1 (Security flagship) complete.** Five components + guidebook + deck, all TDD where code,
all CI-green. 32 tests across four Python packages. Next: the best-practice verification pass.

CI/Taskfile are package-aware (iterate dirs with pyproject.toml). uv confirmed (CPython 3.14).
FastMCP 3.x middleware API verified inline via WebFetch after the subagent spike kept 529-ing;
adapter built and tested green against the real library.

## Branch & Tests
- Branch: `staging` (correct working branch). Code repo → staging-first workflow applies.
- Working tree: in progress (planning edits).
- Last CI: n/a (no CI yet); HEAD `1a7c83f`.
- Tests: none yet (no code). Per the no-skip-tests policy, every competency/exam package needs
  unit/integration/e2e once code exists.

## Verification method
- Research report: provided by Michael (June 2026), treated as authoritative source-of-record.
- Version/tooling claims: independently re-verified via web research (spikes complete 2026-06-23,
  see `version-currency-2026-06-23.md`), because the report flags them as fast-moving.

## Verified vs not
- **Verified:** repo + remote wiring; file layout on disk; all pinned versions (2026-06-23 spikes).
- **NOT yet verified:** exam curriculum/blueprint (spike in flight). No code written or tested yet.

## Phase History
_(append-only. Each phase transition adds one line, oldest first.)_
- 2026-06-23T16:11:23Z init-state migrated pre-lifecycle PROJECT_STATE.md → Phase 1.2 Plan
- 2026-06-23T16:11:23Z 1.2 added Phase 6 exam-prep track; wrote docs/spec-currency.md; curriculum spike landed
- 2026-06-23T16:25:45Z 1.3 → 2.x plan approved (sha256:e0bb135ce836); Phase 0 scaffolding implemented + verified
- 2026-06-23T16:30:00Z 3.2 → 3.3 Phase 0 + threat models promoted to main (ff to 49b08c2, CI green)
- 2026-06-24 2.x Phase 1 (b) policy gateway started: TDD on the pure-Python policy decision core
