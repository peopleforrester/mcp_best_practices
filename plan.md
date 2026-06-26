# Remediation Plan — Round 5 (senior review 2026-06-26)

Full pass over the 2026-06-26 senior review. TDD per phase: red test, minimal fix, full gate, one
commit. Two prior rounds' plans are superseded; the audit trail lives in decisions.md / PROJECT_STATE.md.

## Phases

1. **H1 — registry $schema is stale.** server.json pins 2025-09-29; 2025-12-11 exists (verified live
   2026-06-27) and the repo's own spike already documents it. Bump to 2025-12-11 and add a test that
   asserts the shipped $schema matches the expected current version so CI catches future drift.
2. **H3 — capstone discards injection findings.** finding_sink defaults to discard and no test observes
   a finding. Default the capstone to a real (structlog) sink and add a test proving a detected
   injection in a tool result produces an observable finding.
3. **H2 — rate limiter keys on the spoofable leftmost XFF.** Flip to the right-most entry (Michael's
   call) and add a multi-hop XFF test. Comment notes the contested Railway nuance and that edge
   rate-limiting is the production control.
4. **M1 — eval harness crashes on required-param tools.** It calls every tool with {}. Make the call
   best-effort: on a ToolError, skip the response-size probe (log it), still score the static metrics.
   Add a required-param tool to the test server and assert no crash.
5. **M2 — A2A demo ships a canned delegate in production source.** Move LocalSpecialist into the test
   tier, drop it from the package __init__ exports, keep the AgentDelegate Protocol seam shipped.
6. **M3 — redaction docstring overclaims input coverage.** The composed middleware sanitizes egress
   only. Align the docstring with what the path actually does.
7. **M4 — registry validator accepts uninstallable entries.** packages: [{}] passes. Validate each
   package has identifier / registryType / transport; fix the test that baked the empty object as valid.
8. **M5 — get_pod_status error mapping is asymmetric and untested.** Map 403/500 to labeled ToolErrors
   like find_pods; add tests for the 403/500 paths.
9. **Nits cluster.** Strengthen wrong-invariant tests (/exam checks every item, findings assert real
   content, gateway/passthrough/A2A tests assert behavior not tautology); narrow the Ed25519 except;
   one-line guidebook notes for the policy allow-rule foot-gun and OAuth signed-byte caveat.
10. **Config/pin drift.** packageManager pnpm pin vs CLAUDE.md, TS caret ranges → exact pins,
    exactOptionalPropertyTypes on, reconcile Node version note. Close the open dependabot remote branch.

## Deferred (carried)
- M9 eval-namespacing metric, A2A async seam, pagination DRY (from round 4).
- Taskfile ts:test `pnpm -r` bug (CI loops per-package; unaffected).
