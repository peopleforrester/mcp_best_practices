<!-- ABOUTME: Durable project state for the MCP SME portfolio monorepo; read this FIRST each session.
ABOUTME: Reconcile against git log / git status / test results before trusting it. -->

# Project State: mcp_best_practices

Phase: 1.2 Plan
Approved: pending

## Lifecycle
- [x] 1.1 Research
- [x] 1.2 Plan
- [ ] 1.3 Approve  ← you are here (plan written; awaiting Michael's explicit approval to seal the contract)
- [ ] 2.1 Test
- [ ] 2.2 Implement
- [ ] 2.3 Verify
- [ ] 3.1 Stage
- [ ] 3.2 Confirm CI
- [ ] 3.3 Promote

## Contracts
_(none yet. The build plan in `docs/BUILD_PLAN.md` is the proposed plan; it becomes a sealed
contract at 1.3 with ts + sha256.)_

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
- [ ] Root `CLAUDE.md` + `.claude/settings.json`
- [ ] Taskfile + GitHub Actions CI shell
- [ ] MkDocs Material scaffold + README banner

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
