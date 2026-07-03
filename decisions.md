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

## 2026-06-27T01:00:00Z · 3.x · Round 5: second senior review, full TDD pass

Ran a second /review-senior, independently verified every finding before acting, then remediated all
ten phases TDD. Three decisions worth recording:

- H1 was my own round-4 error. I had concluded server.json's 2025-09-29 schema was current after
  probing only 2025-11-25 (which 404s). A live CDN probe on 2026-06-27 shows 2025-12-11 exists and is
  newer, and my own architecture-registry spike already documented it. Bumped to 2025-12-11 and added a
  currency-lock test so CI catches this class of drift. Lesson logged: a "verified" note that locks in
  an incomplete check is worse than no note.

- H2 (rate-limit XFF): the review said switch from the left-most to the right-most entry. I flagged
  that this may be wrong for Railway, whose own docs call the left-most the real client (the platform's
  XFF handling is contested and was changing as of early 2026). Michael chose to apply the right-most
  fix anyway. Implemented with a multi-hop test; the code comment records the contested nuance and that
  the real control is edge rate-limiting. If Railway's behavior is confirmed to populate the left-most,
  this should be revisited.

- Dependabot PR #6 (ruff + fastapi bumps across 9 dirs) was incorporated into this pass rather than
  merged or closed-and-lost: ruff floor raised to >=0.15.20 across all 10 packages (the PR missed the
  capstone package, added after it opened), fastapi bumped to 0.138.1 in the quiz app, then PR #6 closed
  with a note. fastmcp 3.4.2 / mcp 1.28.0 still agree across all locks (lockdrift invariant intact).

Two of the review's nits were declined with reasons: the OAuth gateway_forward / passthrough tests are
behavioral contracts, not tautologies; and the Node engines >=22 vs CI Node 24 pairing is a valid
floor-plus-tested-version setup, not drift.

## 2026-07-03T00:00:00Z · 3.x · Round 6: third senior review, full TDD pass

Ran a third multi-agent /review-senior, independently verified every finding before acting, then
remediated all eight phases TDD. Decisions worth recording:

- Rate limiter: Michael chose to implement the control rather than soften the docs, so the policy
  gateway gained a per-client token bucket (injected clock) enforced as a DENY + audit and demonstrated
  in the capstone. The threat models had claimed gateway rate limiting that did not exist.

- k8s find_pods 404 was my own round-4/5 error: `list_namespaced_pod` returns an empty 200 for a
  missing namespace, never a 404, so the mapping was dead and the round-5 test fed a 404 the real API
  never produces. Removed the branch, corrected the test, added a missing-namespace-empty test.

- Threat-model claim drift (the flagship's biggest credibility gap): the models attributed token
  validation, tool-description pinning, per-call audience re-check, action/token budgets, and cosign to
  the shipped gateway; none are wired (the OAuth package is standalone; Ed25519, not cosign, is built).
  Implementing all of those was out of scope, and a full rewrite of six threat-model files was too
  broad, so the reconciliation is a README implemented-vs-target scope note plus inline markers on the
  most definitive present-tense over-claims (token validation "at the gateway", per-call audience
  re-check, description pinning, cosign present-tense). The mitigations still describe the target
  defense-in-depth design; the note makes the implemented subset explicit.

- Declined two nits with reasons: the injection detector / redaction breadth is documented as
  heuristic/best-effort (not a false claim), and the OAuth gateway_forward / passthrough tests are
  behavioral contracts, not tautologies. Deferred (unchanged): pagination DRY, A2A async seam, the
  Taskfile ts:test `pnpm -r` bug, and wiring per-request identity into the gateway adapter (now a
  docstring caveat).

Repo at 141 tests, all green. The round-5 session was also never journaled; backfilling round 5 + 6
into the engineering journal alongside this.

## 2026-07-03T06:00:00Z · 3.x · Round 7: end-to-end architecture + code + website review

Four parallel reviewers. The round-6 code verified regression-free, so the round was mostly truth
work: presentation-layer claim drift and CI posture. Decisions worth recording:

- Publish the docs site. The MkDocs site was strict-built in CI but deployed nowhere, so the
  portfolio's most credibility-bearing surface was invisible. Added a Pages deploy job (main only) and
  enabled Pages (build_type=workflow). This makes the site public, which "remediate all of it"
  authorized; flagged beforehand with no objection. Rendering the full track guidebooks inline was
  deferred: their links point at sibling source and do not resolve off-tree, so the site gets a
  Teaching Material index that links to source rather than a broken inline copy.

- Implement the elicitation demo rather than delete the claim. The docs claimed elicitation/HITL and
  even said it was "used in the security track", with zero `ctx.elicit` calls in the repo. Built a real
  `archive_report` confirmation tool (accept-true acts; decline, cancel, and accept-false do not) with
  three tests over the in-memory client's elicitation handler, then made the docs describe it. A
  documented `type: ignore` covers a confirmed fastmcp 3.4.2 + mypy 2.1 overload mis-resolution.

- Add security scanning to the repo that teaches supply-chain security. osv-scanner over the lockfiles
  and CodeQL (python + javascript-typescript) now run in CI; a wheel-parity job serves the built wheel
  over uvicorn and probes it, closing the class of packaging regression that source-tree tests cannot
  see; a CycloneDX SBOM is published as an artifact. On-theme for the flagship, and it makes the repo
  practice what it teaches.

- Threat-model audit wording. The three threat models round 6 had not touched described an audit record
  with raw parameters and a result hash. That contradicts the shipped fingerprint-only design and the
  portfolio's own MCP01 stance even as target design, so the wording was corrected to the sha256
  fingerprint and the result-hash / tamper-evidence framed as target design.

- Railway "Wait for CI" (checkSuites) was left off and deferred to a dashboard toggle: the read that
  confirmed checkSuites=false at session start began returning INTERNAL_SERVER_ERROR, so the trigger id
  could not be read to run the mutation safely. Not fabricating an API success for a one-click setting.
