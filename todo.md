# Remediation Progress: Round 7 (end-to-end review, 2026-07-03)

- [x] R1: TokenBucket eviction + param validation + event-loop note (S-M1/S-L7)
- [x] R2: bank loader per-entry isinstance -> labeled ValueError (T-M1)
- [x] R3: real ctx.elicit HITL demo in 03-tooling + fix false claims (WS-H3)
  - note: documented type-ignore for an observed fastmcp 3.4.2 + mypy 2.1 overload mis-resolution
    (minimal repro confirmed); runtime covered by 3 tests (accept-true, accept-false, decline)
- [x] R4: frontend a11y fieldset/legend + title/meta/favicon/backlink (T-M3/WS-L3)
  - surfaced: the wheel force-include block was redundant (hatchling default inclusion already ships
    every file under src/mcp_quiz, verified by wheel inspection); removed it. R13c's parity smoke
    remains the durable guard.
- [x] R5: 413-log comment (right-most) + peer-address fallback (T-M2/T-L5)
- [x] R6: small code cluster (k8s fake ns-read, is False, getData comment, basket annotations,
      Token.audience typing, defensive-branch comment)
- [ ] R7: exam bank (header wording, weak distractor rewrite, NSA CSI verification attempt)
- [ ] R8: security-track docs truth pass 2 (3 threat models' audit wording + markers, README table,
      guidebook sentence, gateway README eval order + scope note, capstone README, control lists)
- [ ] R9: front-door truth (README status/live URL/teaching index/cosign/Go-Rust/elicitation,
      docs index, CLAUDE.md map, quiz-app README, drop hardcoded test counts)
- [ ] R10: decks (03 offset, 06 live URL, 04 rate limiter)
- [ ] R11: sealed-plan banner on BUILD_PLAN
- [ ] R12: site content (guidebooks/threat models/ecosystem/curriculum in nav, decks as assets,
      site_url, strict green)
- [ ] R13: CI (Pages deploy, security scanning, wheel parity + SBOM, RC backstop cron)
- [ ] R14: Railway Wait-for-CI on (checkSuites was false)
- [ ] R15: wrap (gate, state, push, PR, verify deploys, journal)

## Deferred (with reasons)
- Deck CDN-only assets (fine once published); cosign real backend (planned; SBOM is the near-term nod)
- Carried: pagination DRY, A2A async seam, ts:test pnpm -r, TS depth, k8s Protocol typing, handles TTL,
  detector/redaction breadth
