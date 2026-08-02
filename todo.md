# Progress: MCP 2026-07-28-final adoption (framing flip + labeled preview)

- [ ] P1: rewrite docs/spec-currency.md to 2026-07-28-final reality + SDK-support state
- [ ] P2: front door (README, docs/index, CLAUDE.md, AGENTS.md, PROJECT_STATE, MEMORY, mkdocs)
- [ ] P3: threat models (6) + guidebooks + decks spec-boundary wording
- [ ] P4: RC-readiness spike superseded; version-currency framing; reminder cron repointed
- [ ] P5: labeled preview server on fastmcp 4.0-beta / mcp 2.0 (verify API first; exclude from lockdrift)
- [ ] P6: exam bank "RC, not final" items corrected + curriculum RC notes
- [ ] P7: verify + wrap (gate, state, push, CI, PR, deploys, journal)

## Verified (2026-07-28, primary sources)
- 2026-07-28 spec FINAL (blog.modelcontextprotocol.io). mcp 2.0.0 final; fastmcp 3.4.5->mcp1.29 stable,
  4.0.0b1->mcp2.0 beta; TS sdk 1.30.0.

## Integration landmines
- lockdrift CI enforces one fastmcp/mcp version across locks -> exclude the preview package.
- CI python matrix runs all packages -> the beta-dep preview must install + test green in CI.
