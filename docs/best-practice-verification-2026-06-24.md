<!-- ABOUTME: Best-practice verification of the repo as of 2026-06-24: currency, correctness, alignment.
ABOUTME: Records the deterministic checks, the review findings, what was fixed, and what is deferred. -->

# Best-Practice Verification (2026-06-24)

Verification that the MCP portfolio, through the completed security flagship track, follows current
best practice. Three independent reviews plus deterministic checks. Substantive findings were fixed
in this pass; the rest are recorded as deliberate follow-ups.

## Verdict

The path is sound and current. The security track is built on the latest stable spec, maps to the
authoritative frameworks (OWASP MCP Top 10, NSA CSI, the MCP authorization spec, RFC 8707), and is
test-first with real cryptography and a real FastMCP integration rather than mocks. The fixes below
closed one HIGH correctness issue and several medium items; the deferred items are operational
hardening that does not change correctness.

## Deterministic checks

- **Tests:** 39 across four packages, all passing (policy-gateway 15, guardrails 11,
  oauth-confused-deputy 8, signed-registry 5).
- **Lint:** ruff clean in every package.
- **Docs:** `mkdocs build --strict` passes (no broken nav or links).
- **Prose:** no em-dashes in authored docs.
- **Reproducibility:** Python pinned via `.python-version` (3.13); suite re-verified on it.

## Currency recheck (2026-06-24)

The pinned versions were re-verified against official sources. The two time-sensitive facts hold: the
`2026-07-28` spec is still a Release Candidate (not final), and the Python SDK v2 beta has not shipped
(still alpha; the 2026-06-30 target is days away). Three minor drifts within the same lines were found
and the pins updated: rmcp 1.7 to 1.8, C#/.NET SDK 1.2 to 1.4, pnpm 11.8.x to 11.9.0. Detail in
`research/version-currency-2026-06-23.md`.

## Findings fixed in this pass

| Sev | Area | Finding | Fix |
|---|---|---|---|
| HIGH | signed-registry | A malformed trusted-signer key raised `ValueError` in the admission path (crash, not reject) | Parse keys once at construction; a malformed key is stored unusable so admission fails closed. Added a malformed-key test. |
| MED | policy-gateway | ALLOW rules were dead code (consent gate ran first), misleading a maintainer | ALLOW rules now run before the consent gate and satisfy it (operator pre-authorization). Added allow-rule and deny-wins tests. |
| MED | policy-gateway | `audit_sink` defaulted to silent discard (violates the no-silent-fallback rule) | Made `audit_sink` a required argument. |
| MED | guardrails | "default-deny" framing overstated a best-effort regex redactor | Reframed as best-effort/not-exhaustive; added PEM, GitHub fine-grained PAT, and JWT shapes; one redaction recorded per occurrence. Added multi-finding and new-shape tests. |
| MED | oauth-demo | `aud` modeled only as a string; RFC 8707 permits an array | Validation accepts string or list audiences. Added a list-audience test. |
| MED | oauth-demo | Passthrough prohibition was only a side effect of the audience check | Added `gateway_forward` that structurally refuses to forward an inbound token (`TokenPassthroughForbidden`). Added a test. |
| MED | CI | No concurrency control or job timeouts; PR runs duplicated push runs | Added `concurrency` with cancel-in-progress, `timeout-minutes` per job, and a `pull_request` branch filter. |

## Deferred follow-ups (operational, not correctness)

Recorded here rather than fixed now, because this is a teaching portfolio (not production) and these
do not change behavior or correctness:

- **Pin GitHub Actions to commit SHAs** and adopt `astral-sh/setup-uv` (caching) plus a Dependabot
  config for `github-actions`, `uv`, and `npm`. The github rule prefers SHA pinning.
- **Publish the docs** via a `gh-pages` deploy job on `main`.
- **Add mypy** to the dev groups and a type-check CI step.
- **Broaden ruff rule selection** (`I`, `UP`, `B`) beyond the defaults.
- **A `server.py` wiring example** showing `mcp.add_middleware(PolicyMiddleware(...))` mounted on a
  real server, plus a smoke test.
- **cosign/sigstore `Verifier` backend** for the signed registry (integration-tested), and a
  length-prefixed canonical entry encoding.
- **CodeQL** code scanning.

## What is genuinely well done (per the reviews)

- The policy core is framework-independent with the FastMCP adapter isolated and verified end to end
  against the real library via the in-memory client.
- The audit no-leak guarantee (sha256 fingerprint, never raw arguments) is real and tested at unit
  and end-to-end levels.
- Ed25519 signing and verification use the `cryptography` library correctly, with signature checked
  before any claim is trusted, and the unsigned/untrusted/tampered cases covered with real keys.
- Packaging uses src-layout, committed lockfiles, PEP 735 dependency groups, and least-privilege
  `GITHUB_TOKEN`.
