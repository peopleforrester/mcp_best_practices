<!-- ABOUTME: Durable project state for the MCP SME portfolio monorepo; read this FIRST each session.
ABOUTME: Reconcile against git log / git status / test results before trusting it. -->

# Project State: mcp_best_practices

Phase: 3.3 Promote (all tracks shipped; now in review + maintenance)
Approved: 2026-06-23T16:25:45Z by Michael (sha256:e0bb135ce836)

## Lifecycle (whole project: all six tracks built, tested, promoted to main)
- [x] 1.1 Research  - [x] 1.2 Plan  - [x] 1.3 Approve
- [x] 2.1 Test  - [x] 2.2 Implement  - [x] 2.3 Verify
- [x] 3.1 Stage  - [x] 3.2 Confirm CI  - [x] 3.3 Promote

> Reconciled 2026-06-25: the old "2.2 threat models" line was stale. Reality: all six competency
> tracks plus the exam app are built, CI-green, and on main. The repo is in review + maintenance.
> Latest: a full architecture + code + senior review (4 reviewers) on 2026-06-25, followed by a
> remediation pass (see "Review remediation" below).

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
- [x] best-practice verification pass → `docs/best-practice-verification-2026-06-24.md`

**Phase 1 (Security flagship) complete + verified.** Five components + guidebook + deck. 39 tests
across four packages, all CI-green. Verification pass fixed 1 HIGH + 6 MED findings (3 reviewers);
operational follow-ups (SHA-pin actions, gh-pages deploy, mypy, cosign backend) documented in the
report. Currency rechecked 2026-06-24 (3 minor pin drifts updated).

Next tracks: Fundamentals (01), Tooling (03), Architecture (02), Use cases (05), Exam prep (06).
Each follows the same TDD + guidebook + deck pattern.

**Research spikes for all remaining tracks complete (2026-06-24)** → `docs/research/spikes/`:
typescript-sdk, fastmcp-advanced, tool-design-eval, architecture-registry, a2a-integration,
kubernetes-mcp-server, quiz-app-railway. Key pins/gotchas captured (e.g. TS SDK stable lives on the
`v1.x` branch not `main`; Railway builder is now Railpack; A2A SDK `a2a-sdk` 1.1.0; k8s client 36.0.2).
Building tracks next, in order: Fundamentals → Tooling → Architecture → Use cases → Exam prep.

**Fundamentals (01) done:** Python FastMCP hello + typed/paginated catalog (9 tests), TypeScript
hello server (@modelcontextprotocol/sdk v1.29, 4 vitest tests + typecheck), guidebook + deck. Added a
`typescript` CI job. Go absent locally so Go/Rust accent deferred (would ship unrun).

**Tooling (03) done:** good-vs-anti-pattern tool pair + a deterministic offline eval harness (5
metrics, CI-safe), all four annotation hints (tested), guidebook + deck. 5 tests, ruff clean.

Open tension to raise: a global TypeScript rule (npm, exact pins, stricter tsconfig) conflicts with the
approved build-plan choice of pnpm + the verified pnpm pin. Kept pnpm for repo consistency; flag for
Michael's call before more TS lands.

**Architecture (02) done:** stateless handle pattern, server composition via mount(namespace),
registry server.json + offline validator + illustrative server card. 8 tests, ruff clean, guidebook + deck.

**Use cases (05) done:** read-only Kubernetes MCP server (injected CoreV1Api, offline tests with real
V1Pod models), MCP-to-agent A2A bridge (injected seam), ecosystem map, guidebook + deck. 5 tests.

**Exam prep (06) done:** ordered 13-module curriculum, FastAPI quiz app (validated YAML bank, pure
scoring, answers hidden, /health), Railway config (Railpack + uvicorn), guidebook + deck. 10 tests,
pristine output. Creating the Railway project is gated on Michael's go-ahead.

**ALL TRACKS COMPLETE.** Six post-foundation tracks built (security, fundamentals, tooling,
architecture, use-cases, exam-prep), all TDD, all CI-green, all promoted to main.

**Quiz app deployed to Railway (2026-06-25):** https://mcp-exam-quiz-production.up.railway.app
(project `mcp-exam-quiz`, id 9d556cc5-78b6-4b18-8a07-b845b5d33436, production env). Railpack/uv build,
verified live (/health, /exam answer-hidden, /exam/submit scoring). CLI deploy via `railway up` (not
GitHub-branch-connected); redeploy with `railway up` from `06-exam-prep/quiz-app/`.

Decisions: operational follow-ups will NOT be done (Michael, 2026-06-25). Kept pnpm (no npm switch).

**Browser quiz frontend added (2026-06-25):** `GET /` now serves `static/index.html` (vanilla-JS UI:
load /exam, radio options, submit, scored per-domain result), replacing the bare-URL 404. `/docs`
gives the Swagger explorer. Verified live after redeploy. On `staging` (`5a740a0`); **main promotion
was DENIED, so main (`25961cc`) is one commit behind staging** until Michael approves the main push.

**Exam bank rebuilt to an item-writing rubric (2026-06-25):** after Michael flagged that the original
questions were winged off training data, ran two spikes (`docs/research/spikes/exam-item-writing.md`,
`docs/research/spikes/mcp-question-content.md`) and rebuilt `questions.yaml` to v2 (18 items,
application-leaning, even option lengths, balanced answer positions, distractor-explaining rationales).
Encoded the rubric in `models.Question` + `tests/test_quality.py`. Redeployed; live and verified.

A full code + architecture review (3 reviewers) ran 2026-06-25. Must-fixes DONE 2026-06-25:
- HIGH: `search_items`/`contacts_search` now validate pagination (`Field(ge=1,le=100)` limit,
  `Field(ge=0)` cursor); limit=0/cursor<0 are rejected, no more infinite cursor loop. Tested.
- MED: quiz `static/index.html` rebuilt with createElement/textContent (no `.innerHTML` sink) plus
  fetch error handling; regression-guarded by a test.
- Minor: `get_pod_status` reads the named pod (read_namespaced_pod, 404 -> ToolError); added
  `03-tooling/test_contacts.py` (6 direct tests). Repo total now 96 tests (92 Python + 4 TS).

### Review remediation 2026-06-25 (round 2, after the 4-reviewer pass)
Fixed in code:
- Public quiz app hardened (the senior/arch HIGH credibility gap): externalized JS/CSS so a strict
  CSP applies (`default-src 'self'`, docs exempted), security headers, a request-body cap (413), a
  per-client rate limit (429), and a bounded `answers` map (Field max_length 500). All tested.
- signed-registry: `canonical_payload` is now injective JSON (no `\n`-join ambiguity); added a
  cross-signer rejection test.
- architecture handles: `create_basket` mints a uuid4 handle (removes the non-atomic counter race and
  predictable ids); docstring corrected re the in-process dict vs a shared store.
- oauth resource_server: non-list `aud` coerced safely (no TypeError on a scalar claim).
- policy-gateway audit: dropped `default=str` so non-JSON args fail loudly, not a non-deterministic hash.
- bank loader enforces unique ids; eval_harness `clear_params` no longer penalizes zero-param tools.
- Tightened weak tests (security-heaviest strict, scorecard full-equality), added /exam/submit
  negative tests. Spec spike `mcp-rc-2026-07-28-readiness.md` written + 3 spikes added to docs nav.

### Round 3 (2026-06-25): Michael said "do all of them" - all six DONE
1. Deploy traceability: GIT_SHA stamped + surfaced at /health (live shows the deployed commit). The
   GitHub auto-deploy *connection* is the only remaining piece and needs Michael's one-time Railway
   GitHub-App authorization (interactive); the SHA-traceability part is done.
2. SHA-pinned all CI actions to commit SHAs (checkout v7, setup-node v6, setup-uv v8); replaced the
   curl|sh uv install with pinned setup-uv; added `.github/dependabot.yml`.
3. mypy added to every package + shared root `mypy.ini`; CI type-checks each package (caught + fixed
   an untyped comprehension in contacts.py). Taskfile gains `py:types`.
4. De-dup: root `ruff.toml` (removed 9 copies); new CI `lockdrift` job (fastmcp/mcp must agree across
   the 10 locks).
5. Composed capstone server `04-security/capstone/` (registry admission + policy gateway + guardrails
   + audit in one path; 5 e2e tests prove they compose). The senior's "strongest absent artifact".
6. Observability: structlog JSON request logging + env-gated OTel on the quiz app; Railway app-sleep
   enabled (idle cost to zero).
Repo total: 108 tests (104 Python across 10 packages + 4 TS), all packages ruff + mypy clean.

Railway deploy is CLI-based (`railway up --service mcp-exam-quiz`), not GitHub-connected, so it does
not auto-deploy on push. Open question with Michael: connect Railway to the existing monorepo
(`peopleforrester/mcp_best_practices`) with service root dir `06-exam-prep/quiz-app` + watch path
(recommended), vs a separate repo. GitHub App authorization is an interactive dashboard action.

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
