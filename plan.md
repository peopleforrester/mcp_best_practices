# Remediation Plan — Round 6 (senior review 2026-07-02)

Full pass over the round-6 senior review. Findings independently verified before acting. TDD per phase:
red test, minimal fix, full gate, one commit. Prior rounds' plans superseded; audit trail in
decisions.md / PROJECT_STATE.md.

## Phases

1. **T1 (rate limiter, credibility gap): the policy gateway now enforces the per-client rate limit the
   threat models claim.** Six threat-model rows cite "per-client rate limiting at the policy gateway"
   but no limiter exists in the gateway. Add a token-bucket limiter (injected clock), wire it into the
   engine's decision path so an over-limit call is a DENY with reason "rate limit exceeded", matched
   rule "rate_limit", and a normal audit record. Per Michael: implement it, do not soften the docs.
2. **T2 (k8s find_pods 404 is dead code, my prior-round error): drop the 404 mapping.**
   `list_namespaced_pod` on a missing namespace returns HTTP 200 + empty list, never 404, so the
   404 -> "namespace not found" branch cannot fire. Remove it, keep 403 + generic; fix the round-5
   test that fed a synthetic 404, and add a test that a missing namespace yields count 0.
3. **T3 (YAML loader crashes on boot): harden bank.py.** An empty file (`None`) or a missing
   `questions` key raises TypeError/KeyError at import time -> Railway restart loop. Guard with
   `isinstance` + key presence -> clear ValueError; catch `yaml.YAMLError`.
4. **T4 (eval side-effect overclaim): the harness only invokes read-only tools.** It calls every
   no-required-param tool with `{}`, which would execute a mutating no-arg tool. Restrict invocation to
   tools annotated `readOnlyHint=True`; annotate the demo read tools (correct tool design anyway). A
   mutating no-arg tool is not invoked.
5. **T5 (eval doc accuracy): correct the guidebook/docstrings.** The `namespaced` metric checks
   snake_case + a separator, not a verified domain prefix; the harness does not "invoke each once"
   (required-param and non-read-only tools are skipped) and is only side-effect-free over read-only
   tools; `concise_response` is unmeasured (defaults true) for uninvoked tools. Say all of that plainly.
6. **T6 (oversized-body path is invisible): log the 413.** The body-cap middleware is outermost, so an
   over-limit request returns 413 before the logging/rate-limit guard, leaving a public un-throttled,
   unlogged path. Emit a structured log line on the 413 branch so it is observable.
7. **T7 (stale docs): fix the use-cases README test count (5 -> 7) and any other stale counts found.**
8. **T8 (systemic claim drift, security-flagship H1): reconcile the threat-model / README gateway
   claims with what the gateway implements.** The threat models attribute token/iss/exp/aud validation,
   tool-description pinning, per-call audience re-check, and budgets to the policy gateway; none are
   wired (the OAuth package is standalone). Relabel those mitigations as "target design" or
   "demonstrated separately in oauth-confused-deputy/", keeping only what the gateway actually does
   (allowlist, consent, deny/allow rules, audit, and now the token-bucket rate limit from T1) as
   "implemented." Add a docstring caveat that the adapter uses a fixed demo client identity (M1), and
   fix the guardrails README body still claiming ingress coverage (M2). Folded low items: sanitize any
   structured value not just dicts (L1); distinguish the consent-satisfied audit rule (L5); validate or
   drop the drifting server-card.json; make eval `concise_response` a third unmeasured state excluded
   from the score rather than a free pass.

## Deferred (carried, still intentional)
- Injection detector / redaction breadth (documented heuristic/best-effort).
- Pagination DRY across packages (cross-package independence is intentional).
- A2A async seam (labeled demo); Taskfile `ts:test` `pnpm -r` bug (CI loops per-package).
- Gateway per-request identity is a fixed demo constant (guidebook caveat, not wired to a session).

## Also outstanding (not from this review)
- Round-5 session was never journaled; backfill round 5 + round 6 into the engineering journal at the end.
