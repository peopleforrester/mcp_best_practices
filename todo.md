# Progress: September 2026 currency sweep

- [x] 1: migrate all packages to FastMCP 4.0.4 / mcp 2.2.0 (151 python tests green)
- [x] 2: HITL rewritten for multi-round-trip (SEP-2322); 3 behaviour tests unchanged + 1 new mechanism test
- [x] 3: mcp 2.x snake_case rename applied across code (comments keep the wire names)
- [x] 4: preview package renamed to server-python-stateless; lockdrift exclusion removed
- [x] 5: docs refreshed (spec-currency rewritten, README, index, AGENTS, guidebooks, threat-models, MEMORY, PROJECT_STATE)
- [ ] 6: repoint the spec-currency reminder workflow
- [ ] 7: npm security alerts + version drift + code-scanning notes
- [ ] 8: ship (staging, CI, promote, close #50 and superseded PRs)

## Verified (2026-09-17)
- spec 2026-07-28 still current; fastmcp 4.0.4 stable since 2026-08-31; mcp 2.2.0; TS sdk 1.30.0.
