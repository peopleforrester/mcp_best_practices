# Remediation Plan: Round 7 (end-to-end architecture + code + website review, 2026-07-03)

Full pass over four parallel review reports (architecture five-pillar, website/presentation, security
flagship fresh pass, non-security tracks fresh pass). Findings independently verified before acting.
TDD per phase where testable; one commit per phase; staging -> CI -> PR to main. Prior rounds' plans
superseded; audit trail in decisions.md / PROJECT_STATE.md.

## Code phases (risk-first)

- **R1 (S-M1/S-L7): TokenBucket hardening.** The gateway's DoS control is itself a memory-DoS vector
  under attacker-controlled client ids: `_state` never evicts (the quiz app's limiter does). Add
  stale-entry eviction past a max_principals cap, validate capacity/refill in __post_init__, and add a
  one-sentence single-threaded-event-loop note. Tests for eviction and bad params.
- **R2 (T-M1): bank loader per-entry type check.** A non-dict question entry escapes round 6's
  hardening as a context-free TypeError at import. isinstance per entry -> labeled ValueError + test.
- **R3 (WS-H3): implement the elicitation/HITL demo the docs already claim.** Zero `elicit` calls
  exist repo-wide while README/docs/CLAUDE.md/guidebook claim it (the guidebook falsely says it is
  used in the security track). Build a small real `ctx.elicit` confirmation flow in 03-tooling
  (verify the installed FastMCP 3.4.2 API first), tested with the in-memory client's
  elicitation_handler; then fix the wording everywhere to point at the real module.
- **R4 (T-M3/WS-L3): public frontend a11y + polish.** fieldset/legend per question (radio groups are
  not associated with stems), plus title, meta description, favicon, and a repo backlink. Lock with
  asset tests.
- **R5 (T-M2/T-L5): 413-log consistency.** Fix my round-7 comment that says "left-most" XFF where the
  code (correctly) takes right-most; fall back to the ASGI peer address instead of "unknown".
- **R6 (small code cluster):** k8s fake read_namespaced_pod filters by namespace (T-L4);
  test_eval `is False` not falsy (T-L1); comment explaining getData's readOnlyHint (T-L2);
  ToolAnnotations on the basket tools (T-L8); `Token.audience: str | list[str]` typing (S-L8);
  honest "defensive, unreachable under FastMCP 3.4.2" comment on the list write-back branch (S-L6).
- **R7 (exam bank): item quality.** Header overclaim ("never the longest" -> matches the enforced
  <=40% rule) (T-L6); rewrite the throwaway q-mcp-vs-a2a distractor into a real misconception (T-L9);
  attempt primary-source verification of the q-nsa-egress NSA CSI paraphrase (T-L7), time-boxed:
  verified -> tighten wording, unverifiable -> keep the honest caveat and log it.

## Documentation-truth phases

- **R8 (S-M2/S-M3/S-M4/S-L5/S-L9/WS-M4): security-track claim reconciliation, part 2.** The three
  threat models round 6 did not edit describe an audit record with raw parameters + result hash,
  contradicting the shipped fingerprint-only design (wrong even as target design); the README's
  "marked inline" promise is false for those files, and its "built control" table lists unbuilt
  controls. Fix client.md/host.md/data-stores.md audit wording + inline markers, correct the README
  table, fix the guidebook's "gateway calls these on arguments and results" sentence, add the rate
  limiter to the gateway README evaluation order (now factually wrong), capstone README, guidebook
  control list, and a tools/call-only scope note.
- **R9 (WS-H1/WS-H2/W3/WS-M1/W4/WS-L2/WS-L4/A-M2 + count policy): front-door truth.** Rewrite the
  README status (six tracks shipped, in review/maintenance), add the live quiz URL + a
  teaching-material index, fix cosign -> "Ed25519 today, cosign planned", Go/Rust -> planned, update
  elicitation wording to point at R3's real code, "conformance-style" in docs/index, fix CLAUDE.md
  map (glossary, elicitation row), quiz-app README (ABOUTME contradiction, retired railway-up flow,
  logs-only observability posture), and drop hardcoded test counts from track READMEs (third
  staleness in three rounds; counts live in CI, not prose).
- **R10 (WS-M3/WS-M5 + rate-limit deck row): deck touch-ups.** 03 deck cursor -> offset; 06 deck
  Railway slide -> live URL; 04 deck control list gains the rate limiter.
- **R11 (WS-M2): sealed-plan banner.** Admonition atop docs/BUILD_PLAN.md: sealed 2026-06-23, live
  status in PROJECT_STATE.md; remove ambiguity of the "current" marker without editing the sealed
  body. Logged in decisions.md (banner is a reading note, not a plan change).

## Site + CI + infra phases

- **R12 (W1/W2/WS-H5): publish the teaching content on the site.** Bring guidebooks, threat models,
  ecosystem map, and curriculum into the MkDocs nav (wrapper/symlink mechanism; convert code-relative
  links that strict mode flags into GitHub blob URLs), ship the six Reveal decks as static assets,
  set site_url. Strict build green locally.
- **R13 (A-H1/A-H2/A-M1/A-L2): CI upgrades.** (a) Pages deploy job on main + enable Pages
  (build_type workflow); (b) security scanning: osv-scanner/pip-audit over the uv locks + CodeQL
  (python, js/ts), SHA-pinned per repo convention; (c) quiz-app wheel parity smoke (build wheel,
  clean-install, hit /health and /) + CycloneDX SBOM artifact; (d) scheduled RC-final backstop
  (cron opens/updates a dated issue ahead of 2026-07-28).
- **R14 (A-L1, verified checkSuites:false): enable Railway "Wait for CI"** via the service
  repo-trigger mutation. Infra mutation, reversible, called out in the summary.
- **R15: wrap.** Full repo gate, PROJECT_STATE/decisions/CHANGELOG, push staging, CI green, PR to
  main, merge, verify Railway deploy + Pages live, journal the session.

## Deferred (with reasons)

- Decks load Reveal from CDN only (WS-L5): acceptable once published online; offline presenting is
  not a current use case.
- Carried from prior rounds: pagination DRY, A2A async seam, Taskfile ts:test pnpm -r bug, TS track
  depth, k8s Any-vs-Protocol, handles TTL, injection-detector/redaction breadth.
- Cosign/sigstore real backend: still planned; SBOM step in R13c is the near-term provenance nod.
