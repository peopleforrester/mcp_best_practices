# Remediation Progress — Round 6 (senior review 2026-07-02)

- [x] T1 (H1 credibility): token-bucket rate limiter in the policy gateway + audit + tests
- [x] T2 (my prior error): k8s find_pods drop dead 404 mapping; fix test; missing-ns-empty test
- [x] T3 (boot crash): YAML bank loader hardening (clear errors, catch YAMLError)
- [x] T4 (side-effect): eval invokes only readOnlyHint tools; annotate demo read tools; concise unmeasured state
- [ ] T5 (doc accuracy): eval namespaced/invokes-once/no-side-effects; guardrails README ingress claim
- [ ] T6 (observability): body-cap 413 path emits a structured log line
- [ ] T7 (stale docs): use-cases README test count 5 -> 7
- [ ] T8 (systemic claim drift): reconcile threat-model gateway claims; fixed-identity caveat;
      structured-redaction on any value; consent audit rule; server-card.json

## Deferred (carried, intentional)
- Injection detector / redaction breadth (documented heuristic/best-effort)
- Pagination DRY across packages; A2A async seam; Taskfile ts:test pnpm -r bug
- TS track depth (no TS catalog analog); gateway per-request identity wiring (doc caveat only)

## Also outstanding
- Backfill round-5 + round-6 into the engineering journal at the end
