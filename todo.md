# Remediation Progress — Round 5 (senior review 2026-06-26)

- [x] R1 (H1): registry server.json $schema → 2025-12-11 + currency-lock test
- [x] R2 (H3): capstone defaults to a real injection-finding sink + observing test
- [x] R3 (H2): rate limiter keys on right-most XFF + multi-hop test
- [x] R4 (M1): eval harness best-effort tool call (no crash on required params)
- [x] R5 (M2): move LocalSpecialist to the test tier, keep the Protocol seam shipped
- [x] R6 (M3): align redaction docstring with egress-only reality
- [ ] R7 (M4): registry validator checks package internals + fix the baked test
- [ ] R8 (M5): get_pod_status maps 403/500 to labeled ToolError + tests
- [ ] R9 (nits): strengthen wrong-invariant tests; narrow Ed25519 except; guidebook caveats
- [ ] R10 (config): pnpm/Node/TS pin drift, exactOptionalPropertyTypes, close dependabot branch

## Deferred (carried)
- M9 eval namespacing metric; A2A async seam; pagination DRY
- Taskfile ts:test `pnpm -r` bug (CI loops per-package; unaffected)
