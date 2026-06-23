<!-- ABOUTME: Durable project state for the MCP SME portfolio monorepo; read this FIRST each session.
ABOUTME: Reconcile against git log / git status / test results before trusting it. -->

# PROJECT_STATE.md — MCP SME Portfolio Monorepo

_Last updated: 2026-06-23_

## Plan summary
Polyglot, security-first MCP subject-matter-expert portfolio: five competency directories
(security flagship → fundamentals → tooling → architecture → use-cases), each with working
code + guidebook + Reveal.js deck. Built against MCP `2025-11-25` (stable) with forward-compat
notes for the `2026-07-28` RC. Full plan in `docs/BUILD_PLAN.md`; founding research in
`docs/research/mcp-sme-portfolio-research-2026-06.md`.

## Task checklist (Phase 0 — Foundations)
- [x] Git repo init + remote `peopleforrester/mcp_best_practices` + main/staging
- [x] Research report ingested to `docs/research/`
- [x] Polyglot `.gitignore` (incl. cosign private-key patterns)
- [x] Build plan written (`docs/BUILD_PLAN.md`)
- [x] Verification spikes complete → `docs/research/version-currency-2026-06-23.md`
- [ ] `docs/spec-currency.md`
- [ ] Root `CLAUDE.md` + `.claude/settings.json`
- [ ] Taskfile + GitHub Actions CI shell
- [ ] MkDocs Material scaffold + README banner

## Last completed step
Ran both verification spikes; wrote `docs/research/version-currency-2026-06-23.md`; folded the
verified pins + corrections (cosign v3, Go SDK stable, Python SDK v2 still alpha, etc.) into
`docs/BUILD_PLAN.md`.

## Next step
Write `docs/spec-currency.md` (`2025-11-25` ↔ `2026-07-28` RC migration guide) and the root
`CLAUDE.md` (<200 lines) + `.claude/settings.json`. Then begin Phase 1 (Security) with threat models.

## Branch & test status
- Branch: `staging` (correct working branch). Code repo → staging-first workflow applies.
- Tests: none yet (no code). Per the no-skip-tests policy, every competency package needs
  unit/integration/e2e once code exists.

## Verification method
- Research report: provided by Michael (June 2026), treated as authoritative source-of-record.
- Version/tooling claims: being **independently re-verified via web research** this session
  (spikes), because the report flags them as fast-moving / re-verify-at-build-time.

## Verified vs not
- **Verified:** repo + remote wiring (git push succeeded); file layout on disk.
- **NOT yet verified against reality:** every version-pinned claim in the report (spec revision
  currency, SDK v2 timing, FastMCP/reveal.js/MkDocs/cosign versions). Spikes in flight.
- No code written or tested yet.
