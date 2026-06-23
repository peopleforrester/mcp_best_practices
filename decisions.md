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

## 2026-06-23T16:25:45Z · 1.3 · build plan APPROVED by Michael

Michael formally approved `docs/BUILD_PLAN.md`. Contract sealed: sha256:e0bb135ce836 (full:
e0bb135ce8360f252086110c37dcdbe3ae982c253ccf82d078a7878d24fd4df5). The plan is now read-only;
amendments require `/prd-amend` + re-approval. Advanced to Phase 2.2 to finish Phase 0 scaffolding.
2.1 Test is CONDITIONAL-skipped for the config scaffolding (root CLAUDE.md, settings.json, Taskfile,
CI shell, mkdocs.yml, README): no application logic to test yet. Test infrastructure (pytest/vitest)
lands with Phase 1 security code, where 2.1 becomes mandatory.
